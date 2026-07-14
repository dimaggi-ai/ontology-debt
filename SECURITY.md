# Security

Supported version: 0.1.x.

To report a vulnerability privately, use GitHub's private vulnerability
reporting on this repository (Security → Report a vulnerability) rather than
a public issue.

Notes for users:

- API keys belong in a local `.env` (gitignored) or your environment — never
  in commitment packs, transcripts, or commits.
- Transcripts and reports under `results/` contain every probe prompt and
  model response verbatim. If your packs encode sensitive domain knowledge,
  treat `results/` as sensitive too.
- Commitment packs are data, not code: the loader parses YAML with
  `yaml.safe_load` and compiles user-supplied regex patterns. Untrusted
  packs can still cause pathological regex runtimes — review packs from
  third parties before running them.
