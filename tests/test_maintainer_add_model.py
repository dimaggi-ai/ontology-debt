"""models.yaml entry generation: strict charset gate, idempotence, collisions."""

import pytest
import yaml

from ontodebt.maintainer import add_model
from ontodebt.maintainer.audit_pr_body import extract_model_summary, render

MODELS_YAML = """\
models:
  - name: existing
    provider: openai
    model_id: gpt-9-2026-01-01
    max_tokens: 3000
"""


def test_spec_parsing_rejects_bad_provider_and_unsafe_ids():
    assert add_model.parse_spec("openai:gpt-10") == ("openai", "gpt-10")
    with pytest.raises(add_model.AddModelError, match="provider"):
        add_model.parse_spec("huggingface:meta-llama/x")
    for bad in ["openai:gpt 10", "openai:gpt;rm -rf", 'openai:gpt"x', "openai:-leading"]:
        with pytest.raises(add_model.AddModelError, match="charset"):
            add_model.parse_spec(bad)


def test_append_reuse_and_collision(tmp_path):
    path = tmp_path / "models.yaml"
    path.write_text(MODELS_YAML)

    name, added = add_model.ensure_model(path, "openai", "gpt-10-2026-07-01")
    assert added and name == "gpt-10-2026-07-01"
    doc = yaml.safe_load(path.read_text())
    entry = next(m for m in doc["models"] if m["name"] == name)
    assert entry["provider"] == "openai" and entry["max_tokens"] == 3000
    assert entry["input_price_per_mtok"] == 0.0  # TODO surfaced to the PR checklist

    # idempotent: same spec reuses the entry
    name2, added2 = add_model.ensure_model(path, "openai", "gpt-10-2026-07-01")
    assert name2 == name and not added2
    assert path.read_text().count("gpt-10-2026-07-01") >= 1

    # existing provider+id under a different name is reused, not duplicated
    name3, added3 = add_model.ensure_model(path, "openai", "gpt-9-2026-01-01")
    assert name3 == "existing" and not added3

    # a name collision with a different entry is refused
    with pytest.raises(add_model.AddModelError, match="collision"):
        add_model.ensure_model(path, "anthropic", "existing")


REPORT = """\
# ontodebt audit report

## gpt-10-2026-07-01

> ⚠️ RUN UNRELIABLE: 30% of probes errored.

- Model id (as invoked): `gpt-10-2026-07-01`
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- **Overall violation rate: 0.4%** (3/750 answered probes)
- **Overall contradiction rate: 2.0%** (3/150 checkable paraphrase clusters)

| t |
|---|

## other-model

- **Overall violation rate: 9.9%**
"""


def test_pr_body_extracts_only_the_named_models(tmp_path):
    report = tmp_path / "report.md"
    report.write_text(REPORT)
    body = render(report, ["gpt-10-2026-07-01"])
    assert "0.4%" in body and "9.9%" not in body
    assert "checklist" in body.lower()
    assert extract_model_summary(REPORT, "missing-model")[0].startswith("- (no section")


def test_pr_body_keeps_warning_banners():
    """A RUN UNRELIABLE banner must never be silently dropped from the PR."""
    lines = extract_model_summary(REPORT, "gpt-10-2026-07-01")
    assert any("RUN UNRELIABLE" in line for line in lines)
