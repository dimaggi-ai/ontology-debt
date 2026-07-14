"""Markdown report generation with the numbers that make an audit credible:
Wilson CIs, separated violation vs contradiction rates, paraphrase accuracy
ranges (never just the mean), format-nonconformance, cost, and pinned model
snapshots."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from .agent_audit import AgentVerdict, RuleFinding, RulePack, Transcript
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
        error_rate = total_err / total_probes if total_probes else 0.0
        if error_rate > 0.2:
            lines.append(
                f"> ⚠️ **RUN UNRELIABLE: {error_rate:.0%} of probes errored.** "
                f"Headline rates below are computed on the surviving probes and "
                f"should not be trusted; the ledger was not updated from this run "
                f"if errors exceeded 50%."
            )
            lines.append("")
        lines.append(f"- Model id (as invoked): `{record.model_id}`")
        lines.append(f"- Run: `{record.run_id}` started {record.started_at}")
        lines.append(
            f"- Probes: {total_probes} ({total_answered} answered, "
            f"{total_noncon} nonconformant, {total_err} errors)"
        )
        lines.append(
            f"- Tokens: {record.total_input_tokens:,} in / {record.total_output_tokens:,} out"
            + (f" - estimated cost ${cost:.2f}" if cost else "")
        )
        total_checkable = sum(cs.n_checkable_scenarios for cs in stats.values())
        overall_viol_rate = total_viol / total_answered if total_answered else 0.0
        overall_contra_rate = total_incons / total_checkable if total_checkable else 0.0
        pessimistic = (
            (total_viol + total_noncon) / (total_answered + total_noncon)
            if (total_answered + total_noncon)
            else 0.0
        )
        lines.append(
            f"- **Overall violation rate: {_pct(overall_viol_rate)}** "
            f"({total_viol}/{total_answered} answered probes; "
            f"pessimistic bound counting nonconformance as failure: {_pct(pessimistic)})"
        )
        lines.append(
            f"- **Overall contradiction rate: {_pct(overall_contra_rate)}** "
            f"({total_incons}/{total_checkable} checkable paraphrase clusters; "
            f"{total_scen - total_checkable} of {total_scen} clusters untestable)"
        )
        if total_links:
            lines.append(f"- Link constraints broken: {total_link_contra}/{total_links}")
        if ledger:
            lines.append(f"- Open debt (weighted): **{ledger.total_debt(record.model_name)}**")
        lines.append("")
        lines.append(
            "| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) "
            "| Accuracy range across paraphrases | Nonconf. | n answered |"
        )
        lines.append("|---|---|---|---|---|---|---|")
        for cid in sorted(stats):
            cs = stats[cid]
            viol = (
                f"{_pct(cs.violation_rate)} {_ci(cs.violation_ci)}"
                if cs.n_answered
                else "—"
            )
            contra = (
                f"{_pct(cs.contradiction_rate)} {_ci(cs.contradiction_ci)}"
                if cs.n_checkable_scenarios
                else "—"
            )
            acc_range = cs.accuracy_range
            acc = f"{_pct(acc_range[0])} – {_pct(acc_range[1])}" if acc_range else "—"
            lines.append(
                f"| {cs.title} | {cs.severity} "
                f"| {viol} | {contra} | {acc} "
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
        "separately. Violation rates condition on answered probes (the pessimistic bound above "
        "counts nonconformance as failure); contradiction rates condition on checkable clusters "
        "(>= 2 answered variants). Link checks use the strict majority answer of each cluster; "
        "ties and under-answered clusters are excluded as indeterminate, and symmetric link "
        "declarations are deduplicated. Full transcripts are recorded alongside this report.*"
    )
    return "\n".join(lines) + "\n"


def render_agent_report(
    agent_name: str,
    run_id: str,
    packs: list[RulePack],
    transcripts: list[Transcript],
    findings: list[RuleFinding],
    ledger: Ledger | None = None,
) -> str:
    """Markdown report for an offline agent-transcript audit."""
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append("# ontodebt agent audit report")
    lines.append("")
    lines.append(f"Generated: {now}")
    lines.append("")

    verdict_counts = Counter(f.verdict for f in findings)
    n_rules = sum(len(p.rules) for p in packs)
    lines.append(f"## {agent_name}")
    lines.append("")
    lines.append(f"- Run: `{run_id}`")
    lines.append(
        f"- Transcripts: {len(transcripts)} "
        f"({', '.join('`' + t.id + '`' for t in sorted(transcripts, key=lambda t: t.id))})"
    )
    lines.append(f"- Rules: {n_rules} across {len(packs)} pack(s)")
    lines.append(
        f"- Checks: {len(findings)} — "
        f"**{verdict_counts[AgentVerdict.VIOLATION.value]} violations**, "
        f"**{verdict_counts[AgentVerdict.CONTRADICTION.value]} contradictions**, "
        f"{verdict_counts[AgentVerdict.PASS.value]} passes, "
        f"{verdict_counts[AgentVerdict.NOT_APPLICABLE.value]} not applicable"
    )
    if ledger:
        lines.append(f"- Open agent debt (weighted): **{ledger.total_debt(agent_name)}**")
    lines.append("")

    by_key: dict[tuple[str, str], list[RuleFinding]] = {}
    for f in findings:
        by_key.setdefault((f.pack_id, f.rule_id), []).append(f)

    for pack in packs:
        lines.append(f"### {pack.title} (`{pack.id}`)")
        lines.append("")
        lines.append("| Rule | Type | Sev | Pass | Violation | Contradiction | N/A |")
        lines.append("|---|---|---|---|---|---|---|")
        for rule in pack.rules:
            counts = Counter(f.verdict for f in by_key.get((pack.id, rule.id), []))
            lines.append(
                f"| {rule.id}: {rule.title} | {rule.type} | {rule.severity} "
                f"| {counts[AgentVerdict.PASS.value]} "
                f"| {counts[AgentVerdict.VIOLATION.value]} "
                f"| {counts[AgentVerdict.CONTRADICTION.value]} "
                f"| {counts[AgentVerdict.NOT_APPLICABLE.value]} |"
            )
        lines.append("")

    failures = [
        f for f in findings
        if f.verdict in (AgentVerdict.VIOLATION.value, AgentVerdict.CONTRADICTION.value)
    ]
    lines.append("### Findings")
    lines.append("")
    if not failures:
        lines.append("No violations or contradictions.")
    else:
        for f in sorted(failures, key=lambda f: (f.pack_id, f.rule_id, f.transcript_id)):
            lines.append(
                f"- **{f.rule_id}@{f.transcript_id}** — {f.verdict} ({f.severity}): {f.rule_title}"
            )
            for ev in f.evidence:
                lines.append(
                    f"  - turn {ev['turn']} ({ev['role']}): \"{ev['excerpt']}\" — {ev['note']}"
                )
    lines.append("")

    lines.append("---")
    lines.append(
        "*Methodology: deterministic regex rules over recorded agent transcripts — no LLM "
        "judge, no live agent, fully reproducible given transcript + rules. Violations "
        "(transcript contradicts a declared behavioral commitment) and contradictions (the "
        "agent contradicts itself) are counted separately. A rule whose precondition never "
        "fired is not applicable: it neither accrues debt nor pays it down. Assertion "
        "stability requires >= 2 captured values, mirroring the chat harness's checkable-"
        "cluster rule. File order is the temporal order; `turn` is display metadata.*"
    )
    return "\n".join(lines) + "\n"
