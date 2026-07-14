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
    scenario_id: str          # scenario id, or "a~b" for link items
    kind: str                 # violation | contradiction | link_contradiction
    severity: str
    status: str               # open | paid
    first_seen_run: str
    last_seen_run: str
    paid_in_run: str = ""
    last_paid_in_run: str = ""   # survives re-opening: payment history is kept
    times_reopened: int = 0

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

    def _reconcile(
        self,
        *,
        model_name: str,
        run_id: str,
        cid: str,
        sid: str,
        kind: str,
        severity: str,
        present: bool,
        payable: bool,
        counters: dict[str, int],
    ) -> None:
        """Reconcile one (scenario, kind) finding against the ledger.

        `present` - the failure was observed this run. `payable` - the run
        produced enough evidence to certify absence (a violation needs at
        least one answered variant; a contradiction needs a *checkable*
        cluster - one answered variant can never demonstrate consistency).
        """
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
                    severity=severity,
                    status="open",
                    first_seen_run=run_id,
                    last_seen_run=run_id,
                )
                counters["accrued"] += 1
            else:
                if existing.status == "paid":
                    existing.status = "open"
                    existing.last_paid_in_run = existing.paid_in_run
                    existing.paid_in_run = ""
                    existing.times_reopened += 1
                    counters["renewed"] += 1
                existing.last_seen_run = run_id
        elif existing is not None and existing.status == "open" and payable:
            existing.status = "paid"
            existing.paid_in_run = run_id
            existing.last_paid_in_run = run_id
            counters["paid"] += 1

    def update(self, model_name: str, run_id: str, stats: dict[str, CommitmentStats]) -> dict[str, int]:
        """Reconcile a run against the ledger. Returns counts of changes."""
        counters = {"accrued": 0, "paid": 0, "renewed": 0}
        for cid, cs in stats.items():
            for sid, outcome in cs.scenario_outcomes.items():
                # Chat commitments have one severity per pack; agent rules
                # carry their own, surfaced via scenario_severities.
                severity = cs.scenario_severities.get(sid, cs.severity)
                self._reconcile(
                    model_name=model_name, run_id=run_id, cid=cid, sid=sid,
                    kind="violation", severity=severity,
                    present=outcome.violated, payable=bool(outcome.answers),
                    counters=counters,
                )
                self._reconcile(
                    model_name=model_name, run_id=run_id, cid=cid, sid=sid,
                    kind="contradiction", severity=severity,
                    present=outcome.inconsistent, payable=outcome.checkable,
                    counters=counters,
                )
            # Link-constraint breaks accrue too (a checked link is payable
            # by construction: both clusters were determinate).
            for (a, b, _rel), broken in cs.link_results.items():
                self._reconcile(
                    model_name=model_name, run_id=run_id, cid=cid, sid=f"{a}~{b}",
                    kind="link_contradiction", severity=cs.severity,
                    present=broken, payable=True,
                    counters=counters,
                )
        return counters


def load_ledger(path: Path) -> Ledger:
    if not path.exists():
        return Ledger()
    raw = json.loads(path.read_text())
    return Ledger(items={k: DebtItem(**v) for k, v in raw["items"].items()})


def save_ledger(ledger: Ledger, path: Path) -> None:
    path.write_text(
        json.dumps({"items": {k: asdict(v) for k, v in ledger.items.items()}}, indent=1)
    )
