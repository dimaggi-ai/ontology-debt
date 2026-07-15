# ontodebt audit report

Generated: 2026-07-15 02:12 UTC

## claude-fable5

- Model id (as invoked): `claude-fable-5-via-assistant`
- Run: `claude-fable5-20260715T021200682Z` started 2026-07-15T02:12:00.682578+00:00
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- Tokens: 56,067 in / 1,500 out
- **Overall violation rate: 0.0%** (0/750 answered probes; pessimistic bound counting nonconformance as failure: 0.0%)
- **Overall contradiction rate: 0.0%** (0/150 checkable paraphrase clusters; 0 of 150 clusters untestable)
- Link constraints broken: 0/31
- Open debt (weighted): **0**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Entity Persistence | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Negation Invariance | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Object Permanence | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Quantity Conservation | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |

## Open debt ledger

| Model | Commitment | Scenario | Kind | Severity | First seen | Last seen |
|---|---|---|---|---|---|---|
| gpt-nano | causal_ordering | co-002 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | causal_ordering | co-002 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-008 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-008 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-012 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-012 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-013 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-013 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-019 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-019 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-006 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-006 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-006~tc-007 | link_contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-007 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-007 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-009 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-009 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-012 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-012 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-013 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-013 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-015 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-015 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-018 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-018 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-021 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-021 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-022 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-022 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-023 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-023 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-mini | temporal_consistency | tc-024 | contradiction | high | gpt-mini-20260715T020937924Z | gpt-mini-20260715T020937924Z |
| gpt-nano | temporal_consistency | tc-024 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-mini | temporal_consistency | tc-024 | violation | high | gpt-mini-20260715T020937924Z | gpt-mini-20260715T020937924Z |
| gpt-nano | temporal_consistency | tc-024 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | entity_persistence | ep-008 | contradiction | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | entity_persistence | ep-008 | violation | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-mini | entity_persistence | ep-022 | contradiction | medium | gpt-mini-20260715T020937924Z | gpt-mini-20260715T020937924Z |
| gpt-mini | entity_persistence | ep-022 | violation | medium | gpt-mini-20260715T020937924Z | gpt-mini-20260715T020937924Z |
| gpt-nano | negation_invariance | ni-001 | contradiction | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | negation_invariance | ni-001 | violation | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | quantity_conservation | qc-024 | contradiction | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | quantity_conservation | qc-024 | violation | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |

---
*Methodology: constrained-format probes, deterministic verdicts (no LLM judge). Violations (wrong vs. declared commitment) and contradictions (model disagreeing with itself across paraphrases or linked scenarios) are counted separately. **Violation-rate CIs are scenario-cluster bootstraps** (2000 resamples, seed 0): paraphrases within a scenario are dependent, so a probe-level Wilson interval would be optimistically narrow. Contradiction-rate CIs are Wilson intervals at the scenario level (the cluster unit). Violation rates condition on answered probes and are read alongside the pessimistic bound (nonconformance counted as failure) and the nonconformant count - three-way answered-correct / answered-wrong / nonconformant, not one privileged rate. Contradiction rates condition on checkable clusters (>= 2 answered variants). Link checks use the strict majority answer of each cluster; ties and under-answered clusters are excluded as indeterminate, and symmetric link declarations are deduplicated. The weighted debt total is an ordinal prioritization heuristic, not an interval-scale measurement. Full transcripts are recorded alongside this report.*
