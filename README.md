# Ontology Debt

[![ci](https://github.com/dimaggi-ai/ontology-debt/actions/workflows/ci.yml/badge.svg)](https://github.com/dimaggi-ai/ontology-debt/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

**Audit the world-model of a chat LLM (Anthropic- or OpenAI-compatible APIs) against ontological commitments *you* declare — and track the debt.**

> Package name: `ontology-debt` (PyPI release imminent — install from source below for now) · Command: `ontodebt` · A [DIMAGGI AI](https://dimaggi.ai) open-source project.

`ontodebt` is a small Python library + CLI. You declare typed, testable commitments about how the world works (object permanence, causal ordering, temporal consistency, …) as YAML. The harness probes a model with paraphrase families of constrained-format questions, detects two kinds of failure — **violations** (the model contradicts your commitment) and **contradictions** (the model contradicts *itself* across paraphrases or logically linked scenarios) — and accrues every unresolved failure into a persistent, per-model **debt ledger** that is paid down only when a later run passes.

It **audits and accounts**. It does not repair answers (unlike the BeliefBank → REFLEX MaxSAT-repair lineage), it does not ship a fixed benchmark (your commitments are the dataset), and it checks semantic invariants across *sets* of answers rather than asserting on single outputs (unlike per-output assertion frameworks such as promptfoo or DeepEval — into whose CI runs this ledger can feed).

## Why

Teams increasingly have a *declared domain model* — an ontology, a glossary, a set of invariants their product logic assumes — and no tooling-mature way to check a live LLM against it. The SHACL/OWL stack validates RDF data, not model behavior. Extraction benchmarks test reading, not holding. Generic eval harnesses assert on single outputs with no ontology typing, no cross-answer contradiction checking, and no memory between runs. Practitioners have said the quiet part in print — *"practical pipelines for converting ontologies into eval scripts are nascent"* (Ojitha, *Ontology Evals for LLMs*, Oct 2025) — and one 2025 attempt at a reasoner-checked correction loop ([arXiv:2504.07640](https://arxiv.org/abs/2504.07640)) was withdrawn by its authors.

`ontodebt` is a deliberately small answer to that gap, plus one framing borrowed from software engineering: a failed check is not a number in a report, it is **debt** — it stays on the books, weighted by the severity *you* assigned, until the model (or your commitment) changes.

The name says what it measures: **ontology debt** — the accumulated, unresolved gap between the world-model a system is supposed to hold and the one it demonstrably operates with. (Jorge Arango sketched a kindred idea for product terminology as "ontological debt" in 2024; the software-engineering term *epistemic debt* — Ionescu et al. 2019, and a 2026 revival for AI-assisted coding — names related but distinct concepts. See [Terminology](#terminology).)

## Quickstart

```bash
git clone https://github.com/dimaggi-ai/ontology-debt && cd ontology-debt
python3 -m venv .venv && .venv/bin/pip install -e ".[all]"

# Lint the commitment packs
.venv/bin/ontodebt validate

# What will it cost?
.venv/bin/ontodebt estimate --models claude-sonnet-5,gpt-5.1

# Dry run, no API keys, deterministic mock model. The mock's "debt" is
# fabricated by construction - it demonstrates the pipeline (verdicts,
# ledger accrual and pay-down), it does not measure anything.
.venv/bin/ontodebt run --models mock

# Real audit: put keys in .env (never in shell history), then
echo 'ANTHROPIC_API_KEY=sk-ant-...' >> .env
echo 'OPENAI_API_KEY=sk-...' >> .env
.venv/bin/ontodebt run --models claude-sonnet-5,gpt-5.1
```

Outputs land in `results/`: a markdown report with Wilson 95% CIs, a full per-probe transcript (JSONL), the raw run records, and `ledger.json` — the debt ledger.

## What a commitment looks like

```yaml
# illustrative example - ids abbreviated; see commitments/ for the real packs
id: object_permanence
title: "Object permanence"
statement: >
  An object that becomes occluded or unobserved continues to exist
  and retains its properties.
severity: high
scenarios:
  - id: ex-001
    setup: >
      A red ball rolls behind an opaque wooden screen. Nothing touches
      the ball after that.
    question: "Does the red ball still exist? Answer with exactly one word: Yes or No."
    paraphrases:
      - "Is the red ball still in existence? Answer with exactly one word: Yes or No."
      # ... 3 more
    expected: { type: choice, values: ["Yes", "No"], value: "Yes" }
    difficulty: basic
    links:
      # ex-002 asks the complementary question ("Has the ball stopped
      # existing?"), so a consistent model must answer the two differently.
      - { relation: different_answer, target: ex-002 }
```

Six packs ship with the repo (150 scenarios, 750 probes per model): `object_permanence`, `entity_persistence`, `temporal_consistency`, `causal_ordering`, `negation_invariance`, `quantity_conservation`. The first four descend from the probe taxonomy of core-knowledge evaluations (CoreCognition 2024, EWOK 2024); they are *illustrative packs*, not a benchmark claim — the point of the tool is that you write packs for **your** domain.

## Design decisions (and what they buy)

- **No LLM judge anywhere in the loop.** Every probe uses a constrained answer format, so every verdict is a deterministic string comparison. This trades open-text coverage for zero judge-validation burden and full reproducibility of the analysis given a transcript. (LLM judges that ship without a published human-agreement number are a known false-positive factory; we opted out of that problem class for v0.1.)
- **Violations ≠ contradictions.** A model can be consistently wrong (violation, no contradiction) or inconsistently right (contradiction, low violation rate). The report keeps the columns separate because the two failure modes have different fixes.
- **Format nonconformance is its own bucket.** A rambling answer is not evidence about the world-model; it is evidence about instruction-following. Counting it as a violation would inflate the headline number.
- **Ranges, not just means.** Accuracy is reported as a *range across paraphrase positions* — paraphrase sensitivity is a finding, not noise.
- **No sampling-parameter theater.** Current-generation Anthropic models reject `temperature`; several OpenAI reasoning models do too. We pass none and report run-to-run stability empirically instead of pretending `temperature=0` buys determinism.
- **Debt semantics.** `ledger.json` persists across runs. A violation, paraphrase contradiction, or broken link constraint accrues an item, weighted by commitment severity (high = 5, medium = 3, low = 1); a later passing run pays it down — but only when the run produced enough evidence (a contradiction item needs a re-testable cluster, not a single lucky answer); a regression re-opens it, preserving first-seen, last-paid, and reopen counts. `ontodebt ledger` shows the open book. A run in which more than half the probes error is treated as invalid and never touches the ledger.

## Agent transcripts (v0.2 preview)

The chat harness audits what a model *says*. `ontodebt audit-agent` audits what an agent *did*: it replays a **recorded transcript** (JSONL: `user`/`assistant`/`tool` events) against **behavioral commitments** you declare — fully offline, no API keys, no live agent, and the same no-LLM-judge rule as everywhere else in this tool.

```bash
.venv/bin/ontodebt audit-agent --transcripts session.jsonl --rules agent_commitments/
```

v0.2 supports exactly three rule types, all regex-based and deterministic:

```yaml
- id: ti-001
  title: "Announced test runs happen"
  type: promise_kept        # also: assertion_stability, forbidden_after
  severity: high
  promise_pattern: '(?i)\b(?:i''ll|i will|let me)\b[^.!?\n]{0,80}\brun\b[^.!?\n]{0,80}\btests?\b'
  fulfillment_pattern: '(?i)\b(?:pytest|npm test|go test|cargo test)\b'
  rationale: >
    An agent that says it will run the tests and never invokes a test
    runner has silently dropped its own verification step.
```

`promise_kept` (a promise with no later fulfillment is a **violation**), `assertion_stability` (a repeated claim that drifts is a **contradiction** — the agent disagreeing with itself), and `forbidden_after` (an event occurring after a declared boundary is a **violation**). Findings feed the *same* debt ledger, with per-rule severity and the same evidence-gated paydown: a rule whose precondition never fired can neither accrue debt nor pay it down.

Honest scope: these are regex proxies over surface text — they detect evidence of behavior, not intent, and the shipped `agent_commitments/task_integrity.yaml` pack says in each rationale what its pattern cannot see. Semantic matching is deliberately future work, because it would reintroduce the judge-validation burden v0.1 opted out of. Format, semantics, and positioning: [docs/agent-audit.md](docs/agent-audit.md).

## Results

> **First maintainers' audit: pending.** When it runs, the report, ledger, and full transcripts will be committed here with the exact model ids invoked. Until then, [`examples/mock-run/`](examples/mock-run/) shows exactly what a report and ledger look like — generated by the deterministic mock model, whose numbers are fabricated by construction. Run `ontodebt run` to audit current snapshots yourself — model behavior drifts, which is rather the point of keeping a ledger.

## Related work — what this is not

Every individual mechanism here has strong prior art. The composition — user-declared typed commitments + declared paraphrase-family probing of current chat APIs + violation *and* contradiction detection + a persistent debt ledger — is, to our knowledge, unshipped as a whole; **the ledger is the one component for which we could locate no precedent at all**. (Paraphrases are hand-authored in the packs, not generated at runtime — unlike CheckList's perturbation generation; runtime generation is a natural v0.2.) Corrections welcome.

| Prior work | What it does | How `ontodebt` differs |
|---|---|---|
| [BeliefBank](https://arxiv.org/abs/2109.14723) (EMNLP 2021), memory-of-beliefs line | Symbolic belief store + weighted constraints; MaxSAT flips inconsistent answers | The conceptual ancestor. It *repairs* consistency on a fixed shipped constraint set for one 2021 model; `ontodebt` *audits and accounts*, on commitments you declare, against current APIs |
| [REFLEX](https://aclanthology.org/2023.emnlp-main.877/) (EMNLP 2023), [ConCoRD](https://arxiv.org/abs/2211.11875) (EMNLP 2022) | Belief-graph / NLI + MaxSAT consistency repair at inference time | Same lineage: repair vs. audit. We deliberately claim no new detection *method* |
| [CheckList](https://github.com/marcotcr/checklist) (ACL 2020) | Declared behavioral tests + perturbation generation for pre-LLM classifiers | Closest OSS ancestor in UX. No constraint semantics *between* answers, no contradiction graph, no persistence. Think "CheckList for the ontology layer of chat LLMs, with an accounting model" |
| [ChatProtect](https://github.com/eth-sri/ChatProtect) (ICLR 2024), SelfCheckGPT | Self-contradiction detection within one generated text / across samples | Ours is cross-answer over commitment-derived probe sets, tied to a ledger |
| [ParaRel](https://github.com/yanaiela/pararel) (TACL 2021), SCORE (2025), BECEL (COLING 2022) | Paraphrase/negation consistency benchmarks (largely fixed datasets, encoder-era) | We adopt their protocols (paraphrase families, range reporting) as *harness mechanics* over user-declared content |
| [AuditLLM](https://huggingface.co/spaces/Amirizaniani/AuditLLM) (LREC-COLING 2024) | Runtime paraphrase-probe generation + cross-answer inconsistency flagging, as a hosted demo | No declared commitments or gold labels, no violation-vs-contradiction split, no persistence; similarity-scored rather than deterministic |
| Metamorphic testing of LLMs — [PromptOps](https://github.com/MUICT-SERU/PromptOps), LLMORPH | Semantic-preserving perturbations + output-invariance checks (robustness framing, similarity-based) | We declare typed commitments with expected answers and logical links, split violations from contradictions, and keep books across runs |
| Agent belief-consistency benchmarks (BeliefShift, NeuroState-Bench, 2026) | Fixed longitudinal benchmarks of belief drift/contradiction in agents | They benchmark agent memory across sessions; we audit declared world-model commitments of the base model and account for failures over time |
| EWOK (2024), CoreCognition (2024), ChronoScope (ACL 2026) | Fixed benchmarks of world-knowledge / core-cognition / temporal consistency | Our default packs borrow their category vocabulary, with citation. They benchmark; this tool lets you declare and track |
| arXiv 2604.14525 (2026) | Extracts "commitments" from answers within one reasoning case; solver-checked contradiction density + repair | Vocabulary collision, different object: theirs are *extracted post-hoc* and repaired immediately; ours are *user-declared ex ante* and ledgered longitudinally |
| [promptfoo](https://github.com/promptfoo/promptfoo), [DeepEval](https://github.com/confident-ai/deepeval) | Per-output assertion DSLs, CI regression tracking | No ontology typing, no cross-answer contradiction checks over probe sets (promptfoo's `select-best` ranks outputs; DeepEval's conversational metrics judge within one dialog), no debt semantics. Complementary: export ledger deltas into their CI gates |
| [Giskard](https://docs.giskard.ai) LLM scan | Generated-pair coherency/sycophancy detection — a real shipped cross-answer check | LLM-judged, fixed detector categories, no user-declared commitments, per-scan rather than ledgered |
| xpSHACL violation KG, ROBOT report / ODK | Continuous validation with violation records — for RDF data / ontologies as the system under test | We invert the target: the *LLM* is the system under audit; the pattern ("ROBOT report where the model is the codebase") is borrowed with thanks |

## Terminology

- **Ontological commitment** is used here in the practical sense — an assertion a system is committed to holding — not in Quine's full philosophical sense, and not in the sense of arXiv 2604.14525's *extracted* reasoning commitments, nor agent task-state "commitment integrity."
- **Ontology debt** (this project): the weighted sum of open ledger items — unresolved violations and contradictions against declared commitments. Distinct from *technical debt* (code), *ontological debt* (Jorge Arango, 2024: product terminology drift), and *epistemic debt* (Ionescu et al. 2019: rework from process ignorance; 2026 usage: human understanding lagging AI-generated code).
- **And no, this is not a formal ontology.** There are no classes, axioms, or reasoner here — commitments are flat typed assertions with pairwise links, and "ontology" is used in the practical sense of a declared world-model. If you prefer the duller, more accurate name, this is *declared-invariant consistency tracking with an accounting model*. We chose the name that says what it costs you.

## Limitations (read before citing)

1. **Text-side only.** Object permanence *et al.* are tested as linguistic competence over described scenes, not perception. Video/embodied benchmarks (TOC-Bench, WM-ABench) test the other half.
2. **Constrained formats trade coverage for determinism.** Open-text failure modes are invisible to v0.1 by design.
3. **Six packs ≠ an ontology.** The shipped packs are worked examples. Real value requires writing packs for your own domain model.
4. **Gold labels are human-spot-checked, not crowd-validated.** Every scenario passed an adversarial review pass for ambiguity; that is weaker than multi-annotator agreement. Dispute a label by opening an issue — that is the ledger working as intended.
5. **Conditioning on answered probes can deflate as well as protect.** Nonconformance is plausibly informative missingness (harder probes provoke hedging), so the headline violation rate conditions on compliance; the report therefore also prints a pessimistic bound counting nonconformance as failure. Read both.
6. **Model ids are as-invoked, not guaranteed immutable.** Pin dated snapshot ids in `models.yaml` where the provider offers them; the report labels the id it actually called.
7. **A high pass rate is not safety.** These are floor checks. Passing all 750 probes means the floor holds, nothing more.

## Development

```bash
.venv/bin/pip install -e ".[dev]"   # adds pytest to the quickstart install
.venv/bin/python -m pytest          # unit tests (mock provider, no network)
.venv/bin/ontodebt run --models mock --limit 3   # 90-probe smoke audit
```

Apache-2.0 license. Issues and pack contributions welcome — especially domain packs (medicine, law, finance) and disputed gold labels.
