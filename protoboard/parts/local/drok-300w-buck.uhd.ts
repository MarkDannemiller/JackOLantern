/**
 * DROK 300 W adjustable buck, 3.5-30 V in, 0.8-29 V out, 10 A (vendor page). No reverse-polarity protection.
 * Sources: research/sourcing/20261024-bom.json (verified on vendor page). Set the output per use (instance name says it).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { powerStage } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const DROK_300W_BUCK_ELECTRICAL: ModuleDef = powerStage({
  id: "drok-300w-buck", name: "DROK 300 W adjustable buck (10 A)", manufacturer: "DROK", part_number: "300W CC/CV buck",
  description: "Adjustable step-down converter, CC/CV, 10 A max; Vin must be at least Vout + 1 V.",
  categories: ["power.regulator"], tags: ["buck"], sources: [{ id: "src_vendor", name: "DROK product page (BOM row)", url: "https://www.droking.com/" }],
  vin: [3.5, 30], vout: [0.8, 29], iout: 10, dims: [85, 58, 33], mass_g: 105,
  traits: [{ type: "usage_note", params: { note: "No reverse-polarity protection: XT60 polarised connectors on the input.", source: "research/sourcing/20261024-bom.json" } }],
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const DROK_300W_BUCK: ModuleDef = withMech(DROK_300W_BUCK_ELECTRICAL as ModuleDef, "jj-body-drok");
