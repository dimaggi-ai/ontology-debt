# ontodebt audit report

Generated: 2026-07-15 03:04 UTC

## claude-fable5-frontier

- Model id (as invoked): `claude-fable-5-via-assistant`
- Run: `claude-fable5-frontier-20260715T023944571Z` started 2026-07-15T02:39:44.571662+00:00
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

## gpt-4.1-mini

- Model id (as invoked): `gpt-4.1-mini-2025-04-14`
- Run: `gpt-4.1-mini-20260715T025655566Z` started 2026-07-15T02:56:55.566359+00:00
- Probes: 300 (300 answered, 0 nonconformant, 0 errors)
- Tokens: 51,526 in / 300 out - estimated cost $0.02
- **Overall violation rate: 29.3%** (88/300 answered probes; pessimistic bound counting nonconformance as failure: 29.3%)
- **Overall contradiction rate: 31.7%** (19/60 checkable paraphrase clusters; 0 of 60 clusters untestable)
- Link constraints broken: 3/20
- Open debt (weighted): **230**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Compositional Causality: Chains, Preemption, and Overdetermination | high | 9.3% [0.0%, 25.3%] | 6.7% [1.2%, 29.8%] | 86.7% – 93.3% | 0 | 75 |
| Multi-Hop Temporal Ordering and Duration Arithmetic | high | 25.3% [9.3%, 44.0%] | 46.7% [24.8%, 69.9%] | 66.7% – 86.7% | 0 | 75 |
| Nested and Scoped Negation | high | 6.7% [0.0%, 20.0%] | 0.0% [0.0%, 20.4%] | 93.3% – 93.3% | 0 | 75 |
| Stacked Conservation | high | 76.0% [58.7%, 92.0%] | 73.3% [48.0%, 89.1%] | 20.0% – 33.3% | 0 | 75 |

## gpt-4o-mini

- Model id (as invoked): `gpt-4o-mini-2024-07-18`
- Run: `gpt-4o-mini-20260715T025724711Z` started 2026-07-15T02:57:24.711468+00:00
- Probes: 300 (299 answered, 1 nonconformant, 0 errors)
- Tokens: 51,526 in / 383 out - estimated cost $0.01
- **Overall violation rate: 35.5%** (106/299 answered probes; pessimistic bound counting nonconformance as failure: 35.7%)
- **Overall contradiction rate: 36.7%** (22/60 checkable paraphrase clusters; 0 of 60 clusters untestable)
- Link constraints broken: 3/19
- Open debt (weighted): **265**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Compositional Causality: Chains, Preemption, and Overdetermination | high | 8.0% [0.0%, 21.3%] | 13.3% [3.7%, 37.9%] | 86.7% – 93.3% | 0 | 75 |
| Multi-Hop Temporal Ordering and Duration Arithmetic | high | 45.9% [26.7%, 66.2%] | 66.7% [41.7%, 84.8%] | 46.7% – 60.0% | 1 | 74 |
| Nested and Scoped Negation | high | 1.3% [0.0%, 4.0%] | 6.7% [1.2%, 29.8%] | 93.3% – 100.0% | 0 | 75 |
| Stacked Conservation | high | 86.7% [66.7%, 100.0%] | 60.0% [35.7%, 80.2%] | 13.3% – 13.3% | 0 | 75 |

## gpt-5-mini

- Model id (as invoked): `gpt-5-mini-2025-08-07`
- Run: `gpt-5-mini-20260715T025248554Z` started 2026-07-15T02:52:48.554171+00:00
- Probes: 300 (300 answered, 0 nonconformant, 0 errors)
- Tokens: 51,226 in / 32,824 out - estimated cost $0.08
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

## gpt-5-nano

- Model id (as invoked): `gpt-5-nano-2025-08-07`
- Run: `gpt-5-nano-20260715T025521382Z` started 2026-07-15T02:55:21.382920+00:00
- Probes: 300 (300 answered, 0 nonconformant, 0 errors)
- Tokens: 51,226 in / 49,785 out - estimated cost $0.02
- **Overall violation rate: 0.3%** (1/300 answered probes; pessimistic bound counting nonconformance as failure: 0.3%)
- **Overall contradiction rate: 1.7%** (1/60 checkable paraphrase clusters; 0 of 60 clusters untestable)
- Link constraints broken: 0/22
- Open debt (weighted): **10**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Compositional Causality: Chains, Preemption, and Overdetermination | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Multi-Hop Temporal Ordering and Duration Arithmetic | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Nested and Scoped Negation | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Stacked Conservation | high | 1.3% [0.0%, 4.0%] | 6.7% [1.2%, 29.8%] | 93.3% – 100.0% | 0 | 75 |

