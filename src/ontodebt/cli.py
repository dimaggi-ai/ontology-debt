"""ontodebt command-line interface.

    ontodebt validate                     # lint all commitment packs
    ontodebt estimate --models m1,m2      # probe counts + cost projection
    ontodebt run --models m1,m2           # execute the audit
    ontodebt report                       # render markdown from saved runs
    ontodebt ledger                       # show open debt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .analysis import analyze
from .ledger import load_ledger, save_ledger
from .providers import load_model_configs, preflight
from .report import estimate_cost, render_report
from .runner import load_run, run_probes, save_run
from .schema import build_probes, load_commitments

DEFAULT_COMMITMENTS = Path("commitments")
DEFAULT_MODELS = Path("models.yaml")
DEFAULT_RESULTS = Path("results")


def _load_env_file(path: Path = Path(".env")) -> None:
    """Minimal .env loader (KEY=value lines) so keys never live in shell history."""
    import os

    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def cmd_validate(args: argparse.Namespace) -> int:
    commitments = load_commitments(args.commitments)
    total_scenarios = sum(len(c.scenarios) for c in commitments)
    total_probes = sum(c.probe_count() for c in commitments)
    for c in commitments:
        adversarial = sum(1 for s in c.scenarios if s.difficulty == "adversarial")
        links = sum(len(s.links) for s in c.scenarios)
        print(
            f"  {c.id:24s} {len(c.scenarios):3d} scenarios "
            f"({adversarial} adversarial, {links} links) -> {c.probe_count():4d} probes [{c.severity}]"
        )
    print(f"\nOK: {len(commitments)} commitments, {total_scenarios} scenarios, {total_probes} probes.")
    return 0


def cmd_estimate(args: argparse.Namespace) -> int:
    commitments = load_commitments(args.commitments)
    configs = load_model_configs(args.models_file)
    names = args.models.split(",") if args.models else list(configs)
    probes = list(build_probes(commitments, limit_scenarios=args.limit))
    # Rough token estimate: chars/3.5 for input. Output defaults to ~6 tokens
    # per probe, but reasoning models bill hidden thinking tokens as output -
    # models.yaml can override with est_output_tokens_per_probe.
    est_in = sum(len(p.prompt) + 220 for p in probes) / 3.5
    print(f"{len(probes)} probes per model\n")
    total = 0.0
    for name in names:
        cfg = configs[name]
        est_out = len(probes) * cfg.est_output_tokens_per_probe
        cost = est_in / 1e6 * cfg.input_price_per_mtok + est_out / 1e6 * cfg.output_price_per_mtok
        total += cost
        print(f"  {name:24s} ~{est_in:,.0f} in / ~{est_out:,.0f} out tokens -> ~${cost:.2f}")
    print(f"\nEstimated total: ~${total:.2f} (rough; pricing from models.yaml; "
          f"reasoning-model output includes hidden thinking tokens)")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    _load_env_file()
    commitments = load_commitments(args.commitments, only=args.only.split(",") if args.only else None)
    configs = load_model_configs(args.models_file)
    names = args.models.split(",") if args.models else list(configs)
    # Validate every requested model up front - a typo must fail before any
    # API spend, not after the first model has already run.
    unknown = [n for n in names if n not in configs]
    if unknown:
        print(
            f"Unknown model(s): {', '.join(unknown)}. "
            f"Available: {', '.join(configs)}",
            file=sys.stderr,
        )
        return 2
    missing = preflight([configs[n] for n in names])
    if missing:
        print(
            f"Missing credentials for the requested models: {', '.join(missing)}. "
            f"Put them in your environment or a local .env file (see README: Quickstart).",
            file=sys.stderr,
        )
        return 2
    probes = list(build_probes(commitments, limit_scenarios=args.limit))
    args.results.mkdir(parents=True, exist_ok=True)

    ledger_path = args.results / "ledger.json"
    ledger = load_ledger(ledger_path)
    runs = []
    for name in names:
        cfg = configs[name]
        print(f"Running {len(probes)} probes against {name} ({cfg.model_id}) ...")
        record = run_probes(
            probes,
            cfg,
            max_workers=args.workers,
            transcript_path=args.results / f"transcript-{name}.jsonl",
        )
        save_run(record, args.results / f"run-{record.run_id}.json")
        stats = analyze(record, commitments)
        error_rate = (
            sum(1 for r in record.results if r.error) / len(record.results)
            if record.results
            else 0.0
        )
        if error_rate > 0.5:
            # A mostly-errored run proves nothing; reconciling it against the
            # ledger would fabricate a clean (or dirty) bill of health.
            print(
                f"  WARNING: {error_rate:.0%} of probes errored - run treated as "
                f"INVALID; ledger not updated for {name}.",
                file=sys.stderr,
            )
        else:
            changes = ledger.update(name, record.run_id, stats)
            # Persist reconciliation immediately so a failure on a later model
            # never loses a completed model's ledger state.
            save_ledger(ledger, ledger_path)
            print(
                f"  done. cost ~${estimate_cost(record, cfg):.2f} | "
                f"debt accrued {changes['accrued']}, paid {changes['paid']}, renewed {changes['renewed']}"
            )
        runs.append((record, cfg, stats))

    report = render_report(runs, ledger)
    report_path = args.results / "report.md"
    report_path.write_text(report)
    print(f"\nReport written to {report_path}")
    print(f"Ledger written to {ledger_path}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    commitments = load_commitments(args.commitments)
    configs = load_model_configs(args.models_file)
    ledger = load_ledger(args.results / "ledger.json")
    latest: dict[str, object] = {}
    for path in sorted(args.results.glob("run-*.json")):
        record = load_run(path)
        if record.model_name not in configs:
            print(
                f"warning: skipping {path.name} - model '{record.model_name}' "
                f"not in {args.models_file}",
                file=sys.stderr,
            )
            continue
        prior = latest.get(record.model_name)
        if prior is None or record.started_at > prior.started_at:  # type: ignore[union-attr]
            latest[record.model_name] = record
    runs = [
        (record, configs[name], analyze(record, commitments))
        for name, record in sorted(latest.items())
    ]
    if not runs:
        print("No saved runs found. Run `ontodebt run` first.", file=sys.stderr)
        return 1
    print(render_report(runs, ledger))
    return 0


def cmd_ledger(args: argparse.Namespace) -> int:
    ledger = load_ledger(args.results / "ledger.json")
    items = ledger.open_items(args.model)
    if not items:
        print("No open debt.")
        return 0
    print(json.dumps([vars(i) for i in items], indent=1))
    print(f"\nTotal weighted debt: {ledger.total_debt(args.model)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ontodebt", description=__doc__)
    parser.add_argument("--version", action="version", version=f"ontodebt {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--commitments", type=Path, default=DEFAULT_COMMITMENTS)
        p.add_argument("--models-file", type=Path, default=DEFAULT_MODELS)
        p.add_argument("--results", type=Path, default=DEFAULT_RESULTS)

    p = sub.add_parser("validate", help="lint commitment packs")
    common(p)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("estimate", help="probe counts and cost projection")
    common(p)
    p.add_argument("--models", default="")
    p.add_argument("--limit", type=int, default=None, help="limit scenarios per commitment")
    p.set_defaults(func=cmd_estimate)

    p = sub.add_parser("run", help="execute the audit")
    common(p)
    p.add_argument("--models", default="", help="comma-separated model names from models.yaml")
    p.add_argument("--only", default="", help="comma-separated commitment ids")
    p.add_argument("--limit", type=int, default=None, help="limit scenarios per commitment (smoke test)")
    p.add_argument("--workers", type=int, default=8)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("report", help="render markdown report from saved runs")
    common(p)
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("ledger", help="show open debt items")
    common(p)
    p.add_argument("--model", default=None)
    p.set_defaults(func=cmd_ledger)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:  # friendly config errors (e.g. missing API key)
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
