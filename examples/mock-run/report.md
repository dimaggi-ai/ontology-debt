# ontodebt audit report

Generated: 2026-07-14 22:44 UTC

## mock

- Model id (as invoked): `mock-v0`
- Run: `mock-20260714T224412939Z` started 2026-07-14T22:44:12.939804+00:00
- Probes: 750 (685 answered, 65 nonconformant, 0 errors)
- Tokens: 55,664 in / 1,500 out
- **Overall violation rate: 47.7%** (327/685 answered probes; pessimistic bound counting nonconformance as failure: 52.3%)
- **Overall contradiction rate: 25.5%** (35/137 checkable paraphrase clusters; 13 of 150 clusters untestable)
- Link constraints broken: 20/30
- Open debt (weighted): **554**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 43.2% [34.8%, 52.0%] | 40.0% [23.4%, 59.3%] | 52.0% – 64.0% | 0 | 125 |
| Entity Persistence | medium | 48.0% [39.4%, 56.7%] | 32.0% [17.2%, 51.6%] | 48.0% – 60.0% | 0 | 125 |
| Negation Invariance | medium | 46.4% [37.9%, 55.1%] | 8.0% [2.2%, 25.0%] | 52.0% – 56.0% | 0 | 125 |
| Object Permanence | high | 47.8% [38.9%, 56.9%] | 17.4% [7.0%, 37.1%] | 47.8% – 65.2% | 10 | 115 |
| Quantity Conservation | medium | 52.9% [42.4%, 63.2%] | 11.8% [3.3%, 34.3%] | 41.2% – 52.9% | 40 | 85 |
| Temporal Consistency | high | 50.0% [40.8%, 59.2%] | 40.9% [23.3%, 61.3%] | 40.9% – 59.1% | 15 | 110 |

## Open debt ledger

| Model | Commitment | Scenario | Kind | Severity | First seen | Last seen |
|---|---|---|---|---|---|---|
| mock | causal_ordering | co-002 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-004 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-004 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-006 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-006 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-007~co-008 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-008 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-008 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-009 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-009 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-011 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-012 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-012 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-013 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-014 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-014 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-015 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-017 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-017 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-018 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-018 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-019~co-020 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-020 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-020 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-021 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-021 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-021~co-022 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | causal_ordering | co-023 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-001~op-002 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-001~op-021 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-002 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-002 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-004 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-009 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-009 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-011 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-012~op-013 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-013 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-014 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-016 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-016 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-016~op-017 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-018 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-020 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-021 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-021 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-022 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | object_permanence | op-024 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-001 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-001~tc-002 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-003 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-003 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-006 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-006~tc-007 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-008 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-008 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-010~tc-011 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-011 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-012 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-013 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-013 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-015 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-015 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-016 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-016 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-018 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-018 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-020 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-021 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-022 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-022 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-022~tc-023 | link_contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-023 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-023 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-024 | contradiction | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | temporal_consistency | tc-024 | violation | high | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-001~ep-016 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-003 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-003~ep-018 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-004 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-005 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-005 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-007 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-007 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-010 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-010 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-011 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-012 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-014 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-014 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-016 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-016 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-017 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-019 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-019 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-021 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-022 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-022 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-023 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-025 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | entity_persistence | ep-025 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-001~ni-002 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-002 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-003 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-003 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-003~ni-004 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-005 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-005 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-005~ni-006 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-007~ni-008 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-008 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-009~ni-010 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-010 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-014 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-015 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-017 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-019 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-021 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-023 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | negation_invariance | ni-025 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-002 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-002~qc-003 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-005 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-009 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-009 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-010~qc-018 | link_contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-013 | contradiction | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-013 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-015 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-016 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-018 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-020 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-021 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |
| mock | quantity_conservation | qc-025 | violation | medium | mock-20260714T224412939Z | mock-20260714T224412939Z |

---
*Methodology: constrained-format probes, deterministic verdicts (no LLM judge), Wilson 95% intervals. Violations (wrong vs. declared commitment) and contradictions (model disagreeing with itself across paraphrases or linked scenarios) are counted separately. Violation rates condition on answered probes (the pessimistic bound above counts nonconformance as failure); contradiction rates condition on checkable clusters (>= 2 answered variants). Link checks use the strict majority answer of each cluster; ties and under-answered clusters are excluded as indeterminate, and symmetric link declarations are deduplicated. Full transcripts are recorded alongside this report.*
