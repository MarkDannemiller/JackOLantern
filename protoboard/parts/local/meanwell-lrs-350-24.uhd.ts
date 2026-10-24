/**
 * Mean Well LRS-350-24: 24 V 14.6 A 350 W enclosed supply, 90-132 / 180-264 VAC in (tier C indoor input).
 * Sources: research/sourcing/20261024-bom.json.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerOut, Ground, AcPower } from "@deltarobotics/uhd";
import { part } from "./lib/jj";

export const MEANWELL_LRS_350_24: ModuleDef = part({
  id: "meanwell-lrs-350-24", name: "Mean Well LRS-350-24", manufacturer: "Mean Well", part_number: "LRS-350-24",
  description: "Mains power supply: a third input on the ideal-diode OR, so Jack can run all day indoors.",
  categories: ["power.power_supply"], tags: ["mains", "24v"], sources: [{ id: "src_mw", name: "Mean Well LRS-350", url: "https://www.meanwell.com/" }],
  interfaces: [...AcPower({ id: "ac_in", role: "input", voltageV: [90, 264], powerW: 350 }), PowerOut({ id: "v24", name: "+V", voltageV: 24, maxCurrentA: 14.6 }), Ground({ id: "gnd", name: "-V" })],
});
