# ontodebt audit report

Generated: 2026-07-15 03:04 UTC

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

## gpt-4.1-mini

- Model id (as invoked): `gpt-4.1-mini-2025-04-14`
- Run: `gpt-4.1-mini-20260715T023714751Z` started 2026-07-15T02:37:14.751842+00:00
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- Tokens: 86,049 in / 750 out - estimated cost $0.04
- **Overall violation rate: 1.9%** (14/750 answered probes; pessimistic bound counting nonconformance as failure: 1.9%)
- **Overall contradiction rate: 5.3%** (8/150 checkable paraphrase clusters; 0 of 150 clusters untestable)
- Link constraints broken: 0/31
- Open debt (weighted): **76**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 1.6% [0.0%, 4.0%] | 8.0% [2.2%, 25.0%] | 96.0% – 100.0% | 0 | 125 |
| Entity Persistence | medium | 3.2% [0.0%, 9.6%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Negation Invariance | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Object Permanence | high | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Quantity Conservation | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 5.6% [0.8%, 12.0%] | 16.0% [6.4%, 34.7%] | 92.0% – 96.0% | 0 | 125 |

## gpt-4o-mini

- Model id (as invoked): `gpt-4o-mini-2024-07-18`
- Run: `gpt-4o-mini-20260715T023831411Z` started 2026-07-15T02:38:31.411384+00:00
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- Tokens: 86,049 in / 1,207 out - estimated cost $0.01
- **Overall violation rate: 3.6%** (27/750 answered probes; pessimistic bound counting nonconformance as failure: 3.6%)
- **Overall contradiction rate: 6.0%** (9/150 checkable paraphrase clusters; 0 of 150 clusters untestable)
- Link constraints broken: 1/31
- Open debt (weighted): **106**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 5.6% [1.6%, 9.6%] | 24.0% [11.5%, 43.4%] | 84.0% – 100.0% | 0 | 125 |
| Entity Persistence | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Negation Invariance | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Object Permanence | high | 4.0% [0.0%, 12.0%] | 0.0% [0.0%, 13.3%] | 96.0% – 96.0% | 0 | 125 |
| Quantity Conservation | medium | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 11.2% [0.8%, 23.2%] | 8.0% [2.2%, 25.0%] | 88.0% – 92.0% | 0 | 125 |

## gpt-5-mini

- Model id (as invoked): `gpt-5-mini-2025-08-07`
- Run: `gpt-5-mini-20260715T023032501Z` started 2026-07-15T02:30:32.501233+00:00
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- Tokens: 85,299 in / 34,252 out - estimated cost $0.09
- **Overall violation rate: 0.5%** (4/750 answered probes; pessimistic bound counting nonconformance as failure: 0.5%)
- **Overall contradiction rate: 2.7%** (4/150 checkable paraphrase clusters; 0 of 150 clusters untestable)
- Link constraints broken: 0/31
- Open debt (weighted): **36**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 1.6% [0.0%, 4.0%] | 8.0% [2.2%, 25.0%] | 96.0% – 100.0% | 0 | 125 |
| Entity Persistence | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Negation Invariance | medium | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Object Permanence | high | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Quantity Conservation | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |

## gpt-5-nano

- Model id (as invoked): `gpt-5-nano-2025-08-07`
- Run: `gpt-5-nano-20260715T023353849Z` started 2026-07-15T02:33:53.849162+00:00
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- Tokens: 85,299 in / 57,998 out - estimated cost $0.03
- **Overall violation rate: 1.2%** (9/750 answered probes; pessimistic bound counting nonconformance as failure: 1.2%)
- **Overall contradiction rate: 5.3%** (8/150 checkable paraphrase clusters; 0 of 150 clusters untestable)
- Link constraints broken: 0/31
- Open debt (weighted): **64**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Entity Persistence | medium | 2.4% [0.0%, 4.8%] | 12.0% [4.2%, 30.0%] | 96.0% – 100.0% | 0 | 125 |
| Negation Invariance | medium | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Object Permanence | high | 3.2% [0.0%, 7.2%] | 12.0% [4.2%, 30.0%] | 96.0% – 100.0% | 0 | 125 |
| Quantity Conservation | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |

## gpt-5.4

- Model id (as invoked): `gpt-5.4-2026-03-05`
- Run: `gpt-5.4-20260715T022839253Z` started 2026-07-15T02:28:39.253881+00:00
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- Tokens: 85,299 in / 10,455 out - estimated cost $0.21
- **Overall violation rate: 0.3%** (2/750 answered probes; pessimistic bound counting nonconformance as failure: 0.3%)
- **Overall contradiction rate: 1.3%** (2/150 checkable paraphrase clusters; 0 of 150 clusters untestable)
- Link constraints broken: 0/31
- Open debt (weighted): **20**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Entity Persistence | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Negation Invariance | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Object Permanence | high | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Quantity Conservation | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |

## gpt-frontier

- Model id (as invoked): `gpt-5.5-2026-04-23`
- Run: `gpt-frontier-20260715T013500952Z` started 2026-07-15T01:35:00.952134+00:00
- Probes: 750 (645 answered, 0 nonconformant, 105 errors)
- Tokens: 73,233 in / 10,824 out - estimated cost $0.20
- **Overall violation rate: 0.0%** (0/645 answered probes; pessimistic bound counting nonconformance as failure: 0.0%)
- **Overall contradiction rate: 0.0%** (0/141 checkable paraphrase clusters; 9 of 150 clusters untestable)
- Link constraints broken: 0/28
- Open debt (weighted): **0**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 19.4%] | 100.0% – 100.0% | 0 | 64 |
| Entity Persistence | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 96 |
| Negation Invariance | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 110 |
| Object Permanence | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Quantity Conservation | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |

