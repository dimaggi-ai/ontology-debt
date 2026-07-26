"""Phase-4 guard: is a PR diff a pure, recomputable report regeneration?

"Mechanical" means: every changed file is the `report.md` of a known results
directory, and nothing else - no transcripts, no ledgers, no code, no packs.
The auto-merge workflow additionally *recomputes* each report from the
committed run files and requires a byte-identical match, so the answer to
"should this merge itself" is never an LLM's opinion or even this module's
alone: it is `ontodebt report` agreeing with the diff.

Ships alongside `AUTOMERGE_MECHANICAL` (a repo variable that defaults to
unset = disabled); until a human flips it, this guard only ever *labels*.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ._common import github_output, load_json

DEFAULT_CONFIG = Path("maintainer/config.json")


def is_mechanical(changed: list[str], report_dirs: dict[str, str]) -> tuple[bool, str]:
    if not changed:
        return False, "empty diff"
    allowed = {f"{results}/report.md" for results in report_dirs}
    offending = [f for f in changed if f not in allowed]
    if offending:
        return False, f"non-mechanical file in diff: {offending[0]}"
    return True, f"all {len(changed)} changed file(s) are known report regenerations"


def recompute_plan(changed: list[str], report_dirs: dict[str, str]) -> list[tuple[str, str]]:
    """(results_dir, commitments_dir) pairs the workflow must recompute."""
    plan = []
    for results, commitments in sorted(report_dirs.items()):
        if f"{results}/report.md" in changed:
            plan.append((results, commitments))
    return plan


def _normalized_report_lines(path: Path) -> list[str]:
    """Report lines minus the volatile bits: the 'Generated:' wall-clock line
    (render_report stamps the current minute, so byte-identity is impossible
    across runs) and trailing blank lines (`ontodebt report > f` gains one
    newline over cmd_run's write_text). Everything substantive must match."""
    lines = [
        line for line in Path(path).read_text().splitlines()
        if not line.startswith("Generated: ")
    ]
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def reports_equivalent(committed: Path, recomputed: Path) -> bool:
    return _normalized_report_lines(committed) == _normalized_report_lines(recomputed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--files-from", type=Path, default=None,
                        help="file with one changed path per line (git diff --name-only)")
    parser.add_argument("--compare", type=Path, nargs=2, metavar=("COMMITTED", "RECOMPUTED"),
                        help="exit 0 iff the two reports match modulo the Generated line")
    parser.add_argument("--plan-out", type=Path, default=None)
    parser.add_argument("--github-output", default=None)
    args = parser.parse_args(argv)

    if args.compare:
        same = reports_equivalent(args.compare[0], args.compare[1])
        print(f"reports_equivalent={same}")
        return 0 if same else 1
    if args.files_from is None:
        parser.error("one of --files-from or --compare is required")

    config = load_json(args.config, {})
    report_dirs: dict[str, str] = config.get("report_dirs", {})
    changed = [line.strip() for line in args.files_from.read_text().splitlines() if line.strip()]

    mechanical, reason = is_mechanical(changed, report_dirs)
    print(f"mechanical={mechanical}: {reason}")
    github_output({"mechanical": str(mechanical).lower(), "reason": reason}, args.github_output)

    if mechanical and args.plan_out:
        plan = recompute_plan(changed, report_dirs)
        args.plan_out.write_text("\n".join(f"{r}\t{c}" for r, c in plan) + "\n")
    return 0 if mechanical else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
