/**
 * Pololu D24V50F5 5 V 5 A step-down regulator (item 2851), input up to 38 V.
 * Sources: research/sourcing/20261024-bom.json (Pololu). The minimum input is an assumption (headroom over 5 V).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { powerStage } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const POLOLU_D24V50F5_ELECTRICAL: ModuleDef = powerStage({
  id: "pololu-d24v50f5", name: "Pololu D24V50F5 5 V 5 A buck", manufacturer: "Pololu", part_number: "D24V50F5 (#2851)",
  description: "Fixed 5 V, 5 A synchronous step-down regulator for a Raspberry Pi.",
  categories: ["power.regulator"], tags: ["buck", "5v"], sources: [{ id: "src_pololu", name: "Pololu #2851", url: "https://www.pololu.com/product/2851" }],
  vin: [6, 38], vout: 5, iout: 5,
  traits: [{ type: "assumption", params: { field: "minimum input", value: "6 V", reason: "Only the 38 V maximum was recorded; the M18 pack (15-21 V) is far above any minimum." } }],
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const POLOLU_D24V50F5: ModuleDef = withMech(POLOLU_D24V50F5_ELECTRICAL as ModuleDef, "jj-body-pololu");
