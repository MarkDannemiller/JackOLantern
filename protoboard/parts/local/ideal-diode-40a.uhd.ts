/**
 * DIY-Module / GODIYMODULES 40-60 A ideal-diode module, single channel, positive line (listing).
 * Sources: research/sourcing/20261024-bom.json. Reverse voltage < 40 V; controller IC not stated.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { powerStage } from "./lib/jj";

export const IDEAL_DIODE_40A: ModuleDef = powerStage({
  id: "ideal-diode-40a", name: "Ideal-diode module, 40 A", manufacturer: "DIY-Module", part_number: "40A-60A ideal diode module",
  description: "MOSFET ideal diode in the positive line: several sources OR-ed onto one bus, so a pack can be swapped while the other runs.",
  categories: ["power.distribution"], tags: ["ideal-diode", "hot-swap"], sources: [{ id: "src_listing", name: "BOM row (listing)", url: "https://www.amazon.com/s?k=ideal+diode+module+40A" }],
  vin: [0, 40], vout: [0, 40], iout: 40,
});
