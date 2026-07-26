"""L3 action: draft a harder commitment pack. The ONLY module with an LLM.

The LLM is fenced to *candidate generation*. Everything that decides is
deterministic or human:

1. A proposer call drafts a full pack in YAML (style-anchored on an existing
   pack). Fences are stripped; the YAML must parse.
2. Every scenario is validated by the package's own loaders
   (`load_commitment`) - the same code that gates hand-written packs.
   Schema-invalid scenarios are dropped, not repaired.
3. An independent adversary call per scenario tries to argue for a
   *different* answer. Anything not answered with an explicit UNDISPUTED
   verdict is dropped - fail-closed, because "hard because ambiguous" is the
   one way a pack can rot the project's gold labels.
4. The surviving pack must still pass `load_commitment` as a whole and meet
   a minimum-scenario floor, or the whole proposal fails.

The output lands in `commitments-frontier-draft/` on a PR labeled
`never-automerge`. A human promotes it (or not). No draft ever scores a
model until that human move.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

from ..schema import load_commitment
from ._common import FetchError, http_post_json, utc_today

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-opus-4-8"

CompleteFn = Callable[[str, str, int], str]  # (system, prompt, max_tokens) -> text


class ProposeError(RuntimeError):
    pass


# --------------------------------------------------------------------------- LLM plumbing

def api_complete_factory(api_key: str, model: str) -> CompleteFn:
    def complete(system: str, prompt: str, max_tokens: int) -> str:
        try:
            response = http_post_json(
                ANTHROPIC_URL,
                {
                    "model": model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}],
                },
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
            )
        except FetchError as exc:
            raise ProposeError(f"Anthropic API call failed: {exc}") from exc
        return "".join(
            block.get("text", "") for block in response.get("content", []) if block.get("type") == "text"
        )

    return complete


PROPOSER_SYSTEM = """You draft candidate test scenarios for Ontology Debt, an LLM world-model audit tool with fully deterministic scoring. Your output will be machine-validated and adversarially reviewed; anything ambiguous or malformed is discarded, not repaired.

Output RAW YAML ONLY - no markdown fences, no commentary before or after."""

PROPOSER_TEMPLATE = """Draft a new commitment pack for the theme: {theme}

Hard requirements (violations are dropped by deterministic validation):
- Top-level fields: id: {pack_id}, title, statement (2-4 sentences describing the invariant), severity: high, lineage: ["drafted by the maintainer loop {today}; human review required before any scoring use"], scenarios.
- Exactly {n} scenarios, ids {prefix}-001 ... {prefix}-{n:03d}.
- Every scenario: setup (a concrete situation), question, exactly 4 paraphrases (same question, genuinely different wording), expected, rationale, difficulty: adversarial. No links.
- Every question and paraphrase ends with an explicit constrained-answer instruction, e.g. "Answer with exactly one word: Yes or No." or "Answer with a single number and nothing else."
- expected is either {{type: choice, values: [...], value: <gold>}} or {{type: exact, value: "<gold>"}}. The gold answer must be a single word or single number.
- rationale is a NUMBERED MECHANICAL DERIVATION: each step a single operation or inference, so a reviewer can recompute the gold answer step by step.
- Scenarios must be HARD BECAUSE MULTI-STEP (compose at least three operations, hops, or scope changes), NEVER hard because ambiguous. All facts needed must be stated in the setup; no reliance on debatable world knowledge, units left implicit, or trick wording.

Style anchor - match the tone, concreteness, and format of this existing pack:

{style_text}
"""

ADVERSARY_SYSTEM = """You are an adversarial reviewer for an LLM audit pack. Your ONLY job is to find a defensible reading of the scenario under which the gold answer is WRONG - a second interpretation, a missing fact, an ambiguity of scope, unit, or timing.

