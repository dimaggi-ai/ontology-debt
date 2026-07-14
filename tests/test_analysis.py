import pytest

from ontodebt.analysis import analyze, wilson_interval
from ontodebt.runner import ProbeResult, RunRecord
from ontodebt.schema import Commitment, Expected, Link, LinkRelation, Scenario


def make_result(sid, variant, verdict, answer, cid="demo"):
    return ProbeResult(
        commitment_id=cid,
        scenario_id=sid,
        variant_index=variant,
        prompt="p",
        response=answer,
        answer=answer,
        verdict=verdict,
        severity="high",
        input_tokens=10,
        output_tokens=2,
        latency_s=0.1,
    )


def make_commitment(links=()):
    exp = Expected(type="choice", values=("yes", "no"), value="yes")
    scenarios = (
        Scenario(id="s1", setup="x", question="q", paraphrases=("q2",), expected=exp, links=tuple(links)),
        Scenario(id="s2", setup="x", question="q", paraphrases=("q2",), expected=exp),
    )
    return Commitment(id="demo", title="Demo", statement="", severity="high", scenarios=scenarios)


def test_wilson_interval_known():
    lo, hi = wilson_interval(0, 0)
    assert (lo, hi) == (0.0, 0.0)
    # Pinned literature values (z=1.96), 4 decimal places.
    assert wilson_interval(5, 10) == (pytest.approx(0.2366, abs=1e-4), pytest.approx(0.7634, abs=1e-4))
    assert wilson_interval(0, 20) == (pytest.approx(0.0, abs=1e-4), pytest.approx(0.1611, abs=1e-4))
    assert wilson_interval(8, 10) == (pytest.approx(0.4902, abs=1e-4), pytest.approx(0.9433, abs=1e-4))


def test_violation_and_consistency_separated():
    # s1: both variants answer "no" -> 2 violations, but self-consistent.
    # s2: variants disagree ("yes"/"no") -> 1 violation, inconsistent cluster.
    results = [
        make_result("s1", 0, "violation", "no"),
        make_result("s1", 1, "violation", "no"),
        make_result("s2", 0, "pass", "yes"),
        make_result("s2", 1, "violation", "no"),
    ]
    record = RunRecord("r1", "mock", "mock-v0", "now", results)
    stats = analyze(record, [make_commitment()])["demo"]
    assert stats.n_violations == 3
    assert stats.n_inconsistent_scenarios == 1  # only s2
    assert stats.scenario_outcomes["s1"].inconsistent is False
    assert stats.scenario_outcomes["s2"].inconsistent is True


def test_link_contradiction():
    commitment = make_commitment(links=[Link(LinkRelation.SAME_ANSWER, "s2")])
    results = [
        make_result("s1", 0, "pass", "yes"),
        make_result("s1", 1, "pass", "yes"),
        make_result("s2", 0, "violation", "no"),
        make_result("s2", 1, "violation", "no"),
    ]
    record = RunRecord("r1", "mock", "mock-v0", "now", results)
    stats = analyze(record, [commitment])["demo"]
    assert stats.n_links_checked == 1
    assert stats.n_link_contradictions == 1


def test_nonconformant_not_counted_as_violation():
    results = [
        make_result("s1", 0, "nonconformant", ""),
        make_result("s1", 1, "pass", "yes"),
    ]
    record = RunRecord("r1", "mock", "mock-v0", "now", results)
    stats = analyze(record, [make_commitment()])["demo"]
    assert stats.n_violations == 0
    assert stats.n_nonconformant == 1
    assert stats.n_answered == 1
    assert stats.scenario_outcomes["s1"].inconsistent is False


def test_contradiction_denominator_excludes_untestable_clusters():
    # s1: one answered variant -> untestable, must not deflate the rate.
    # s2: two answered variants that disagree -> inconsistent.
    results = [
        make_result("s1", 0, "pass", "yes"),
        make_result("s1", 1, "nonconformant", ""),
        make_result("s2", 0, "pass", "yes"),
        make_result("s2", 1, "violation", "no"),
    ]
    record = RunRecord("r1", "mock", "mock-v0", "now", results)
    stats = analyze(record, [make_commitment()])["demo"]
    assert stats.n_scenarios == 2
    assert stats.n_checkable_scenarios == 1
    assert stats.n_inconsistent_scenarios == 1
    assert stats.contradiction_rate == 1.0  # of checkable clusters, not 0.5 of all


def test_cluster_answer_requires_strict_majority():
    from ontodebt.analysis import ScenarioOutcome

    tied = ScenarioOutcome(scenario_id="s", answers=["yes", "no"])
    assert tied.cluster_answer == ""            # tie -> indeterminate, never guessed
    single = ScenarioOutcome(scenario_id="s", answers=["yes"])
    assert single.cluster_answer == ""          # one answer can't be a majority signal
    majority = ScenarioOutcome(scenario_id="s", answers=["yes", "yes", "no"])
    assert majority.cluster_answer == "yes"


def test_symmetric_links_deduplicated():
    # Both directions declared -> must count as ONE checked constraint.
    c1 = make_commitment(links=[Link(LinkRelation.SAME_ANSWER, "s2")])
    scenarios = list(c1.scenarios)
    scenarios[1] = Scenario(
        id="s2", setup="x", question="q", paraphrases=("q2",),
        expected=scenarios[1].expected,
        links=(Link(LinkRelation.SAME_ANSWER, "s1"),),
    )
    commitment = Commitment(id="demo", title="Demo", statement="", severity="high", scenarios=tuple(scenarios))
    results = [
        make_result("s1", 0, "pass", "yes"),
        make_result("s1", 1, "pass", "yes"),
        make_result("s2", 0, "violation", "no"),
        make_result("s2", 1, "violation", "no"),
    ]
    record = RunRecord("r1", "mock", "mock-v0", "now", results)
    stats = analyze(record, [commitment])["demo"]
    assert stats.n_links_checked == 1
    assert stats.n_link_contradictions == 1