## gpt-mini

- Model id (as invoked): `gpt-5.4-mini-2026-03-17`
- Run: `gpt-mini-20260715T020937924Z` started 2026-07-15T02:09:37.924826+00:00
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- Tokens: 85,299 in / 15,436 out - estimated cost $0.05
- **Overall violation rate: 0.3%** (2/750 answered probes; pessimistic bound counting nonconformance as failure: 0.3%)
- **Overall contradiction rate: 1.3%** (2/150 checkable paraphrase clusters; 0 of 150 clusters untestable)
- Link constraints broken: 0/31
- Open debt (weighted): **16**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Entity Persistence | medium | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Negation Invariance | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Object Permanence | high | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Quantity Conservation | medium | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 13.3%] | 100.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |

## gpt-nano

- Model id (as invoked): `gpt-5.4-nano-2026-03-17`
- Run: `gpt-nano-20260715T021044571Z` started 2026-07-15T02:10:44.571442+00:00
- Probes: 750 (750 answered, 0 nonconformant, 0 errors)
- Tokens: 85,299 in / 12,703 out - estimated cost $0.01
- **Overall violation rate: 3.7%** (28/750 answered probes; pessimistic bound counting nonconformance as failure: 3.7%)
- **Overall contradiction rate: 12.7%** (19/150 checkable paraphrase clusters; 0 of 150 clusters untestable)
- Link constraints broken: 1/31
- Open debt (weighted): **183**

| Commitment | Sev | Violation rate (95% CI) | Contradiction rate (95% CI) | Accuracy range across paraphrases | Nonconf. | n answered |
|---|---|---|---|---|---|---|
| Causal Ordering | high | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Entity Persistence | medium | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Negation Invariance | medium | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Object Permanence | high | 4.8% [0.8%, 9.6%] | 16.0% [6.4%, 34.7%] | 88.0% – 100.0% | 0 | 125 |
| Quantity Conservation | medium | 0.8% [0.0%, 2.4%] | 4.0% [0.7%, 19.5%] | 96.0% – 100.0% | 0 | 125 |
| Temporal Consistency | high | 14.4% [8.0%, 21.6%] | 44.0% [26.7%, 62.9%] | 80.0% – 88.0% | 0 | 125 |

## Open debt ledger

