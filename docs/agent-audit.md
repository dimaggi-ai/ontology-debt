# Agent-transcript auditing (v0.2) — design note

`ontodebt audit-agent` is the measure leg for agents: it audits **recorded**
agent transcripts against **declared behavioral commitments**, offline and
deterministically, and accrues failures into the same severity-weighted debt
ledger the chat harness uses. This note explains where it sits relative to
prior work, and specifies the transcript and rule formats precisely enough to
reimplement the verdicts.

## Positioning — why this is whitespace

Research on agent commitment/consistency has moved fast in 2026
(NeuroState-Bench, BeliefShift, ReliabilityBench, Apr–Jun 2026): those papers
establish that agents drift on their own stated beliefs and task state, and
they ship *benchmarks* — fixed datasets scoring models against the authors'
scenarios. None of them ship a tool that audits *your* agent's transcripts
against *your* commitments, with memory between audits. That composition —
user-declared behavioral invariants + offline transcript replay + a
persistent debt ledger — is the same gap `ontodebt` fills for chat models,
one level up the stack.

The closest shipped system is Anthropic's **Petri** (2025), and the contrast
is the point:

| | Petri | `ontodebt audit-agent` |
|---|---|---|
| Goal | *Elicit* concerning behavior (safety exploration) | *Audit* recorded behavior against declared commitments |
| Driver | LLM auditor agents steer live conversations | Offline replay; no live agent, no keys |
| Verdict | LLM judges score transcripts on safety dimensions | Deterministic regex checks; same input, same verdict, always |
| Scenarios | Seed instructions, open-ended | Rules you declare in YAML, versioned with your repo |
| Output | Scored transcripts for human triage | Verdicts + a debt ledger that persists across audits |

Complementary, not competing: Petri finds behaviors you didn't know to look
for; `ontodebt` holds the line on behaviors you have explicitly committed to.
Per-output assertion frameworks (promptfoo, DeepEval) can assert on a single
agent response, but have no cross-event temporal semantics (promise → later
fulfillment, trigger → no later occurrence, claim → same claim later) and no
memory between runs.

The **no-LLM-judge invariant is preserved**: every verdict below is a regex
match over recorded text. This trades semantic coverage for zero
judge-validation burden and full reproducibility — the same trade v0.1 made
for chat probes, applied to transcripts.

## Transcript format

A transcript is a JSONL file — one JSON object per line, one event per
object, in the order events occurred. Blank lines are ignored. Unknown keys
are ignored (project richer formats down to these fields).

```json
{"turn": 3, "role": "assistant", "content": "I'll run the tests."}
{"turn": 4, "role": "tool", "content": "12 passed in 0.4s", "tool_name": "bash", "tool_args": {"command": "pytest -q"}}
```

| field | required | type | meaning |
|---|---|---|---|
| `turn` | yes | int ≥ 0 | conversational turn; **display metadata only** |
| `role` | yes | `user` \| `assistant` \| `tool` | who produced the event |
| `content` | yes | string (may be empty) | message text or tool output |
| `tool_name` | no | string | tool involved, for tool calls/results |
| `tool_args` | no | object | the tool's arguments |

Two semantics worth stating explicitly:

- **File order is the temporal order.** `turn` never reorders events; it only
  labels evidence in reports.
- **Search text.** Patterns are searched (`re.search`, not `match`) against
  `content` for user/assistant events; events carrying a `tool_name` expose
  `"<tool_name> <canonical-JSON-args> <content>"` (canonical = sorted keys),
  so one regex can match a tool by name, argument, or output.
- **Transcript id = file stem, treated as a stable session name.** Ledger
  items are keyed per (rule, transcript id). Re-recording the same named
  session — e.g. a nightly scripted task — and re-auditing is what pays a
  ledger item down or renews it. A one-off transcript's debt stays open until
  you either re-record it or retire the id: that is the ledger telling you
  the failure was never re-tested.

## Rule format

Rule packs live in `agent_commitments/*.yaml`:

