import json
from pathlib import Path

from ontodebt.providers import ModelConfig
from ontodebt.runner import load_run, run_probes, save_run
from ontodebt.schema import Commitment, Expected, Scenario, build_probes


def make_commitment():
    exp = Expected(type="choice", values=("Yes", "No"), value="Yes")
    scenarios = tuple(
        Scenario(
            id=f"s{i}",
            setup="A ball rolls behind a screen.",
            question="Does the ball exist? Answer with exactly one word: Yes or No.",
            paraphrases=("Is the ball there? Answer with exactly one word: Yes or No.",),
            expected=exp,
        )
        for i in range(3)
    )
    return Commitment(id="demo", title="Demo", statement="", severity="medium", scenarios=scenarios)


def test_mock_run_end_to_end(tmp_path: Path):
    config = ModelConfig(name="mock", provider="mock", model_id="mock-v0", params={"failure_rate": 0.0})
    probes = list(build_probes([make_commitment()]))
    transcript = tmp_path / "t.jsonl"
    record = run_probes(probes, config, max_workers=2, transcript_path=transcript, progress=False)

    assert len(record.results) == 6
    assert all(r.verdict == "pass" for r in record.results)
    # Stable ordering regardless of thread completion order.
    assert [r.variant_index for r in record.results] == [0, 1, 0, 1, 0, 1]

    lines = transcript.read_text().strip().splitlines()
    assert len(lines) == 6
    assert json.loads(lines[0])["model"] == "mock-v0"

    path = tmp_path / "run.json"
    save_run(record, path)
    loaded = load_run(path)
    assert loaded.run_id == record.run_id
    assert loaded.results == record.results
