# Questions

<!--
PHASE 1. Two sections, and things move from the first to the second.

An answer without its source becomes folklore in two weeks, so every answered
question keeps the source and the date.

An open question that has quietly become a design assumption is not a
question any more: record it in protoboard/docs/decisions.md as an
assumption, with what would resolve it.

The open list is also what blocks the research sign-off (project.md,
Sign-offs). Anything still open at sign-off is parked deliberately, with a
reason, in the sign-off row.
-->

## Open

<!-- Each one: the question, who can answer it, and what it blocks. -->

1. **Head mass.** The CAD gives geometry but no mass. A weighing of the built head, or materials and infill to estimate it. Mark. Blocks: tip check, neck mount loads.
3. **Maxed tier budget.** No cap given. Mark. Blocks: hand choice for tier C.
4. **Overall height and look.** Torso height above the floor, character proportions, costume or hard shell, indoors or outdoors (rain). Mark. Blocks: mast length, sealing, arm lengths.
5. **What the hands must hold, and how long.** Candy bowl, bag, sign, lantern? Weight? Mark. Blocks: payload in the torque sizing (assumed 0.25 kg).
6. **Three tiers in the stack.** One stack project with the root switched per tier, or three stack projects. Mark. Blocks: level 2 onward.
7. **Runtime target and swapping.** Hours per evening; is hot swap needed in tier A? Which M18 packs are on hand? Mark. Blocks: power design.
8. **Head power today.** What supply and servo voltage the head runs on now. Mark. Blocks: power rails.
9. **M18 pack protection.** What an M18 pack does with no tool electronics attached (over-discharge). Research. Blocks: whether we add our own low-voltage cutoff (assumed yes).

- [ ] <question> Blocks: <what cannot be decided until this is answered>. Owner: <name>.

## Answered

<!-- Each one: the answer, the source, the date. -->

- <answer> Source: <document, URL or meeting note path>. Answered: YYYY-MM-DD.
