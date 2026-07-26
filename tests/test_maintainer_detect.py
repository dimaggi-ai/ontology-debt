"""Detector: diff logic, baseline semantics, and the fail-closed rules.

The dead-key regression lives here: an errored or empty pull must raise -
it can never be recorded as "no models", which is how a revoked key once
produced a false-clean state elsewhere in this project's history.
"""

import json

import pytest

from ontodebt.maintainer import detect
from ontodebt.maintainer._common import FetchError

CONFIG = {
    "families": ["gpt-", "claude", "qwen"],
    "ignore_global": ["preview", "-latest$"],
    "ignore_by_provider": {"openai": ["embedding", "whisper"], "huggingface": ["gguf"]},
    "hf_orgs": ["Qwen"],
    "max_new_audits": 2,
}


def pulls_for(models_by_provider):
    return [
        detect.ProviderPull(provider, monitored=True, models=models)
        for provider, models in models_by_provider.items()
    ]


def test_baseline_records_everything_and_fires_nothing():
    pulls = pulls_for({"openai": {"gpt-9": {"created": 1}, "whisper-3": {"created": 2}}})
    registry, triggers, baselines, ignored = detect.diff_registry({}, pulls, CONFIG)
    assert baselines == ["openai"]
    assert triggers == []
    assert set(registry["providers"]["openai"]["models"]) == {"gpt-9", "whisper-3"}


def test_new_relevant_model_fires_and_irrelevant_is_recorded_silently():
    registry, _, _, _ = detect.diff_registry(
        {}, pulls_for({"openai": {"gpt-9": {"created": 1}}}), CONFIG
    )
    pulls = pulls_for(
        {"openai": {"gpt-9": {"created": 1}, "gpt-10": {"created": 3}, "text-embedding-9": {"created": 4}}}
    )
    registry2, triggers, baselines, ignored = detect.diff_registry(registry, pulls, CONFIG)
    assert baselines == []
    assert [(t.kind, t.model_id) for t in triggers] == [("new_model", "gpt-10")]
    assert ignored == {"openai": 1}
    # both are recorded so neither re-fires tomorrow
    assert "text-embedding-9" in registry2["providers"]["openai"]["models"]
    _, triggers3, _, ignored3 = detect.diff_registry(registry2, pulls, CONFIG)
    assert triggers3 == [] and ignored3 == {}


def test_ignore_patterns_suppress_alias_churn():
    registry, _, _, _ = detect.diff_registry(
        {}, pulls_for({"openai": {"gpt-9": {"created": 1}}}), CONFIG
    )
    pulls = pulls_for(
        {"openai": {"gpt-9": {"created": 1}, "gpt-10-preview": {"created": 2}, "gpt-10-latest": {"created": 3}}}
    )
    _, triggers, _, ignored = detect.diff_registry(registry, pulls, CONFIG)
    assert triggers == []
    assert ignored == {"openai": 2}


def test_silent_bump_fires_on_metadata_change():
    registry, _, _, _ = detect.diff_registry(
        {}, pulls_for({"openai": {"gpt-9": {"created": 1, "owned_by": "a"}}}), CONFIG
    )
    pulls = pulls_for({"openai": {"gpt-9": {"created": 1, "owned_by": "b"}}})
    _, triggers, _, _ = detect.diff_registry(registry, pulls, CONFIG)
    assert [(t.kind, t.model_id) for t in triggers] == [("silent_bump", "gpt-9")]


def test_deprecation_fires_once_and_return_does_not_refire():
    registry, _, _, _ = detect.diff_registry(
        {}, pulls_for({"openai": {"gpt-9": {"created": 1}, "gpt-8": {"created": 0}}}), CONFIG
    )
    gone = pulls_for({"openai": {"gpt-9": {"created": 1}}})
    registry2, triggers, _, _ = detect.diff_registry(registry, gone, CONFIG)
    assert [(t.kind, t.model_id) for t in triggers] == [("deprecation", "gpt-8")]
    # still gone tomorrow: no refire
    _, triggers2, _, _ = detect.diff_registry(registry2, gone, CONFIG)
    assert triggers2 == []
    # comes back: status cleared silently, no trigger storm
    back = pulls_for({"openai": {"gpt-9": {"created": 1}, "gpt-8": {"created": 0}}})
    registry3, triggers3, _, _ = detect.diff_registry(registry2, back, CONFIG)
    assert triggers3 == []
    assert "status" not in registry3["providers"]["openai"]["models"]["gpt-8"]


def test_unmonitored_provider_leaves_registry_untouched():
    registry, _, _, _ = detect.diff_registry(
        {}, pulls_for({"openai": {"gpt-9": {"created": 1}}}), CONFIG
    )
    pulls = [detect.ProviderPull("openai", monitored=False, note="no key")]
    registry2, triggers, baselines, _ = detect.diff_registry(registry, pulls, CONFIG)
    assert registry2 == registry and triggers == [] and baselines == []


def test_missing_key_is_unmonitored_not_an_error():
    pulls = detect.pull_providers({}, {"hf_orgs": []}, fetchers=None)
    assert all(not p.monitored for p in pulls)
    assert any("not configured" in p.note for p in pulls)


def test_dead_key_cannot_report_clean():
    """Burn regression: an errored pull raises; it is never an empty list."""
    fetchers = {"openai": lambda: (_ for _ in ()).throw(FetchError("HTTP 401"))}
    with pytest.raises(detect.DetectorError, match="Fail-closed"):
        detect.pull_providers({"OPENAI_API_KEY": "sk-dead"}, CONFIG, fetchers)


