"""Deterministic analysis: violation rates, paraphrase contradictions,
link-constraint contradictions, and Wilson confidence intervals.

Two failure kinds are kept strictly separate (a model can be consistently
wrong, or inconsistently right — conflating them hides both):

- **violation** - an answered probe contradicts the commitment's expected answer.
- **contradiction** - the model disagrees *with itself*: either across
  paraphrase variants of one scenario (invariance break) or across scenarios
  joined by a declared link constraint.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field

from .runner import ProbeResult, RunRecord
from .schema import Commitment, LinkRelation, Verdict


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


@dataclass
class ScenarioOutcome:
    scenario_id: str
    answers: list[str] = field(default_factory=list)      # normalized, answered variants only
    verdicts: list[str] = field(default_factory=list)     # all variants
    inconsistent: bool = False   # paraphrase variants disagreed with each other

    @property
    def violated(self) -> bool:
        return Verdict.VIOLATION.value in self.verdicts

    @property
    def majority_answer(self) -> str:
        if not self.answers:
            return ""
        counts: dict[str, int] = defaultdict(int)
        for a in self.answers:
            counts[a] += 1
        return max(sorted(counts), key=lambda a: counts[a])


@dataclass
class CommitmentStats:
    commitment_id: str
    title: str
    severity: str
    n_probes: int = 0
    n_answered: int = 0
    n_violations: int = 0
    n_nonconformant: int = 0
    n_errors: int = 0
    n_scenarios: int = 0
    n_inconsistent_scenarios: int = 0     # paraphrase invariance breaks
    n_link_contradictions: int = 0        # declared link constraint breaks
    n_links_checked: int = 0
    variant_accuracy: list[float] = field(default_factory=list)  # per variant position
    scenario_outcomes: dict[str, ScenarioOutcome] = field(default_factory=dict)

    @property
    def violation_rate(self) -> float:
        return self.n_violations / self.n_answered if self.n_answered else 0.0

    @property
    def violation_ci(self) -> tuple[float, float]:
        return wilson_interval(self.n_violations, self.n_answered)

    @property
    def contradiction_rate(self) -> float:
        return self.n_inconsistent_scenarios / self.n_scenarios if self.n_scenarios else 0.0

    @property
    def contradiction_ci(self) -> tuple[float, float]:
        return wilson_interval(self.n_inconsistent_scenarios, self.n_scenarios)

    @property
    def accuracy_range(self) -> tuple[float, float]:
        if not self.variant_accuracy:
            return (0.0, 0.0)
        return (min(self.variant_accuracy), max(self.variant_accuracy))


def analyze(record: RunRecord, commitments: list[Commitment]) -> dict[str, CommitmentStats]:
    by_commitment: dict[str, list[ProbeResult]] = defaultdict(list)
    for r in record.results:
        by_commitment[r.commitment_id].append(r)

    commitment_index = {c.id: c for c in commitments}
    stats: dict[str, CommitmentStats] = {}

    for cid, results in sorted(by_commitment.items()):
        commitment = commitment_index.get(cid)
        cs = CommitmentStats(
            commitment_id=cid,
            title=commitment.title if commitment else cid,
            severity=commitment.severity if commitment else "medium",
        )

        by_scenario: dict[str, list[ProbeResult]] = defaultdict(list)
        for r in results:
            by_scenario[r.scenario_id].append(r)

        # Per-variant-position accuracy (paraphrase sensitivity range).
        by_variant: dict[int, list[ProbeResult]] = defaultdict(list)

        for sid, sresults in sorted(by_scenario.items()):
            sresults.sort(key=lambda r: r.variant_index)
            outcome = ScenarioOutcome(scenario_id=sid)
            for r in sresults:
                cs.n_probes += 1
                outcome.verdicts.append(r.verdict)
                by_variant[r.variant_index].append(r)
                if r.verdict == Verdict.ERROR.value:
                    cs.n_errors += 1
                elif r.verdict == Verdict.NONCONFORMANT.value:
                    cs.n_nonconformant += 1
                else:
                    cs.n_answered += 1
                    outcome.answers.append(r.answer)
                    if r.verdict == Verdict.VIOLATION.value:
                        cs.n_violations += 1
            # Paraphrase invariance: all answered variants must agree.
            if len(set(outcome.answers)) > 1:
                outcome.inconsistent = True
                cs.n_inconsistent_scenarios += 1
            cs.n_scenarios += 1
            cs.scenario_outcomes[sid] = outcome

        for _, vresults in sorted(by_variant.items()):
            answered = [r for r in vresults if r.verdict in (Verdict.PASS.value, Verdict.VIOLATION.value)]
            if answered:
                acc = sum(1 for r in answered if r.verdict == Verdict.PASS.value) / len(answered)
                cs.variant_accuracy.append(acc)

        # Declared link constraints between scenarios.
        if commitment:
            for scenario in commitment.scenarios:
                source = cs.scenario_outcomes.get(scenario.id)
                if source is None or not source.majority_answer:
                    continue
                for link in scenario.links:
                    target = cs.scenario_outcomes.get(link.target)
                    if target is None or not target.majority_answer:
                        continue
                    cs.n_links_checked += 1
                    same = source.majority_answer == target.majority_answer
                    if link.relation is LinkRelation.SAME_ANSWER and not same:
                        cs.n_link_contradictions += 1
                    elif link.relation is LinkRelation.DIFFERENT_ANSWER and same:
                        cs.n_link_contradictions += 1

        stats[cid] = cs

    return stats
