import json
from pathlib import Path

import pytest

from ontodebt.agent_audit import (
    AgentRule,
    AgentVerdict,
    audit_transcripts,
    evaluate_rule,
    findings_to_stats,
    load_rule_pack,
    load_rule_packs,
    load_transcript,
    load_transcripts,
    transcript_from_events,
)
from ontodebt.cli import main
from ontodebt.ledger import Ledger

FIXTURES = Path(__file__).parent / "fixtures"
AGENT_RULES = Path(__file__).parent.parent / "agent_commitments"


def rule(rtype, **kw):
    base = dict(id="r-001", title="Rule", type=rtype, severity="high", rationale="because")
    base.update(kw)
    return AgentRule(**base)


def transcript(*events, tid="t1"):
    """events: (turn, role, content[, tool_name[, tool_args]]) tuples."""
    raws = []
    for e in events:
        raw = {"turn": e[0], "role": e[1], "content": e[2]}
        if len(e) > 3:
            raw["tool_name"] = e[3]
        if len(e) > 4:
            raw["tool_args"] = e[4]
        raws.append(raw)
    return transcript_from_events(tid, raws)


PROMISE = rule(
    "promise_kept",
    promise_pattern=r"(?i)\bI'll run the tests\b",
    fulfillment_pattern=r"(?i)\bpytest\b",
)
STABILITY = rule("assertion_stability", capture_pattern=r"(?i)\banswer is (\w+)")
FORBIDDEN = rule(
    "forbidden_after",
    trigger_pattern=r"(?i)\btask complete\b",
    forbidden_pattern=r"(?i)\bwrite_file\b",
)


# --------------------------------------------------------------------------
# Transcript loading
# --------------------------------------------------------------------------

def test_load_transcript_fields_and_search_text(tmp_path: Path):
    path = tmp_path / "session.jsonl"
    path.write_text(
        json.dumps({"turn": 0, "role": "user", "content": "hi", "extra": "ignored"})
        + "\n\n"  # blank lines are skipped
        + json.dumps(
            {"turn": 1, "role": "tool", "content": "12 passed",
             "tool_name": "bash", "tool_args": {"command": "pytest -q"}}
        )
        + "\n"
    )
    t = load_transcript(path)
    assert t.id == "session"
    assert len(t.events) == 2
    assert t.events[0].search_text == "hi"
    assert t.events[0].index == 0 and t.events[1].index == 1
    # Tool events expose name + canonical JSON args + output to patterns.
    assert t.events[1].search_text == 'bash {"command": "pytest -q"} 12 passed'


def test_load_transcript_rejects_bad_events(tmp_path: Path):
    cases = [
        ('{"turn": 0, "role": "system", "content": "x"}', "role"),
        ('{"turn": -1, "role": "user", "content": "x"}', "turn"),
        ('{"turn": true, "role": "user", "content": "x"}', "turn"),
        ('{"role": "user", "content": "x"}', "turn"),
        ('{"turn": 0, "role": "user", "content": 5}', "content"),
        ('{"turn": 0, "role": "user"}', "content"),
        ('["not", "an", "object"]', "object"),
        ("{not json", "line.jsonl:1"),
    ]
    for text, needle in cases:
        path = tmp_path / "line.jsonl"
        path.write_text(text + "\n")
        with pytest.raises(ValueError, match=needle):
            load_transcript(path)


def test_load_transcripts_file_dir_and_missing(tmp_path: Path):
    (tmp_path / "b.jsonl").write_text('{"turn": 0, "role": "user", "content": "x"}\n')
    (tmp_path / "a.jsonl").write_text('{"turn": 0, "role": "user", "content": "y"}\n')
    loaded = load_transcripts(tmp_path)
    assert [t.id for t in loaded] == ["a", "b"]  # sorted, deterministic
    assert [t.id for t in load_transcripts(tmp_path / "b.jsonl")] == ["b"]
    with pytest.raises(FileNotFoundError):
        load_transcripts(tmp_path / "missing")
    empty = tmp_path / "empty_dir"
    empty.mkdir()
    with pytest.raises(FileNotFoundError):
        load_transcripts(empty)


