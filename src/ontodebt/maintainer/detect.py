"""L1 trigger: deterministic model-release detector. No LLM anywhere.

Pulls the model-list APIs of each configured provider, diffs the result
against a committed registry (`maintainer/known_models.json`), and reports
three kinds of trigger:

- ``new_model``    an id appears that the registry has never seen
- ``silent_bump``  a known id's metadata hash changed (alias repoints,
                   version field changes) without a new id
- ``deprecation``  a known id disappeared from the provider's list

Fail-closed by construction (this is where the project's "dead API key
produced a false-clean audit" burn is structurally prevented):

- a provider whose key is *present* but whose pull errors (401, network,
  non-JSON) raises ``DetectorError`` and the run goes red - an errored pull
  is never treated as an empty model list;
- a monitored provider returning *zero* models raises too;
- a provider whose key is *absent* is reported loudly as UNMONITORED, and
  its registry section is left untouched.

The first successful pull for a provider establishes a baseline: every id is
recorded, nothing fires. Relevance (which new ids deserve an issue/audit) is
a pure regex gate from committed config - the detector cannot hallucinate a
model because triggers are a set difference over a committed raw payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from ._common import (
    FetchError,
    github_output,
    http_get_json,
    load_json,
    save_json,
    utc_now_iso,
    utc_today,
)

DEFAULT_CONFIG = Path("maintainer/config.json")
DEFAULT_REGISTRY = Path("maintainer/known_models.json")
DEFAULT_PAYLOAD_DIR = Path("maintainer/payloads")
DEFAULT_STATE_DIR = Path("maintainer/state")

AUDITABLE_PROVIDERS = ("anthropic", "openai")  # providers the harness can audit today

# Providers pulled through a sliding window (top-N by recency) rather than a
# complete listing: absence from the window means "aged out", not "gone", so
# deprecation triggers would be false alarms and are suppressed.
WINDOWED_PROVIDERS = ("huggingface",)


class DetectorError(RuntimeError):
    """A monitored provider could not be pulled cleanly. Fail red; never guess."""


# --------------------------------------------------------------------------- fetchers

def fetch_anthropic(api_key: str) -> dict[str, dict]:
    models: dict[str, dict] = {}
    after = ""
    for _ in range(10):  # pagination cap
        url = "https://api.anthropic.com/v1/models?limit=100" + (
            f"&after_id={after}" if after else ""
        )
        data = http_get_json(
            url, headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"}
        )
        for item in data.get("data", []):
            models[str(item["id"])] = {
                "display_name": item.get("display_name", ""),
                "created_at": item.get("created_at", ""),
            }
        if not data.get("has_more"):
            break
        after = str(data.get("last_id", ""))
        if not after:
            break
    return models


def fetch_openai(api_key: str) -> dict[str, dict]:
    data = http_get_json(
        "https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {api_key}"}
    )
    return {
        str(item["id"]): {"created": item.get("created", 0), "owned_by": item.get("owned_by", "")}
        for item in data.get("data", [])
    }


def fetch_gemini(api_key: str) -> dict[str, dict]:
    models: dict[str, dict] = {}
    token = ""
    for _ in range(10):
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000"
            + (f"&pageToken={token}" if token else "")
        )
        data = http_get_json(url, headers={"x-goog-api-key": api_key})
        for item in data.get("models", []):
            model_id = str(item.get("name", "")).removeprefix("models/")
            if model_id:
                models[model_id] = {
                    "display_name": item.get("displayName", ""),
                    "version": item.get("version", ""),
                }
        token = str(data.get("nextPageToken", ""))
        if not token:
            break
    return models


def fetch_huggingface(orgs: list[str]) -> dict[str, dict]:
    """Public endpoint, no key. Metadata is limited to fields that do not
    churn (likes/downloads change hourly and would fire false silent-bumps)."""
    models: dict[str, dict] = {}
    for org in orgs:
        data = http_get_json(
            "https://huggingface.co/api/models?author="
            + org
            + "&sort=createdAt&direction=-1&limit=50"
        )
        for item in data:
            model_id = str(item.get("modelId") or item.get("id") or "")
            if model_id:
                models[model_id] = {"created_at": str(item.get("createdAt", ""))}
    return models


# --------------------------------------------------------------------------- pulling

@dataclass(frozen=True)
class ProviderPull:
    provider: str
    monitored: bool
    models: dict[str, dict] = field(default_factory=dict)
    note: str = ""


def pull_providers(env: dict, config: dict, fetchers: dict | None = None) -> list[ProviderPull]:
    """Pull every provider. Missing key => loudly UNMONITORED. Errored or
    empty pull on a monitored provider => DetectorError (fail-closed)."""
    fetchers = fetchers or {
        "anthropic": lambda: fetch_anthropic(env["ANTHROPIC_API_KEY"]),
        "openai": lambda: fetch_openai(env["OPENAI_API_KEY"]),
        "gemini": lambda: fetch_gemini(env["GEMINI_API_KEY"]),
        "huggingface": lambda: fetch_huggingface(config.get("hf_orgs", [])),
    }
    key_env = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
    pulls: list[ProviderPull] = []
    for provider, fetch in fetchers.items():
        needed = key_env.get(provider)
        if needed and not env.get(needed):
            pulls.append(
                ProviderPull(provider, monitored=False, note=f"{needed} not configured; provider unmonitored")
            )
            continue
        if provider == "huggingface" and not config.get("hf_orgs"):
            pulls.append(ProviderPull(provider, monitored=False, note="no hf_orgs configured"))
            continue
        try:
            models = fetch()
        except FetchError as exc:
            raise DetectorError(
                f"{provider}: pull failed ({exc}). Fail-closed: an errored pull is "
                f"never treated as an empty model list."
            ) from exc
        if not models:
            raise DetectorError(
                f"{provider}: returned zero models. Fail-closed: refusing to record "
                f"an empty list (this is how a dead key would masquerade as clean)."
            )
        pulls.append(ProviderPull(provider, monitored=True, models=models))
    return pulls


# --------------------------------------------------------------------------- diffing

def meta_hash(meta: dict) -> str:
    return hashlib.sha256(json.dumps(meta, sort_keys=True).encode()).hexdigest()[:16]


def is_relevant(provider: str, model_id: str, config: dict) -> bool:
    low = model_id.lower()
    families = config.get("families", [])
    if not any(re.search(f, low) for f in families):
        return False
    ignores = list(config.get("ignore_global", []))
    ignores += config.get("ignore_by_provider", {}).get(provider, [])
    return not any(re.search(p, low) for p in ignores)


@dataclass(frozen=True)
class Trigger:
    kind: str        # new_model | silent_bump | deprecation
    provider: str
    model_id: str
    detail: str = ""


def diff_registry(
    registry: dict, pulls: list[ProviderPull], config: dict
) -> tuple[dict, list[Trigger], list[str], dict[str, int]]:
    """Pure function: (registry, pulls) -> (new_registry, triggers, baselines, ignored_counts).

    Unmonitored providers leave their registry section untouched. Irrelevant
    new ids are still recorded (so they don't re-diff daily) but never fire.
    """
    registry = json.loads(json.dumps(registry))  # deep copy; never mutate input
    providers = registry.setdefault("providers", {})
    triggers: list[Trigger] = []
    baselines: list[str] = []
    ignored_counts: dict[str, int] = {}
    now = utc_now_iso()

    for pull in pulls:
        if not pull.monitored:
            continue
        section = providers.setdefault(pull.provider, {})
        known = section.setdefault("models", {})
        if not known:
            for model_id, meta in sorted(pull.models.items()):
                known[model_id] = {"hash": meta_hash(meta), "meta": meta, "first_seen": now}
            section["baseline_established"] = now
            baselines.append(pull.provider)
            continue

        for model_id, meta in sorted(pull.models.items()):
            new_hash = meta_hash(meta)
            entry = known.get(model_id)
            if entry is None:
                known[model_id] = {"hash": new_hash, "meta": meta, "first_seen": now}
                if is_relevant(pull.provider, model_id, config):
                    triggers.append(Trigger("new_model", pull.provider, model_id))
                else:
                    ignored_counts[pull.provider] = ignored_counts.get(pull.provider, 0) + 1
            else:
                if entry.get("status") == "gone":  # returned after a deprecation; no refire
                    entry.pop("status", None)
                if entry["hash"] != new_hash:
                    detail = f"metadata changed: {entry['meta']} -> {meta}"
                    entry["hash"], entry["meta"], entry["last_changed"] = new_hash, meta, now
                    if is_relevant(pull.provider, model_id, config):
                        triggers.append(Trigger("silent_bump", pull.provider, model_id, detail))

        if pull.provider in WINDOWED_PROVIDERS:
            continue  # aged out of the window != deprecated; never fire or mark
        for model_id, entry in sorted(known.items()):
            if model_id not in pull.models and entry.get("status") != "gone":
                entry["status"] = "gone"
                entry["gone_at"] = now
                if is_relevant(pull.provider, model_id, config):
                    triggers.append(Trigger("deprecation", pull.provider, model_id))

    return registry, triggers, baselines, ignored_counts


def audit_specs(triggers: list[Trigger], config: dict) -> str:
    """New relevant models on providers the harness can audit, capped."""
    specs = [
        f"{t.provider}:{t.model_id}"
        for t in triggers
        if t.kind == "new_model" and t.provider in AUDITABLE_PROVIDERS
    ]
    return ",".join(specs[: int(config.get("max_new_audits", 3))])


# --------------------------------------------------------------------------- rendering

def render_issue(
    triggers: list[Trigger],
    baselines: list[str],
    pulls: list[ProviderPull],
    ignored_counts: dict[str, int],
    specs: str,
    coverage_lost: list[str] | None = None,
) -> tuple[str, str]:
    today = utc_today()
    coverage_lost = coverage_lost or []
    n_new = sum(1 for t in triggers if t.kind == "new_model")
    n_bump = sum(1 for t in triggers if t.kind == "silent_bump")
    n_gone = sum(1 for t in triggers if t.kind == "deprecation")
    title = f"Model watch {today}: {n_new} new, {n_bump} changed, {n_gone} deprecated"
    if not triggers and baselines:
        title = f"Model watch {today}: baseline established ({', '.join(baselines)})"
    if not triggers and not baselines and coverage_lost:
        title = f"Model watch {today}: PROVIDER COVERAGE LOST ({', '.join(coverage_lost)})"

    lines = [
        "<!-- ontodebt-maintainer:detect -->",
        "Deterministic model-registry diff (no LLM involved). Raw payloads and the",
        "registry update are committed alongside this issue; every claim below is a",
        "set operation over those files.",
        "",
    ]
    if triggers:
        lines += ["| Kind | Provider | Model | Detail |", "|---|---|---|---|"]
        lines += [
            f"| {t.kind} | {t.provider} | `{t.model_id}` | {t.detail or ''} |" for t in triggers
        ]
        lines.append("")
    if specs:
        lines += [
            f"**Proposed audits** (capped): `{specs}`",
            "",
            "If the spend-gated audit job was approved, a PR with the run results",
            "follows. If the approval was declined or expired, the registry has",
            "already recorded these models (they will not re-fire), so re-run the",
            "audit manually with:",
            "",
            f"    gh workflow run maintainer-detect.yml -f audit_specs='{specs}'",
            "",
        ]
    if coverage_lost:
        lines += [
            "",
            "## ⚠ PROVIDER COVERAGE LOST",
            "These providers were monitored on a previous run and are now",
            "unmonitored (secret removed or renamed). The loop is blind to them",
            "until the key is restored:",
        ]
        lines += [f"- **{p}**" for p in coverage_lost]
        lines.append("")
    if baselines:
        lines.append(
            f"Baseline established for: {', '.join(baselines)} (all current ids recorded; nothing fired)."
        )
    unmonitored = [p for p in pulls if not p.monitored]
    if unmonitored:
        lines += ["", "**Unmonitored providers** (loud by design):"]
        lines += [f"- {p.provider}: {p.note}" for p in unmonitored]
    if ignored_counts:
        lines.append("")
        lines.append(
            "New-but-irrelevant ids recorded without firing: "
            + ", ".join(f"{k} ({v})" for k, v in sorted(ignored_counts.items()))
        )
    return title, "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- main

def run_detector(
    config_path: Path,
    registry_path: Path,
    payload_dir: Path,
    state_dir: Path,
    env: dict,
    fetchers: dict | None = None,
) -> dict:
    config = load_json(config_path, None)
    if config is None:
        raise DetectorError(f"config not found: {config_path}")
    registry = load_json(registry_path, {"providers": {}})

    pulls = pull_providers(env, config, fetchers)
    new_registry, triggers, baselines, ignored = diff_registry(registry, pulls, config)

    # "Loudly unmonitored" must survive quiet days: persist the monitoring map
    # and alert on any monitored -> unmonitored transition (a deleted secret),
    # not only when some other trigger happens to open an issue.
    prev_monitoring: dict = registry.get("monitoring", {})
    monitoring = {p.provider: ("monitored" if p.monitored else "unmonitored") for p in pulls}
    new_registry["monitoring"] = monitoring
    coverage_lost = sorted(
        provider
        for provider, state in monitoring.items()
        if state == "unmonitored" and prev_monitoring.get(provider) == "monitored"
    )
    for pull in pulls:
        if not pull.monitored:
            print(f"::warning::provider unmonitored: {pull.provider} ({pull.note})")

    registry_changed = new_registry != registry
    if registry_changed:
        save_json(registry_path, new_registry)
        changed_providers = {
            p.provider
            for p in pulls
            if p.monitored
            and registry.get("providers", {}).get(p.provider) != new_registry["providers"].get(p.provider)
        }
        for provider in sorted(changed_providers):
            save_json(
                Path(payload_dir) / f"{utc_today()}-{provider}.json",
                {"pulled_at": utc_now_iso(), "models": pulls_by(pulls, provider).models},
            )

    specs = audit_specs(triggers, config)
    title, body = render_issue(triggers, baselines, pulls, ignored, specs, coverage_lost)
    issue_needed = bool(triggers or baselines or coverage_lost)
    if issue_needed:
        state_dir = Path(state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "detect-issue.md").write_text(body)

    return {
        "triggers": len(triggers),
        "baselines": len(baselines),
        "issue_needed": issue_needed,
        "issue_title": title,
        "audit_specs": specs,
        "registry_changed": registry_changed,
        "unmonitored": [p.provider for p in pulls if not p.monitored],
    }


def pulls_by(pulls: list[ProviderPull], provider: str) -> ProviderPull:
    return next(p for p in pulls if p.provider == provider)


def main(argv: list[str] | None = None, fetchers: dict | None = None, env: dict | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--payload-dir", type=Path, default=DEFAULT_PAYLOAD_DIR)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument("--github-output", default=None)
    args = parser.parse_args(argv)

    import os

    try:
        result = run_detector(
            args.config, args.registry, args.payload_dir, args.state_dir,
            env=dict(os.environ) if env is None else env,
            fetchers=fetchers,
        )
    except DetectorError as exc:
        print(f"DETECTOR FAILED (red by design): {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=1))
    github_output(
        {
            "triggers": result["triggers"],
            "issue_needed": str(result["issue_needed"]).lower(),
            "issue_title": result["issue_title"],
            "audit_specs": result["audit_specs"],
            "registry_changed": str(result["registry_changed"]).lower(),
        },
        args.github_output,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
