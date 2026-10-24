# Decisions

One entry per engineering decision: context, options, choice, evidence.

## D1 2026-10-24: the existing head is modelled as built, from the received CAD and the 2023 code

- **Context:** Mark asked for the head recreated in UHD. Received: `inbox/20261024-head-assembly.{f3z,stp}` (Head Assembly v79, 2023-12-01) and `inbox/20261024-facade.{f3z,stp}` (Facade v61, 2023-11-13).
- **Choice:** internals from Head Assembly v79; facade panels and outer envelope from Facade v61. Facade v61 embeds an older Head Assembly v74 (2023-10-02, eye mechanism v21), so its internals are not used.
- **Structure:** `src/head/head.uhd.ts` (jj-head) with `eye-mechanism.uhd.ts` and `neck.uhd.ts`; bought parts in `parts/local/` (project-researched) and `parts/catalog/` (towerpro-sg90@2, dsservo-ds3225mg-180@3).
- **Wiring:** the PCA9685 channel map and Pi GPIO are the code's (`software/head/motion_controller.py`), not a wiring diagram. Unconfirmed wiring stays a `data_gap`, never a guessed link.

## D2 2026-10-24: DS3225MG 270° as a local variant of the catalog 180° part

- **Context:** the catalog has only `dsservo-ds3225mg-180`; the code sets `actuation_range = 270` on channels 6, 7 and 9.
- **Choice:** `parts/local/dsservo-ds3225mg-270.uhd.ts` imports the vendored catalog JSON and changes only the id, name, travel note and an `assumption` trait. DSSERVO publishes one datasheet for both builds. Artifact paths are remapped from the library layout to `parts/catalog/dsservo-ds3225mg-180/`.

## D3 2026-10-24: unidentified parts are partial local definitions, not guesses

- Raspberry Pi 4 B, PCA9685 breakout, OV5647 IR-cut camera, NEMA 17 pancake stepper, step/dir driver and yaw home switch are not in the Protoboard catalog (Pi 4: only the Pi 5 is). Each is a partial definition with only the interfaces the head uses, cited to the code, the CAD component names or the vendor docs. Models, ratings and supplies the files do not state are `data_gap` or `assumption` traits.
- Not modelled at all (no evidence of what they are): the eye LEDs and their drive, the audio output, amplifier and speaker, the lazy-susan bearing, gears, push rods and inserts. They are listed as data gaps on the head and neck.
- Verification (`uhd-part-research`, `uhd-part-verify`) is level-4 work. The URL sources in `parts/evidence/*/sources.json` are marked not fetched.

## D4 2026-10-24: STEP/DIR wired with a link-scoped composition

- The Pi has no step/dir port of its own; its GPIO26/19/13 are composed on the link `yaw_step_dir` and mated to the driver's `step_dir` composite. Linking the driver's leaves one by one is not possible: a leaf bound into a composite is not a boundary interface, so it cannot be exported.

## Check dispositions, 2026-10-24

| Diagnostic | Disposition |
|---|---|
| `UHD_UNPOWERED head:pi_5v_in`, `head:servo_vplus_in` | Expected. The head's supplies come from the torso power system, which is not modelled until the brief is signed. The 2023 head supply is undocumented (research/questions.md Q8). |

## D5 2026-10-24: three tiers in one stack project, chosen by JJ_TIER

- The stack has one `root` per project and no product variants. `protoboard.config.ts` picks the root from `JJ_TIER` (`a`, `b`, `c`; default `b`): `JJ_TIER=a protoboard check`. The head, base, torso blocks and parts are shared; `src/tiers/tier-<t>.uhd.ts` holds each system, `src/arms/arms.uhd.ts` the arms. Logged as stack friction (variants). Drafted before the brief was signed, on Mark's instruction to build all three overnight (2026-10-24).

## D6 2026-10-24: tier contents, fitted to the caps (new spend; research/sourcing/20261024-bom-final.md)

