"""Pack proposer: the LLM is a candidate generator; everything that decides
is deterministic. Schema-invalid scenarios drop, adversary-disputed scenarios
drop (fail-closed on anything but an explicit UNDISPUTED), thin packs refuse
to emit, and the final draft must pass the repo's own pack loader."""

import pytest
import yaml

from ontodebt.maintainer import propose
from ontodebt.schema import load_commitment

PACK_YAML = """\
id: test_pack
title: "Test Pack"
statement: "A drafted invariant pack used only in tests."
severity: high
scenarios:
  - id: tp-001
    setup: "A box holds 4 coins. Two are removed, then the remainder doubled."
    question: "How many coins are in the box? Answer with a single number and nothing else."
    paraphrases:
      - "What is the final coin count in the box? Answer with a single number and nothing else."
      - "After all steps, how many coins does the box hold? Answer with a single number and nothing else."
      - "State the number of coins now in the box. Answer with a single number and nothing else."
      - "Give the box's coin total. Answer with a single number and nothing else."
    expected:
      type: exact
      value: "4"
    rationale: "1. Start 4. 2. Remove 2 -> 2. 3. Double -> 4."
    difficulty: adversarial
  - id: tp-002
    setup: "Broken scenario."
    question: "Is it broken? Answer with exactly one word: Yes or No."
    paraphrases:
      - "Broken? Answer with exactly one word: Yes or No."
    expected:
      type: choice
      values: ["Yes", "No"]
      value: "Maybe"
    rationale: "Invalid: gold not among values."
    difficulty: adversarial
  - id: tp-003
    setup: "A shelf holds 3 marbles; each is swapped for two pebbles."
    question: "How many pebbles are on the shelf? Answer with a single number and nothing else."
    paraphrases:
      - "What is the pebble count on the shelf? Answer with a single number and nothing else."
      - "After the swaps, how many pebbles sit on the shelf? Answer with a single number and nothing else."
      - "State the shelf's pebble total. Answer with a single number and nothing else."
      - "Give the number of pebbles now on the shelf. Answer with a single number and nothing else."
    expected:
      type: exact
      value: "6"
    rationale: "1. 3 marbles. 2. Each -> 2 pebbles. 3. 3*2=6."
    difficulty: adversarial
"""


def fake_complete(system, prompt, max_tokens):
    if system == propose.PROPOSER_SYSTEM:
        return "```yaml\n" + PACK_YAML + "\n```"  # fences must be stripped
    # adversary: dispute the pebble scenario, clear the coin scenario
    if "pebbles" in prompt:
        return "DISPUTED: 'swapped for' could mean replaced by one pair total.\nReasoning..."
    return "UNDISPUTED\nThe derivation is airtight."


def test_pipeline_drops_invalid_and_disputed_keeps_valid(tmp_path):
    final, dispositions = propose.generate_pack(
        "conservation under substitution", "test_pack", "style", fake_complete,
        n_scenarios=3, min_keep=1,
    )
    by_id = {d.scenario_id: d for d in dispositions}
    assert by_id["tp-001"].kept
    assert not by_id["tp-002"].kept and by_id["tp-002"].reason.startswith("schema:")
    assert not by_id["tp-003"].kept and by_id["tp-003"].reason.startswith("adversary:")
    assert [s["id"] for s in final["scenarios"]] == ["tp-001"]

    path = propose.write_pack(final, tmp_path / "draft")
    commitment = load_commitment(path)  # the repo's own gate accepts the draft
    assert commitment.id == "test_pack"
    assert "human review required" in yaml.safe_load(path.read_text())["lineage"][0]


def test_thin_pack_refuses_to_emit():
    def all_disputed(system, prompt, max_tokens):
        if system == propose.PROPOSER_SYSTEM:
            return PACK_YAML
        return "DISPUTED: everything is ambiguous."

    with pytest.raises(propose.ProposeError, match="min_keep"):
        propose.generate_pack("t", "test_pack", "s", all_disputed, 3, min_keep=1)


def test_empty_adversary_reply_is_fail_closed():
    def empty_adv(system, prompt, max_tokens):
        if system == propose.PROPOSER_SYSTEM:
            return PACK_YAML
        return ""

    with pytest.raises(propose.ProposeError):
        propose.generate_pack("t", "test_pack", "s", empty_adv, 3, min_keep=1)


def test_non_yaml_proposer_output_fails_closed():
    def garbage(system, prompt, max_tokens):
        return "Sure! Here are some scenarios: [unclosed"

    with pytest.raises(propose.ProposeError, match="YAML|scenarios"):
        propose.generate_pack("t", "test_pack", "s", garbage, 3, min_keep=1)


def test_llm_supplied_id_cannot_steer_the_write_path(tmp_path):
    """The pack id (and so the filename) is always the CLI-validated one;
    a deviating proposer response must not control a filesystem path."""
    evil_yaml = PACK_YAML.replace("id: test_pack", "id: ../../evil")

    def evil_complete(system, prompt, max_tokens):
        if system == propose.PROPOSER_SYSTEM:
            return evil_yaml
        return "UNDISPUTED"

    final, _ = propose.generate_pack("t", "test_pack", "s", evil_complete, 3, min_keep=1)
    assert final["id"] == "test_pack"
    path = propose.write_pack(final, tmp_path / "draft")
    assert path.parent == (tmp_path / "draft")
    assert path.name == "test_pack.yaml"


def test_write_pack_rejects_unsafe_id(tmp_path):
    with pytest.raises(propose.ProposeError, match="charset"):
        propose.write_pack({"id": "../../evil", "scenarios": []}, tmp_path / "draft")


def test_strip_fences():
    assert propose.strip_fences("```yaml\nid: x\n```") == "id: x"
    assert propose.strip_fences("id: x") == "id: x"


def test_pr_body_lists_every_disposition():
    dispositions = [
        propose.Disposition("tp-001", True, "kept"),
        propose.Disposition("tp-002", False, "schema: bad gold"),
    ]
    body = propose.render_pr_body("theme", "claude-opus-4-8", "draft/x.yaml", dispositions)
    assert "never auto-merge" in body.lower()
    assert "tp-001" in body and "tp-002" in body
