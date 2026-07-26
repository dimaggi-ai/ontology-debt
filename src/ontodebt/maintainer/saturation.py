"""L3 trigger: saturation check. Pure ledger arithmetic; no LLM, no network.

The hard tier is "saturated" when at least ``min_clean_models`` distinct
models hold it completely clean - zero violations, zero paraphrase
contradictions, zero broken links - across their latest committed runs.
Cleanliness reuses the exact analysis the report uses (`analyze`), and a run
that would be INVALID under the harness's >50%-errored rule can never count
as clean (a dead key is not a passing grade; that burn stays fixed).

When saturation fires, the output is an *issue*, not a pack: authoring new
scenarios is the crown-jewel risk and stays behind the human-dispatched,
spend-gated pack-proposal workflow.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..analysis import analyze
from ..runner import RunRecord, load_run
from ..schema import load_commitments
from ._common import github_output, utc_today

DEFAULT_STATE_DIR = Path("maintainer/state")
INVALID_ERROR_RATE = 0.5    # mirrors the harness's ledger-validity rule
MIN_ANSWERED_FRACTION = 0.9  # a model that dodges probes is not holding a tier


def latest_runs(results_dir: Path) -> dict[str, RunRecord]:
    latest: dict[str, RunRecord] = {}
    for path in sorted(Path(results_dir).glob("run-*.json")):
        record = load_run(path)
        prior = latest.get(record.model_name)
        if prior is None or record.started_at > prior.started_at:
            latest[record.model_name] = record
    return latest


def model_verdict(record: RunRecord, commitments) -> tuple[bool, dict]:
    """(clean, detail). Clean means: a valid, *complete* run - every scenario
    of every commitment probed, nearly everything answered - with zero
    violations / contradictions / link breaks.

    Two ways a run must never masquerade as clean: a mostly-errored run (dead
    key; zero violations because nothing was asked) and a partial run (a
    --limit/--only smoke test covering a sliver of the tier). Both are marked
    in the detail instead of counted.
    """
    n = len(record.results)
    errors = sum(1 for r in record.results if r.error)
    detail = {"probes": n, "errors": errors, "violations": 0, "contradictions": 0, "links": 0}
    if n == 0 or errors / n > INVALID_ERROR_RATE:
        detail["invalid"] = True
        return False, detail

    expected_pairs = {(c.id, s.id) for c in commitments for s in c.scenarios}
    expected_probes = sum(c.probe_count() for c in commitments)
    got_pairs = {(r.commitment_id, r.scenario_id) for r in record.results}
    if got_pairs != expected_pairs or n != expected_probes:
        detail["partial"] = True
        return False, detail

    stats = analyze(record, commitments)
    answered = sum(s.n_answered for s in stats.values())
    detail["violations"] = sum(s.n_violations for s in stats.values())
    detail["contradictions"] = sum(s.n_inconsistent_scenarios for s in stats.values())
    detail["links"] = sum(s.n_link_contradictions for s in stats.values())
    if answered / n < MIN_ANSWERED_FRACTION:
        detail["low_answer_rate"] = True
        return False, detail
    clean = (
        detail["violations"] == 0
        and detail["contradictions"] == 0
        and detail["links"] == 0
    )
    return clean, detail


def render_issue(
    results_dir: Path, verdicts: dict[str, tuple[bool, dict]], min_clean: int
) -> tuple[str, str]:
    clean = sorted(name for name, (ok, _) in verdicts.items() if ok)
    tier = Path(results_dir).name
    title = f"Saturation: {len(clean)} model(s) hold `{tier}` clean - time for a harder tier"
    lines = [
        f"<!-- ontodebt-maintainer:saturation:{tier} -->",
        f"Pure arithmetic over the latest committed runs in `{results_dir}`",
        f"(threshold: {min_clean} clean models). A clean model means zero",
        "violations, zero paraphrase contradictions, zero broken links, on a",
        "valid run (>50%-errored runs can never count as clean).",
        "",
        "| Model | Probes | Errors | Violations | Contradictions | Link breaks | Clean |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in sorted(verdicts):
        ok, d = verdicts[name]
        if d.get("invalid"):
            flag = "INVALID RUN"
        elif d.get("partial"):
            flag = "PARTIAL RUN"
        elif d.get("low_answer_rate"):
            flag = "LOW ANSWER RATE"
        else:
            flag = "yes" if ok else "no"
        lines.append(
            f"| {name} | {d['probes']} | {d['errors']} | {d['violations']} |"
            f" {d['contradictions']} | {d['links']} | {flag} |"
        )
    lines += [
        "",
        f"Clean: {', '.join(clean) if clean else 'none'}.",
        "",
        "**Next step (human-dispatched, spend-gated, never auto-merged):** run the",
        "`maintainer-pack-proposal` workflow with a theme for the next tier.",
        "Scenarios must be hard because they are multi-step, never because they",
        "are ambiguous; an adversary pass and the pack loaders gate every draft,",
        "and the resulting PR carries the `never-automerge` label.",
        f"",
        f"_Generated {utc_today()}._",
    ]
    return title, "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--commitments", type=Path, required=True)
    parser.add_argument("--min-clean", type=int, default=2)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument("--github-output", default=None)
    args = parser.parse_args(argv)

    commitments = load_commitments(args.commitments)
    runs = latest_runs(args.results)
    if not runs:
        print(f"no runs in {args.results}; nothing to check", file=sys.stderr)
        github_output({"saturated": "false"}, args.github_output)
        return 0

    verdicts = {name: model_verdict(record, commitments) for name, record in runs.items()}
    n_clean = sum(1 for ok, _ in verdicts.values() if ok)
    saturated = n_clean >= args.min_clean

    title = ""
    if saturated:
        title, body = render_issue(args.results, verdicts, args.min_clean)
        state_dir = Path(args.state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "saturation-issue.md").write_text(body)

    print(f"clean={n_clean}/{len(verdicts)} saturated={saturated}")
    github_output(
        {"saturated": str(saturated).lower(), "issue_title": title, "clean": n_clean},
        args.github_output,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