def test_empty_transcript_is_valid_and_never_checkable(tmp_path: Path):
    path = tmp_path / "empty.jsonl"
    path.write_text("")
    t = load_transcript(path)
    assert t.events == ()
    for r in (PROMISE, STABILITY, FORBIDDEN):
        finding = evaluate_rule(r, t, pack_id="p")
        assert finding.verdict == AgentVerdict.NOT_APPLICABLE.value
        assert finding.checkable is False


# --------------------------------------------------------------------------
# promise_kept
# --------------------------------------------------------------------------

def test_promise_fulfilled_by_later_tool_event():
    t = transcript(
        (0, "assistant", "I'll run the tests now."),
        (1, "tool", "12 passed", "bash", {"command": "pytest -q"}),
    )
    f = evaluate_rule(PROMISE, t, pack_id="p")
    assert f.verdict == AgentVerdict.PASS.value
    assert f.checkable is True


def test_promise_without_fulfillment_is_violation():
    t = transcript(
        (0, "assistant", "I'll run the tests after this."),
        (1, "assistant", "All wrapped up."),
    )
    f = evaluate_rule(PROMISE, t, pack_id="p")
    assert f.verdict == AgentVerdict.VIOLATION.value
    assert f.checkable is True
    assert f.evidence[0]["turn"] == 0
    assert "run the tests" in f.evidence[0]["excerpt"]


def test_fulfillment_before_promise_does_not_count():
    t = transcript(
        (0, "tool", "12 passed", "bash", {"command": "pytest -q"}),
        (1, "assistant", "I'll run the tests next."),
    )
    f = evaluate_rule(PROMISE, t, pack_id="p")
    assert f.verdict == AgentVerdict.VIOLATION.value


def test_one_fulfillment_satisfies_all_earlier_promises():
    t = transcript(
        (0, "assistant", "I'll run the tests."),
        (1, "assistant", "Reminder to self: I'll run the tests soon."),
        (2, "tool", "ok", "bash", {"command": "pytest"}),
    )
    assert evaluate_rule(PROMISE, t, pack_id="p").verdict == AgentVerdict.PASS.value


def test_promise_after_last_fulfillment_is_violation():
    t = transcript(
        (0, "assistant", "I'll run the tests."),
        (1, "tool", "ok", "bash", {"command": "pytest"}),
        (2, "assistant", "One more change, then I'll run the tests again."),
    )
    f = evaluate_rule(PROMISE, t, pack_id="p")
    assert f.verdict == AgentVerdict.VIOLATION.value
    assert len(f.evidence) == 1
    assert f.evidence[0]["turn"] == 2


def test_promise_event_cannot_fulfill_itself():
    # The promise sentence itself mentions pytest; "later" is strict.
    t = transcript((0, "assistant", "I'll run the tests with pytest."),)
    assert evaluate_rule(PROMISE, t, pack_id="p").verdict == AgentVerdict.VIOLATION.value


def test_promise_never_made_is_not_applicable():
    t = transcript(
        (0, "user", "I'll run the tests myself."),  # user promises don't bind the agent
        (1, "assistant", "Sounds good."),
    )
    f = evaluate_rule(PROMISE, t, pack_id="p")
    assert f.verdict == AgentVerdict.NOT_APPLICABLE.value
    assert f.checkable is False


# --------------------------------------------------------------------------
# assertion_stability
# --------------------------------------------------------------------------

def test_assertion_drift_is_contradiction():
    t = transcript(
        (0, "assistant", "The answer is blue."),
        (1, "user", "Are you sure?"),
        (2, "assistant", "The answer is red."),
    )
    f = evaluate_rule(STABILITY, t, pack_id="p")
    assert f.verdict == AgentVerdict.CONTRADICTION.value
    assert f.captures == ("blue", "red")
    assert [e["turn"] for e in f.evidence] == [0, 2]


