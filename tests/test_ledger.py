from ontodebt.analysis import CommitmentStats, ScenarioOutcome
from ontodebt.ledger import Ledger


def stats_with(sid, violated, inconsistent, answered=True, n_answers=2, link_results=None):
    outcome = ScenarioOutcome(scenario_id=sid)
    outcome.answers = ["yes"] * n_answers if answered else []
    if violated:
        outcome.verdicts = ["violation"]
    else:
        outcome.verdicts = ["pass"]
    outcome.inconsistent = inconsistent
    cs = CommitmentStats(commitment_id="demo", title="Demo", severity="high")
    cs.scenario_outcomes = {sid: outcome}
    if link_results:
        cs.link_results = link_results
    return {"demo": cs}


def test_accrue_pay_renew_cycle():
    ledger = Ledger()

    changes = ledger.update("m", "run1", stats_with("s1", violated=True, inconsistent=False))
    assert changes["accrued"] == 1
    assert ledger.total_debt("m") == 5  # high severity weight

    changes = ledger.update("m", "run2", stats_with("s1", violated=False, inconsistent=False))
    assert changes["paid"] == 1
    assert ledger.total_debt("m") == 0

    changes = ledger.update("m", "run3", stats_with("s1", violated=True, inconsistent=False))
    assert changes["renewed"] == 1
    assert ledger.total_debt("m") == 5


def test_no_paydown_without_answers():
    ledger = Ledger()
    ledger.update("m", "run1", stats_with("s1", violated=True, inconsistent=False))
    # Model errored/nonconformant on every variant: debt must stay open.
    ledger.update("m", "run2", stats_with("s1", violated=False, inconsistent=False, answered=False))
    assert ledger.total_debt("m") == 5


def test_contradiction_tracked_separately():
    ledger = Ledger()
    ledger.update("m", "run1", stats_with("s1", violated=True, inconsistent=True))
    kinds = {i.kind for i in ledger.open_items("m")}
    assert kinds == {"violation", "contradiction"}


def test_contradiction_not_paid_on_untestable_cluster():
    """One answered variant can never demonstrate consistency."""
    ledger = Ledger()
    ledger.update("m", "run1", stats_with("s1", violated=False, inconsistent=True))
    assert {i.kind for i in ledger.open_items("m")} == {"contradiction"}
    # Run 2: only one variant answered -> cluster untestable -> no paydown.
    ledger.update("m", "run2", stats_with("s1", violated=False, inconsistent=False, n_answers=1))
    assert {i.kind for i in ledger.open_items("m")} == {"contradiction"}
    # Run 3: fully answered, consistent -> paid.
    ledger.update("m", "run3", stats_with("s1", violated=False, inconsistent=False, n_answers=2))
    assert ledger.open_items("m") == []


def test_link_contradictions_accrue_and_pay():
    ledger = Ledger()
    broken = {("s1", "s2", "same_answer"): True}
    ledger.update("m", "run1", stats_with("s1", violated=False, inconsistent=False, link_results=broken))
    items = ledger.open_items("m")
    assert len(items) == 1 and items[0].kind == "link_contradiction"
    assert items[0].scenario_id == "s1~s2"
    fixed = {("s1", "s2", "same_answer"): False}
    ledger.update("m", "run2", stats_with("s1", violated=False, inconsistent=False, link_results=fixed))
    assert ledger.open_items("m") == []


def test_reopen_preserves_payment_history():
    ledger = Ledger()
    ledger.update("m", "run1", stats_with("s1", violated=True, inconsistent=False))
    ledger.update("m", "run2", stats_with("s1", violated=False, inconsistent=False))
    ledger.update("m", "run3", stats_with("s1", violated=True, inconsistent=False))
    item = ledger.open_items("m")[0]
    assert item.first_seen_run == "run1"
    assert item.last_paid_in_run == "run2"
    assert item.times_reopened == 1