| | A Beginner | B Midrange | C Maxed |
|---|---|---|---|
| Total (2026-10-24 prices) | $498.05 of $500 | $1,174.95 of $1,200 | $2,139.69 (no cap) |
| Arm joints | 3 + grip: shoulder flex, shoulder out, elbow (DS3235 x2, DS3225MG) | 5 + 2-actuator hand: + upper-arm twist, wrist twist (STS3215) | 6 + AmazingHand: + wrist pitch (STS3250 heavy joints) |
| Gravity joints | direct drive + extension-spring counterbalance | 22:60 GT2 belts (2.73:1) + spring | 2.73:1 belts + spring |
| Hand | printed mitt, 1 MG996R | glove hand, fingers + thumb (2 STS3215) | Pollen AmazingHand, 8 DOF, own 5 V and USB |
| Control | head Pi 4 + 2nd PCA9685 at 0x41 | head Pi 4 + one Feetech USB bus adapter per arm | torso Pi 5 for arms and hands; head keeps its Pi 4 |
| Power | 1 M18, LVC, inline fuses, E-stop in the servo bucks' 18 V input | 2 M18 OR-ed by ideal diodes (hot swap), INA228 monitor, LVC, fuse block, E-stop relay | B + 24 V mains as a third OR input; custom power board next revision |
| Torso | 1/4 in plywood ribs | 2020 aluminium frame | 2020 aluminium frame |

Changes made to fit the caps, and why: tier A dropped the belt stages (the spring carries gravity), the separate fuse block (inline holders), the 18 AWG spool (servo extension leads), the relay (the E-stop opens the servo bucks' input, < 10 A), the collar and the INA; the shirt is bring-your-own ($11.98 more if bought). Tier B uses STS3215 everywhere on belt stages instead of STS3250 (saves ~$405; STS3250's $97 price is a weak search snippet).

## D7 2026-10-24: sizing results (cad/analysis.py, from the CAD masses)

Arm straight out, 0.25 kg payload (assumption), worst static case:

| Tier | Arm mass | Shoulder needs | Shoulder actuator (rated / stall) | Spring needed | Elbow needs | Elbow actuator (rated / stall) |
|---|---|---|---|---|---|---|
| A | 1.35 kg | 61.5 kg.cm | DS3235 ~10.7 / 32 | ~51 kg.cm (5.0 N.m) | 21.0 | DS3225 ~8.2 / 24.5 |
| B | 1.48 kg | 59.7 | STS3215 x2.73: 27.3 / 81.8 | ~32 kg.cm (3.2 N.m) | 18.5 | 27.3 / 81.8 |
| C | 1.63 kg | 68.0 | STS3250 x2.73: 43.6 / 136 | ~24 kg.cm (2.4 N.m) | 23.1 | 43.6 / 136 |

- Hobby servos publish no continuous rating: one third of stall is assumed for holding.
- Consequences: every tier needs the shoulder spring. Tier A cannot hold a loaded forearm horizontal for long (elbow at its stall): its gestures keep a loaded forearm within ~45 deg of vertical. Tier C direct-drive STS3250 could not hold the arm at all (stall 50 < 68), hence the belts.
- Tip-over: ~150-160 N (15-16 kgf) at shoulder height tips the figure with both arms out (62-66 kg incl. an assumed 2 kg head, 24 in skirt). Recommendation: two 25 lb sandbags on the skirt at events, or tether to a post.
- Printed plastic: ~0.6-1.0 kg per tier from the CAD (bought 2-3 kg with waste).

## D8 2026-10-24: tier C hand power and bus

- The AmazingHand's SCS0009 servos run on 5 V; the Waveshare adapter wants 9-12.6 V matching the servos, so the hands keep the Seeed kit's own controller on USB and get one 5 V Pololu D36V50F5 each. The torso Pi 5 needs 5.1 V: `protoboard check` rejected the fixed 5.0 V Pololu (UHD_LINK_STATE), so it gets an adjustable DROK set to 5.1 V.
- The hand bucks hang off the E-stop relay output with the arm bucks, so the E-stop stops the hands too. Open: the relay's 24 V coil pull-in from a 15-21 V pack is unverified (bench test).

## Check dispositions, tiers (2026-10-24)

| Tier | Result | Disposition |
|---|---|---|
| A | 0 errors, 0 warnings | |
| B | 0 errors, 0 warnings | |
| C | 0 errors, 2 warnings | `UHD_UNPOWERED pi5:5v_1/5v_2`: the Pi 5's header 5 V pins are fed internally from USB-C and not used here. |
