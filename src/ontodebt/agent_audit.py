"""Offline agent-transcript auditing: deterministic behavioral rules over
recorded agent sessions — the measure leg for agents.

The chat harness (schema/runner/analysis) audits what a model *says* against
declared world-model commitments. This module audits what an agent *did*,
after the fact, against declared behavioral commitments. It is fully offline:
no API keys, no live agent, no LLM judge — every verdict is a regex check
over a recorded transcript, so the same transcript and rules always produce
the same verdicts.

Transcript format
-----------------
A transcript is a JSONL file: one JSON object per line, one event per object,
in the order the events occurred (file order is the temporal order; `turn` is
display metadata for humans and evidence, not an ordering key). Blank lines
are ignored. Fields:

    {"turn": 3, "role": "assistant", "content": "I'll run the tests."}
    {"turn": 4, "role": "tool", "content": "12 passed in 0.4s",
     "tool_name": "bash", "tool_args": {"command": "pytest -q"}}

- ``turn`` (required, int >= 0): the conversational turn the event belongs to.
- ``role`` (required): one of ``user`` | ``assistant`` | ``tool``.
- ``content`` (required, str; may be empty): message text or tool output.
- ``tool_name`` (optional, str): set on tool-call/tool-result events.
- ``tool_args`` (optional, object): the tool's arguments.

Unknown extra keys are ignored, so transcripts exported from richer formats
need only be projected down to these fields. The transcript id is the file
stem; treat it as a *stable session name* — re-recording the same named
session and re-auditing is what pays down (or renews) its ledger items.

Rule patterns are searched against an event's ``search_text``: the content
for user/assistant messages, and ``"<tool_name> <canonical-JSON-args>
<content>"`` for events carrying a tool name (canonical = sorted keys), so a
single regex can match a tool by name, by arguments, or by output.

Rule types (v0.2 — deliberately small and sound)
------------------------------------------------
- ``promise_kept`` — if an *assistant* event matches ``promise_pattern``, a
  strictly later assistant or tool event must match ``fulfillment_pattern``
  before the transcript ends. ``fulfillment_role`` (default ``any-agent``)
  restricts who may fulfill: set it to ``tool`` so the agent's own prose
  cannot satisfy its own promise — only recorded tool activity can. Each
  promise needs its own later fulfillment (one fulfillment event satisfies
  every promise before it). A promise with no later fulfillment is a
  **violation**.
- ``assertion_stability`` — ``capture_pattern`` (exactly one capture group)
  extracts asserted values from *assistant* events; all captured values in
  one transcript must be identical after whitespace-collapse + casefold.
  Drift is a **contradiction** (the agent disagrees with itself). Fewer than
  two captures is untestable, mirroring the chat harness's checkable-cluster
  rule.
- ``forbidden_after`` — after the first event matching ``trigger_pattern``
  (optionally scoped by ``trigger_role``), no strictly later assistant or
  tool event may match ``forbidden_pattern``. An occurrence is a
  **violation**. User events can trigger a rule but never violate one — only
  the agent's own actions are on the hook.

A rule whose precondition never fired (no promise made, fewer than two
captures, trigger never matched) is **not applicable**: it can neither accrue
debt nor pay it down — absence of evidence is not evidence of compliance.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml

from .analysis import CommitmentStats, ScenarioOutcome
from .schema import _check_redos

RULE_TYPES = ("promise_kept", "assertion_stability", "forbidden_after")
EVENT_ROLES = ("user", "assistant", "tool")
AGENT_ACTION_ROLES = ("assistant", "tool")  # roles that can fulfill or violate
TRIGGER_ROLES = ("any",) + EVENT_ROLES
FULFILLMENT_ROLES = ("any-agent",) + AGENT_ACTION_ROLES


class AgentVerdict(str, Enum):
    PASS = "pass"
    VIOLATION = "violation"          # transcript contradicts the commitment
    CONTRADICTION = "contradiction"  # agent contradicts itself
    NOT_APPLICABLE = "not_applicable"  # rule's precondition never fired


# --------------------------------------------------------------------------
# Transcripts
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class TranscriptEvent:
    index: int  # 0-based position in the file: the ordering authority
    turn: int
    role: str
    content: str
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)

    @property
    def search_text(self) -> str:
        """Deterministic text that rule patterns are searched against."""
        if self.tool_name:
            args = (
                json.dumps(self.tool_args, sort_keys=True, ensure_ascii=False)
                if self.tool_args
                else ""
            )
            return " ".join(part for part in (self.tool_name, args, self.content) if part)
        return self.content


@dataclass(frozen=True)
class Transcript:
    id: str  # file stem; a stable session name for ledger purposes
    path: str
    events: tuple[TranscriptEvent, ...]


def _parse_event(raw: object, index: int, ctx: str) -> TranscriptEvent:
    if not isinstance(raw, dict):
        raise ValueError(f"{ctx}: event must be a JSON object, got {type(raw).__name__}")
    turn = raw.get("turn")
    if isinstance(turn, bool) or not isinstance(turn, int) or turn < 0:
        raise ValueError(f"{ctx}: 'turn' must be a non-negative integer")
    role = raw.get("role")
    if role not in EVENT_ROLES:
        raise ValueError(f"{ctx}: 'role' must be one of {'|'.join(EVENT_ROLES)}, got {role!r}")
    content = raw.get("content")
    if not isinstance(content, str):
        raise ValueError(f"{ctx}: 'content' must be a string (may be empty)")
    tool_name = raw.get("tool_name", "")
    if not isinstance(tool_name, str):
        raise ValueError(f"{ctx}: 'tool_name' must be a string")
    tool_args = raw.get("tool_args", {})
    if not isinstance(tool_args, dict):
        raise ValueError(f"{ctx}: 'tool_args' must be an object")
    return TranscriptEvent(
        index=index, turn=turn, role=role, content=content,
        tool_name=tool_name, tool_args=tool_args,
    )


def transcript_from_events(transcript_id: str, raw_events: list[dict], path: str = "") -> Transcript:
    """Build an in-memory transcript (also the parsing core of the loader)."""
    events = tuple(
        _parse_event(raw, i, f"{transcript_id}[{i}]") for i, raw in enumerate(raw_events)
    )
    return Transcript(id=transcript_id, path=path, events=events)


def load_transcript(path: Path) -> Transcript:
    if "@" in path.stem:
        # '@' is the separator in ledger scenario ids ("rule@transcript");
        # allowing it in a session name would let two sessions collide.
        raise ValueError(
            f"{path.name}: transcript file name must not contain '@' "
            f"(reserved as the rule@transcript ledger separator)"
        )
    try:
        # utf-8-sig: tolerate a UTF-8 BOM (common in Windows-exported files).
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path.name}: not valid UTF-8: {exc}") from exc
    raws: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            raws.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{lineno}: invalid JSON: {exc}") from exc
    events = tuple(
        _parse_event(raw, i, f"{path.name}: event {i}") for i, raw in enumerate(raws)
    )
    return Transcript(id=path.stem, path=str(path), events=events)


def load_transcripts(path: Path) -> list[Transcript]:
    """Load one .jsonl file, or every *.jsonl in a directory (sorted)."""
    if path.is_file():
        return [load_transcript(path)]
    if path.is_dir():
        files = sorted(path.glob("*.jsonl"))
        if not files:
            raise FileNotFoundError(f"no *.jsonl transcripts found in {path}")
        return [load_transcript(f) for f in files]
    raise FileNotFoundError(f"transcript path not found: {path}")


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentRule:
    id: str
    title: str
    type: str      # promise_kept | assertion_stability | forbidden_after
    severity: str  # low | medium | high
    rationale: str
    promise_pattern: str = ""
    fulfillment_pattern: str = ""
    capture_pattern: str = ""
    trigger_pattern: str = ""
    forbidden_pattern: str = ""
    trigger_role: str = "any"  # forbidden_after only: any | user | assistant | tool
    fulfillment_role: str = "any-agent"  # promise_kept only: any-agent | assistant | tool


@dataclass(frozen=True)
class RulePack:
    id: str
    title: str
    statement: str
    rules: tuple[AgentRule, ...]


_FIELDS_BY_TYPE = {
    "promise_kept": ("promise_pattern", "fulfillment_pattern"),
    "assertion_stability": ("capture_pattern",),
    "forbidden_after": ("trigger_pattern", "forbidden_pattern"),
}
_PATTERN_FIELDS = tuple(sorted({f for fs in _FIELDS_BY_TYPE.values() for f in fs}))


def _compile(pattern: str, ctx: str, fname: str) -> re.Pattern:
    try:
        return re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"{ctx}: {fname} is not a valid regex: {exc}") from exc


def _parse_rule(raw: object, pack_id: str) -> AgentRule:
    if not isinstance(raw, dict):
        raise ValueError(
            f"{pack_id}: each rule must be a mapping, got {type(raw).__name__}"
        )
    rule_id = str(raw.get("id", ""))
    ctx = f"{pack_id}/{rule_id or '<missing id>'}"
    if not rule_id:
        raise ValueError(f"{ctx}: rule requires an id")
    if "@" in rule_id:
        # '@' is the separator in ledger scenario ids ("rule@transcript").
        raise ValueError(f"{ctx}: rule id must not contain '@'")
    rtype = str(raw.get("type", ""))
    if rtype not in RULE_TYPES:
        raise ValueError(f"{ctx}: type must be one of {'|'.join(RULE_TYPES)}, got {rtype!r}")
    severity = str(raw.get("severity", ""))
    if severity not in ("low", "medium", "high"):
        raise ValueError(f"{ctx}: severity must be low|medium|high")
    rationale = str(raw.get("rationale", "")).strip()
    if not rationale:
        raise ValueError(f"{ctx}: rule requires a rationale (say why the pattern is a fair proxy)")
    if not str(raw.get("title", "")).strip():
        raise ValueError(f"{ctx}: rule requires a title")
    trigger_role = str(raw.get("trigger_role", "any"))
    if trigger_role not in TRIGGER_ROLES:
        raise ValueError(f"{ctx}: trigger_role must be one of {'|'.join(TRIGGER_ROLES)}")
    if trigger_role != "any" and rtype != "forbidden_after":
        raise ValueError(f"{ctx}: trigger_role is only valid for forbidden_after rules")
    fulfillment_role = str(raw.get("fulfillment_role", "any-agent"))
    if fulfillment_role not in FULFILLMENT_ROLES:
        raise ValueError(
            f"{ctx}: fulfillment_role must be one of {'|'.join(FULFILLMENT_ROLES)}"
        )
    if fulfillment_role != "any-agent" and rtype != "promise_kept":
        raise ValueError(f"{ctx}: fulfillment_role is only valid for promise_kept rules")

    required = _FIELDS_BY_TYPE[rtype]
    for fname in _PATTERN_FIELDS:
        value = str(raw.get(fname, ""))
        if fname in required and not value:
            raise ValueError(f"{ctx}: {rtype} requires {fname}")
        if fname not in required and value:
            raise ValueError(f"{ctx}: {fname} is not a valid field for {rtype}")
    for fname in required:
        pattern = str(raw[fname])
        compiled = _compile(pattern, ctx, fname)
        # The haystack is agent-controlled text and Python's `re` has no
        # timeout, so reject catastrophic-backtracking shapes at load time.
        _check_redos(pattern, f"{ctx}: {fname}")
        if fname == "capture_pattern" and compiled.groups != 1:
            raise ValueError(
                f"{ctx}: capture_pattern must have exactly one capture group, has {compiled.groups}"
            )

    return AgentRule(
        id=rule_id,
        title=str(raw["title"]).strip(),
        type=rtype,
        severity=severity,
        rationale=rationale,
        promise_pattern=str(raw.get("promise_pattern", "")),
        fulfillment_pattern=str(raw.get("fulfillment_pattern", "")),
        capture_pattern=str(raw.get("capture_pattern", "")),
        trigger_pattern=str(raw.get("trigger_pattern", "")),
        forbidden_pattern=str(raw.get("forbidden_pattern", "")),
        trigger_role=trigger_role,
        fulfillment_role=fulfillment_role,
    )


def load_rule_pack(path: Path) -> RulePack:
    try:
        with open(path, encoding="utf-8-sig") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path.name}: invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(
            f"{path.name}: rule pack must be a YAML mapping with 'id', 'title' "
            f"and 'rules', got {type(raw).__name__}"
        )
    for key in ("id", "title"):
        if not str(raw.get(key, "")).strip():
            raise ValueError(f"{path.name}: rule pack requires a non-empty '{key}'")
    pack_id = str(raw["id"])
    raw_rules = raw.get("rules", [])
    if not isinstance(raw_rules, list):
        raise ValueError(f"{path.name}: 'rules' must be a list")
    rules = tuple(_parse_rule(r, pack_id) for r in raw_rules)
    if not rules:
        raise ValueError(f"{pack_id}: rule pack has no rules")
    seen: set[str] = set()
    for r in rules:
        if r.id in seen:
            raise ValueError(f"{pack_id}: duplicate rule id {r.id}")
        seen.add(r.id)
    return RulePack(
        id=pack_id,
        title=str(raw["title"]),
        statement=str(raw.get("statement", "")).strip(),
        rules=rules,
    )


def load_rule_packs(directory: Path) -> list[RulePack]:
    packs = [load_rule_pack(p) for p in sorted(directory.glob("*.yaml"))]
    if not packs:
        raise FileNotFoundError(f"no rule pack YAML files found in {directory}")
    seen: set[str] = set()
    for pack in packs:
        if pack.id in seen:
            raise ValueError(f"duplicate rule pack id: {pack.id}")
        seen.add(pack.id)
    return packs


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------

@dataclass
class RuleFinding:
    """One rule checked against one transcript. `checkable` means the rule's
    precondition fired, i.e. the run is evidence the ledger may pay down on."""

    pack_id: str
    rule_id: str
    rule_title: str
    rule_type: str
    transcript_id: str
    severity: str
    verdict: str  # AgentVerdict value
    checkable: bool
    captures: tuple[str, ...] = ()  # assertion_stability: normalized values, in order
    evidence: list[dict] = field(default_factory=list)


def _excerpt(text: str, match: re.Match, radius: int = 40) -> str:
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    snippet = " ".join(text[start:end].split())
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{snippet}{suffix}"


def _evidence(event: TranscriptEvent, match: re.Match, note: str) -> dict:
    return {
        "turn": event.turn,
        "event_index": event.index,
        "role": event.role,
        "excerpt": _excerpt(event.search_text, match),
        "note": note,
    }


def _normalize_capture(value: str) -> str:
    return " ".join(value.split()).casefold()


def _finding(rule: AgentRule, pack_id: str, transcript: Transcript, **kw) -> RuleFinding:
    return RuleFinding(
        pack_id=pack_id,
        rule_id=rule.id,
        rule_title=rule.title,
        rule_type=rule.type,
        transcript_id=transcript.id,
        severity=rule.severity,
        **kw,
    )


def _eval_promise_kept(rule: AgentRule, pack_id: str, transcript: Transcript) -> RuleFinding:
    promise_re = re.compile(rule.promise_pattern)
    fulfil_re = re.compile(rule.fulfillment_pattern)
    promises: list[tuple[TranscriptEvent, re.Match]] = []
    last_fulfillment = -1
    for event in transcript.events:
        text = event.search_text
        if event.role == "assistant":
            m = promise_re.search(text)
            if m:
                promises.append((event, m))
        if (
            event.role in AGENT_ACTION_ROLES
            and rule.fulfillment_role in ("any-agent", event.role)
            and fulfil_re.search(text)
        ):
            last_fulfillment = event.index
    if not promises:
        return _finding(
            rule, pack_id, transcript,
            verdict=AgentVerdict.NOT_APPLICABLE.value, checkable=False,
        )
    # A fulfillment satisfies every promise strictly before it; a promise
    # needs at least one strictly later fulfillment.
    broken = [(e, m) for e, m in promises if e.index >= last_fulfillment]
    if broken:
        return _finding(
            rule, pack_id, transcript,
            verdict=AgentVerdict.VIOLATION.value, checkable=True,
            evidence=[_evidence(e, m, "promise with no later fulfillment") for e, m in broken],
        )
    return _finding(rule, pack_id, transcript, verdict=AgentVerdict.PASS.value, checkable=True)


def _eval_assertion_stability(rule: AgentRule, pack_id: str, transcript: Transcript) -> RuleFinding:
    capture_re = re.compile(rule.capture_pattern)
    captured: list[tuple[TranscriptEvent, re.Match, str]] = []
    for event in transcript.events:
        if event.role != "assistant":
            continue
        for m in capture_re.finditer(event.search_text):
            captured.append((event, m, _normalize_capture(m.group(1))))
    values = tuple(v for _, _, v in captured)
    evidence = [
        _evidence(e, m, f"asserted value: {v!r}") for e, m, v in captured
    ]
    if len(captured) < 2:
        # One assertion cannot drift; mirror the chat harness's rule that a
        # cluster with < 2 answers is untestable, not consistent.
        return _finding(
            rule, pack_id, transcript,
            verdict=AgentVerdict.NOT_APPLICABLE.value, checkable=False,
            captures=values, evidence=evidence,
        )
    if len(set(values)) > 1:
        return _finding(
            rule, pack_id, transcript,
            verdict=AgentVerdict.CONTRADICTION.value, checkable=True,
            captures=values, evidence=evidence,
        )
    return _finding(
        rule, pack_id, transcript,
        verdict=AgentVerdict.PASS.value, checkable=True, captures=values,
    )


def _eval_forbidden_after(rule: AgentRule, pack_id: str, transcript: Transcript) -> RuleFinding:
    trigger_re = re.compile(rule.trigger_pattern)
    forbidden_re = re.compile(rule.forbidden_pattern)
    trigger: tuple[TranscriptEvent, re.Match] | None = None
    for event in transcript.events:
        if rule.trigger_role not in ("any", event.role):
            continue
        m = trigger_re.search(event.search_text)
        if m:
            trigger = (event, m)
            break
    if trigger is None:
        return _finding(
            rule, pack_id, transcript,
            verdict=AgentVerdict.NOT_APPLICABLE.value, checkable=False,
        )
    trigger_event, trigger_match = trigger
    hits = []
    for event in transcript.events[trigger_event.index + 1:]:
        if event.role not in AGENT_ACTION_ROLES:
            continue
        m = forbidden_re.search(event.search_text)
        if m:
            hits.append(_evidence(event, m, "forbidden event after trigger"))
    if hits:
        return _finding(
            rule, pack_id, transcript,
            verdict=AgentVerdict.VIOLATION.value, checkable=True,
            evidence=[_evidence(trigger_event, trigger_match, "trigger"), *hits],
        )
    return _finding(rule, pack_id, transcript, verdict=AgentVerdict.PASS.value, checkable=True)


_EVALUATORS = {
    "promise_kept": _eval_promise_kept,
    "assertion_stability": _eval_assertion_stability,
    "forbidden_after": _eval_forbidden_after,
}


def evaluate_rule(rule: AgentRule, transcript: Transcript, pack_id: str = "") -> RuleFinding:
    return _EVALUATORS[rule.type](rule, pack_id, transcript)


def audit_transcripts(packs: list[RulePack], transcripts: list[Transcript]) -> list[RuleFinding]:
    """Every rule against every transcript, in deterministic order."""
    ordered = sorted(transcripts, key=lambda t: t.id)
    findings: list[RuleFinding] = []
    for pack in packs:
        for rule in pack.rules:
            for transcript in ordered:
                findings.append(evaluate_rule(rule, transcript, pack_id=pack.id))
    return findings


# --------------------------------------------------------------------------
# Ledger integration
# --------------------------------------------------------------------------

def findings_to_stats(packs: list[RulePack], findings: list[RuleFinding]) -> dict[str, CommitmentStats]:
    """Shape findings into the stats structure `Ledger.update` consumes.

    One ledger scenario per (rule, transcript): scenario_id = "rule@transcript".
    promise_kept / forbidden_after failures are *violations* (the transcript
    contradicts the commitment); assertion_stability failures are
    *contradictions* (the agent contradicts itself). Payability reuses the
    chat semantics untouched: a violation item pays down only when the rule
    was exercised (`answers` non-empty), a contradiction item only when the
    cluster was checkable (>= 2 captures).
    """
    titles = {p.id: p.title for p in packs}
    stats: dict[str, CommitmentStats] = {}
    for f in findings:
        cs = stats.get(f.pack_id)
        if cs is None:
            cs = CommitmentStats(
                commitment_id=f.pack_id,
                title=titles.get(f.pack_id, f.pack_id),
                severity="medium",  # fallback only; every rule sets its own below
            )
            stats[f.pack_id] = cs
        sid = f"{f.rule_id}@{f.transcript_id}"
        outcome = ScenarioOutcome(scenario_id=sid)
        if f.rule_type == "assertion_stability":
            # Gate on checkable (>= 2 captures): a single-capture run is NOT
            # APPLICABLE and must not read as evidence that pays down an old
            # item under the same sid (e.g. after a rule changes type).
            outcome.answers = list(f.captures) if f.checkable else []
            outcome.verdicts = ["pass"]
            outcome.inconsistent = f.verdict == AgentVerdict.CONTRADICTION.value
        else:
            outcome.answers = ["exercised"] if f.checkable else []
            outcome.verdicts = [
                "violation" if f.verdict == AgentVerdict.VIOLATION.value else "pass"
            ]
        cs.scenario_outcomes[sid] = outcome
        cs.scenario_severities[sid] = f.severity
        cs.n_scenarios += 1
    return stats
