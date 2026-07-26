# The maintainer loop

This repository maintains itself - up to a hard human gate. A set of small,
mostly-deterministic jobs watch for new models, new prior art, and saturation
of the hard tier, then *propose* work as issues and pull requests. Nothing
merges itself, nothing publishes itself, and no LLM ever touches scoring.

The organizing rule is inherited from the audit harness (which refuses to use
an LLM judge):

> **The agent proposes, deterministic code decides, a human merges.**

Every consequential yes/no - is there a new model? was the pull
authenticated? does this paper exist? does this quote appear in the fetched
source? is the tier saturated? is this diff mechanical? - is a string or set
operation in committed code (`src/ontodebt/maintainer/`), covered by tests.

## The three loops

### L1 - model watch and audit (`maintainer-detect.yml`, daily)

A deterministic detector pulls the model-list APIs (Anthropic, OpenAI,
Gemini, and public Hugging Face org feeds) and diffs them against a
committed registry (`maintainer/known_models.json`). New relevant ids,
silent metadata bumps, and deprecations each open a digest issue; raw
payloads are committed next to the registry so every trigger is a
reviewable git diff.

Fail-closed by construction:

- a provider with no key is loudly **UNMONITORED**, never silently skipped;
- a provider whose pull errors (bad key, network) turns the run **red** -
  an errored pull is never recorded as an empty model list;
- a monitored provider returning zero models is also an error.

When a new relevant model appears on an auditable provider, a second job -
gated by the `maintainer-spend` environment, i.e. a human clicking approve -
runs the ordinary `ontodebt run` against it and opens a PR containing the
models.yaml entry, the transcripts, and the regenerated report. The PR body
is rendered deterministically from the report. A human reviews and merges.

### L2 - prior-art watch (`maintainer-prior-art.yml`, weekly)

Searches arXiv, OpenAlex, and GitHub for recent work overlapping this
project's novelty claim, scores candidates with a committed keyword table,
and applies the **fetch-then-quote verifier**: a candidate only surfaces if
its id re-fetches from the source API *and* the stored verbatim quote
appears in the re-fetched text. A fabricated citation cannot produce a real
fetched quote - that failure mode is structurally closed, and
`tests/test_maintainer_prior_art.py::test_fabricated_citation_is_rejected`
keeps it closed.

Output is an issue. The related-work table is edited only by a human.

### L3 - saturation and pack proposal (`maintainer-saturation.yml` weekly;
`maintainer-pack-proposal.yml` manual)

Saturation is pure arithmetic over committed runs: when at least two models
hold the hard tier completely clean (zero violations, contradictions, and
link breaks, on valid runs - a >50%-errored run can never count as clean),
an issue proposes authoring a harder tier.

Authoring itself is the only place an LLM appears, and it is fenced:

1. a proposer call drafts a full pack in YAML;
2. every scenario is validated by the same loaders that gate hand-written
   packs - invalid scenarios are dropped, not repaired;
3. an independent adversary call per scenario hunts for a second defensible
   answer; anything not explicitly `UNDISPUTED` is dropped (fail-closed);
4. the surviving pack must still pass `ontodebt validate`, and the PR is
   labeled `never-automerge`.

A draft becomes a scoring pack only when a human promotes it out of
`commitments-frontier-draft/`.

## Phase 4 - narrow auto-merge (shipped disabled)

`maintainer-automerge.yml` can merge exactly one artifact class: a
`report.md` regeneration that `ontodebt report` reproduces identically from
committed run files (identical modulo the `Generated:` wall-clock line and
trailing newlines - see `reports_equivalent`), touching nothing else. It
does nothing until a human sets the repo variable
`AUTOMERGE_MECHANICAL=true`, and it additionally needs the repository's
"Allow auto-merge" setting enabled. Audits, transcripts, ledgers,
citations, packs, and code never auto-merge.

## Configuration

**Setup order matters.** Create the `maintainer-spend` environment *with a
required reviewer* before anything else: referencing a nonexistent
environment makes GitHub auto-create it with no protection rules, which
would silently un-gate spend. The workflows therefore also require the repo
variable `MAINTAINER_SPEND_CONFIRMED=true`, which the human sets only after
configuring the reviewer - a belt-and-braces guard against exactly that.

| What | Where | Notes |
|---|---|---|
| Kill switch | repo variable `MAINTAINER_LOOP_ENABLED` | set to `false` to stop every loop job |
| Spend gate | environment `maintainer-spend` | required reviewer = the maintainer; API keys live here |
| Spend-gate confirmation | repo variable `MAINTAINER_SPEND_CONFIRMED` | set to `true` only after the environment has its required reviewer |
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` | environment/repo secrets | absent keys degrade to UNMONITORED, they never fake cleanliness |
| `MAINTAINER_APP_ID`, `MAINTAINER_APP_PRIVATE_KEY` | repo secrets (optional) | a GitHub App token lets CI run on loop-opened PRs; without it PRs still open via `GITHUB_TOKEN` |
| `OPENALEX_MAILTO` | repo variable (optional) | joins OpenAlex's polite pool |
| Relevance gates, keyword weights, thresholds | `maintainer/config.json` | committed, reviewable, deterministic |
| Auto-merge opt-in | repo variable `AUTOMERGE_MECHANICAL` | unset/false = disabled |

## What is deliberately not automated

- **Merging to `main` and releases.** A GitHub Release publishes to PyPI via
  trusted publishing; both stay human.
- **The final related-work sentence.** The watcher surfaces verified
  candidates; the human writes the claim.
- **Gold-label admission.** Draft packs never auto-merge, however many
  filters they passed. Ambiguity is subtle; credibility is expensive.

## Why this shape

This project was burned twice while being built: an LLM-hallucinated
citation nearly landed in the related-work table, and a revoked API key once
produced a run that looked clean because nothing was actually asked. Both
burns are now permanent regression tests
(`test_fabricated_citation_is_rejected`,
`test_dead_key_cannot_report_clean`), and the loop is designed so that those
two classes of error are structurally unable to reach `main` - not because
an agent is careful, but because the checks are not the agent's to skip.