## gpt-5.4

- Model id (as invoked): `gpt-5.4-2026-03-05`
- Run: `gpt-5.4-20260715T025107231Z` started 2026-07-15T02:51:07.231239+00:00
- Probes: 300 (300 answered, 0 nonconformant, 0 errors)
- Tokens: 51,226 in / 15,206 out - estimated cost $0.22
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

## gpt-frontier

- Model id (as invoked): `gpt-5.5-2026-04-23`
- Run: `gpt-frontier-20260715T023945147Z` started 2026-07-15T02:39:45.147212+00:00
- Probes: 300 (300 answered, 0 nonconformant, 0 errors)
- Tokens: 51,226 in / 13,740 out - estimated cost $0.20
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

## gpt-mini

- Model id (as invoked): `gpt-5.4-mini-2026-03-17`
- Run: `gpt-mini-20260715T025205121Z` started 2026-07-15T02:52:05.121830+00:00
- Probes: 300 (300 answered, 0 nonconformant, 0 errors)
- Tokens: 51,226 in / 16,793 out - estimated cost $0.05
- **Overall violation rate: 0.3%** (1/300 answered probes; pessimistic bound counting nonconformance as failure: 0.3%)
- **Overall contradiction rate: 1.7%** (1/60 checkable paraphrase clusters; 0 of 60 clusters untestable)
- Link constraints broken: 0/22
- Open debt (weighted): **10**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Compositional Causality: Chains, Preemption, and Overdetermination | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Multi-Hop Temporal Ordering and Duration Arithmetic | high | 1.3% [0.0%, 4.0%] | 6.7% [1.2%, 29.8%] | 93.3% – 100.0% | 0 | 75 |
| Nested and Scoped Negation | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Stacked Conservation | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |

## gpt-nano

- Model id (as invoked): `gpt-5.4-nano-2026-03-17`
- Run: `gpt-nano-20260715T025432926Z` started 2026-07-15T02:54:32.926634+00:00
- Probes: 300 (300 answered, 0 nonconformant, 0 errors)
- Tokens: 51,226 in / 20,366 out - estimated cost $0.01
- **Overall violation rate: 3.3%** (10/300 answered probes; pessimistic bound counting nonconformance as failure: 3.3%)
- **Overall contradiction rate: 10.0%** (6/60 checkable paraphrase clusters; 0 of 60 clusters untestable)
- Link constraints broken: 0/22
- Open debt (weighted): **60**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Compositional Causality: Chains, Preemption, and Overdetermination | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 20.4%] | 100.0% – 100.0% | 0 | 75 |
| Multi-Hop Temporal Ordering and Duration Arithmetic | high | 6.7% [0.0%, 14.7%] | 20.0% [7.0%, 45.2%] | 86.7% – 100.0% | 0 | 75 |
| Nested and Scoped Negation | high | 1.3% [0.0%, 4.0%] | 6.7% [1.2%, 29.8%] | 93.3% – 100.0% | 0 | 75 |
| Stacked Conservation | high | 5.3% [0.0%, 14.7%] | 13.3% [3.7%, 37.9%] | 93.3% – 100.0% | 0 | 75 |

## Open debt ledger