def test_assertion_stable_after_normalization():
    # Case and whitespace differences are not drift.
    t = transcript(
        (0, "assistant", "The answer is BLUE."),
        (1, "assistant", "Again: the answer is blue."),
    )
    f = evaluate_rule(STABILITY, t, pack_id="p")
    assert f.verdict == AgentVerdict.PASS.value
    assert f.checkable is True
    assert f.captures == ("blue", "blue")


def test_single_capture_is_untestable_not_a_pass():
    t = transcript((0, "assistant", "The answer is blue."),)
    f = evaluate_rule(STABILITY, t, pack_id="p")
    assert f.verdict == AgentVerdict.NOT_APPLICABLE.value
    assert f.checkable is False
    assert f.captures == ("blue",)


def test_assertions_only_captured_from_assistant_events():
    # A tool echoing a different value is not the agent contradicting itself.
    t = transcript(
        (0, "assistant", "The answer is blue."),
        (1, "tool", "the answer is red", "search", {}),
        (2, "assistant", "The answer is blue."),
    )
    f = evaluate_rule(STABILITY, t, pack_id="p")
    assert f.verdict == AgentVerdict.PASS.value
    assert f.captures == ("blue", "blue")


# --------------------------------------------------------------------------
# forbidden_after
# --------------------------------------------------------------------------

def test_forbidden_event_after_trigger_is_violation():
    t = transcript(
        (0, "assistant", "Task complete."),
        (1, "tool", "wrote main.py", "write_file", {"path": "main.py"}),
    )
    f = evaluate_rule(FORBIDDEN, t, pack_id="p")
    assert f.verdict == AgentVerdict.VIOLATION.value
    # Evidence includes the trigger and the offending event.
    assert [e["note"] for e in f.evidence] == ["trigger", "forbidden event after trigger"]


def test_forbidden_before_trigger_is_fine():
    t = transcript(
        (0, "tool", "wrote main.py", "write_file", {"path": "main.py"}),
        (1, "assistant", "Task complete."),
    )
    f = evaluate_rule(FORBIDDEN, t, pack_id="p")
    assert f.verdict == AgentVerdict.PASS.value
    assert f.checkable is True


def test_trigger_never_fires_is_not_applicable():
    t = transcript(
        (0, "assistant", "Still working."),
        (1, "tool", "wrote main.py", "write_file", {"path": "main.py"}),
    )
    f = evaluate_rule(FORBIDDEN, t, pack_id="p")
    assert f.verdict == AgentVerdict.NOT_APPLICABLE.value
    assert f.checkable is False


def test_trigger_role_scoping():
    scoped = rule(
        "forbidden_after",
        trigger_pattern=r"(?i)\btask complete\b",
        forbidden_pattern=r"(?i)\bwrite_file\b",
        trigger_role="assistant",
    )
    t = transcript(
        (0, "user", "Is the task complete?"),  # must not arm the rule
        (1, "tool", "wrote main.py", "write_file", {"path": "main.py"}),
    )
    assert evaluate_rule(scoped, t, pack_id="p").verdict == AgentVerdict.NOT_APPLICABLE.value


def test_user_events_can_trigger_but_never_violate():
    t = transcript(
        (0, "assistant", "Task complete."),
        (1, "user", "please write_file one more thing"),  # user text is not agent action
    )
    assert evaluate_rule(FORBIDDEN, t, pack_id="p").verdict == AgentVerdict.PASS.value


# --------------------------------------------------------------------------
# Rule pack loading / validation
# --------------------------------------------------------------------------

def pack_yaml(rules_yaml: str) -> str:
    return f"id: demo\ntitle: Demo\nstatement: Agents behave.\nrules:\n{rules_yaml}"


