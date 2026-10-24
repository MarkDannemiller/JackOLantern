# Worklog

<!--
READ FIRST, WRITE LAST.

This is the one source of "what is true now". A project spans many sessions
across days or weeks, across separate agents and stop/starts. State survives
context loss because it lives in this file, not in any one chat.

  Every session STARTS by reading `## Current State

**Status:** Design drafted for all three tiers (before the brief is signed, on Mark's instruction 2026-10-24 night). Report ready for Mark. Nothing committed, ordered or pushed.

**What is true now:**

- Head modelled in UHD from the received Fusion/STEP (`protoboard/src/head/`, parts in `protoboard/parts/local/`), with its geometry converted to `protoboard/out/cad/head-*.glb` (`cad/tools/step2glb.py`).
- Three tiers as stack systems, chosen by `JJ_TIER=a|b|c` (`protoboard/src/tiers/`, arms `src/arms/arms.uhd.ts`). `protoboard check`: A and B 0 errors 0 warnings; C 0 errors, 2 dispositioned warnings (`docs/decisions.md`).
- Priced BOMs (`research/sourcing/20261024-bom-final.md`): A $498.05 / B $1,174.95 / C $2,139.69, new spend, 2026-10-24 prices.
- Parametric CAD of base, torso, costume, arms and hands per tier (`protoboard/cad/joyful_jack_cad.py`), sizing checks (`cad/analysis.py`), renders and animations (`cad/render/`), all in `protoboard/out/` (regenerable, not committed).
- Report: `deliverables/2026-10-25-design-report/` (index.html + media; rebuild with build_report.py and prepare_media.py), published privately at https://claude.ai/artifact/QbR7gZmdQYLXZfdUdeZ3D1

**Next actions:**

1. Mark reviews the report, picks a tier (recommended B), answers `research/questions.md`, signs `protoboard/docs/brief.md`.
2. Mark's go to commit, create `Delta-Robotics-Inc/2026-10-24-joyful-jack`, push and add the hub submodule (commands from `projects.mjs adopt`); then retire `projects/internal/JackOLantern` and the empty `26-1024-Pumpkin`.
3. Level 4 for the chosen tier: verify the project-researched parts (`uhd-part-research`/`verify`), re-price from vendor pages.
4. Bench: weigh the head, measure power draw, relay pull-in at 15 V, LVC set point, tip test.

**Blockers:**

Brief unsigned; tier choice; commit/repo creation wait on Mark.

---

## Sessions

<!--
Newest entry at the TOP. Copy the block below for each session.
Every claim points at a real artifact so it can be checked.
-->

### 2026-10-24/25 - session 3 (head model, three tiers, renders, report)

- **Goal:** Mark: recreate the head in UHD from the Fusion/STEP files; design and render three tiers (< $500, <= $1200, maxed with humanoid hands); a report for a non-technical reader, with exploded and walkthrough animations.
- **Done:** head UHD model; STEP -> GLB; three tier systems checked clean; priced BOMs fitted to caps (research agent + own lookups); CAD for all tiers; sizing analysis (found tier C direct drive could not hold the arm -> belts; tier A needs real springs); 14 Cycles stills, 4 animations, Protoboard diagram captures; report built and published.
- **Decisions and why:** `protoboard/docs/decisions.md` D1-D8.
- **Blockers and open questions:** `research/questions.md`; bench tests listed in the report.
- **Left to do:** see Next actions.

### 2026-10-24 - session 2 (sourcing)

- **Goal:** Price and specify parts for all three tiers (web search and fetch only).
- **Done:** `research/sourcing/20261024-bom.json` (97 rows: shared 24, A 19, B 19, C 32 incl. B carry-over, 3 swap alternates at qty 0) and `research/sourcing/20261024-bom.md` (tables, totals, swaps, risks, gaps).
- **Key values:** shared $423.94; A $904.33 (over by $404.33; $760.87 after the cheap swaps, so the cap needs a scope decision); B $1,603.24 (over by $403.24; $1,158.70 with all-STS3215 + 2.73:1 belts + the shared swaps); C $2,132.76.
- **Findings:** assume an M18 pack does not cut itself off behind a plain adapter (Power Tool Institute; adapter vendors), so the XH-M609 cutoff stays. AmazingHand: 8 SCS0009 per hand, 400 g, Apache 2.0 / CC BY 4.0, Seeed kit $99 per hand, grip force unpublished; recommended for tier C.
- **Blockers and open questions:** STS3250 has no authorised US price; most retail prices are search snippets (amazon-data and distributor-data degraded); relay pull-in at 15 V untested.
- **Left to do:** Mark's cap decision; re-price the STS3250 from Feetech direct; bench-test the 24 V coil relay at 15 V.

### 2026-10-24 - session 1

- **Goal:** Turn the old JackOLantern repo into a hub project and propose a body-and-arms plan at three price points.
- **Done:** adopt + restructure (see Current State); `research/20261024-plan.md`; `protoboard/docs/brief.md` draft; `research/questions.md`; `inbox/manifest.json`.
- **Decisions and why:** head code under `protoboard/software/head/` (the template keeps firmware and software inside the stack project). Proposed only, pending sign-off: spring counterbalance at the shoulder in every tier, a wide base skirt under the bucket, dual-M18 hot swap from tier B.
- **Blockers and open questions:** `research/questions.md`.
- **Left to do:** see Next actions.
- **Checkpoint:** <!-- the checkpoint written at session end: `node tools/projects.mjs checkpoint joyful-jack` from the hub root -->
