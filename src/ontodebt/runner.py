"""Probe execution and result records.

Runs every probe against a model with a small thread pool, records a full
transcript (one JSON line per probe), and computes deterministic verdicts.
"""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .providers import ModelConfig, Provider, make_provider
from .schema import SYSTEM_PROMPT, Probe, Verdict, normalize_answer


@dataclass(frozen=True)
class ProbeResult:
    commitment_id: str
    scenario_id: str
    variant_index: int
    prompt: str
    response: str
    answer: str            # normalized extracted answer ("" if none)
    verdict: str           # Verdict value
    severity: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    error: str = ""


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    model_name: str
    model_id: str
    started_at: str
    results: list[ProbeResult]

    @property
    def total_input_tokens(self) -> int:
        return sum(r.input_tokens for r in self.results)

    @property
    def total_output_tokens(self) -> int:
        return sum(r.output_tokens for r in self.results)


def run_probes(
    probes: list[Probe],
    config: ModelConfig,
    max_workers: int = 8,
    transcript_path: Path | None = None,
    progress: bool = True,
) -> RunRecord:
    provider = make_provider(config)
    started = datetime.now(timezone.utc)
    run_id = f"{config.name}-{started.strftime('%Y%m%dT%H%M%SZ')}"
    results: list[ProbeResult] = []
    lock = threading.Lock()
    transcript_file = open(transcript_path, "a") if transcript_path else None

    def work(probe: Probe) -> ProbeResult:
        completion = provider.complete(SYSTEM_PROMPT, probe.prompt)
        if completion.error:
            verdict = Verdict.ERROR
            answer = ""
        else:
            verdict = probe.expected.check(completion.text)
            answer = normalize_answer(completion.text)
        return ProbeResult(
            commitment_id=probe.commitment_id,
            scenario_id=probe.scenario_id,
            variant_index=probe.variant_index,
            prompt=probe.prompt,
            response=completion.text,
            answer=answer,
            verdict=verdict.value,
            severity=probe.severity,
            input_tokens=completion.input_tokens,
            output_tokens=completion.output_tokens,
            latency_s=round(completion.latency_s, 3),
            error=completion.error,
        )

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(work, p) for p in probes]
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                with lock:
                    results.append(result)
                    if transcript_file:
                        record = {"run_id": run_id, "model": config.model_id, **asdict(result)}
                        transcript_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                        transcript_file.flush()
                if progress and (i % 50 == 0 or i == len(probes)):
                    print(f"  [{config.name}] {i}/{len(probes)} probes")
    finally:
        if transcript_file:
            transcript_file.close()

    # Stable order: by commitment, scenario, variant (thread completion order varies).
    results.sort(key=lambda r: (r.commitment_id, r.scenario_id, r.variant_index))
    return RunRecord(
        run_id=run_id,
        model_name=config.name,
        model_id=config.model_id,
        started_at=started.isoformat(),
        results=results,
    )


def save_run(record: RunRecord, path: Path) -> None:
    payload = {
        "run_id": record.run_id,
        "model_name": record.model_name,
        "model_id": record.model_id,
        "started_at": record.started_at,
        "results": [asdict(r) for r in record.results],
    }
    path.write_text(json.dumps(payload, indent=1, ensure_ascii=False))


def load_run(path: Path) -> RunRecord:
    payload = json.loads(path.read_text())
    return RunRecord(
        run_id=payload["run_id"],
        model_name=payload["model_name"],
        model_id=payload["model_id"],
        started_at=payload["started_at"],
        results=[ProbeResult(**r) for r in payload["results"]],
    )