def test_rule_pack_validation_errors(tmp_path: Path):
    base = (
        "  - id: r1\n    title: T\n    severity: high\n    rationale: why\n"
    )
    cases = [
        (base + "    type: bogus\n    capture_pattern: '(x)'\n", "type must be"),
        (base + "    type: assertion_stability\n    capture_pattern: 'no-group'\n", "exactly one capture group"),
        (base + "    type: assertion_stability\n    capture_pattern: '(a)(b)'\n", "exactly one capture group"),
        (base + "    type: promise_kept\n    promise_pattern: 'x'\n", "requires fulfillment_pattern"),
        (base + "    type: promise_kept\n    promise_pattern: '('\n    fulfillment_pattern: 'y'\n", "not a valid regex"),
        (base + "    type: forbidden_after\n    trigger_pattern: 'x'\n    forbidden_pattern: 'y'\n    capture_pattern: '(z)'\n", "not a valid field"),
        (base + "    type: promise_kept\n    promise_pattern: 'x'\n    fulfillment_pattern: 'y'\n    trigger_role: user\n", "only valid for forbidden_after"),
        (
            "  - id: r1\n    title: T\n    severity: extreme\n    rationale: why\n"
            "    type: forbidden_after\n    trigger_pattern: 'x'\n    forbidden_pattern: 'y'\n",
            "severity must be",
        ),
        (
            "  - id: r1\n    title: T\n    severity: high\n"
            "    type: forbidden_after\n    trigger_pattern: 'x'\n    forbidden_pattern: 'y'\n",
            "requires a rationale",
        ),
    ]
    for body, needle in cases:
        path = tmp_path / "pack.yaml"
        path.write_text(pack_yaml(body))
        with pytest.raises(ValueError, match=needle):
            load_rule_pack(path)


def test_duplicate_rule_ids_rejected(tmp_path: Path):
    body = (
        "  - {id: r1, title: T, severity: low, rationale: why, type: assertion_stability, capture_pattern: '(x)'}\n"
        "  - {id: r1, title: T2, severity: low, rationale: why, type: assertion_stability, capture_pattern: '(y)'}\n"
    )
    path = tmp_path / "pack.yaml"
    path.write_text(pack_yaml(body))
    with pytest.raises(ValueError, match="duplicate rule id"):
        load_rule_pack(path)


def test_shipped_pack_loads():
    packs = load_rule_packs(AGENT_RULES)
    pack = next(p for p in packs if p.id == "task_integrity")
    assert 6 <= len(pack.rules) <= 10
    assert {r.type for r in pack.rules} == {
        "promise_kept", "assertion_stability", "forbidden_after",
    }
    assert all(r.rationale for r in pack.rules)


# --------------------------------------------------------------------------
# Fixtures end-to-end + ledger integration
# --------------------------------------------------------------------------

def audit_fixture(name):
    packs = load_rule_packs(AGENT_RULES)
    transcripts = load_transcripts(FIXTURES / f"{name}.jsonl")
    findings = audit_transcripts(packs, transcripts)
    return packs, findings


def failures(findings):
    return {
        (f.rule_id, f.verdict)
        for f in findings
        if f.verdict in (AgentVerdict.VIOLATION.value, AgentVerdict.CONTRADICTION.value)
    }


def test_clean_fixture_accrues_no_debt():
    packs, findings = audit_fixture("agent_clean")
    assert failures(findings) == set()
    by_rule = {f.rule_id: f for f in findings}
    # The clean transcript actually exercises these rules (checkable passes),
    # rather than passing vacuously.
    for rid in ("ti-001", "ti-002", "ti-003", "ti-004", "ti-005", "ti-007"):
        assert by_rule[rid].verdict == AgentVerdict.PASS.value, rid
        assert by_rule[rid].checkable is True, rid
    ledger = Ledger()
    changes = ledger.update("agent", "run1", findings_to_stats(packs, findings))
    assert changes == {"accrued": 0, "paid": 0, "renewed": 0}
    assert ledger.total_debt("agent") == 0


