"""Markdown report generation with the numbers that make an audit credible:
Wilson CIs, separated violation vs contradiction rates, paraphrase accuracy
ranges (never just the mean), format-nonconformance, cost, and pinned model
snapshots."""

from __future__ import annotations

from datetime import datetime, timezone

from .analysis import CommitmentStats
from .ledger import Ledger
from .providers import ModelConfig
from .runner import RunRecord


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def _ci(ci: tuple[float, float]) -> str:
    return f"[{_pct(ci[0])}, {_pct(ci[1])}]"


def estimate_cost(record: RunRecord, config: ModelConfig) -> float:
    return (
        record.total_input_tokens / 1_000_000 * config.input_price_per_mtok
        + record.total_output_tokens / 1_000_000 * config.output_price_per_mtok
    )


def render_report(
    runs: list[tuple[RunRecord, ModelConfig, dict[str, CommitmentStats]]],
    ledger: Ledger | None = None,
) -> str:
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append("# ontodebt audit report")
    lines.append("")
    lines.append(f"Generated: {now}")
    lines.append("")

    for record, config, stats in runs:
        total_probes = sum(cs.n_probes for cs in stats.values())
        total_viol = sum(cs.n_violations for cs in stats.values())
        total_answered = sum(cs.n_answered for cs in stats.values())
        total_scen = sum(cs.n_scenarios for cs in stats.values())
        total_incons = sum(cs.n_inconsistent_scenarios for cs in stats.values())
        total_noncon = sum(cs.n_nonconformant for cs in stats.values())
        total_err = sum(cs.n_errors for cs in stats.values())
        total_links = sum(cs.n_links_checked for cs in stats.values())
        total_link_contra = sum(cs.n_link_contradictions for cs in stats.values())
        cost = estimate_cost(record, config)

        lines.append(f"## {record.model_name}")
        lines.append("")
        lines.append(f"- Model snapshot: `{record.model_id}`")
        lines.append(f"- Run: `{record.run_id}` started {record.started_at}")
        lines.append(
            f"- Probes: {total_probes} ({total_answered} answered, "
            f"{total_noncon} nonconformant, {total_err} errors)"
        )
        lines.append(
            f"- Tokens: {record.total_input_tokens:,} in / {record.total_output_tokens:,} out"
            + (f" - estimated cost ${cost:.2f}" if cost else "")
        )
        overall_viol_rate = total_viol / total_answered if total_answered else 0.0
        overall_contra_rate = total_incons / total_scen if total_scen else 0.0
        lines.append(f"- **Overall violation rate: {_pct(overall_viol_rate)}** ({total_viol}/{total_answered} answered probes)")
        lines.append(f"- **Overall contradiction rate: {_pct(overall_contra_rate)}** ({total_incons}/{total_scen} paraphrase clusters)")
        if total_links:
            lines.append(f"- Link constraints broken: {total_link_contra}/{total_links}")
        if ledger:
            lines.append(f"- Open debt (weighted): **{ledger.total_debt(record.model_name)}**")
        lines.append("")
        lines.append(
            "| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) "
            "| Accuracy range across paraphrases | Nonconf. | n |"
        )
        lines.append("|---|---|---|---|---|---|---|")
        for cid in sorted(stats):
            cs = stats[cid]
            lo, hi = cs.accuracy_range
            lines.append(
                f"| {cs.title} | {cs.severity} "
                f"| {_pct(cs.violation_rate)} {_ci(cs.violation_ci)} "
                f"| {_pct(cs.contradiction_rate)} {_ci(cs.contradiction_ci)} "
                f"| {_pct(lo)} – {_pct(hi)} "
                f"| {cs.n_nonconformant} | {cs.n_answered} |"
            )
        lines.append("")

    if ledger:
        lines.append("## Open debt ledger")
        lines.append("")
        open_items = ledger.open_items()
        if not open_items:
            lines.append("No open debt. 🎉")
        else:
            lines.append("| Model | Commitment | Scenario | Kind | Severity | First seen | Last seen |")
            lines.append("|---|---|---|---|---|---|---|")
            for item in open_items:
                lines.append(
                    f"| {item.model_name} | {item.commitment_id} | {item.scenario_id} "
                    f"| {item.kind} | {item.severity} | {item.first_seen_run} | {item.last_seen_run} |"
                )
        lines.append("")

    lines.append("---")
    lines.append(
        "*Methodology: constrained-format probes, deterministic verdicts (no LLM judge), "
        "Wilson 95% intervals. Violations (wrong vs. declared commitment) and contradictions "
        "(model disagreeing with itself across paraphrases or linked scenarios) are counted "
        "separately. Full transcripts are committed alongside this report.*"
    )
    return "\n".join(lines) + "\n"
