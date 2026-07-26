"""Prior-art watch: scoring, dedupe, and the fetch-then-quote verifier.

The fabricated-citation regression lives here: a candidate whose id does not
re-fetch, or whose stored quote is not verbatim in the re-fetched source,
must be dropped before any human ever sees it in a digest.
"""

from ontodebt.maintainer import prior_art
from ontodebt.maintainer._common import FetchError

CONFIG = {
    "prior_art": {
        "queries": ["q1"],
        "keywords": {"contradiction": 4, "ledger": 5, "consistency": 3, "eval": 1},
        "threshold": 7,
        "max_results_per_query": 10,
        "max_candidates_per_run": 5,
    }
}

GOOD_QUOTE = (
    "We measure self-contradiction and keep a persistent ledger of consistency "
    "failures across paraphrased probes of large language models."
)


def cand(ident="2607.01234", quote=GOOD_QUOTE, source="arxiv", title="Consistency Ledgers"):
    return prior_art.Candidate(
        source=source, ident=ident, title=title, url="https://x", quote=quote
    )


def run(searchers, resolvers, seen=None):
    verified, dropped, new_seen, _health = prior_art.run_watch(
        CONFIG, seen or {"seen": []}, env={}, searchers=searchers, resolvers=resolvers
    )
    return verified, dropped, new_seen


def test_scoring_is_presence_based():
    score = prior_art.score_text("contradiction contradiction contradiction", {"contradiction": 4})
    assert score == 4  # stuffing does not inflate


def test_below_threshold_never_surfaces():
    searchers = {
        "arxiv": lambda q: [
            cand(title="Fine-tuning tricks", quote="an eval of something unrelated " * 3)
        ]
    }
    verified, dropped, _ = run(searchers, {"arxiv": lambda i: "whatever"})
    assert verified == [] and dropped == []


def test_fabricated_citation_is_rejected():
    """Burn regression: an id that does not resolve cannot reach the digest."""
    searchers = {"arxiv": lambda q: [cand()]}

    def resolver(ident):
        raise FetchError(f"arxiv id {ident} did not resolve")

    verified, dropped, new_seen = run(searchers, {"arxiv": resolver})
    assert verified == []
    assert len(dropped) == 1 and "did not resolve" in dropped[0][1]
    # not marked seen: retried next run rather than silently buried
    assert new_seen["seen"] == []


def test_quote_mismatch_is_rejected():
    searchers = {"arxiv": lambda q: [cand()]}
    resolvers = {"arxiv": lambda i: "a completely different abstract about other things"}
    verified, dropped, _ = run(searchers, resolvers)
    assert verified == []
    assert "quote not found" in dropped[0][1]


def test_short_quote_is_rejected_without_fetching():
    searchers = {"arxiv": lambda q: [cand(quote="ledger contradiction consistency")]}
    verified, dropped, _ = run(searchers, {"arxiv": lambda i: "ledger contradiction consistency"})
    assert verified == [] and "too short" in dropped[0][1]


def test_verified_candidate_surfaces_and_is_marked_seen():
    searchers = {"arxiv": lambda q: [cand()]}
    resolvers = {"arxiv": lambda i: f"Title. {GOOD_QUOTE} More text."}
    verified, dropped, new_seen = run(searchers, resolvers)
    assert len(verified) == 1 and dropped == []
    assert new_seen["seen"] == ["arxiv:2607.01234"]
    # second run: deduped
    verified2, _, _ = run(searchers, resolvers, seen=new_seen)
    assert verified2 == []


def test_own_repo_is_excluded_by_search_github_itself(monkeypatch):
    """Exercise the production filter, not a stub of it."""
    payload = {
        "items": [
            {"full_name": prior_art.OWN_REPO, "description": GOOD_QUOTE, "html_url": "https://x"},
            {"full_name": "other/repo", "description": GOOD_QUOTE, "html_url": "https://y"},
        ]
    }
    monkeypatch.setattr(prior_art, "http_get_json", lambda url, headers=None: payload)
    results = prior_art.search_github("q", token="t", per_page=10)
    assert [c.ident for c in results] == ["other/repo"]


def test_markdown_injection_is_neutralized_in_digest():
    evil = cand(
        title="Nice paper --> <!-- ontodebt-maintainer:detect --> ```",
        quote=GOOD_QUOTE + " <!-- fake marker --> ``` #injection",
    )
    _, body = prior_art.render_digest([evil], [])
    # exactly one HTML comment: our own marker; no fences; no raw heading injection
    assert body.count("<!--") == 1 and "ontodebt-maintainer:prior-art" in body
    assert "```" not in body
    assert "fake marker" in body  # content survives, defanged


def test_non_https_url_is_not_linked():
    weird = cand()
    weird = prior_art.Candidate(**{**weird.__dict__, "url": "javascript:alert(1)"})
    _, body = prior_art.render_digest([weird], [])
    assert "javascript:" not in body and "(no https url)" in body


def test_fully_blind_watch_returns_error(tmp_path):
    """All searchers failing every query must go red, not quietly green."""
    import json

    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(CONFIG))

    def broken(q):
        raise FetchError("HTTP 503")

    rc = prior_art.main(
        ["--config", str(config_path), "--seen", str(tmp_path / "seen.json"),
         "--state-dir", str(tmp_path / "state")],
        searchers={"arxiv": broken, "openalex": broken},
        resolvers={},
        env={},
    )
    assert rc == 1


def test_digest_renders_verified_and_dropped():
    title, body = prior_art.render_digest(
        [cand()], [(cand(ident="9999.00001"), "id did not resolve: x")]
    )
    assert "1 verified" in title
    assert "2607.01234" in body and "9999.00001" in body
    assert "fetch-then-quote" in body
