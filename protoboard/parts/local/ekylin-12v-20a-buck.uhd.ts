/**
 * EKYLIN 24 V-to-12 V 20 A 240 W step-down converter, 15-40 V in (listing).
 * Sources: research/sourcing/20261024-bom.json.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { powerStage } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const EKYLIN_12V_20A_BUCK_ELECTRICAL: ModuleDef = powerStage({
  id: "ekylin-12v-20a-buck", name: "EKYLIN 12 V 20 A buck", manufacturer: "EKYLIN", part_number: "24V to 12V 20A 240W",
  description: "Fixed 12 V, 20 A step-down converter; 15-40 V input covers the M18 pack and a 24 V mains supply.",
  categories: ["power.regulator"], tags: ["buck", "12v"], sources: [{ id: "src_listing", name: "BOM row (listing)", url: "https://www.amazon.com/s?k=EKYLIN+24V+to+12V+20A" }],
  vin: [15, 40], vout: 12, iout: 20,
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const EKYLIN_12V_20A_BUCK: ModuleDef = withMech(EKYLIN_12V_20A_BUCK_ELECTRICAL as ModuleDef, "jj-body-ekylin");
