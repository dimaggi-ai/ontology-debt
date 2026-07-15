# ontodebt audit report

Generated: 2026-07-15 01:11 UTC

## frontier-clean

- Model id (as invoked): `claude-fable-5-via-assistant`
- Run: `frontier-clean-20260715T011106907Z` started 2026-07-15T01:11:06.907628+00:00
- Probes: 300 (300 answered, 0 nonconformant, 0 errors)
- Tokens: 38,910 in / 600 out
- **Overall violation rate: 0.0%** (0/300 answered probes; pessimistic bound counting nonconformance as failure: 0.0%)
- **Overall contradiction rate: 0.0%** (0/60 checkable paraphrase clusters; 0 of 60 clusters untestable)
- Link constraints broken: 0/22
- Open debt (weighted): **0**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Compositional Causality: Chains, Preemption, and Overdetermination | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Multi-Hop Temporal Ordering and Duration Arithmetic | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Nested and Scoped Negation | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Stacked Conservation | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |

## Open debt ledger

No open debt. 🎉

---
*Methodology: constrained-format probes, deterministic verdicts (no LLM judge). Violations (wrong vs. declared commitment) and contradictions (model disagreeing with itself across paraphrases or linked scenarios) are counted separately. **Violation-rate CIs are scenario-cluster bootstraps** (2000 resamples, seed 0): paraphrases within a scenario are dependent, so a probe-level Wilson interval would be optimistically narrow. Contradiction-rate CIs are Wilson intervals at the scenario level (the cluster unit). Violation rates condition on answered probes and are read alongside the pessimistic bound (nonconformance counted as failure) and the nonconformant count - three-way answered-correct / answered-wrong / nonconformant, not one privileged rate. Contradiction rates condition on checkable clusters (>= 2 answered variants). Link checks use the strict majority answer of each cluster; ties and under-answered clusters are excluded as indeterminate, and symmetric link declarations are deduplicated. The weighted debt total is an ordinal prioritization heuristic, not an interval-scale measurement. Full transcripts are recorded alongside this report.*
