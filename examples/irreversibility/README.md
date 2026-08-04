# Irreversibility recognition: a two-tier audit

Can a language model be trusted to judge, from the facts in front of it, whether
an autonomous action can be **undone**? This measurement asks exactly that, with
the repo's deterministic harness (no LLM judge; every verdict reproducible from
the committed transcripts).

It matters because the danger in agentic systems is not a wrong answer, it is a
wrong **irreversible action**: a settled wire, a `DROP TABLE`, a sent message. If
a model cannot reliably and *stably* tell which actions cannot be taken back, that
judgment cannot be delegated to it.

## Packs

- `commitments-irreversibility/irreversibility_recognition.yaml` (easy tier) and
  `commitments-irreversibility-hard/irreversibility_recognition_hard.yaml` (hard
  tier): each scenario describes one concrete agent action with every fact needed,
  and asks whether it can be undone by ordinary means. The hard tier makes the
  answer hinge on a subtle stated detail with distractors (a cancel window with
  time elapsed; a DELETE that already fired a settled refund; a transfer whose
  principal returns but whose fee does not), so surface pattern-matching on the
  verb is not enough.
- `commitments-irreversibility/safe_default_gating.yaml`: given an explicit
  safety rule ("require human confirmation before any action that cannot be
  undone"), does the model apply it correctly?

Every scenario passed two independent gates before shipping: an adversarial
ambiguity reviewer and a blind recomputation of the gold answer.

## Results (violation rate / contradiction rate)

Both columns are the **recognition** pack only, so easy (17 scenarios, 85 probes)
and hard (31 scenarios, 155 probes) are directly comparable. Violation rate is per
probe; contradiction rate is per scenario cluster (5 paraphrases each).

| Model | easy recognition | hard recognition |
|---|---|---|
| Claude Fable 5 | 0.0% / 0.0% | 0.0% / 0.0% |
| Gemini 3.1-pro | 0.0% / 0.0% | (not obtained; preview rate limits) |
| GPT-5 | 1.2% / 5.9% | 1.3% / 6.5% |
| Gemini 3.6-flash | 1.2% / 5.9% | 1.3% / 6.5% |
| GPT-5-mini | 1.2% / 5.9% | 2.6% / 9.7% |
| GPT-5-nano | 3.5% / 17.6% | 1.3% / 6.5% |
| Gemini 3.1-flash-lite | 7.1% / 5.9% | 7.1% / 12.9% |

The **safe-default gating** pack (15 scenarios) is held clean (0% / 0%) by every
model, so on this set rule-following is not the failure point; the signal above is
attributable to *recognition*. Gating is reported separately from recognition
here; folding it into the easy column would dilute the recognition rates by
roughly half, so these numbers are recognition-only.

## What it says (and does not)

Read these as small counts, not just percentages — a 6.5% hard contradiction rate
is **2 of 31 scenarios**.

- Frontier models are **largely reliable but not perfectly consistent**. Claude
  Fable 5 is spotless on this 48-scenario recognition set (0 of 48). GPT-5 and
  Gemini-3.6-flash each miss 2 of 31 hard scenarios (1.3%) yet, because each miss is
  an isolated flip on 1 of the scenario's 5 paraphrases, contradict themselves on
  6.5% of scenarios.
- **The smallest model is the least reliable on both axes.** Gemini 3.1-flash-lite
  misjudges 11 of 155 hard probes (7.1%) and flip-flops on 4 of 31 hard scenarios
  (12.9%). We do not claim a smooth monotonic decline with capability — GPT-5-nano,
  for instance, is better than GPT-5-mini on the hard tier — only that the one small
  model here is clearly the weakest.
- **Contradiction usually exceeds violation, but not universally.** On the hard
  tier and for most models the contradiction rate is several times the violation
  rate — expected when a miss is an isolated paraphrase flip (violation counts that
  probe, contradiction counts the whole scenario). The exception is flash-lite on
  the easy tier (7.1% violation vs 5.9% contradiction): there it is *consistently*
  wrong on some scenarios — the worse failure mode, since a stable wrong answer
  never even flags itself as unstable.

This is not "models cannot recognize irreversibility." It is: recognition is good
but not certain, and not perfectly stable. A governance layer that is ~99% correct
but a few percent self-inconsistent about whether an action can be undone is not
something to put in front of an irreversible action *on its own*. That is the
argument for classifying reversibility **deterministically and externally** as a
floor, rather than delegating it solely to model judgment. Tool Guard's
reversibility classifier (github.com/dimaggi-ai/tool-guard-core) is that external
floor — itself a structural classifier with its own limits (see its README), not a
proof of safety.

## Limitations

Small scenario counts (easy recognition 17, gating 15, hard 31), so rates are
coarse and a one-scenario change moves a hard rate by 3.2 points. Scenarios are
text-described, not executed. Gold labels passed an adversarial ambiguity review
and an independent blind re-adjudication, both weaker than large-panel
multi-annotator agreement. The multi-model failures cluster on one construction —
a destructive-sounding operation over recomputable data (read-through caches,
verified backups) — so the hard tier's discriminating power leans partly on that
single trick. Gemini 3.1-pro on the hard tier could not be obtained (preview-model
rate limits). Recognition of irreversibility is a *necessary* condition for safe
autonomy, not a sufficient one.

## Reproduce

Score the committed transcripts (no API access needed — `report` reads the saved
`run-*.json` and rewrites `report.md`):

```
# hard tier
ontodebt report --commitments commitments-irreversibility-hard \
  --models-file models-irreversibility.yaml --results examples/irreversibility/hard
# easy tier (recognition + gating packs live together)
ontodebt report --commitments commitments-irreversibility \
  --models-file models-irreversibility.yaml --results examples/irreversibility/easy
```

To re-run the API models live (needs `OPENAI_API_KEY` / `GEMINI_API_KEY`), swap
`report` for `run --models gpt-5,gpt-5-mini,...`. The `claude-fable5` row was
collected keyless via Claude Code subagents; its exact responses are committed and
replayed deterministically (`answers-claude-fable5.json`), so its 0/0 result
regenerates with no API key and no subagent harness. Only the **verdicts** are
meaningful for that row; its token counts and cost in the report are synthetic
(the deterministic replay does not carry real usage), so ignore the Fable
tokens/cost line. The verdicts (violations/contradictions) are exact.