```yaml
id: task_integrity
title: "Task integrity"
statement: >
  What the pack as a whole commits the agent to.
rules:
  - id: ti-001
    title: "Announced test runs happen"
    type: promise_kept
    severity: high            # low | medium | high (weights 1 / 3 / 5)
    rationale: >
      Required. Say why the pattern is a fair proxy - and what it cannot see.
    promise_pattern: '...'
    fulfillment_pattern: '...'
```

Every rule carries `id`, `title`, `type`, `severity`, and a **required
`rationale`** — mirroring the chat schema's spirit that a commitment you
cannot justify is not a commitment. Patterns are Python regexes; add `(?i)`
for case-insensitivity. Load-time validation rejects unknown types, bad
severities, non-compiling patterns, fields that don't belong to the type,
duplicate ids, and `capture_pattern`s without exactly one capture group.

### Rule semantics (v0.2 — exactly three types)

| type | fields | fails when | failure kind | not applicable when |
|---|---|---|---|---|
| `promise_kept` | `promise_pattern`, `fulfillment_pattern` | an **assistant** event matches the promise and **no strictly later** assistant/tool event matches the fulfillment | violation | no promise ever matched |
| `assertion_stability` | `capture_pattern` (1 group) | ≥ 2 values captured from **assistant** events and they are not all identical after whitespace-collapse + casefold | contradiction | fewer than 2 captures |
| `forbidden_after` | `trigger_pattern`, `forbidden_pattern`, optional `trigger_role` | after the **first** trigger match, a strictly later assistant/tool event matches the forbidden pattern | violation | trigger never matched |

Fine print, chosen deliberately:

- *Strictly later.* An event never fulfills its own promise ("I'll run the
  tests with pytest" is a promise, not a fulfillment). One fulfillment event
  satisfies every promise before it; a promise after the last fulfillment is
  broken.
- *Only the agent is on the hook.* Promises and assertions are read from
  assistant events; fulfillments and forbidden occurrences from
  assistant/tool events. User text can *trigger* a `forbidden_after` rule
  (an instruction) but can never fulfill or violate anything.
- *`trigger_role`* (default `any`) scopes who can arm a `forbidden_after`
  rule — so "no edits after the agent declares done" cannot be armed by a
  user asking "done?".
- *Not applicable is a first-class outcome.* Absence of evidence is not
  evidence of compliance: an unexercised rule neither accrues debt nor pays
  it down. `assertion_stability` needs ≥ 2 captures to certify stability —
  the exact analogue of the chat harness's rule that a paraphrase cluster
  with < 2 answered variants is untestable, not consistent.

## Ledger and report integration

Findings are shaped into the same `CommitmentStats` structure the ledger
already reconciles — pack id as the commitment, `"<rule>@<transcript>"` as the
scenario, `--agent-name` as the model column — so accrual, evidence-gated
paydown, re-opening, and payment history are literally the chat code paths,
not a parallel implementation. The one extension made for agents is
`scenario_severities`: chat packs carry one severity per commitment, agent
rules carry their own, and the ledger honors the per-item value.
`ontodebt audit-agent` writes `agent-report.md`, an `agent-run-*.json`
findings record (full evidence trail), and updates `results/ledger.json`.

## Limitations (read before relying on it)

1. **Regex proxies see surface text, not meaning.** A retraction ("I was
   wrong — it's actually in `b.py`") reads as drift; an agent that *claims*
   it applied a fix satisfies a claim-accepting fulfillment pattern; a test
   runner not named in the pattern reads as a broken promise. Each shipped
   rule's rationale states its blind spots; write yours the same way.
2. **Semantic matching is future work, on purpose.** NLI or embedding
   matchers would widen coverage and reintroduce exactly the judge-validation
   burden this tool opted out of. If it ever ships, it will be opt-in and
   labeled as a different evidence class, never silently mixed into
   deterministic verdicts.
3. **Rules fire per transcript.** Cross-transcript invariants ("the agent
   tells every user the same policy") are a natural v0.3; today's stability
   checks are within one session.
4. **A clean audit is not agent safety.** These are floor checks on declared
   commitments — the same caveat as the chat harness, one level up.
