/**
 * Generic "Power Wheel Adapter for Milwaukee M18": M18 dock with on/off switch, 30 A fuse and 12 AWG leads.
 * Sources: research/sourcing/20261024-bom.json (listing; max permissible current 18 or 20 A, listings disagree; no LVC).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerIn, PowerOut, Ground } from "@deltarobotics/uhd";
import { part } from "./lib/jj";

export const M18_POWER_WHEEL_ADAPTER: ModuleDef = part({
  id: "m18-power-wheel-adapter", name: "M18 battery adapter (switch, 30 A fuse, 12 AWG)", manufacturer: "Generic", part_number: "Power Wheel Adapter for Milwaukee M18",
  description: "Dock that takes an M18 pack and brings it out on 12 AWG leads through an on/off switch and a 30 A fuse.",
  categories: ["connector.power_connector"], tags: ["m18", "adapter"],
  sources: [{ id: "src_listing", name: "BOM row (listing)", url: "https://www.newegg.com/" }],
  interfaces: [
    PowerIn({ id: "dock_plus", name: "Dock B+", voltageV: [15, 21] }), Ground({ id: "dock_minus", name: "Dock B-" }),
    PowerOut({ id: "lead_plus", name: "Lead + (red, 12 AWG)", voltageV: [15, 21], maxCurrentA: 18 }), Ground({ id: "lead_minus", name: "Lead - (black)" }),
  ],
  traits: [
    { type: "supplied_from", params: { interfaceId: "lead_plus", via: "switch and 30 A fuse", source: "dock_plus" } },
    { type: "source_discrepancy", params: { field: "max current", values: ["18 A", "20 A"], sources: ["listings"], resolution: "18 A used" } },
  ],
});
