# Maintainer decisions ledger

The loop records everything it does: issues, commits, transcripts, payloads.
This file records the one thing it cannot: why the human gate decided.
Every accept, decline, or defer on a loop-surfaced artifact gets one dated
row and one line of reason, appended at check-in time. The same line goes
as a closing comment on the artifact itself. No reconstruction from memory;
that is the failure mode this whole repository exists to prevent.

| Date | Artifact | Decision | Reason |
|---|---|---|---|
| 2026-07-29 | Issue #2: gradient-frontier saturation | Accepted: build tier-3 | Five-model strategy review consolidated; de-saturation gates the cross-lab study. Execution delegated to the maintainer agent under blanket approval; kill-gate: tier-3 must produce measurable spread at the frontier or the study stops. |
| 2026-10-14 | Prior-art candidate `openalex:W7219783798`: i-score toolkit (structural-density), https://doi.org/10.5281/zenodo.23143162 (surfaced in a manual check-in; no GitHub issue exists) | Seen; related-work table unchanged | Noted, no related-work change for now. |
