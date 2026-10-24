# joyful-jack: brief

**DRAFT, 2026-10-24, not signed.** Written from Mark's request of 2026-10-24
and the existing head code. Full plan: `../../research/20261024-plan.md`.
Open questions: `../../research/questions.md`.

## Purpose

Joyful Jack is a pumpkin-head animatronic character that greets people
(Halloween events, demos). It runs unattended for long stretches, is easy to
move, and stands on its own.

## Requirements

1. Torso, no legs, standing on a ballasted base (a paint bucket of concrete) on a mast. Must not tip when bumped or leaned on (target load TBD: Q4).
2. Battery and power electronics inside the torso, on Milwaukee M18 packs, swappable without removing the costume.
3. Runs for extended periods. Hours per pack: **TBD: Q7**.
4. Two motorised arms with simple character hands that can grasp an object (payload **TBD: Q5**, assumed 0.25 kg).
5. Keeps and powers the existing head (Raspberry Pi 4B, PCA9685, neck stepper, camera, audio).
6. Safe among children: emergency stop, limited speed and grip force, no pinch points, arms fall to a rest pose on power loss.

## Three designs

Caps are new spend; the existing head is reused (Mark, 2026-10-24).

| Tier | Cap | Arms | Hands |
|---|---|---|---|
| A Beginner | under $500 ($498.05 designed) | 3 joints + grip, hobby servos, shoulder springs | 1-actuator cartoon mitt |
| B Midrange | up to $1200 ($1,174.95 designed) | 5 joints, Feetech STS3215 with feedback, belts + springs | 2-actuator glove hand |
| C Maxed | no cap ($2,139.69 designed) | 6 joints, STS3250/STS3215, belts + springs | Pollen AmazingHand, 8 DOF |

Designed 2026-10-24/25 before this brief was signed, on Mark's instruction ("build all the versions"); see docs/decisions.md D5-D8 and the report in deliverables/2026-10-25-design-report/.

## Acceptance

TBD: set with Mark at sign-off (runtime on one pack, tip test load, gesture set).

## Research sign-off

- [ ] Research complete, brief agreed. Signed: ________ Date: ________
