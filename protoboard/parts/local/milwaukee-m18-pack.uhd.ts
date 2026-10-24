/**
 * Milwaukee M18 REDLITHIUM pack (owned; HD12.0 48-11-1812 or XC8.0 48-11-1880) — Joyful Jack's battery.
 * Sources: research/sourcing/20261024-bom.json (reference rows): 18 V nominal, 12.0 / 8.0 Ah from retailer listings and model names.
 * Modelling notes: the pack's terminals are the M18 slide; the adapter dock mates it. The voltage window is an
 * assumption (5 cells in series, 3.0-4.2 V per cell); over-discharge protection without a Milwaukee tool is not
 * assured (Power Tool Institute), so the system adds its own low-voltage cutoff.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerOut, Ground } from "@deltarobotics/uhd";
import { part } from "./lib/jj";

export const MILWAUKEE_M18_PACK: ModuleDef = part({
  id: "milwaukee-m18-pack", name: "Milwaukee M18 REDLITHIUM pack (owned)", manufacturer: "Milwaukee Tool", part_number: "48-11-1812 (HD12.0) / 48-11-1880 (XC8.0)",
  description: "18 V nominal Li-ion power-tool pack: 12.0 Ah (216 Wh) or 8.0 Ah (144 Wh). Owned; not on the BOM.",
  categories: ["power.battery"], tags: ["m18", "li-ion", "owned"],
  sources: [{ id: "src_bom", name: "BOM reference rows (listings)", url: "https://www.milwaukeetool.com/products/details/m18-redlithium-compact-battery-two-pack/48-11-1811" },
            { id: "src_pti", name: "Power Tool Institute: battery adapters", url: "https://www.powertoolinstitute.com/?p=376" }],
  interfaces: [PowerOut({ id: "pack_plus", name: "B+", voltageV: [15, 21], nominalV: 18 }), Ground({ id: "pack_minus", name: "B-" })],
  traits: [
    { type: "assumption", params: { field: "voltage window", value: "15-21 V", reason: "5 Li-ion cells in series at 3.0-4.2 V each; Milwaukee publishes only 18 V nominal." } },
    { type: "usage_note", params: { note: "Discharge protection without a Milwaukee tool attached is not assured: the system's XH-M609 cuts off at ~15-16 V.", source: "https://www.powertoolinstitute.com/?p=376" } },
  ],
  mass_g: 1542, dims: [152, 86, 99],
});
