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


def test_expected_exact_number():
    exp = Expected(type="exact", value="3")
    assert exp.check("3") is Verdict.PASS
    assert exp.check("three") is Verdict.VIOLATION


def test_load_and_probes(commitment):
    assert commitment.id == "demo"
    assert commitment.probe_count() == 4
    probes = list(build_probes([commitment]))
    assert len(probes) == 4
    assert probes[0].variant_index == 0
    assert "ball rolls behind" in probes[0].prompt


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
