# Worklog

<!--
READ FIRST, WRITE LAST.

This is the one source of "what is true now". A project spans many sessions
across days or weeks, across separate agents and stop/starts. State survives
context loss because it lives in this file, not in any one chat.

  Every session STARTS by reading `## Current State

**Status:** Full-hardware design, build guides and Isaac Sim proof for all three tiers (session 4, 2026-10-25). Report revision 2 published privately. Brief still unsigned; nothing ordered. Committed and pushed to Mark's public repo `MarkDannemiller/JackOLantern` on his go (session 4).

**What is true now:**

- Full-hardware mechanical model: every printed part, bought part and fastener placed by mates (`protoboard/cad/mech`, build123d; `build.py --parts`, `gen_uhd.py`); generated into UHD (`src/mech/*.gen*`); `protoboard check` A 0/0, B 0/0, C 0 errors + 2 dispositioned warnings. Decisions D9-D15 in `protoboard/docs/decisions.md`.
- Joints: GT3 9 mm belts 3:1 on hollow hubs over 6806-2RS; shoulder zero-length-spring balancer (2 x Century 90CS) on every tier; tier A on DS3235/DS3225 belt joints; tier C J1/J2/J4 STS3250.
- Build guides: `protoboard release` 0.2.0-a/b/c (units body, arm_r, arm_l; gitignored), merged per tier in `deliverables/2026-10-25-build-guides/` (70 / 100 / 106 pages).
- BOM v2 from model quantities (`research/sourcing/20261025-bom-v2.md`, `build_bom_v2.py`): A $894.06 / B $1,381.40 / C $2,370.13, plus a few TBD rows (14/16/20/26 AWG wire, M5 tap; hardened dowels stand-in). Caps lifted by Mark for this round.
- Wiring cut lists per tier: `protoboard/docs/wiring/harness-<t>.md` (21 / 35 / 43 cables).
- Isaac Sim 6.2 (`protoboard/cad/mech/sim`, results `protoboard/docs/sim-results.md`, D15): wave and reach pass on all tiers with the balancer and belt torque limits; arm straight out sideways is outside the envelope; tip 154-164 N (205-215 N with two sandbags).
- Renders and animations of the detailed model: `protoboard/cad/render/render_mech.py` (outputs in `protoboard/out/renders/mech`, regenerable).
- Report revision 2: `deliverables/2026-10-25-design-report/` (build_report.py, prepare_media.py), published at https://claude.ai/artifact/QbR7gZmdQYLXZfdUdeZ3D1

**Next actions:**

1. Mark reviews report rev 2 and the build guides; picks a tier (recommended B); answers `research/questions.md`; signs `protoboard/docs/brief.md`.
2. Mark decides whether to rewrite public history to drop the DSSERVO STEP pushed in 603453e (D14).
3. Price the TBD rows (browser access to Home Depot, McMaster, SDP-SI); confirm SHCS kit per-size counts.
4. Bench: set servo torque limits (D15) before first power-up; weigh the head; power draw; relay pull-in at 15 V; LVC set point; tip test.
5. Optional: J2 balancer if a sideways T-pose gesture is wanted; arm cover shells for the costume.

**Blockers:**

Brief unsigned; tier choice; history rewrite decision (Mark).

---

## Sessions

<!--
Newest entry at the TOP. Copy the block below for each session.
Every claim points at a real artifact so it can be checked.
-->

### 2026-10-25 - session 4 (full hardware, build guides, Isaac Sim)

- **Goal:** Mark: model every bolt, harness and real component instead of simple joints; make each tier constructable with a stack build guide; price beyond the caps; prove feasibility in Isaac Sim; commit to his public repo and continue.
- **Done:** full-hardware build123d model and UHD generation; GT3 belt joints, shoulder cable balancer (torsion-spring concept found wrong, D11); tier A moved to belt joints after the sim showed direct drive failing (D12); harness cut lists; BOM v2 from model quantities with a pricing agent's research; releases 0.2.0-a/b/c and merged guides; fixed a build123d glTF export bug that misplaced parts in the guide figures; Isaac Sim batches with belt torque limits and a kinematically correct wave (D15); new Blender pipeline for the detailed model (stills, explode and walkthrough videos, sim video); report rev 2.
- **Decisions and why:** D9-D15.
- **Friction logged:** pkill self-match (repeat), build123d glTF location bug, tech-docs standalone failure, guide figure framing, wave definition drift, sourcing sites unreadable, Blender join.
- **Left to do:** see Next actions.

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