def test_empty_pull_from_monitored_provider_raises():
    """Second half of the burn: zero models from a live provider is a fault."""
    fetchers = {"openai": lambda: {}}
    with pytest.raises(detect.DetectorError, match="zero models"):
        detect.pull_providers({"OPENAI_API_KEY": "sk-live"}, CONFIG, fetchers)


def test_detector_failure_leaves_registry_untouched(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(CONFIG))
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps({"providers": {"openai": {"models": {"gpt-9": {"hash": "x", "meta": {}}}}}}))
    before = registry_path.read_text()
    fetchers = {"openai": lambda: (_ for _ in ()).throw(FetchError("HTTP 401"))}
    rc = detect.main(
        [
            "--config", str(config_path), "--registry", str(registry_path),
            "--payload-dir", str(tmp_path / "payloads"), "--state-dir", str(tmp_path / "state"),
        ],
        fetchers=fetchers,
        env={"OPENAI_API_KEY": "sk-dead"},
    )
    assert rc == 1
    assert registry_path.read_text() == before


def test_hf_window_ageout_never_fires_deprecation():
    """HF is a sliding top-N window: falling out of it is not deprecation."""
    registry, _, _, _ = detect.diff_registry(
        {}, pulls_for({"huggingface": {"Qwen/Qwen-1": {"created_at": "a"}, "Qwen/Qwen-2": {"created_at": "b"}}}), CONFIG
    )
    aged_out = pulls_for({"huggingface": {"Qwen/Qwen-2": {"created_at": "b"}, "Qwen/Qwen-3": {"created_at": "c"}}})
    registry2, triggers, _, _ = detect.diff_registry(registry, aged_out, CONFIG)
    kinds = {t.kind for t in triggers}
    assert "deprecation" not in kinds
    assert ("new_model", "Qwen/Qwen-3") in [(t.kind, t.model_id) for t in triggers]
    # the aged-out model keeps its plain entry (no 'gone' status)
    assert "status" not in registry2["providers"]["huggingface"]["models"]["Qwen/Qwen-1"]


def test_coverage_loss_is_loud_even_with_no_other_triggers(tmp_path):
    """A deleted secret must surface as an issue, not degrade silently."""
    import json

    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(CONFIG))
    registry_path = tmp_path / "registry.json"
    output_path = tmp_path / "gh_output"
    args = [
        "--config", str(config_path), "--registry", str(registry_path),
        "--payload-dir", str(tmp_path / "payloads"), "--state-dir", str(tmp_path / "state"),
        "--github-output", str(output_path),
    ]
    # run 1: monitored baseline
    assert detect.main(args, fetchers={"openai": lambda: {"gpt-9": {"created": 1}}},
                       env={"OPENAI_API_KEY": "sk-live"}) == 0
    # run 2: same world, but the key is gone -> unmonitored transition.
    # (explicit fetchers dict: the missing-key check short-circuits before the
    # fetcher is called, and default fetchers would hit the live HF API)
    keyless_fetchers = {"openai": lambda: {}}
    assert detect.main(args, fetchers=keyless_fetchers, env={}) == 0
    assert "issue_needed=true" in output_path.read_text()
    issue = (tmp_path / "state" / "detect-issue.md").read_text()
    assert "PROVIDER COVERAGE LOST" in issue and "openai" in issue
    # run 3: still unmonitored -> steady state, no fresh alert
    assert detect.main(args, fetchers=keyless_fetchers, env={}) == 0
    last = output_path.read_text().splitlines()[-5:]
    assert any("issue_needed=false" in line for line in last)


def test_audit_specs_capped_and_auditable_only():
    triggers = [
        detect.Trigger("new_model", "openai", "gpt-10"),
        detect.Trigger("new_model", "huggingface", "Qwen/Qwen-99"),
        detect.Trigger("new_model", "anthropic", "claude-x"),
        detect.Trigger("new_model", "openai", "gpt-11"),
        detect.Trigger("silent_bump", "openai", "gpt-9"),
    ]
    assert detect.audit_specs(triggers, CONFIG) == "openai:gpt-10,anthropic:claude-x"


def test_end_to_end_main_writes_registry_payload_and_issue(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(CONFIG))
    registry_path = tmp_path / "registry.json"
    output_path = tmp_path / "gh_output"
    fetchers = {"openai": lambda: {"gpt-9": {"created": 1}}}
    env = {"OPENAI_API_KEY": "sk-live"}
    args = [
        "--config", str(config_path), "--registry", str(registry_path),
        "--payload-dir", str(tmp_path / "payloads"), "--state-dir", str(tmp_path / "state"),
        "--github-output", str(output_path),
    ]
    assert detect.main(args, fetchers=fetchers, env=env) == 0  # baseline
    outputs = output_path.read_text()
    assert "registry_changed=true" in outputs and "triggers=0" in outputs
    assert (tmp_path / "state" / "detect-issue.md").exists()  # baseline notice

    fetchers = {"openai": lambda: {"gpt-9": {"created": 1}, "gpt-10": {"created": 2}}}
    assert detect.main(args, fetchers=fetchers, env=env) == 0
    outputs = output_path.read_text()
    assert "triggers=1" in outputs and "audit_specs=openai:gpt-10" in outputs
    issue = (tmp_path / "state" / "detect-issue.md").read_text()
    assert "gpt-10" in issue and "new_model" in issue
    assert list((tmp_path / "payloads").glob("*-openai.json"))
