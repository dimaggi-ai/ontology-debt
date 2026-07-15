"""Model providers. Each provider answers a single prompt and reports usage.

Providers are intentionally thin: no retry logic beyond what the official
SDKs do themselves, no streaming, no tools. Sampling parameters are supplied
per-model from models.yaml because provider APIs disagree about what is
accepted (current-generation Anthropic models reject `temperature`; several
OpenAI reasoning models do too).
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    error: str = ""


@dataclass(frozen=True)
class ModelConfig:
    name: str                 # display name, e.g. "claude-sonnet-5"
    provider: str             # anthropic | openai | mock
    model_id: str             # exact API model id
    max_tokens: int = 100
    params: dict = field(default_factory=dict)   # provider-specific extras, passed through
    input_price_per_mtok: float = 0.0
    output_price_per_mtok: float = 0.0
    est_output_tokens_per_probe: float = 6.0     # reasoning models bill hidden thinking tokens


class Provider:
    def complete(self, system: str, prompt: str) -> Completion:  # pragma: no cover - interface
        raise NotImplementedError


class AnthropicProvider(Provider):
    def __init__(self, config: ModelConfig):
        import anthropic  # lazy: optional dependency

        self._anthropic = anthropic
        self._client = anthropic.Anthropic()
        self._config = config

    def complete(self, system: str, prompt: str) -> Completion:
        start = time.monotonic()
        try:
            response = self._client.messages.create(
                model=self._config.model_id,
                max_tokens=self._config.max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
                **self._config.params,
            )
        except self._anthropic.APIError as exc:  # typed SDK errors, incl. rate limits after retries
            return Completion("", 0, 0, time.monotonic() - start, error=f"{type(exc).__name__}: {exc}")
        text = "".join(block.text for block in response.content if block.type == "text")
        return Completion(
            text=text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_s=time.monotonic() - start,
        )


class OpenAIProvider(Provider):
    def __init__(self, config: ModelConfig):
        import openai  # lazy: optional dependency

        self._openai = openai
        self._client = openai.OpenAI()
        self._config = config

    def complete(self, system: str, prompt: str) -> Completion:
        start = time.monotonic()
        try:
            response = self._client.chat.completions.create(
                model=self._config.model_id,
                max_completion_tokens=self._config.max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                **self._config.params,
            )
        except self._openai.OpenAIError as exc:
            return Completion("", 0, 0, time.monotonic() - start, error=f"{type(exc).__name__}: {exc}")
        choice = response.choices[0]
        usage = response.usage
        return Completion(
            text=choice.message.content or "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            latency_s=time.monotonic() - start,
        )


class ClaudeCLIProvider(Provider):
    """Uses the local `claude -p` CLI (Claude Code authentication) as the model
    under test - no API key required. Exercises the full provider path against
    a live Claude model; handy for validating a run, or for auditing when you
    have a Claude Code subscription but no raw API key.
    """

    def __init__(self, config: ModelConfig):
        import shutil

        if shutil.which("claude") is None:
            raise RuntimeError(
                "the `claude` CLI is not on PATH; install Claude Code or use an API provider"
            )
        self._config = config
        self._cli_model = config.params.get("cli_model")  # optional --model override

    def complete(self, system: str, prompt: str) -> Completion:
        import subprocess

        cmd = ["claude", "-p", f"{system}\n\n{prompt}", "--output-format", "json"]
        if self._cli_model:
            cmd += ["--model", self._cli_model]
        start = time.monotonic()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return Completion("", 0, 0, time.monotonic() - start, error="claude -p timed out")
        elapsed = time.monotonic() - start
        if proc.returncode != 0:
            return Completion("", 0, 0, elapsed, error=f"claude -p exit {proc.returncode}: {proc.stderr[:200]}")
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            return Completion("", 0, 0, elapsed, error=f"claude -p returned non-JSON: {exc}")
        if payload.get("is_error"):
            return Completion("", 0, 0, elapsed, error=str(payload.get("result", "cli error"))[:200])
        usage = payload.get("usage") or {}
        return Completion(
            text=str(payload.get("result", "")),
            input_tokens=int(usage.get("input_tokens", 0) or 0),
            output_tokens=int(usage.get("output_tokens", 0) or 0),
            latency_s=elapsed,
        )


class MockProvider(Provider):
    """Deterministic offline provider for tests, dry runs, and replay.

    Default: answers "Yes" to everything unless `answer_book` overrides a
    prompt; `failure_rate` deterministically flips a fraction (keyed by prompt
    hash). Its numbers are fabricated by construction - it demonstrates the
    pipeline, never a finding. `raise_error` makes every call fail (to test
    the harness's error handling).

    REPLAY mode (`answer_book_path`): loads a `{prompt: recorded_response}`
    JSON and replays it - a prompt with no recorded answer errors rather than
    fabricating "Yes". This is how a committed set of real model responses is
    re-scored deterministically by anyone, with no API access.
    """

    def __init__(self, config: ModelConfig):
        self._config = config
        p = config.params
        self._failure_rate = float(p.get("failure_rate", 0.0))
        self._answer_book: dict[str, str] = dict(p.get("answer_book", {}))
        self._raise_error = str(p.get("raise_error", ""))
        self._replay = False
        path = p.get("answer_book_path")
        if path:
            with open(path) as f:
                self._answer_book.update(json.load(f))
            self._replay = True

    def complete(self, system: str, prompt: str) -> Completion:
        if self._raise_error:
            return Completion("", 0, 0, 0.0, error=self._raise_error)
        if self._replay:
            if prompt not in self._answer_book:
                return Completion("", 0, 0, 0.0, error="no recorded answer for this prompt")
            resp = self._answer_book[prompt]
            return Completion(text=resp, input_tokens=len(prompt) // 4, output_tokens=2, latency_s=0.0)
        digest = int(hashlib.sha256(prompt.encode()).hexdigest(), 16)
        fail = (digest % 10_000) / 10_000 < self._failure_rate
        answer = self._answer_book.get(prompt, "Yes")
        if fail:
            answer = "No" if answer.lower() == "yes" else "Yes"
        return Completion(text=answer, input_tokens=len(prompt) // 4, output_tokens=2, latency_s=0.0)


def make_provider(config: ModelConfig) -> Provider:
    if config.provider == "anthropic":
        _require_env("ANTHROPIC_API_KEY")
        return AnthropicProvider(config)
    if config.provider == "openai":
        _require_env("OPENAI_API_KEY")
        return OpenAIProvider(config)
    if config.provider == "claude_cli":
        return ClaudeCLIProvider(config)  # uses Claude Code auth, no API key
    if config.provider == "mock":
        return MockProvider(config)
    raise ValueError(f"unknown provider: {config.provider}")


def _require_env(name: str) -> None:
    if not os.environ.get(name):
        raise RuntimeError(
            f"{name} is not set. Put it in your environment or a local .env file "
            f"(see README: Quickstart)."
        )


REQUIRED_ENV = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}


def preflight(configs: list[ModelConfig]) -> list[str]:
    """Return every missing credential for the requested models, all at once."""
    missing = []
    for cfg in configs:
        var = REQUIRED_ENV.get(cfg.provider)
        if var and not os.environ.get(var) and var not in missing:
            missing.append(var)
    return missing


def load_model_configs(path) -> dict[str, ModelConfig]:
    import yaml

    with open(path) as f:
        raw = yaml.safe_load(f)
    configs = {}
    for entry in raw["models"]:
        cfg = ModelConfig(
            name=entry["name"],
            provider=entry["provider"],
            model_id=entry["model_id"],
            max_tokens=int(entry.get("max_tokens", 100)),
            params=dict(entry.get("params", {})),
            input_price_per_mtok=float(entry.get("input_price_per_mtok", 0.0)),
            output_price_per_mtok=float(entry.get("output_price_per_mtok", 0.0)),
            est_output_tokens_per_probe=float(entry.get("est_output_tokens_per_probe", 6.0)),
        )
        configs[cfg.name] = cfg
    return configs