| Model | Commitment | Scenario | Kind | Severity | First seen | Last seen |
|---|---|---|---|---|---|---|
| gpt-nano | causal_ordering | co-002 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-mini | causal_ordering | co-002 | contradiction | high | gpt-5-mini-20260715T023032501Z | gpt-5-mini-20260715T023032501Z |
| gpt-4.1-mini | causal_ordering | co-002 | contradiction | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4o-mini | causal_ordering | co-002 | contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-nano | causal_ordering | co-002 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-mini | causal_ordering | co-002 | violation | high | gpt-5-mini-20260715T023032501Z | gpt-5-mini-20260715T023032501Z |
| gpt-4.1-mini | causal_ordering | co-002 | violation | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4o-mini | causal_ordering | co-002 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-5-mini | causal_ordering | co-003 | contradiction | high | gpt-5-mini-20260715T023032501Z | gpt-5-mini-20260715T023032501Z |
| gpt-5-nano | causal_ordering | co-003 | contradiction | high | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-4o-mini | causal_ordering | co-003 | contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-5-mini | causal_ordering | co-003 | violation | high | gpt-5-mini-20260715T023032501Z | gpt-5-mini-20260715T023032501Z |
| gpt-5-nano | causal_ordering | co-003 | violation | high | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-4o-mini | causal_ordering | co-003 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | causal_ordering | co-005 | contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | causal_ordering | co-005 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4.1-mini | causal_ordering | co-006 | contradiction | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4.1-mini | causal_ordering | co-006 | violation | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4o-mini | causal_ordering | co-010 | contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | causal_ordering | co-010 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | causal_ordering | co-014 | contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | causal_ordering | co-014 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | causal_ordering | co-024 | contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | causal_ordering | co-024 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-nano | object_permanence | op-008 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-nano | object_permanence | op-008 | contradiction | high | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-nano | object_permanence | op-008 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-nano | object_permanence | op-008 | violation | high | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-nano | object_permanence | op-012 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5.4 | object_permanence | op-012 | contradiction | high | gpt-5.4-20260715T022839253Z | gpt-5.4-20260715T022839253Z |
| gpt-5-mini | object_permanence | op-012 | contradiction | high | gpt-5-mini-20260715T023032501Z | gpt-5-mini-20260715T023032501Z |
| gpt-4.1-mini | object_permanence | op-012 | contradiction | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-nano | object_permanence | op-012 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5.4 | object_permanence | op-012 | violation | high | gpt-5.4-20260715T022839253Z | gpt-5.4-20260715T022839253Z |
| gpt-5-mini | object_permanence | op-012 | violation | high | gpt-5-mini-20260715T023032501Z | gpt-5-mini-20260715T023032501Z |
| gpt-4.1-mini | object_permanence | op-012 | violation | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4o-mini | object_permanence | op-012 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | object_permanence | op-012~op-013 | link_contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-nano | object_permanence | op-013 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | object_permanence | op-013 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-nano | object_permanence | op-016 | contradiction | high | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-5-nano | object_permanence | op-016 | violation | high | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-nano | object_permanence | op-019 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-nano | object_permanence | op-019 | contradiction | high | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-nano | object_permanence | op-019 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-nano | object_permanence | op-019 | violation | high | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-nano | temporal_consistency | tc-006 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-4o-mini | temporal_consistency | tc-006 | contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-nano | temporal_consistency | tc-006 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-4o-mini | temporal_consistency | tc-006 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
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
| gpt-5.4 | temporal_consistency | tc-015 | contradiction | high | gpt-5.4-20260715T022839253Z | gpt-5.4-20260715T022839253Z |
| gpt-4.1-mini | temporal_consistency | tc-015 | contradiction | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4o-mini | temporal_consistency | tc-015 | contradiction | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-nano | temporal_consistency | tc-015 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5.4 | temporal_consistency | tc-015 | violation | high | gpt-5.4-20260715T022839253Z | gpt-5.4-20260715T022839253Z |
| gpt-4.1-mini | temporal_consistency | tc-015 | violation | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4o-mini | temporal_consistency | tc-015 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-nano | temporal_consistency | tc-018 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-018 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-4.1-mini | temporal_consistency | tc-019 | contradiction | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4.1-mini | temporal_consistency | tc-019 | violation | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-nano | temporal_consistency | tc-021 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-4.1-mini | temporal_consistency | tc-021 | contradiction | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-nano | temporal_consistency | tc-021 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-4.1-mini | temporal_consistency | tc-021 | violation | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-nano | temporal_consistency | tc-022 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-4.1-mini | temporal_consistency | tc-022 | contradiction | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-nano | temporal_consistency | tc-022 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-4.1-mini | temporal_consistency | tc-022 | violation | high | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4o-mini | temporal_consistency | tc-022 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-nano | temporal_consistency | tc-023 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | temporal_consistency | tc-023 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-4o-mini | temporal_consistency | tc-023 | violation | high | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-mini | temporal_consistency | tc-024 | contradiction | high | gpt-mini-20260715T020937924Z | gpt-mini-20260715T020937924Z |
| gpt-nano | temporal_consistency | tc-024 | contradiction | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-mini | temporal_consistency | tc-024 | violation | high | gpt-mini-20260715T020937924Z | gpt-mini-20260715T020937924Z |
| gpt-nano | temporal_consistency | tc-024 | violation | high | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | entity_persistence | ep-008 | contradiction | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | entity_persistence | ep-008 | violation | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-nano | entity_persistence | ep-018 | contradiction | medium | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-5-nano | entity_persistence | ep-018 | violation | medium | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-5-nano | entity_persistence | ep-021 | contradiction | medium | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-5-nano | entity_persistence | ep-021 | violation | medium | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-mini | entity_persistence | ep-022 | contradiction | medium | gpt-mini-20260715T020937924Z | gpt-mini-20260715T020937924Z |
| gpt-5-nano | entity_persistence | ep-022 | contradiction | medium | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-mini | entity_persistence | ep-022 | violation | medium | gpt-mini-20260715T020937924Z | gpt-mini-20260715T020937924Z |
| gpt-5-nano | entity_persistence | ep-022 | violation | medium | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-4.1-mini | entity_persistence | ep-024 | contradiction | medium | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-4.1-mini | entity_persistence | ep-024 | violation | medium | gpt-4.1-mini-20260715T023714751Z | gpt-4.1-mini-20260715T023714751Z |
| gpt-nano | negation_invariance | ni-001 | contradiction | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | negation_invariance | ni-001 | violation | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-5-mini | negation_invariance | ni-002 | contradiction | medium | gpt-5-mini-20260715T023032501Z | gpt-5-mini-20260715T023032501Z |
| gpt-5-nano | negation_invariance | ni-002 | contradiction | medium | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-5-mini | negation_invariance | ni-002 | violation | medium | gpt-5-mini-20260715T023032501Z | gpt-5-mini-20260715T023032501Z |
| gpt-5-nano | negation_invariance | ni-002 | violation | medium | gpt-5-nano-20260715T023353849Z | gpt-5-nano-20260715T023353849Z |
| gpt-4o-mini | quantity_conservation | qc-006 | contradiction | medium | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-4o-mini | quantity_conservation | qc-006 | violation | medium | gpt-4o-mini-20260715T023831411Z | gpt-4o-mini-20260715T023831411Z |
| gpt-nano | quantity_conservation | qc-024 | contradiction | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |
| gpt-nano | quantity_conservation | qc-024 | violation | medium | gpt-nano-20260715T021044571Z | gpt-nano-20260715T021044571Z |

---
*Methodology: constrained-format probes, deterministic verdicts (no LLM judge). Violations (wrong vs. declared commitment) and contradictions (model disagreeing with itself across paraphrases or linked scenarios) are counted separately. **Violation-rate CIs are scenario-cluster bootstraps** (2000 resamples, seed 0): paraphrases within a scenario are dependent, so a probe-level Wilson interval would be optimistically narrow. Contradiction-rate CIs are Wilson intervals at the scenario level (the cluster unit). Violation rates condition on answered probes and are read alongside the pessimistic bound (nonconformance counted as failure) and the nonconformant count - three-way answered-correct / answered-wrong / nonconformant, not one privileged rate. Contradiction rates condition on checkable clusters (>= 2 answered variants). Link checks use the strict majority answer of each cluster; ties and under-answered clusters are excluded as indeterminate, and symmetric link declarations are deduplicated. The weighted debt total is an ordinal prioritization heuristic, not an interval-scale measurement. Full transcripts are recorded alongside this report.*

