from ontodebt.analysis import CommitmentStats, ScenarioOutcome
from ontodebt.ledger import Ledger


def stats_with(sid, violated, inconsistent, answered=True):
    outcome = ScenarioOutcome(scenario_id=sid)
    outcome.answers = ["yes"] if answered else []
    if violated:
        outcome.verdicts = ["violation"]
    else:
        outcome.verdicts = ["pass"]
    outcome.inconsistent = inconsistent
    cs = CommitmentStats(commitment_id="demo", title="Demo", severity="high")
    cs.scenario_outcomes = {sid: outcome}
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
