# Joyful Jack build guides, 2026-10-25

One PDF per tier, merged from the Protoboard releases (`protoboard/release/0.2.0-<t>/`, gitignored, rebuilt
with `JJ_TIER=<t> npx protoboard release --version 0.2.0-<t> --allow-dirty` inside `protoboard/`):

| File | Release | Contents |
|---|---|---|
| joyful-jack-tier-a-build-guide.pdf | 0.2.0-a | overview, system guide, body, right arm, left arm |
| joyful-jack-tier-b-build-guide.pdf | 0.2.0-b | same |
| joyful-jack-tier-c-build-guide.pdf | 0.2.0-c | same |

Merged with `pdfunite` from `00-overview.pdf`, `system/assembly-guide.pdf` and `units/{body,arm_r,arm_l}/assembly-guide.pdf`.
Each release also holds a BOM, work order, spec sheet and test plan per unit, which are not merged here.

Status: internal draft for Mark's review; not sent to anyone.

Known layout issues from the stack (logged as friction, not patched here):
- arm figures include one light-grey, already-placed body away from the step's cluster;
- the overview page draws the product image over the description text.

Prices are not in the stack BOMs; see `research/sourcing/20261025-bom-v2.md`.
