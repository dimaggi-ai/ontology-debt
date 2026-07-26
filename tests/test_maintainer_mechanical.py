"""Phase-4 guard: only known report regenerations ever count as mechanical."""

from ontodebt.maintainer import mechanical

REPORT_DIRS = {
    "examples/gradient": "commitments",
    "examples/gradient-frontier": "commitments-frontier",
}


def test_pure_report_regeneration_is_mechanical():
    ok, reason = mechanical.is_mechanical(["examples/gradient/report.md"], REPORT_DIRS)
    assert ok, reason
    ok, _ = mechanical.is_mechanical(
        ["examples/gradient/report.md", "examples/gradient-frontier/report.md"], REPORT_DIRS
    )
    assert ok


def test_anything_else_is_not_mechanical():
    for offending in [
        "examples/gradient/ledger.json",           # ledger: never
        "examples/gradient/transcript-x.jsonl",    # transcripts: never
        "src/ontodebt/analysis.py",                # code: never
        "commitments/object_permanence.yaml",      # packs: never
        "README.md",                               # prose: never
        "examples/unknown-dir/report.md",          # unknown results dir
    ]:
        ok, reason = mechanical.is_mechanical(
            ["examples/gradient/report.md", offending], REPORT_DIRS
        )
        assert not ok and offending in reason


def test_empty_diff_is_not_mechanical():
    ok, reason = mechanical.is_mechanical([], REPORT_DIRS)
    assert not ok and "empty" in reason


def test_recompute_plan_maps_results_to_commitments():
    plan = mechanical.recompute_plan(
        ["examples/gradient-frontier/report.md"], REPORT_DIRS
    )
    assert plan == [("examples/gradient-frontier", "commitments-frontier")]


REPORT_A = "# report\n\nGenerated: 2026-07-15 03:04 UTC\n\n## model\n\n- rate: 0.0%\n"


def test_reports_equivalent_ignores_timestamp_and_trailing_newlines(tmp_path):
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text(REPORT_A)
    # different Generated minute + extra trailing newline (the `> file` path)
    b.write_text(REPORT_A.replace("2026-07-15 03:04", "2026-07-26 19:16") + "\n")
    assert mechanical.reports_equivalent(a, b)


def test_reports_equivalent_rejects_content_changes(tmp_path):
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text(REPORT_A)
    b.write_text(REPORT_A.replace("0.0%", "3.6%"))
    assert not mechanical.reports_equivalent(a, b)