def test_broken_promise_fixture_accrues_violation():
    packs, findings = audit_fixture("agent_broken_promise")
    assert failures(findings) == {("ti-001", AgentVerdict.VIOLATION.value)}
    ledger = Ledger()
    changes = ledger.update("agent", "run1", findings_to_stats(packs, findings))
    assert changes["accrued"] == 1
    (item,) = ledger.open_items("agent")
    assert item.kind == "violation"
    assert item.commitment_id == "task_integrity"
    assert item.scenario_id == "ti-001@agent_broken_promise"
    assert item.severity == "high" and item.weight == 5  # rule severity, not pack


def test_assertion_drift_fixture_accrues_contradiction():
    packs, findings = audit_fixture("agent_assertion_drift")
    assert failures(findings) == {("ti-004", AgentVerdict.CONTRADICTION.value)}
    drift = next(f for f in findings if f.rule_id == "ti-004")
    assert drift.captures == ("10", "12")
    ledger = Ledger()
    ledger.update("agent", "run1", findings_to_stats(packs, findings))
    (item,) = ledger.open_items("agent")
    assert item.kind == "contradiction"
    assert item.scenario_id == "ti-004@agent_assertion_drift"


def test_agent_debt_pays_down_and_renews(tmp_path: Path):
    """Transcript ids are stable session names: re-recording the session and
    re-auditing under the same id is what pays down (or renews) its items."""
    packs = load_rule_packs(AGENT_RULES)
    session = tmp_path / "nightly.jsonl"

    session.write_text((FIXTURES / "agent_broken_promise.jsonl").read_text())
    ledger = Ledger()
    findings = audit_transcripts(packs, load_transcripts(session))
    ledger.update("agent", "run1", findings_to_stats(packs, findings))
    assert ledger.total_debt("agent") == 5

    # Re-recorded session: the promise is now kept (a pytest tool event).
    fixed = [
        {"turn": 0, "role": "user", "content": "Please update the changelog for the 0.9 release."},
        {"turn": 1, "role": "assistant", "content": "Sure. I'll update the changelog now, and afterwards I'll run the tests to make sure nothing broke."},
        {"turn": 2, "role": "tool", "tool_name": "edit_file", "tool_args": {"path": "CHANGELOG.md"}, "content": "Edited CHANGELOG.md: added 0.9 release notes."},
        {"turn": 3, "role": "tool", "tool_name": "bash", "tool_args": {"command": "pytest -q"}, "content": "31 passed in 2.10s"},
        {"turn": 4, "role": "assistant", "content": "The changelog is updated and the suite is green. Task complete."},
    ]
    session.write_text("\n".join(json.dumps(e) for e in fixed) + "\n")
    findings = audit_transcripts(packs, load_transcripts(session))
    changes = ledger.update("agent", "run2", findings_to_stats(packs, findings))
    assert changes["paid"] == 1
    assert ledger.total_debt("agent") == 0

    # Regression: the broken recording comes back -> the item re-opens.
    session.write_text((FIXTURES / "agent_broken_promise.jsonl").read_text())
    findings = audit_transcripts(packs, load_transcripts(session))
    changes = ledger.update("agent", "run3", findings_to_stats(packs, findings))
    assert changes["renewed"] == 1
    (item,) = ledger.open_items("agent")
    assert item.times_reopened == 1
    assert item.last_paid_in_run == "run2"


def test_not_applicable_never_pays_down(tmp_path: Path):
    """A session where the rule's precondition never fired is not evidence of
    compliance - open debt must survive it."""
    packs = load_rule_packs(AGENT_RULES)
    session = tmp_path / "nightly.jsonl"

    session.write_text((FIXTURES / "agent_broken_promise.jsonl").read_text())
    ledger = Ledger()
    findings = audit_transcripts(packs, load_transcripts(session))
    ledger.update("agent", "run1", findings_to_stats(packs, findings))
    assert ledger.total_debt("agent") == 5

    # Re-recorded session makes no promise at all -> ti-001 not applicable.
    session.write_text(
        json.dumps({"turn": 0, "role": "user", "content": "hello"}) + "\n"
        + json.dumps({"turn": 1, "role": "assistant", "content": "hello!"}) + "\n"
    )
    findings = audit_transcripts(packs, load_transcripts(session))
    changes = ledger.update("agent", "run2", findings_to_stats(packs, findings))
    assert changes["paid"] == 0
    assert ledger.total_debt("agent") == 5


