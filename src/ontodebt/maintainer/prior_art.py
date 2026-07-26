"""L2 trigger: prior-art watch with a fetch-then-quote verifier.

Searches arXiv, OpenAlex, and (token permitting) GitHub for recent work that
overlaps this project's novelty claim, scores candidates with a committed
keyword table, and - the load-bearing part - refuses to surface anything it
cannot *re-fetch by id* with the stored verbatim quote contained in the
re-fetched text. A fabricated citation cannot produce a real fetched quote;
this is the structural answer to the project's "LLM-hallucinated citations"
burn. There is no LLM anywhere in this module.

Verified candidates go into a digest issue for the human, who alone writes
any related-work sentence. Only candidates that actually reached a digest
are marked seen; verification failures are retried on the next run rather
than silently buried.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from pathlib import Path

from ._common import (
    FetchError,
    github_output,
    http_get,
    http_get_json,
    load_json,
    normalize_ws,
    save_json,
    utc_today,
)

DEFAULT_CONFIG = Path("maintainer/config.json")
DEFAULT_SEEN = Path("maintainer/prior_art_seen.json")
DEFAULT_STATE_DIR = Path("maintainer/state")
OWN_REPO = "dimaggi-ai/ontology-debt"
MIN_QUOTE_CHARS = 40  # a shorter "quote" verifies nothing

ATOM = "{http://www.w3.org/2005/Atom}"


@dataclass(frozen=True)
class Candidate:
    source: str      # arxiv | openalex | github
    ident: str       # stable id used for re-fetch and dedupe
    title: str
    url: str
    quote: str       # verbatim text captured at search time
    published: str = ""
    score: int = 0


# --------------------------------------------------------------------------- search

def search_arxiv(query: str, max_results: int) -> list[Candidate]:
    url = (
        "http://export.arxiv.org/api/query?search_query="
        + urllib.parse.quote(f"all:{query}")
        + f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    root = ET.fromstring(http_get(url))
    out = []
    for entry in root.findall(f"{ATOM}entry"):
        raw_id = (entry.findtext(f"{ATOM}id") or "").rsplit("/", 1)[-1]
        ident = re.sub(r"v\d+$", "", raw_id)
        summary = (entry.findtext(f"{ATOM}summary") or "").strip()
        if not ident or not summary:
            continue
        out.append(
            Candidate(
                source="arxiv",
                ident=ident,
                title=(entry.findtext(f"{ATOM}title") or "").strip(),
                url=f"https://arxiv.org/abs/{ident}",
                quote=summary[:400],
                published=(entry.findtext(f"{ATOM}published") or "")[:10],
            )
        )
    return out


def _openalex_abstract(work: dict) -> str:
    index = work.get("abstract_inverted_index")
    if not index:
        return ""
    positions: dict[int, str] = {}
    for word, spots in index.items():
        for spot in spots:
            positions[spot] = word
    return " ".join(positions[i] for i in sorted(positions))


def search_openalex(query: str, per_page: int, mailto: str) -> list[Candidate]:
    url = (
        "https://api.openalex.org/works?filter=title_and_abstract.search:"
        + urllib.parse.quote(query)
        + f"&sort=publication_date:desc&per-page={per_page}"
        + (f"&mailto={urllib.parse.quote(mailto)}" if mailto else "")
    )
    data = http_get_json(url)
    out = []
    for work in data.get("results", []):
        ident = str(work.get("id", "")).rsplit("/", 1)[-1]  # W123...
        abstract = _openalex_abstract(work)
        if not ident or not abstract:
            continue
        out.append(
            Candidate(
                source="openalex",
                ident=ident,
                title=str(work.get("display_name", "")),
                url=str(work.get("doi") or work.get("id", "")),
                quote=abstract[:400],
                published=str(work.get("publication_date", "")),
            )
        )
    return out


def search_github(query: str, token: str, per_page: int) -> list[Candidate]:
    url = (
        "https://api.github.com/search/repositories?q="
        + urllib.parse.quote(query)
        + f"&sort=updated&order=desc&per_page={per_page}"
    )
    data = http_get_json(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    out = []
    for repo in data.get("items", []):
        ident = str(repo.get("full_name", ""))
        description = (repo.get("description") or "").strip()
        if not ident or ident == OWN_REPO or not description:
            continue
        out.append(
            Candidate(
                source="github",
                ident=ident,
                title=ident,
                url=str(repo.get("html_url", "")),
                quote=description[:400],
                published=str(repo.get("pushed_at", ""))[:10],
            )
        )
    return out


# --------------------------------------------------------------------------- scoring

def score_text(text: str, keywords: dict[str, int]) -> int:
    """Presence-based (not count-based) so keyword stuffing cannot inflate."""
    low = normalize_ws(text)
    return sum(weight for term, weight in keywords.items() if term.lower() in low)


# --------------------------------------------------------------------------- verify

def resolve_arxiv(ident: str) -> str:
    url = "http://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(ident)
    root = ET.fromstring(http_get(url))
    entry = root.find(f"{ATOM}entry")
    if entry is None:
        raise FetchError(f"arxiv id {ident} did not resolve")
    return (entry.findtext(f"{ATOM}title") or "") + " " + (entry.findtext(f"{ATOM}summary") or "")


def resolve_openalex(ident: str) -> str:
    work = http_get_json("https://api.openalex.org/works/" + urllib.parse.quote(ident))
    return str(work.get("display_name", "")) + " " + _openalex_abstract(work)


def resolve_github(ident: str, token: str) -> str:
    owner_repo = ident.split("/")
    if len(owner_repo) != 2:
        raise FetchError(f"malformed repo id {ident}")
    repo = http_get_json(
        "https://api.github.com/repos/" + urllib.parse.quote(ident, safe="/"),
        headers={"Authorization": f"Bearer {token}"} if token else None,
    )
    return str(repo.get("full_name", "")) + " " + str(repo.get("description") or "")


def verify_candidate(candidate: Candidate, resolvers: dict) -> tuple[bool, str]:
    """The anti-hallucination gate: re-fetch by id, require the stored quote
    verbatim (whitespace-normalized) inside the re-fetched text."""
    if len(candidate.quote) < MIN_QUOTE_CHARS:
        return False, f"quote too short to verify ({len(candidate.quote)} chars)"
    resolver = resolvers.get(candidate.source)
    if resolver is None:
        return False, f"no resolver for source {candidate.source!r}"
    try:
        fetched = resolver(candidate.ident)
    except FetchError as exc:
        return False, f"id did not resolve: {exc}"
    if normalize_ws(candidate.quote) not in normalize_ws(fetched):
        return False, "stored quote not found in re-fetched source"
    return True, "verified"


# --------------------------------------------------------------------------- digest

def _clean_md(text: str) -> str:
    """Neutralize markdown/comment injection from third-party titles/quotes:
    anyone can publish a paper or repo description, so these strings are
    untrusted input to the issue body."""
    text = normalize_ws(text.replace("<!--", " ").replace("-->", " ").replace("```", " "))
    return text.replace("|", "\\|").replace("#", "\\#")


def _safe_url(url: str) -> str:
    return url if url.startswith(("http://", "https://")) else "(no https url)"


def render_digest(verified: list[Candidate], dropped: list[tuple[Candidate, str]]) -> tuple[str, str]:
    title = f"Prior-art watch {utc_today()}: {len(verified)} verified candidate(s)"
    lines = [
        "<!-- ontodebt-maintainer:prior-art -->",
        "Candidates below passed the fetch-then-quote verifier: each id was",
        "re-fetched and the quoted text was found verbatim in the source. The",
        "agent surfaces; a human decides whether the related-work table changes.",
        "Deterministic keyword scoring - no LLM ranked or summarized anything.",
        "",
    ]
    for c in verified:
        lines += [
            f"### {_clean_md(c.title) or c.ident}",
            f"- source: {c.source} | id: `{c.ident}` | published: {c.published or '?'} | score: {c.score}",
            f"- link: {_safe_url(c.url)}",
            f"> {_clean_md(c.quote)[:300]}",
            "",
        ]
    if dropped:
        lines += ["<details><summary>Dropped by the verifier (retried next run)</summary>", ""]
        lines += [f"- {c.source}:`{c.ident}` - {reason}" for c, reason in dropped]
        lines += ["", "</details>"]
    return title, "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- main

def run_watch(
    config: dict,
    seen: dict,
    env: dict,
    searchers: dict | None = None,
    resolvers: dict | None = None,
) -> tuple[list[Candidate], list[tuple[Candidate, str]], dict]:
    pa = config.get("prior_art", {})
    queries: list[str] = pa.get("queries", [])
    keywords: dict[str, int] = pa.get("keywords", {})
    threshold = int(pa.get("threshold", 8))
    per_query = int(pa.get("max_results_per_query", 20))
    cap = int(pa.get("max_candidates_per_run", 10))
    token = env.get("GITHUB_TOKEN", "")
    mailto = env.get("OPENALEX_MAILTO", "")

    if searchers is None:
        searchers = {
            "arxiv": lambda q: search_arxiv(q, per_query),
            "openalex": lambda q: search_openalex(q, per_query, mailto),
        }
        if token:
            searchers["github"] = lambda q: search_github(q, token, min(per_query, 10))
    if resolvers is None:
        resolvers = {
            "arxiv": resolve_arxiv,
            "openalex": resolve_openalex,
            "github": lambda ident: resolve_github(ident, token),
        }

    seen_ids = set(seen.get("seen", []))
    found: dict[tuple[str, str], Candidate] = {}
    health = {name: {"attempts": 0, "failures": 0} for name in searchers}
    for query in queries:
        for name, search in searchers.items():
            health[name]["attempts"] += 1
            try:
                results = search(query)
            except FetchError as exc:
                health[name]["failures"] += 1
                print(f"warning: {name} search failed for {query!r}: {exc}", file=sys.stderr)
                continue
            for c in results:
                key = (c.source, c.ident)
                if f"{c.source}:{c.ident}" in seen_ids or key in found:
                    continue
                score = score_text(c.title + " " + c.quote, keywords)
                if score >= threshold:
                    found[key] = replace(c, score=score)

    ranked = sorted(found.values(), key=lambda c: (-c.score, c.source, c.ident))[:cap]
    verified: list[Candidate] = []
    dropped: list[tuple[Candidate, str]] = []
    for c in ranked:
        ok, reason = verify_candidate(c, resolvers)
        if ok:
            verified.append(c)
        else:
            dropped.append((c, reason))

    new_seen = dict(seen)
    new_seen["seen"] = sorted(seen_ids | {f"{c.source}:{c.ident}" for c in verified})
    return verified, dropped, new_seen, health


def main(
    argv: list[str] | None = None,
    searchers: dict | None = None,
    resolvers: dict | None = None,
    env: dict | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--seen", type=Path, default=DEFAULT_SEEN)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument("--github-output", default=None)
    args = parser.parse_args(argv)

    import os

    config = load_json(args.config, None)
    if config is None:
        print(f"config not found: {args.config}", file=sys.stderr)
        return 1
    seen = load_json(args.seen, {"seen": []})

    verified, dropped, new_seen, health = run_watch(
        config, seen, dict(os.environ) if env is None else env, searchers, resolvers
    )

    # Fail-open is not allowed to be silent: a searcher that failed every
    # query gets a warning annotation; a fully blind watch goes red.
    fully_failed = sorted(
        name for name, h in health.items() if h["attempts"] and h["failures"] == h["attempts"]
    )
    attempted = [name for name, h in health.items() if h["attempts"]]
    if attempted and len(fully_failed) == len(attempted):
        print(f"PRIOR-ART WATCH BLIND (red by design): every searcher failed "
              f"every query: {fully_failed}", file=sys.stderr)
        return 1
    for name in fully_failed:
        print(f"::warning::prior-art searcher fully failed this run: {name}")
    if verified:
        save_json(args.seen, new_seen)
        title, body = render_digest(verified, dropped)
        state_dir = Path(args.state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "prior-art-issue.md").write_text(body)
    else:
        title = ""

    print(f"verified={len(verified)} dropped={len(dropped)}")
    github_output(
        {"novel": len(verified), "issue_title": title, "seen_changed": str(bool(verified)).lower()},
        args.github_output,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
