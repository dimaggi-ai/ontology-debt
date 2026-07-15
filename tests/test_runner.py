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


def test_fail_fast_on_all_errors(tmp_path: Path):
    """A bad key/model id must abort the run, never produce a false-clean report."""
    import pytest

    config = ModelConfig(
        name="mock", provider="mock", model_id="mock-v0",
        params={"raise_error": "AuthenticationError: invalid x-api-key"},
    )
    # 3 scenarios x 2 variants x 2 = enough probes to cross the fail-fast threshold
    probes = list(build_probes([make_commitment()])) * 3
    with pytest.raises(RuntimeError, match="all errored"):
        run_probes(probes, config, max_workers=2, progress=False)


def test_report_banner_on_high_error_rate():
    from ontodebt.analysis import analyze
    from ontodebt.report import render_report
    from ontodebt.runner import ProbeResult, RunRecord

    results = [
        ProbeResult("demo", f"s{i}", v, "p", "", "", "error", "medium", 0, 0, 0.0, error="boom")
        for i in range(3) for v in range(2)
    ]
    record = RunRecord("r1", "mock", "mock-v0", "now", results)
    config = ModelConfig(name="mock", provider="mock", model_id="mock-v0")
    report = render_report([(record, config, analyze(record, [make_commitment()]))])
    assert "RUN UNRELIABLE" in report


def test_claude_cli_provider(monkeypatch):
    """The claude -p provider parses the CLI's JSON and surfaces errors."""
    import json as _json
    import shutil
    import subprocess

    from ontodebt.providers import ClaudeCLIProvider

    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/claude")

    def fake_ok(*a, **k):
        return subprocess.CompletedProcess(
            a, 0,
            stdout=_json.dumps({"result": "Yes", "is_error": False,
                                "usage": {"input_tokens": 10, "output_tokens": 2}}),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_ok)
    prov = ClaudeCLIProvider(ModelConfig(name="cli", provider="claude_cli", model_id="x"))
    c = prov.complete("sys", "prompt")
    assert c.text == "Yes" and c.input_tokens == 10 and not c.error

    def fake_blocked(*a, **k):
        return subprocess.CompletedProcess(
            a, 0, stdout=_json.dumps({"result": "blocked", "is_error": True}), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_blocked)
    c2 = prov.complete("sys", "prompt")
    assert c2.error and c2.text == ""


def test_replay_provider(tmp_path: Path):
    """Replay mode returns recorded answers and errors on unrecorded prompts."""
    import json as _json

    from ontodebt.providers import make_provider
    from ontodebt.schema import SYSTEM_PROMPT

    book = tmp_path / "answers.json"
    book.write_text(_json.dumps({"the sky?": "Yes"}))
    cfg = ModelConfig(name="replay", provider="mock", model_id="rec",
                      params={"answer_book_path": str(book)})
    prov = make_provider(cfg)
    hit = prov.complete(SYSTEM_PROMPT, "the sky?")
    assert hit.text == "Yes" and not hit.error
    miss = prov.complete(SYSTEM_PROMPT, "unrecorded")
    assert miss.error and miss.text == ""  # never fabricates an answer


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