| Model | Commitment | Scenario | Kind | Severity | First seen | Last seen |
|---|---|---|---|---|---|---|
| gpt-4.1-mini | compositional_causality | cc-004 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4.1-mini | compositional_causality | cc-004 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | compositional_causality | cc-010 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | compositional_causality | cc-010 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | compositional_causality | cc-014 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | compositional_causality | cc-014 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | compositional_causality | cc-014 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | multihop_temporal | mt-001 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | multihop_temporal | mt-001 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-002 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-002 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-002 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-002 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-003 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-003 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-003 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-003 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | multihop_temporal | mt-004 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | multihop_temporal | mt-004 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-005 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-005 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-005 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-005 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-007 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-007 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-007 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-007 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | multihop_temporal | mt-008 | contradiction | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | multihop_temporal | mt-008 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-008 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | multihop_temporal | mt-008 | violation | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | multihop_temporal | mt-008 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-008 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-010 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-010 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-010~mt-011 | link_contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-010~mt-011 | link_contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | multihop_temporal | mt-011 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | multihop_temporal | mt-011 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | multihop_temporal | mt-012 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4.1-mini | multihop_temporal | mt-012 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-012 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-mini | multihop_temporal | mt-013 | contradiction | high | gpt-mini-20260715T025205121Z | gpt-mini-20260715T025205121Z |
| gpt-nano | multihop_temporal | mt-013 | contradiction | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4o-mini | multihop_temporal | mt-013 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-mini | multihop_temporal | mt-013 | violation | high | gpt-mini-20260715T025205121Z | gpt-mini-20260715T025205121Z |
| gpt-nano | multihop_temporal | mt-013 | violation | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4o-mini | multihop_temporal | mt-013 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | multihop_temporal | mt-014 | contradiction | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | multihop_temporal | mt-014 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-014 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | multihop_temporal | mt-014 | violation | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | multihop_temporal | mt-014 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | multihop_temporal | mt-014 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | nested_negation | nn-003 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | nested_negation | nn-003 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | nested_negation | nn-012 | contradiction | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-nano | nested_negation | nn-012 | violation | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | nested_negation | nn-014~nn-015 | link_contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4.1-mini | nested_negation | nn-015 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4.1-mini | stacked_conservation | sc-001 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-001 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-001 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-001 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-002 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4.1-mini | stacked_conservation | sc-002 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-002 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-5-nano | stacked_conservation | sc-003 | contradiction | high | gpt-5-nano-20260715T025521382Z | gpt-5-nano-20260715T025521382Z |
| gpt-4.1-mini | stacked_conservation | sc-003 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-003 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-5-nano | stacked_conservation | sc-003 | violation | high | gpt-5-nano-20260715T025521382Z | gpt-5-nano-20260715T025521382Z |
| gpt-4.1-mini | stacked_conservation | sc-003 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-003 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-004 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-004 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-004 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-004 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-005~sc-015 | link_contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-005~sc-015 | link_contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | stacked_conservation | sc-006 | contradiction | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | stacked_conservation | sc-006 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-006 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | stacked_conservation | sc-006 | violation | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | stacked_conservation | sc-006 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-006 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-007 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-007 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-007 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-007 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-008 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4.1-mini | stacked_conservation | sc-008 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-008 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | stacked_conservation | sc-009 | contradiction | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | stacked_conservation | sc-009 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-009 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-nano | stacked_conservation | sc-009 | violation | high | gpt-nano-20260715T025432926Z | gpt-nano-20260715T025432926Z |
| gpt-4.1-mini | stacked_conservation | sc-009 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-009 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | stacked_conservation | sc-010 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-010 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-010 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | stacked_conservation | sc-011 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4o-mini | stacked_conservation | sc-011~sc-013 | link_contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-012 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-012 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-012 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-012 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-013 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4.1-mini | stacked_conservation | sc-013 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4.1-mini | stacked_conservation | sc-014 | contradiction | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-014 | contradiction | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-014 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-014 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |
| gpt-4.1-mini | stacked_conservation | sc-015 | violation | high | gpt-4.1-mini-20260715T025655566Z | gpt-4.1-mini-20260715T025655566Z |
| gpt-4o-mini | stacked_conservation | sc-015 | violation | high | gpt-4o-mini-20260715T025724711Z | gpt-4o-mini-20260715T025724711Z |

---
*Methodology: constrained-format probes, deterministic verdicts (no LLM judge). Violations (wrong vs. declared commitment) and contradictions (model disagreeing with itself across paraphrases or linked scenarios) are counted separately. **Violation-rate CIs are scenario-cluster bootstraps** (2000 resamples, seed 0): paraphrases within a scenario are dependent, so a probe-level Wilson interval would be optimistically narrow. Contradiction-rate CIs are Wilson intervals at the scenario level (the cluster unit). Violation rates condition on answered probes and are read alongside the pessimistic bound (nonconformance counted as failure) and the nonconformant count - three-way answered-correct / answered-wrong / nonconformant, not one privileged rate. Contradiction rates condition on checkable clusters (>= 2 answered variants). Link checks use the strict majority answer of each cluster; ties and under-answered clusters are excluded as indeterminate, and symmetric link declarations are deduplicated. The weighted debt total is an ordinal prioritization heuristic, not an interval-scale measurement. Full transcripts are recorded alongside this report.*

