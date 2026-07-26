"""Deterministic models.yaml entry generation for newly detected models.

Appends a conservative entry (no sampling params, pricing left at 0.0 with a
TODO the PR checklist surfaces) rather than guessing provider-specific knobs
a brand-new model may reject. The id is validated against a strict charset
before it is interpolated anywhere.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

from ._common import github_output, utc_today

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/:-]*$")
PROVIDERS = ("anthropic", "openai")


class AddModelError(RuntimeError):
    pass


def parse_spec(spec: str) -> tuple[str, str]:
    provider, _, model_id = spec.partition(":")
    if provider not in PROVIDERS:
        raise AddModelError(f"unsupported provider {provider!r} (auditable: {PROVIDERS})")
    if not SAFE_ID.match(model_id):
        raise AddModelError(f"model id fails the safe-charset gate: {model_id!r}")
    return provider, model_id


def entry_text(provider: str, model_id: str) -> str:
    return (
        f"\n  # Added by the maintainer loop ({utc_today()}) - review before merging.\n"
        f'  - name: "{model_id}"\n'
        f"    provider: {provider}\n"
        f'    model_id: "{model_id}"\n'
        f"    max_tokens: 3000\n"
        f"    input_price_per_mtok: 0.0    # TODO(maintainer): verify against the provider pricing page\n"
        f"    output_price_per_mtok: 0.0   # TODO(maintainer): verify\n"
        f"    est_output_tokens_per_probe: 350\n"
    )


def ensure_model(models_path: Path, provider: str, model_id: str) -> tuple[str, bool]:
    """Return (registry name, added). Reuses an existing entry when the exact
    provider+model_id pair is already registered."""
    doc = yaml.safe_load(Path(models_path).read_text()) or {}
    for model in doc.get("models", []):
        if model.get("provider") == provider and model.get("model_id") == model_id:
            return str(model["name"]), False
        if model.get("name") == model_id:
            raise AddModelError(
                f"name collision: {model_id!r} already names a different entry"
            )
    with open(models_path, "a") as f:
        f.write(entry_text(provider, model_id))
    # Deterministic self-check: the file must still parse and contain the entry.
    doc = yaml.safe_load(Path(models_path).read_text())
    if not any(
        m.get("provider") == provider and m.get("model_id") == model_id
        for m in doc.get("models", [])
    ):  # pragma: no cover - structural safety net
        raise AddModelError("append self-check failed; models.yaml left inconsistent")
    return model_id, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-file", type=Path, default=Path("models.yaml"))
    parser.add_argument("--specs", required=True, help="comma-separated provider:model_id")
    parser.add_argument("--github-output", default=None)
    args = parser.parse_args(argv)

    names = []
    for spec in [s for s in args.specs.split(",") if s]:
        provider, model_id = parse_spec(spec)
        name, added = ensure_model(args.models_file, provider, model_id)
        names.append(name)
        print(f"{'added' if added else 'exists'}: {name}")
    github_output({"names": ",".join(names)}, args.github_output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