Reply with a verdict on the FIRST line:
DISPUTED: <one sentence: the alternative reading and the answer it yields>
or
UNDISPUTED
Then (optionally) brief reasoning. If you are at all uncertain, say DISPUTED - ambiguity is fatal here and false alarms are cheap."""

ADVERSARY_TEMPLATE = """Scenario setup:
{setup}

Question (constrained format):
{question}

Declared gold answer: {gold}
Allowed answers: {allowed}

Is there any defensible reading under which a careful reasoner should answer differently? First line: DISPUTED: <why> or UNDISPUTED."""


# --------------------------------------------------------------------------- pipeline

def strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    return text.strip()


def validate_single_scenario(pack: dict, scenario: dict) -> str | None:
    """Run one scenario through the real pack loader. Returns an error string
    or None. Links are stripped defensively: drafts may not declare them."""
    scenario = {k: v for k, v in scenario.items() if k != "links"}
    candidate = {
        "id": pack.get("id", "draft"),
        "title": pack.get("title", "draft"),
        "statement": pack.get("statement", "draft statement"),
        "severity": pack.get("severity", "high"),
        "scenarios": [scenario],
    }
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        yaml.safe_dump(candidate, f, sort_keys=False)
        path = Path(f.name)
    try:
        load_commitment(path)
        return None
    except Exception as exc:
        return str(exc)
    finally:
        path.unlink(missing_ok=True)


def adversary_verdict(complete: CompleteFn, scenario: dict) -> tuple[bool, str]:
    """(undisputed, reason). Fail-closed: anything but an explicit leading
    UNDISPUTED counts as disputed."""
    expected = scenario.get("expected", {})
    prompt = ADVERSARY_TEMPLATE.format(
        setup=scenario.get("setup", ""),
        question=scenario.get("question", ""),
        gold=expected.get("value", ""),
        allowed=expected.get("values", "free-form (exact match)"),
    )
    reply = complete(ADVERSARY_SYSTEM, prompt, 1500).strip()
    first = reply.splitlines()[0].strip() if reply else ""
    if first.upper().startswith("UNDISPUTED"):
        return True, "undisputed"
    return False, first[:200] or "empty adversary reply (fail-closed)"


@dataclass
class Disposition:
    scenario_id: str
    kept: bool
    reason: str


def generate_pack(
    theme: str,
    pack_id: str,
    style_text: str,
    complete: CompleteFn,
    n_scenarios: int = 8,
    min_keep: int = 5,
) -> tuple[dict, list[Disposition]]:
    prefix = re.sub(r"[^a-z0-9]+", "", pack_id.lower())[:2] or "xx"
    prompt = PROPOSER_TEMPLATE.format(
        theme=theme,
        pack_id=pack_id,
        n=n_scenarios,
        prefix=prefix,
        today=utc_today(),
        style_text=style_text[:5000],
    )
    raw = strip_fences(complete(PROPOSER_SYSTEM, prompt, 16000))
    try:
        pack = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ProposeError(f"proposer output is not valid YAML: {exc}") from exc
    if not isinstance(pack, dict) or not isinstance(pack.get("scenarios"), list):
        raise ProposeError("proposer output lacks a scenarios list")

    dispositions: list[Disposition] = []
    survivors: list[dict] = []
    for scenario in pack["scenarios"]:
        sid = str(scenario.get("id", "?"))
        error = validate_single_scenario(pack, scenario)
        if error is not None:
            dispositions.append(Disposition(sid, False, f"schema: {error[:200]}"))
            continue
        undisputed, reason = adversary_verdict(complete, scenario)
        if not undisputed:
            dispositions.append(Disposition(sid, False, f"adversary: {reason}"))
            continue
        scenario.pop("links", None)
        survivors.append(scenario)
        dispositions.append(Disposition(sid, True, "kept"))

    if len(survivors) < min_keep:
        raise ProposeError(
            f"only {len(survivors)}/{len(pack['scenarios'])} scenarios survived "
            f"validation+adversary (min_keep={min_keep}); refusing to emit a thin pack. "
            f"Dispositions: {[(d.scenario_id, d.reason) for d in dispositions]}"
        )

    final = {
        # The id (and therefore the output path) is ALWAYS the CLI-validated
        # pack_id - never the LLM's - so a deviating proposer response cannot
        # steer a filesystem write. Mirrors add_model's SAFE_ID gate.
        "id": pack_id,
        "title": pack.get("title", pack_id),
        "statement": pack.get("statement", ""),
        "severity": "high",
        "lineage": pack.get("lineage", [f"drafted by the maintainer loop {utc_today()}; human review required"]),
        "scenarios": survivors,
    }
    return final, dispositions


def write_pack(final: dict, out_dir: Path) -> Path:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", str(final.get("id", ""))):
        raise ProposeError(f"pack id fails the safe-charset gate: {final.get('id')!r}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{final['id']}.yaml"
    if path.resolve().parent != out_dir.resolve():  # pragma: no cover - belt and braces
        raise ProposeError(f"refusing to write outside {out_dir}: {path}")
    path.write_text(yaml.safe_dump(final, sort_keys=False, width=88))
    load_commitment(path)  # the definitive deterministic gate; raises on failure
    return path


def render_pr_body(theme: str, model: str, path: Path, dispositions: list[Disposition]) -> str:
    kept = sum(1 for d in dispositions if d.kept)
    lines = [
        "<!-- ontodebt-maintainer:pack-proposal -->",
        f"Draft pack for theme **{theme}**, proposed by `{model}`, adversarially",
        f"filtered, and validated by the repo's own pack loaders. {kept}/{len(dispositions)}",
        "scenarios survived. **This PR must never auto-merge**: gold labels are the",
        "project's crown jewels, and a draft becomes a scoring pack only when a",
        "human promotes it out of `commitments-frontier-draft/` after review.",
        "",
        f"File: `{path}`",
        "",
        "| Scenario | Kept | Reason |",
        "|---|---|---|",
    ]
    lines += [f"| {d.scenario_id} | {'yes' if d.kept else 'no'} | {d.reason} |" for d in dispositions]
    lines += [
        "",
        "#### Review checklist",
        "- [ ] Every rationale's mechanical derivation recomputes to the gold answer",
        "- [ ] No scenario is hard-because-ambiguous (the adversary is a filter, not a guarantee)",
        "- [ ] Paraphrases are genuinely distinct wordings of the same question",
        "- [ ] Promotion decision: move into `commitments-frontier/` (or reject)",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None, complete: CompleteFn | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--style-pack", type=Path, default=Path("commitments-frontier/stacked_conservation.yaml"))
    parser.add_argument("--out-dir", type=Path, default=Path("commitments-frontier-draft"))
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--min-keep", type=int, default=5)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--pr-body", type=Path, default=None)
    args = parser.parse_args(argv)

    if not re.fullmatch(r"[a-z][a-z0-9_]*", args.pack_id):
        print("pack-id must be lower_snake_case", file=sys.stderr)
        return 2
    if complete is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("ANTHROPIC_API_KEY not set; refusing to run the proposer", file=sys.stderr)
            return 2
        complete = api_complete_factory(api_key, args.model)

    try:
        final, dispositions = generate_pack(
            args.theme, args.pack_id, Path(args.style_pack).read_text(),
            complete, args.n, args.min_keep,
        )
        path = write_pack(final, args.out_dir)
    except ProposeError as exc:
        print(f"PROPOSAL FAILED (fail-closed): {exc}", file=sys.stderr)
        return 1

    if args.pr_body:
        args.pr_body.parent.mkdir(parents=True, exist_ok=True)
        args.pr_body.write_text(render_pr_body(args.theme, args.model, path, dispositions))
    print(f"draft written: {path} ({sum(d.kept for d in dispositions)} scenarios)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
