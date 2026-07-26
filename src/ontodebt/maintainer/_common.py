"""Shared plumbing for the maintainer loop: HTTP, state files, CI outputs.

Standard library only, deliberately: the maintainer loop must run in a bare
`pip install -e .` checkout with no optional extras.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "ontodebt-maintainer (+https://github.com/dimaggi-ai/ontology-debt)"


class FetchError(RuntimeError):
    """An HTTP fetch failed (network, auth, or malformed body)."""


def http_get(url: str, headers: dict | None = None, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise FetchError(f"GET {_redact(url)} -> HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"GET {_redact(url)} -> {exc.reason}") from exc


def http_get_json(url: str, headers: dict | None = None, timeout: int = 30):
    body = http_get(url, headers=headers, timeout=timeout)
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise FetchError(f"GET {_redact(url)} -> non-JSON body") from exc


def http_post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 300):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": USER_AGENT, "Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
        except Exception:  # pragma: no cover - best-effort error detail
            pass
        raise FetchError(f"POST {_redact(url)} -> HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"POST {_redact(url)} -> {exc.reason}") from exc


def _redact(url: str) -> str:
    """Strip query strings from URLs before they reach logs (keys travel there)."""
    return url.split("?", 1)[0]


def load_json(path: Path, default):
    if not Path(path).exists():
        return default
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")


def github_output(pairs: dict[str, str], path: str | None) -> None:
    """Append key=value pairs to a GitHub Actions output file (no-op locally)."""
    if not path:
        return
    lines = []
    for key, value in pairs.items():
        value = str(value)
        if "\n" in value:
            delimiter = f"EOF_{key.upper()}"
            lines.append(f"{key}<<{delimiter}\n{value}\n{delimiter}")
        else:
            lines.append(f"{key}={value}")
    with open(path, "a") as f:
        f.write("\n".join(lines) + "\n")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


_WS = re.compile(r"\s+")


def normalize_ws(text: str) -> str:
    """Lowercase and collapse whitespace - for verbatim-quote containment checks."""
    return _WS.sub(" ", text).strip().lower()
