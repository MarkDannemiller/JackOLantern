/**
 * Pololu D36V50F5 5 V 5.5 A step-down regulator (item 4091), 5.5-50 V in. Tier C: one per AmazingHand.
 * Sources: research/sourcing/20261024-bom.json (verified on vendor page).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { powerStage } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const POLOLU_D36V50F5_ELECTRICAL: ModuleDef = powerStage({
  id: "pololu-d36v50f5", name: "Pololu D36V50F5 5 V 5.5 A buck", manufacturer: "Pololu", part_number: "D36V50F5 (#4091)",
  description: "Fixed 5 V step-down for one AmazingHand's eight micro servos.",
  categories: ["power.regulator"], tags: ["buck", "5v"], sources: [{ id: "src_pololu", name: "Pololu #4091", url: "https://www.pololu.com/product/4091" }],
  vin: [5.5, 50], vout: 5, iout: 5.5, dims: [25.4, 25.4, 9.5],
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const POLOLU_D36V50F5: ModuleDef = withMech(POLOLU_D36V50F5_ELECTRICAL as ModuleDef, "jj-body-pololu");
