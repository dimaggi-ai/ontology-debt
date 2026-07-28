# Maintainer loop: pre-ship review findings

The maintainer loop was adversarially reviewed before its first run
(2026-07-26): three independent passes (correctness; security and CI-safety;
guardrail conformance), with every raised finding then re-verified against
the code by an independent pass whose default was to refute it. 19 findings
survived verification; several described the same defect from different
lenses, consolidating into 12 fixes. All were fixed before launch, in the
same commit that shipped the loop. The first live run then surfaced one
more (#20). 78 tests green after fixes.

This log exists so the claim "it was reviewed" is checkable rather than
taken on faith - the same standard the audit tool applies to models.

| # | Sev | Where | Finding | Fix |
|---|---|---|---|---|
| 1 | major | automerge workflow | Byte-identical recompute gate unsatisfiable: reports embed a wall-clock `Generated:` line, so Phase 4 could never fire | Timestamp-insensitive comparison (`reports_equivalent`) |
| 2 | major | detect workflow | Registry bookkeeping pushed *before* the digest issue, so any issue-creation failure permanently buries the trigger | Surface first, record last: failures now re-fire as recoverable duplicates |
| 3 | major | saturation.py | A partial run (`--limit` smoke test) counted as a clean model holding the tier | Require complete scenario/probe coverage |
| 4 | major | propose.py | LLM-supplied pack `id` used verbatim as the output filename | `id` forced to the CLI-validated value |
| 5 | major | detect.py | "Loudly unmonitored" only surfaced inside issues opened by *other* events; a deleted secret degraded coverage silently | Monitoring map persisted; monitored-to-unmonitored fires its own alert |
| 6 | minor | prior_art.py | Search-backend failures failed open into a quiet `verified=0` | Per-searcher health; a fully blind watch exits red |
| 7 | minor | tests | Own-repo exclusion test stubbed the very filter it claimed to test | Test now exercises `search_github` via patched HTTP |
| 8 | major | detect.py + workflow | New models marked known before the spend-gated audit ran; a declined approval lost the audit with no re-fire path | `audit_specs` manual re-dispatch input; corrected recovery text in the issue |
| 9 | major | propose.py | Same path-escape as #4 seen through the security lens (`../` writes under a `contents:write` token) | Charset gate + out-dir containment check |
| 10 | minor | saturation.py | A probe-dodging run (heavy nonconformance) could count clean with zero violations | Minimum answered fraction |
| 11 | minor | prior_art.py | Markdown/HTML-comment injection via third-party titles and quotes into issue bodies | `_clean_md` sanitizer + https-only links |
| 12 | critical | detect/prior-art workflows | `gh issue create` used labels nothing had created; combined with #2, the guaranteed first failure consumed the trigger forever | Labels pre-created in setup; ordering inverted |
| 13 | major | automerge + docs | Same as #1 via the conformance lens: docs claimed a gate that could never pass | Comparison fixed; docs wording corrected |
| 14 | major | workflows | Spend gate failed open: referencing a nonexistent environment auto-creates it *unprotected* | `MAINTAINER_SPEND_CONFIRMED` variable, set only after the reviewer rule exists |
| 15 | major | detect.py | HF feeds are sliding top-50 windows (6 of 8 watched orgs at the cap), so age-outs fired false deprecations | Windowed providers never fire deprecation |
| 16 | major | detect.py | Same silent-coverage-loss as #5 via the conformance lens | Covered by the monitoring-map fix |
| 17 | minor | detect.py | Digest issue's recovery instruction was wrong (a manual re-run could not re-trigger a recorded model) | Corrected text; see #8 |
| 18 | minor | audit_pr_body.py | The `RUN UNRELIABLE` report banner was silently dropped from PR bodies | Blockquote lines retained |
| 19 | minor | propose.py | Same filename trust as #4/#9 via a third lens | Same fix |
| 20 | (live) | detect workflow | First live run: `git add maintainer/payloads/` is fatal when a registry-only update writes no payloads | One guard (`e2acda9`); harmless thanks to #2's ordering |

Fixed in the shipping commit (`ac253d8`) and `e2acda9`; regression coverage
in `tests/test_maintainer_*.py`.
