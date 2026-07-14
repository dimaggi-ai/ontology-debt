from pathlib import Path

import pytest

from ontodebt.schema import (
    Expected,
    Verdict,
    build_probes,
    load_commitment,
    normalize_answer,
)

YAML = """
id: demo
title: "Demo"
statement: Things exist.
severity: high
scenarios:
  - id: d-001
    setup: A ball rolls behind a screen.
    question: "Does the ball still exist? Answer with exactly one word: Yes or No."
    paraphrases:
      - "Is the ball still in existence? Answer with exactly one word: Yes or No."
    expected: { type: choice, values: ["Yes", "No"], value: "Yes" }
    links:
      - { relation: same_answer, target: d-002 }
  - id: d-002
    setup: A ball rolls behind a screen.
    question: "Is there still a ball behind the screen? Answer with exactly one word: Yes or No."
    paraphrases:
      - "Behind the screen, is the ball there? Answer with exactly one word: Yes or No."
    expected: { type: choice, values: ["Yes", "No"], value: "Yes" }
"""


@pytest.fixture()
def commitment(tmp_path: Path):
    path = tmp_path / "demo.yaml"
    path.write_text(YAML)
    return load_commitment(path)


def test_normalize_answer():
    assert normalize_answer("Yes.") == "yes"
    assert normalize_answer("**No**") == "no"
    assert normalize_answer('  "Yes",') == "yes"
    assert normalize_answer("Answer: No") == "no"
    assert normalize_answer("Yes, the ball still exists.") == "yes"
    assert normalize_answer("3") == "3"
    assert normalize_answer("") == ""
    assert normalize_answer("...") == ""


def test_expected_choice():
    exp = Expected(type="choice", values=("Yes", "No"), value="Yes")
    assert exp.check("Yes") is Verdict.PASS
    assert exp.check("no!") is Verdict.VIOLATION
    assert exp.check("maybe") is Verdict.NONCONFORMANT
    assert exp.check("") is Verdict.NONCONFORMANT


def test_expected_choice_rejects_hedges():
    """Mentioning several allowed options is not an answer."""
    exp = Expected(type="choice", values=("Yes", "No"), value="Yes")
    assert exp.check("Yes and no") is Verdict.NONCONFORMANT
    assert exp.check("Yes or No") is Verdict.NONCONFORMANT       # echoing the option list
    assert exp.check("No, wait, yes") is Verdict.NONCONFORMANT
    assert exp.check("Yes, definitely yes") is Verdict.PASS      # repeated same option is fine


def test_expected_exact_number():
    exp = Expected(type="exact", value="3")
    assert exp.check("3") is Verdict.PASS
    assert exp.check("3.") is Verdict.PASS
    assert exp.check("4") is Verdict.VIOLATION
    # Format failures are NOT world-model violations.
    assert exp.check("three") is Verdict.NONCONFORMANT
    assert exp.check("Yes") is Verdict.NONCONFORMANT
    assert exp.check("Sure, I can help") is Verdict.NONCONFORMANT
    assert exp.check("3 or 4") is Verdict.NONCONFORMANT          # hedge across numbers


def test_expected_regex_conformance():
    exp = Expected(type="regex", pattern="3", conformance=r"\d+")
    assert exp.check("3") is Verdict.PASS
    assert exp.check("7") is Verdict.VIOLATION       # answer-shaped, wrong value
    assert exp.check("banana") is Verdict.NONCONFORMANT


def test_load_and_probes(commitment):
    assert commitment.id == "demo"
    assert commitment.probe_count() == 4
    probes = list(build_probes([commitment]))
    assert len(probes) == 4
    assert probes[0].variant_index == 0
    assert "ball rolls behind" in probes[0].prompt


def test_redos_pattern_rejected(tmp_path: Path):
    bad = YAML.replace(
        'expected: { type: choice, values: ["Yes", "No"], value: "Yes" }\n    links',
        'expected: { type: regex, pattern: "(a+)+" }\n    links',
    )
    path = tmp_path / "redos.yaml"
    path.write_text(bad)
    with pytest.raises(ValueError, match="catastrophic backtracking"):
        load_commitment(path)


def test_safe_regex_accepted(tmp_path: Path):
    ok = YAML.replace(
        'expected: { type: choice, values: ["Yes", "No"], value: "Yes" }\n    links',
        'expected: { type: regex, pattern: "[0-9]+" }\n    links',
    )
    path = tmp_path / "okre.yaml"
    path.write_text(ok)
    load_commitment(path)  # must not raise


def test_bad_link_target(tmp_path: Path):
    bad = YAML.replace("target: d-002", "target: d-999")
    path = tmp_path / "bad.yaml"
    path.write_text(bad)
    with pytest.raises(ValueError, match="link target"):
        load_commitment(path)


def test_value_must_be_in_values(tmp_path: Path):
    bad = YAML.replace('value: "Yes" }\n    links', 'value: "Maybe" }\n    links')
    path = tmp_path / "bad2.yaml"
    path.write_text(bad)
    with pytest.raises(ValueError, match="must be one of"):
        load_commitment(path)
