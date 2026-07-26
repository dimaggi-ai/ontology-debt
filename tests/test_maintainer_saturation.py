"""Saturation: pure arithmetic over runs, with the validity rule preserved.

The false-clean burn regression at this layer: a mostly-errored run has zero
violations by construction and must still never count as a clean model.
"""

from pathlib import Path

from ontodebt.maintainer import saturation
from ontodebt.runner import ProbeResult, RunRecord, save_run
from ontodebt.schema import load_commitments

PACK = """\
id: tiny_pack
title: "Tiny Pack"
statement: "A minimal pack for maintainer tests."
severity: high
scenarios:
  - id: tp-001
    setup: "A jar holds three marbles. Nobody touches it."
    question: "Does the jar still hold three marbles? Answer with exactly one word: Yes or No."
    paraphrases:
      - "Right now, are there still three marbles in the jar? Answer with exactly one word: Yes or No."
    expected:
      type: choice
      values: ["Yes", "No"]
      value: "Yes"
    rationale: "Nothing acted on the jar."
"""


def make_commitments(tmp_path: Path):
    packs = tmp_path / "packs"
    packs.mkdir()
    (packs / "tiny_pack.yaml").write_text(PACK)
    return load_commitments(packs)


def result(variant, verdict, answer, error=""):
    return ProbeResult(
        commitment_id="tiny_pack", scenario_id="tp-001", variant_index=variant,
        prompt="p", response=answer, answer=answer, verdict=verdict,
        severity="high", input_tokens=1, output_tokens=1, latency_s=0.0, error=error,
    )


def record(name, results, started="2026-07-26T00:00:00+00:00"):
    return RunRecord(
        run_id=f"{name}-1", model_name=name, model_id=name, started_at=started, results=results
    )


CLEAN = [result(0, "pass", "yes"), result(1, "pass", "yes")]
DIRTY = [result(0, "violation", "no"), result(1, "pass", "yes")]
ALL_ERRORED = [result(0, "error", "", error="401"), result(1, "error", "", error="401")]


def test_clean_and_dirty_verdicts(tmp_path):
    commitments = make_commitments(tmp_path)
    clean, detail = saturation.model_verdict(record("good", CLEAN), commitments)
    assert clean and detail["violations"] == 0
    dirty, detail = saturation.model_verdict(record("bad", DIRTY), commitments)
    assert not dirty and detail["violations"] == 1 and detail["contradictions"] == 1


def test_all_errored_run_is_never_clean(tmp_path):
    """Burn regression: zero violations via zero answers is not cleanliness."""
    commitments = make_commitments(tmp_path)
    clean, detail = saturation.model_verdict(record("dead-key", ALL_ERRORED), commitments)
    assert not clean
    assert detail.get("invalid") is True
    assert detail["violations"] == 0  # exactly the false-clean shape being refused


def test_partial_run_is_never_clean(tmp_path):
    """A --limit/--only smoke test covering a sliver of the tier must not
    count as 'holds the tier clean'."""
    commitments = make_commitments(tmp_path)
    partial = [result(0, "pass", "yes")]  # 1 of the 2 expected probes
    clean, detail = saturation.model_verdict(record("smoke", partial), commitments)
    assert not clean
    assert detail.get("partial") is True


def test_probe_dodging_is_never_clean(tmp_path):
    """Heavy nonconformance (not errors) has zero violations by construction;
    it still must not read as holding the tier."""
    commitments = make_commitments(tmp_path)
    dodgy = [result(0, "pass", "yes"), result(1, "nonconformant", "")]
    clean, detail = saturation.model_verdict(record("dodger", dodgy), commitments)
    assert not clean
    assert detail.get("low_answer_rate") is True
    assert detail["violations"] == 0


def test_main_fires_only_at_threshold(tmp_path):
    commitments_dir = tmp_path / "packs"
    commitments_dir.mkdir()
    (commitments_dir / "tiny_pack.yaml").write_text(PACK)
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    save_run(record("model-a", CLEAN), results_dir / "run-a.json")
    save_run(record("model-b", DIRTY), results_dir / "run-b.json")
    out = tmp_path / "gh_output"

    args = [
        "--results", str(results_dir), "--commitments", str(commitments_dir),
        "--min-clean", "2", "--state-dir", str(tmp_path / "state"),
        "--github-output", str(out),
    ]
    assert saturation.main(args) == 0
    assert "saturated=false" in out.read_text()

    save_run(record("model-c", CLEAN), results_dir / "run-c.json")
    assert saturation.main(args) == 0
    assert "saturated=true" in out.read_text()
    body = (tmp_path / "state" / "saturation-issue.md").read_text()
    assert "model-a" in body and "model-c" in body
    assert "ontodebt-maintainer:saturation:results" in body  # dedupe marker


def test_latest_run_per_model_wins(tmp_path):
    commitments_dir = tmp_path / "packs"
    commitments_dir.mkdir()
    (commitments_dir / "tiny_pack.yaml").write_text(PACK)
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    save_run(record("m", DIRTY, started="2026-01-01T00:00:00+00:00"), results_dir / "run-old.json")
    save_run(record("m", CLEAN, started="2026-06-01T00:00:00+00:00"), results_dir / "run-new.json")
    runs = saturation.latest_runs(results_dir)
    commitments = load_commitments(commitments_dir)
    clean, _ = saturation.model_verdict(runs["m"], commitments)
    assert clean
