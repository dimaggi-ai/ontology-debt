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

| Model | easy | hard |
|---|---|---|
| Claude Fable 5 | 0.0% / 0.0% | 0.0% / 0.0% |
| Gemini 3.1-pro | 0.0% / 0.0% | (not obtained; preview rate limits) |
| GPT-5 | 0.6% / 3.1% | 1.3% / 6.5% |
| Gemini 3.6-flash | 0.6% / 3.1% | 1.3% / 6.5% |
| GPT-5-nano | 1.9% / 9.4% | 1.3% / 6.5% |
| GPT-5-mini | 0.6% / 3.1% | 2.6% / 9.7% |
| Gemini 3.1-flash-lite | 3.8% / 3.1% | 7.1% / 12.9% |

The **safe-default gating** pack is held clean (0% / 0%) by every model: applying
the rule is easy once reversibility is known, which isolates *recognition* as the
bottleneck.

## What it says (and does not)

- Frontier models are **largely reliable but not perfectly consistent**. Claude is
  spotless; GPT-5 and Gemini-flash misjudge ~1% of the hard cases yet contradict
  themselves (same scenario, reworded) 6.5% of the time.
- **Consistency degrades with capability.** The smallest model here,
  Gemini 3.1-flash-lite, misjudges 7.1% of hard cases and flip-flops on 12.9%.
- **Contradiction outpaces violation at every tier.** Models do not *hold* the
  irreversibility judgment; they re-derive it, sometimes differently.

This is not "models cannot recognize irreversibility." It is: recognition is good
but not certain, and not stable, and it decays below the frontier. A governance
layer that is 99% correct but ~6% self-inconsistent about whether an action can be
undone is not something to put in front of an irreversible action. That is the
argument for classifying reversibility **deterministically and externally** rather
than delegating it to model judgment. Tool Guard's reversibility classifier
(github.com/dimaggi-ai/tool-guard-core) is that external floor.

## Limitations

Small scenario counts (easy recognition 17, gating 15, hard 31), so rates are
coarse. Scenarios are text-described, not executed. Gold labels passed an
adversarial ambiguity review, which is weaker than multi-annotator agreement.
Gemini 3.1-pro on the hard tier could not be obtained (preview-model rate limits).
Recognition of irreversibility is a *necessary* condition for safe autonomy, not a
sufficient one.

## Reproduce

```
ontodebt run --models <name>,... --models-file models-irreversibility.yaml \
  --commitments commitments-irreversibility-hard --results examples/irreversibility/hard
ontodebt report --commitments commitments-irreversibility-hard --results examples/irreversibility/hard
```
