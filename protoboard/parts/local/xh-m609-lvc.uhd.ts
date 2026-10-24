/**
 * XH-M609 digital low-voltage disconnect, 12-36 V in, relay output (20 A contacts per listings).
 * Sources: research/sourcing/20261024-bom.json. Set the cut-off to ~15.0-16.0 V for a 5S pack (TBD from the cell datasheet).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { powerStage } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const XH_M609_LVC_ELECTRICAL: ModuleDef = powerStage({
  id: "xh-m609-lvc", name: "XH-M609 low-voltage cutoff", manufacturer: "Generic", part_number: "XH-M609",
  description: "Measures the pack and opens its relay below a set voltage, so a pack is never run flat.",
  categories: ["component.protection"], tags: ["lvc"], sources: [{ id: "src_listing", name: "BOM row (listings)", url: "https://www.amazon.com/s?k=XH-M609" }],
  vin: [12, 36], vout: [12, 36], iout: 20, dims: [57, 42, 19],
  traits: [{ type: "usage_note", params: { note: "Cut-off set ~15.0-16.0 V (3.0-3.2 V/cell) for the 5S M18 pack; the value is TBD from the cell datasheet.", source: "research/sourcing/20261024-bom.json" } }],
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const XH_M609_LVC: ModuleDef = withMech(XH_M609_LVC_ELECTRICAL as ModuleDef, "jj-body-lvc");
