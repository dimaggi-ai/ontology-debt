# Ontology Debt: the ledger your LLM evals are missing

*Draft — companion essay to [ontodebt](../README.md). ~1,300 words.*

---

Your product logic assumes a world-model. Somewhere in your system there is a set of things that must be true for the code around the LLM to make sense: an occluded object still exists, a cause precedes its effect, a question and its negation cannot both be "yes," a quantity doesn't change because you rephrased the sentence describing it. Nobody wrote these down, because nobody writes down the obvious.

The model you call over an API also has a world-model. It is implicit, statistical, and — this is the uncomfortable part — *not the same one*. Frontier models in 2026 still fail atomic world-model probes, still drift across paraphrases of the same question, still answer a question and its negation the same way often enough to matter. The research literature keeps re-measuring this. The tooling ecosystem keeps not addressing it.

## The gap between validation and behavior

If you work near knowledge graphs, you already own validation tooling — SHACL shapes, OWL reasoners, competency questions, `ROBOT report` running on every pull request. All of it points at one target: the *data*. The ontology is the system under test. Twenty years of semantic-web engineering built a continuous-validation culture, and none of it turns around to face the component that now generates half the answers in the building.

If you work near LLM evals, you own the other half: assertion frameworks that check single outputs, benchmark suites that produce a score per model per week, regression gates in CI. What none of them have is *ontology typing* — a way to say "this failure is a violation of object permanence, severity high" rather than "test 41 failed" — and none of them check answers against *each other*. An eval that scores each output independently cannot see the most characteristic LLM failure there is: the model disagreeing with itself.

One practitioner essay in late 2025 proposed exactly the missing piece — ontology-grounded evals for LLMs (Ojitha, *Ontology Evals for LLMs*, Oct 2025) — and then conceded that "practical pipelines for converting ontologies into eval scripts are nascent." An arXiv preprint that tried to close a related loop with a reasoner-checked correction cycle (arXiv:2504.07640) was withdrawn by its authors. The gap is not hypothetical; people keep walking up to it and then not shipping the tool.

## Scores evaporate. Debt accrues.

The deeper problem is not the missing check. It is what happens to a failure after you find it.

An eval score is a snapshot: 91% this week. Next week the provider ships a new snapshot, the score moves to 93%, and the specific failure that mattered to you — the model saying a covered ball ceased to exist, in exactly the kind of scenario your insurance-claims flow depends on — vanishes into the average. Scores are stateless. Failures are not.

Software engineering solved this framing problem decades ago with *technical debt*: a failure you know about and haven't fixed is not a data point, it is a liability on the books, and it stays on the books until someone pays it down. The same accounting works for world-models:

> **Ontology debt** — the accumulated, unresolved gap between the world-model a system is supposed to hold and the one it demonstrably operates with: the weighted sum of open, declared-commitment violations and self-contradictions.

The framing has cousins that deserve their names kept distinct: Jorge Arango's *ontological debt* (2024) describes product vocabularies drifting from reality; *epistemic debt* (Ionescu et al., 2019; revived in 2026 for AI-assisted coding) describes humans not understanding the systems they operate. Ontology debt, as used here, is narrower and mechanical: it is what a ledger says after an audit.

## What we built

[`ontodebt`](https://github.com/dimaggi-ai/ontology-debt) is a small Python library and CLI that implements the accounting:

1. **You declare commitments** — typed, severity-weighted assertions in YAML, each with scenarios, a canonical question, four paraphrases, and a machine-checkable expected answer.
2. **The harness probes a model** — any chat API — and produces two strictly separated failure counts: **violations** (the model contradicts your commitment) and **contradictions** (the model contradicts itself, across paraphrases of one scenario or across scenarios you declared logically linked).
3. **Failures accrue into a ledger** that persists across runs. A later passing run pays an item down — but only when it produced enough evidence to certify absence; a regression re-opens it, preserving first-seen, last-paid, and reopen history. `ontodebt ledger` shows the open book, weighted by the severity you assigned.

Two design choices do most of the work. First, *there is no LLM judge anywhere in the loop*. Every probe uses a constrained answer format, so every verdict is a deterministic string comparison — reproducible from the recorded transcript by anyone, with no judge-validation study required. That trades away open-text coverage, deliberately: an LLM judge that ships without a published human-agreement number is a false-positive factory, and an audit tool whose auditor hallucinates is a joke that writes itself.

Second, *violations and contradictions never share a column*. A model can be consistently wrong — a genuine world-model gap — or inconsistently right — a robustness gap. They have different fixes (retrain or re-prompt vs. constrain or ensemble), and averaging them into one score hides both.

## What we're not claiming

Every individual mechanism here has prior art, and pretending otherwise would be the fastest way to discredit the useful part. Probing a model's beliefs against declared constraints is the BeliefBank lineage (2021), which went on to *repair* inconsistencies with a MaxSAT solver; we deliberately audit instead of repair. Declared behavioral tests with generated perturbations is CheckList (2020), built for pre-LLM classifiers. Paraphrase-consistency measurement is ParaRel and its descendants. Self-contradiction detection is ChatProtect. The six commitment packs that ship with the tool borrow their category vocabulary — object permanence, causal ordering, temporal consistency — from core-knowledge benchmarks like EWOK and CoreCognition, with citations in every file.

What had not shipped, as far as several days of adversarial literature search could establish, is the composition: *user-declared* typed commitments, probed against *arbitrary current APIs*, with violations *and* cross-answer contradictions detected, feeding a *persistent debt ledger*. If we missed prior art, the repo's issue tracker is open and the related-work table will be corrected — that, too, is the ledger working as intended.

## What the first audit found

*(This section is populated from `results/report.md` after each maintainers' run — pinned model snapshots, full transcripts committed. Numbers below are from the run of {DATE}.)*

- {headline violation rate, per model}
- {headline contradiction rate — the more interesting number}
- {the single most instructive open debt item, quoted verbatim}

## Write packs for your own floor

The shipped packs are worked examples — deliberately basic physics and time, the *floor* of any world-model. The tool becomes useful the day you encode your own floor: the invariants of your claims process, your compliance rules, your domain glossary. Fifty scenarios is an afternoon. The ledger does the remembering after that.

A high pass rate is not safety, and passing 750 probes means only that the floor held. But a floor you can audit, with debts you can name, beats a vibe — and right now, most LLM deployments are running on vibes all the way down.

---

*Code, packs, transcripts, and the ledger: [github.com/dimaggi-ai/ontology-debt](https://github.com/dimaggi-ai/ontology-debt). Disputes about gold labels are welcome — they are the point.*
