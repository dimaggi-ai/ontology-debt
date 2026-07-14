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
import random
from collections import defaultdict
from dataclasses import dataclass, field

from .runner import ProbeResult, RunRecord
from .schema import Commitment, LinkRelation, Verdict


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion of INDEPENDENT trials."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def cluster_bootstrap_ci(
    clusters: list[tuple[int, int]],
    iters: int = 2000,
    seed: int = 0,
    alpha: float = 0.05,
) -> tuple[float, float] | None:
    """Percentile CI for a pooled ratio sum(k)/sum(n), resampling whole
    (k, n) clusters with replacement.

    The probes for one scenario are paraphrases of a single question - they
    are NOT independent Bernoulli trials, so a probe-level Wilson interval on
    the violation rate is optimistically narrow. Resampling at the scenario
    (cluster) level accounts for that within-scenario dependence. Deterministic
    given `seed`, so a report is reproducible. Returns None when fewer than two
    clusters carry observations (between-cluster variance is then unestimable).
    """
    usable = [(k, n) for (k, n) in clusters if n > 0]
    if len(usable) < 2:
        return None
    rng = random.Random(seed)
    m = len(usable)
    rates: list[float] = []
    for _ in range(iters):
        num = den = 0
        for _ in range(m):
            k, n = usable[rng.randrange(m)]
            num += k
            den += n
        rates.append(num / den if den else 0.0)
    rates.sort()
    lo = rates[int((alpha / 2) * iters)]
    hi = rates[min(iters - 1, int((1 - alpha / 2) * iters))]
    return (lo, hi)


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
    def checkable(self) -> bool:
        """Paraphrase consistency is only testable with >= 2 answered variants."""
        return len(self.answers) >= 2

    @property
    def cluster_answer(self) -> str:
        """Strict majority of answered variants; '' when indeterminate.

        Indeterminate means: fewer than 2 answered variants, or no answer
        holds a strict majority (ties). Indeterminate clusters are excluded
        from link-constraint checks rather than guessed at.
        """
        if len(self.answers) < 2:
            return ""
        counts: dict[str, int] = defaultdict(int)
        for a in self.answers:
            counts[a] += 1
        best = max(sorted(counts), key=lambda a: counts[a])
        if counts[best] * 2 > len(self.answers):
            return best
        return ""


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
    n_checkable_scenarios: int = 0        # >= 2 answered variants (consistency testable)
    n_inconsistent_scenarios: int = 0     # paraphrase invariance breaks
    n_link_contradictions: int = 0        # declared link constraint breaks (deduplicated)
    n_links_checked: int = 0
    link_results: dict[tuple[str, str, str], bool] = field(default_factory=dict)  # canonical link -> broken
    variant_accuracy: dict[int, float] = field(default_factory=dict)  # variant position -> accuracy
    scenario_outcomes: dict[str, ScenarioOutcome] = field(default_factory=dict)
    # Per-scenario severity overrides. Chat commitments carry one severity for
    # the whole pack (this stays empty); agent behavioral rules carry their
    # own severity per rule, which the ledger must honor per item.
    scenario_severities: dict[str, str] = field(default_factory=dict)

    @property
    def violation_rate(self) -> float:
        return self.n_violations / self.n_answered if self.n_answered else 0.0

    @property
    def violation_ci(self) -> tuple[float, float] | None:
        """Scenario-cluster bootstrap CI (paraphrases within a scenario are
        dependent, so a probe-level Wilson interval understates the width)."""
        clusters = [
            (sum(1 for v in o.verdicts if v == Verdict.VIOLATION.value), len(o.answers))
            for o in self.scenario_outcomes.values()
        ]
        return cluster_bootstrap_ci(clusters)

    @property
    def contradiction_rate(self) -> float:
        """Inconsistent clusters over *checkable* clusters (>= 2 answered variants).

        Using all scenarios as the denominator would structurally deflate the
        rate for models that break format often - an untestable cluster is
        not a consistent one.
        """
        return (
            self.n_inconsistent_scenarios / self.n_checkable_scenarios
            if self.n_checkable_scenarios
            else 0.0
        )

    @property
    def contradiction_ci(self) -> tuple[float, float]:
        return wilson_interval(self.n_inconsistent_scenarios, self.n_checkable_scenarios)

    @property
    def accuracy_range(self) -> tuple[float, float] | None:
        if not self.variant_accuracy:
            return None
        values = list(self.variant_accuracy.values())
        return (min(values), max(values))


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
            # Only clusters with >= 2 answered variants are testable.
            if outcome.checkable:
                cs.n_checkable_scenarios += 1
                if len(set(outcome.answers)) > 1:
                    outcome.inconsistent = True
                    cs.n_inconsistent_scenarios += 1
            cs.n_scenarios += 1
            cs.scenario_outcomes[sid] = outcome

        for variant_index, vresults in sorted(by_variant.items()):
            answered = [r for r in vresults if r.verdict in (Verdict.PASS.value, Verdict.VIOLATION.value)]
            if answered:
                acc = sum(1 for r in answered if r.verdict == Verdict.PASS.value) / len(answered)
                cs.variant_accuracy[variant_index] = acc

        # Declared link constraints between scenarios, deduplicated to one
        # check per undirected (pair, relation): packs commonly declare both
        # directions, and double-counting would overstate broken counts.
        if commitment:
            canonical: dict[tuple[str, str, str], LinkRelation] = {}
            for scenario in commitment.scenarios:
                for link in scenario.links:
                    a, b = sorted((scenario.id, link.target))
                    canonical[(a, b, link.relation.value)] = link.relation
            for (a, b, rel_value), relation in sorted(canonical.items()):
                source = cs.scenario_outcomes.get(a)
                target = cs.scenario_outcomes.get(b)
                if source is None or target is None:
                    continue
                # Indeterminate clusters (ties, < 2 answers) are excluded,
                # not guessed at.
                if not source.cluster_answer or not target.cluster_answer:
                    continue
                cs.n_links_checked += 1
                same = source.cluster_answer == target.cluster_answer
                broken = (relation is LinkRelation.SAME_ANSWER and not same) or (
                    relation is LinkRelation.DIFFERENT_ANSWER and same
                )
                cs.link_results[(a, b, rel_value)] = broken
                if broken:
                    cs.n_link_contradictions += 1

        stats[cid] = cs

    return stats
