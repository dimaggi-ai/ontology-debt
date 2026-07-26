"""The maintainer loop: agent-assisted, human-gated upkeep of this project.

Design rule, inherited from the scorer itself: **the agent proposes,
deterministic code decides, a human merges.** Every consequential yes/no in
this package - is there a new model, was the pull authenticated, does this
paper exist, does this quote appear in the fetched source, is the hard tier
saturated, is this diff mechanical - is a string/set operation in committed
code. LLMs appear in exactly one module (`propose`), fenced to *drafting*
candidate scenarios that deterministic validation and a human review gate.

Modules
-------
detect       L1 trigger: diff provider model-list APIs against a committed
             registry; fail-closed on auth errors and empty pulls.
add_model    Deterministic models.yaml entry generation for new models.
audit_pr_body  Deterministic PR-body rendering from a generated report.
prior_art    L2 trigger: arXiv/OpenAlex/GitHub watch with a fetch-then-quote
             verifier; a citation that cannot be re-fetched cannot surface.
saturation   L3 trigger: pure ledger arithmetic over committed runs.
propose      L3 action: LLM proposer + independent LLM adversary, output
             validated by the package's own loaders; never auto-merges.
mechanical   Phase-4 guard: is a diff a pure report regeneration?

See docs/maintainer-loop.md for the full design and its guardrails.
"""
