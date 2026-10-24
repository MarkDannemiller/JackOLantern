/**
 * DSSERVO DS3225MG 25 kg digital servo, 270° build — local variant of the
 * catalog part dsservo-ds3225mg-180@3 (parts/catalog/dsservo-ds3225mg-180.json).
 *
 * Sources: the catalog part's sources (parts/catalog/dsservo-ds3225mg-180/sources.json):
 *   - src_datasheet: DSSERVO DS3225 datasheet — https://www.dsservo.com/down.asp?id=24
 *     ("PWM 500-2500 µs ... 180° or 270°": one datasheet covers both builds)
 *
 * Modelling notes:
 *   - Everything but the travel is the catalog definition, unchanged: DSSERVO
 *     publishes one datasheet for both builds.
 *   - Joyful Jack's head uses the 270° build for the jaw and neck pitch: the head
 *     code sets `actuation_range = 270` on PCA9685 channels 6, 7 and 9
 *     (protoboard/software/head/motion_controller.py). Which build is fitted is an
 *     assumption until the servos are checked (trait below).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import BASE from "../catalog/dsservo-ds3225mg-180.json" with { type: "json" };
import { withMech } from "../../src/mech/lib";

const base = BASE as unknown as ModuleDef;

const DSSERVO_DS3225MG_270_ELECTRICAL: ModuleDef = {
  ...base,
  id: "dsservo-ds3225mg-270",
  name: "DSSERVO DS3225MG 25 kg digital servo (270°)",
  part_number: "DS3225MG (270°)",
  description:
    "Standard-size waterproof (IP66) digital servo, metal gears: 4.8-6.8 V, stall torque 21 kg·cm @5 V / 24.5 kg·cm @6.8 V, PWM 500-2500 µs mapped to 0-270°, 40 x 20 x 40.5 mm, 60 g. Local 270° variant of the catalog dsservo-ds3225mg-180.",
  // the catalog's file paths are library paths; the vendored copies sit under parts/catalog/ (origins.json artifactBase)
  artifacts: (base.artifacts ?? []).map((a) =>
    "filePath" in a && typeof a.filePath === "string"
      ? { ...a, filePath: a.filePath.replace("library/parts/dsservo-ds3225mg-180/", "parts/catalog/dsservo-ds3225mg-180/") }
      : a,
  ),
  traits: [
    ...(base.traits ?? []).filter((t) => !(t.type === "usage_note" && (t.params as { topic?: string })?.topic === "variant")),
    {
      type: "usage_note",
      params: {
        topic: "variant",
        note: "270° build: 500-2500 µs maps to 0-270°. DSSERVO publishes one datasheet for the 180° and 270° builds.",
        source: "https://www.dsservo.com/down.asp?id=24",
      },
    },
    {
      type: "assumption",
      params: {
        field: "travel",
        value: "270°",
        reason: "The head code drives the jaw and neck pitch servos with actuation_range = 270 (software/head/motion_controller.py); the fitted servos have not been inspected.",
      },
    },
  ],
};

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const DSSERVO_DS3225MG_270: ModuleDef = withMech(DSSERVO_DS3225MG_270_ELECTRICAL as ModuleDef, "servo-ds3225");
