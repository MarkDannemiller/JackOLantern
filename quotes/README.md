# Quotes

One folder per quote: `q-<number>/` (for example `q-2026-acme-01/`) holding
`quote.json` (the source), `working.md` (INTERNAL: pricing notes, hours, the
budget anchor) and the rendered client PDF. The hub's `quote` skill and
`tools/quote` build, validate and render them: from the hub root,
`npm run quote -- validate projects/<group>/<project>/quotes/q-<number>/quote.json`.

An issued quote is never edited in place. A re-issue of the same scope bumps
`revision`; new scope or new terms get a new number, and the old one is marked
superseded below. Keep `active_quote` in `project.md` pointing at the one in
force.

| Quote | Title | Issued | Total | Status |
|---|---|---|---|---|
| | | | | |

<!-- Status: draft | sent | accepted | declined | superseded (by which). -->
