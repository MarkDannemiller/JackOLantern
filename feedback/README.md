# feedback/

`stack.jsonl` is this project's record of what the **Protoboard stack** got wrong, made hard or
lacked while the project was built on it (dogfooding). One JSON object per line, validated
against the hub's `schemas/stack-feedback.schema.json`, written by
`node tools/projects.mjs feedback add` (from the hub) and the `stack-dogfooding` skill. Screenshots
and other evidence go in `evidence/`, named after the entry id.

Project agents only append. A maintainer's triage (`stack-feedback-triage`) files the entries to
Linear, with client detail removed, and writes the issue ids back. The file merges with git's
union driver; never reorder lines by hand.
