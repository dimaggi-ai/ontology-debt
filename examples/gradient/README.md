# Capability gradient — the floor packs across four models

Every one of the six floor commitment packs (150 scenarios, 750 probes)
audited across a capability gradient. Deterministic scoring, no LLM judge.
Reproduce: `ontodebt run --models claude-fable5,gpt-frontier,gpt-mini,gpt-nano`
(the Claude answers replay from a committed file; the GPT tiers call the API).

| Model | Tier | Violations | Contradictions | Worst pack |
|---|---|---|---|---|
| Claude Fable 5 | frontier | **0.0%** | **0.0%** | — |
| GPT-5.5 | frontier | **0.0%** | **0.0%** | — |
| GPT-5.4-mini | mid | 0.3% | 1.3% | — |
| GPT-5.4-nano | small | **3.7%** | **12.7%** | temporal (44% of clusters self-contradictory) |

Total GPT API cost for this run: **~$0.01** (low-effort answers).

## What it shows

1. **Both frontier models hold the commonsense floor completely.** The premise
   that frontier models still fail basic object-permanence / causality / time
   probes is, in 2026, false for these packs. The tool reports that honestly.
2. **The tool discriminates by capability.** As the model gets smaller, debt
   accrues — cleanly, monotonically. This is the tool earning its keep: it is
   an instrument, and here is its calibration curve.
3. **Contradiction rate outpaces violation rate as capability drops.**
   GPT-5.4-nano is 3.7% *wrong* but 12.7% *self-inconsistent* — it gives
   different answers to trivially-equivalent rephrasings of the same question
   (e.g. "are the dominoes still standing?" answered no/yes/no/no/no). A single
   accuracy number hides this; separating violations from contradictions is the
   whole point. Weaker models are not just more wrong — they are less stable.

## What it does not show

These are the *floor* — deliberately basic world-model invariants. That
frontier models clear them is expected and good. The tool's real value is
(a) this kind of gradient across the models you actually ship, and (b) packs
you write for *your* domain, which no model has been tuned on. A high pass
rate on the floor is a floor, not a safety certificate.

Model ids are as-invoked (`gpt-5.5-2026-04-23`, `gpt-5.4-mini-2026-03-17`,
`gpt-5.4-nano-2026-03-17`; Claude Fable 5 answered via the Claude Code
assistant, recorded and replayed). Full transcripts and the debt ledger are in
this directory.
