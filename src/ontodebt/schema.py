"""Core data model: commitments, scenarios, probes, and verdicts.

A *commitment* is a declared, testable assertion about the world that a
language model is expected to hold consistently (e.g. object permanence).
Each commitment carries *scenarios*; each scenario carries one canonical
question plus paraphrase variants and a machine-checkable expected answer.

Everything here is deliberately deterministic: expected answers use
constrained formats (single word / choice / number) so that verdicts never
require an LLM judge.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterator

import yaml


class Verdict(str, Enum):
    PASS = "pass"
    VIOLATION = "violation"          # answered, but contradicted the commitment
    NONCONFORMANT = "nonconformant"  # did not produce a checkable answer
    ERROR = "error"                  # provider/transport failure


class LinkRelation(str, Enum):
    SAME_ANSWER = "same_answer"        # two scenarios must yield the same normalized answer
    DIFFERENT_ANSWER = "different_answer"


_WORD_RE = re.compile(r"[a-z0-9]+(?:[./-][a-z0-9]+)*")


def _clean(text: str) -> str:
    cleaned = text.strip().lower()
    # Strip common wrappers: markdown emphasis, quotes, leading labels.
    cleaned = re.sub(r"[*_`\"'“”‘’]", "", cleaned)
    cleaned = re.sub(r"^(answer|response)\s*[:\-]\s*", "", cleaned)
    return cleaned


def normalize_answer(text: str) -> str:
    """Normalize a model answer to a comparable token.

    Lowercases, strips markdown/quote/punctuation noise, and returns the
    first word-like token. Constrained-format probes ("Answer with exactly
    one word: Yes or No") make this extraction safe; anything that yields
    no token is treated as nonconformant by the caller. Hedged answers that
    mention several candidate answers are rejected by `Expected.check`, not
    here — this function only extracts.
    """
    match = _WORD_RE.search(_clean(text))
    return match.group(0) if match else ""


@dataclass(frozen=True)
class Expected:
    """Machine-checkable answer spec. `type` is one of exact|choice|regex.

    Verdict semantics: VIOLATION means the model gave a *conforming* answer
    of the wrong value; anything that is not a plausible answer attempt
    (hedges mentioning several options, word-form numbers where digits were
    demanded, rambling) is NONCONFORMANT — a format failure, never evidence
    about the world-model. For `regex`, an optional `conformance` pattern
    defines what counts as answer-shaped; without it, non-matching tokens
    are conservatively NONCONFORMANT unless they match `conformance`.
    """

    type: str
    value: str = ""
    values: tuple[str, ...] = ()
    pattern: str = ""
    conformance: str = ""

    def check(self, answer: str) -> Verdict:
        token = normalize_answer(answer)
        if not token:
            return Verdict.NONCONFORMANT

        if self.type == "exact":
            expected_token = normalize_answer(self.value)
            if expected_token.isdigit():
                # Digits were demanded ("Answer with a single number written
                # in digits."). A non-digit token is a format failure, and a
                # hedge naming several numbers is too.
                digit_groups = set(re.findall(r"\b\d+\b", _clean(answer)))
                if not token.isdigit() or len(digit_groups) > 1:
                    return Verdict.NONCONFORMANT
            return Verdict.PASS if token == expected_token else Verdict.VIOLATION

        if self.type == "choice":
            allowed = {normalize_answer(v) for v in self.values}
            # Reject hedges: if the response mentions more than one distinct
            # allowed option ("Yes and no", "No, wait, yes", echoing
            # "Yes or No"), it did not commit to an answer.
            mentioned = {
                w for w in re.findall(r"[a-z0-9]+", _clean(answer)) if w in allowed
            }
            if len(mentioned) > 1:
                return Verdict.NONCONFORMANT
            correct = normalize_answer(self.value)
            if token == correct:
                return Verdict.PASS
            if token in allowed:
                return Verdict.VIOLATION
            return Verdict.NONCONFORMANT

        if self.type == "regex":
            if re.fullmatch(self.pattern, token) is not None:
                return Verdict.PASS
            if self.conformance and re.fullmatch(self.conformance, token) is not None:
                return Verdict.VIOLATION  # answer-shaped, wrong value
            return Verdict.NONCONFORMANT

        raise ValueError(f"unknown expected.type: {self.type}")


@dataclass(frozen=True)
class Link:
    relation: LinkRelation
    target: str  # scenario id within the same commitment


@dataclass(frozen=True)
class Scenario:
    id: str
    setup: str
    question: str
    paraphrases: tuple[str, ...]
    expected: Expected
    rationale: str = ""
    difficulty: str = "basic"  # basic | adversarial
    links: tuple[Link, ...] = ()

    @property
    def variants(self) -> tuple[str, ...]:
        """Canonical question first, then paraphrases."""
        return (self.question, *self.paraphrases)


@dataclass(frozen=True)
class Commitment:
    id: str
    title: str
    statement: str
    severity: str  # low | medium | high
    scenarios: tuple[Scenario, ...]
    lineage: tuple[str, ...] = ()  # prior work this category descends from

    def probe_count(self) -> int:
        return sum(len(s.variants) for s in self.scenarios)


@dataclass(frozen=True)
class Probe:
    """One concrete question to send to a model."""

    commitment_id: str
    scenario_id: str
    variant_index: int  # 0 = canonical
    prompt: str
    expected: Expected
    severity: str


SYSTEM_PROMPT = (
    "You are answering short factual questions about simple physical and "
    "temporal situations. Answer in the exact format the question requests. "
    "Do not explain, hedge, or add anything beyond the requested answer."
)


def _parse_expected(raw: dict) -> Expected:
    etype = raw.get("type", "exact")
    return Expected(
        type=etype,
        value=str(raw.get("value", "")),
        values=tuple(str(v) for v in raw.get("values", [])),
        pattern=str(raw.get("pattern", "")),
        conformance=str(raw.get("conformance", "")),
    )


def _parse_scenario(raw: dict, commitment_id: str) -> Scenario:
    links = tuple(
        Link(relation=LinkRelation(l["relation"]), target=str(l["target"]))
        for l in raw.get("links", [])
    )
    scenario = Scenario(
        id=str(raw["id"]),
        setup=str(raw["setup"]).strip(),
        question=str(raw["question"]).strip(),
        paraphrases=tuple(str(p).strip() for p in raw.get("paraphrases", [])),
        expected=_parse_expected(raw["expected"]),
        rationale=str(raw.get("rationale", "")).strip(),
        difficulty=str(raw.get("difficulty", "basic")),
        links=links,
    )
    _validate_scenario(scenario, commitment_id)
    return scenario


def _validate_scenario(s: Scenario, commitment_id: str) -> None:
    ctx = f"{commitment_id}/{s.id}"
    if not s.paraphrases:
        raise ValueError(f"{ctx}: scenario must have at least one paraphrase")
    if s.expected.type == "exact" and not s.expected.value:
        raise ValueError(f"{ctx}: exact expected requires value")
    if s.expected.type == "choice":
        if not s.expected.values or not s.expected.value:
            raise ValueError(f"{ctx}: choice expected requires values and value")
        norm = {normalize_answer(v) for v in s.expected.values}
        if normalize_answer(s.expected.value) not in norm:
            raise ValueError(f"{ctx}: expected.value must be one of expected.values")
        if len(norm) != len(s.expected.values):
            raise ValueError(f"{ctx}: expected.values collide after normalization")
    if s.expected.type == "regex" and not s.expected.pattern:
        raise ValueError(f"{ctx}: regex expected requires pattern")
    if s.difficulty not in ("basic", "adversarial"):
        raise ValueError(f"{ctx}: difficulty must be basic|adversarial")


def load_commitment(path: Path) -> Commitment:
    with open(path) as f:
        raw = yaml.safe_load(f)
    cid = str(raw["id"])
    scenarios = tuple(_parse_scenario(s, cid) for s in raw["scenarios"])
    seen: set[str] = set()
    for s in scenarios:
        if s.id in seen:
            raise ValueError(f"{cid}: duplicate scenario id {s.id}")
        seen.add(s.id)
    for s in scenarios:
        for link in s.links:
            if link.target not in seen:
                raise ValueError(f"{cid}/{s.id}: link target {link.target} not found")
    if raw.get("severity", "medium") not in ("low", "medium", "high"):
        raise ValueError(f"{cid}: severity must be low|medium|high")
    return Commitment(
        id=cid,
        title=str(raw["title"]),
        statement=str(raw["statement"]).strip(),
        severity=str(raw.get("severity", "medium")),
        scenarios=scenarios,
        lineage=tuple(str(x) for x in raw.get("lineage", [])),
    )


def load_commitments(directory: Path, only: list[str] | None = None) -> list[Commitment]:
    commitments = []
    for path in sorted(directory.glob("*.yaml")):
        c = load_commitment(path)
        if only and c.id not in only:
            continue
        commitments.append(c)
    if not commitments:
        raise FileNotFoundError(f"no commitment YAML files found in {directory}")
    return commitments


def build_probes(commitments: list[Commitment], limit_scenarios: int | None = None) -> Iterator[Probe]:
    for c in commitments:
        scenarios = c.scenarios[:limit_scenarios] if limit_scenarios else c.scenarios
        for s in scenarios:
            for i, variant in enumerate(s.variants):
                prompt = f"{s.setup}\n\n{variant}"
                yield Probe(
                    commitment_id=c.id,
                    scenario_id=s.id,
                    variant_index=i,
                    prompt=prompt,
                    expected=s.expected,
                    severity=c.severity,
                )
