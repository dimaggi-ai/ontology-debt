"""The debt ledger: violations and contradictions accrue as open debt items,
persist across runs, and are paid down when a later run passes.

This is the piece missing from one-shot eval harnesses: a failure is not a
number in a report, it is an account that stays open until the model (or the
commitment) changes. Severity comes from the commitment declaration.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .analysis import CommitmentStats

SEVERITY_WEIGHT = {"low": 1, "medium": 3, "high": 5}


@dataclass
class DebtItem:
    key: str                  # model|commitment|scenario|kind
    model_name: str
    commitment_id: str
    scenario_id: str
    kind: str                 # violation | contradiction
    severity: str
    status: str               # open | paid
    first_seen_run: str
    last_seen_run: str
    paid_in_run: str = ""

    @property
    def weight(self) -> int:
        return SEVERITY_WEIGHT.get(self.severity, 3)


@dataclass
class Ledger:
    items: dict[str, DebtItem] = field(default_factory=dict)

    def open_items(self, model_name: str | None = None) -> list[DebtItem]:
        items = [i for i in self.items.values() if i.status == "open"]
        if model_name:
            items = [i for i in items if i.model_name == model_name]
        return sorted(items, key=lambda i: (-i.weight, i.commitment_id, i.scenario_id, i.kind))

    def total_debt(self, model_name: str | None = None) -> int:
        return sum(i.weight for i in self.open_items(model_name))

    def update(self, model_name: str, run_id: str, stats: dict[str, CommitmentStats]) -> dict[str, int]:
        """Reconcile a run against the ledger. Returns counts of changes."""
        accrued = paid = renewed = 0
        for cid, cs in stats.items():
            for sid, outcome in cs.scenario_outcomes.items():
                findings = {
                    "violation": outcome.violated,
                    "contradiction": outcome.inconsistent,
                }
                for kind, present in findings.items():
                    key = f"{model_name}|{cid}|{sid}|{kind}"
                    existing = self.items.get(key)
                    if present:
                        if existing is None:
                            self.items[key] = DebtItem(
                                key=key,
                                model_name=model_name,
                                commitment_id=cid,
                                scenario_id=sid,
                                kind=kind,
                                severity=cs.severity,
                                status="open",
                                first_seen_run=run_id,
                                last_seen_run=run_id,
                            )
                            accrued += 1
                        else:
                            if existing.status == "paid":
                                existing.status = "open"
                                existing.paid_in_run = ""
                                renewed += 1
                            existing.last_seen_run = run_id
                    else:
                        # Only pay down if the scenario actually produced answers.
                        if existing is not None and existing.status == "open" and outcome.answers:
                            existing.status = "paid"
                            existing.paid_in_run = run_id
                            paid += 1
        return {"accrued": accrued, "paid": paid, "renewed": renewed}


def load_ledger(path: Path) -> Ledger:
    if not path.exists():
        return Ledger()
    raw = json.loads(path.read_text())
    return Ledger(items={k: DebtItem(**v) for k, v in raw["items"].items()})


def save_ledger(ledger: Ledger, path: Path) -> None:
    path.write_text(
        json.dumps({"items": {k: asdict(v) for k, v in ledger.items.items()}}, indent=1)
    )