def test_single_capture_never_pays_down_stability_debt(tmp_path: Path):
    """One captured assertion cannot demonstrate stability, mirroring the chat
    rule that one answered variant cannot demonstrate consistency."""
    packs = load_rule_packs(AGENT_RULES)
    session = tmp_path / "nightly.jsonl"
    session.write_text((FIXTURES / "agent_assertion_drift.jsonl").read_text())
    ledger = Ledger()
    findings = audit_transcripts(packs, load_transcripts(session))
    ledger.update("agent", "run1", findings_to_stats(packs, findings))
    assert ledger.total_debt("agent") == 5

    session.write_text(
        json.dumps({"turn": 0, "role": "assistant", "content": "In total, 12 tests passed."}) + "\n"
    )
    findings = audit_transcripts(packs, load_transcripts(session))
    changes = ledger.update("agent", "run2", findings_to_stats(packs, findings))
    assert changes["paid"] == 0
    assert ledger.total_debt("agent") == 5


def test_rule_severity_drives_ledger_weight():
    packs = load_rule_packs(AGENT_RULES)
    low = next(p for p in packs if p.id == "task_integrity")
    medium_rules = [r for r in low.rules if r.severity == "medium"]
    assert medium_rules, "pack should carry mixed severities"
    # ti-006 (medium) drifting must weigh 3, not the fallback.
    t = transcript(
        (0, "assistant", "The target branch is main."),
        (1, "assistant", "The target branch is release/1.2."),
    )
    ti_006 = next(r for r in low.rules if r.id == "ti-006")
    finding = evaluate_rule(ti_006, t, pack_id="task_integrity")
    assert finding.verdict == AgentVerdict.CONTRADICTION.value
    ledger = Ledger()
    ledger.update("agent", "run1", findings_to_stats(packs, [finding]))
    (item,) = ledger.open_items("agent")
    assert item.severity == "medium" and item.weight == 3


# --------------------------------------------------------------------------
# CLI end-to-end
# --------------------------------------------------------------------------

def test_cli_audit_agent_end_to_end(tmp_path: Path, capsys):
    results = tmp_path / "results"
    code = main([
        "audit-agent",
        "--transcripts", str(FIXTURES),
        "--rules", str(AGENT_RULES),
        "--results", str(results),
        "--agent-name", "demo-agent",
    ])
    assert code == 0
    out = capsys.readouterr().out
    assert "1 violations, 1 contradictions" in out

    report = (results / "agent-report.md").read_text()
    assert "ti-001@agent_broken_promise" in report
    assert "ti-004@agent_assertion_drift" in report

    ledger = json.loads((results / "ledger.json").read_text())
    keys = set(ledger["items"])
    assert "demo-agent|task_integrity|ti-001@agent_broken_promise|violation" in keys
    assert "demo-agent|task_integrity|ti-004@agent_assertion_drift|contradiction" in keys

    run_files = list(results.glob("agent-run-*.json"))
    assert len(run_files) == 1
    payload = json.loads(run_files[0].read_text())
    assert payload["agent_name"] == "demo-agent"
    assert payload["transcripts"] == [
        "agent_assertion_drift", "agent_broken_promise", "agent_clean",
    ]
    assert any(f["verdict"] == "violation" for f in payload["findings"])


def test_cli_audit_agent_missing_transcripts_is_friendly_error(tmp_path: Path, capsys):
    code = main([
        "audit-agent",
        "--transcripts", str(tmp_path / "nope"),
        "--rules", str(AGENT_RULES),
        "--results", str(tmp_path / "results"),
    ])
    assert code == 2
    assert "error:" in capsys.readouterr().err
