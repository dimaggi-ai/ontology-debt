# Contributing

The most valuable contributions, in order:

## 1. Dispute a gold label

If you can argue a scenario's expected answer is wrong or ambiguous, open an
issue titled `gold-label: <scenario-id>` with your reading of the setup. A
disputed label is not an embarrassment — it is the ledger working as intended.
Confirmed disputes get the scenario reworded or retired, and a credit line.

## 2. Contribute a domain pack

The shipped packs are the *floor* (basic physics and time). The tool becomes
useful when packs encode real domain models — medicine, law, finance,
logistics, your product's invariants. A pack is one YAML file:

- 15–25 scenarios, each: a self-contained `setup`, a canonical `question`,
  4 paraphrases (identical format instruction at the end), a machine-checkable
  `expected`, a one-line `rationale`
- Roughly balanced answers (a yes-bot must score ~50%, not ~90%)
- `difficulty: adversarial` scenarios must be tricky-but-unambiguous, never
  genuinely debatable
- Validate with `ontodebt validate` before opening the PR

Expect an adversarial review of every gold label — that is the bar the
shipped packs cleared.

## 3. Code

`pip install -e ".[dev]"`, then `python -m pytest`. Keep the core invariants:

- **No LLM judge in the verdict path.** Verdicts must stay deterministic
  given a transcript.
- **Violations ≠ contradictions ≠ nonconformance.** Never merge the buckets.
- **The ledger only pays down on evidence.** A debt item must not close on an
  untestable cluster.

Small PRs with a regression test beat large ones.
