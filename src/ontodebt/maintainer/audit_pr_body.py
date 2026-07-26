"""Deterministic PR-body rendering for maintainer audit PRs.

No LLM: the body is extracted verbatim from the regenerated report plus a
fixed review checklist. Prose stays boring so the numbers stay trustworthy.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def extract_model_summary(report_text: str, model_name: str) -> list[str]:
    """Return the bullet lines of a model's report section (id, probes, rates)
    plus any blockquote banners (e.g. the RUN UNRELIABLE warning) - dropping a
    warning banner from the PR body would be silent optimism."""
    pattern = re.compile(
        rf"^## {re.escape(model_name)}\n(.*?)(?=^## |\Z)", re.M | re.S
    )
    match = pattern.search(report_text)
    if not match:
        return [f"- (no section for `{model_name}` found in the report - investigate)"]
    return [
        line for line in match.group(1).splitlines()
        if line.startswith("- ") or line.startswith("> ")
    ]


def render(report_path: Path, models: list[str]) -> str:
    report_text = Path(report_path).read_text()
    lines = [
        "<!-- ontodebt-maintainer:audit-pr -->",
        "Automated audit of newly detected model(s), opened by the maintainer loop.",
        "Scoring is the repo's deterministic harness; transcripts are committed in",
        "this PR and every number below can be recomputed from them with",
        "`ontodebt report`. No LLM wrote or judged any result.",
        "",
    ]
    for model in models:
        lines.append(f"### `{model}`")
        lines += extract_model_summary(report_text, model)
        lines.append("")
    lines += [
        "#### Review checklist (human gate - nothing here merges itself)",
        "- [ ] Pricing TODOs in `models.yaml` filled from the provider's pricing page",
        "- [ ] Spot-check a few transcripts (`examples/gradient/transcript-*.jsonl`)",
        "- [ ] Nonconformant/error counts sane (a >50% errored run never touches the ledger)",
        "- [ ] Decide whether the README results table should include this model",
        "- [ ] Optional follow-up: hard tier via "
        "`ontodebt run --commitments commitments-frontier --results examples/gradient-frontier "
        "--models <name>`",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--models", required=True, help="comma-separated registry names")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    body = render(args.report, [m for m in args.models.split(",") if m])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(body)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
