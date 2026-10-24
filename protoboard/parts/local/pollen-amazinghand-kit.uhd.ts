/**
 * Pollen Robotics AmazingHand, Seeed developer kit (right SKU 100063642 / left 100062181): 4 fingers x 2 DOF,
 * 8 Feetech SCS0009 servos in the palm, 400 g, external 5 V / 2 A; software Apache-2.0, design CC BY 4.0.
 * Sources: https://github.com/pollen-robotics/AmazingHand ; research/sourcing/20261024-bom.json.
 * Modelling notes: the kit's own controller talks to the host over USB (the Waveshare adapter wants 9-12.6 V, the
 * SCS0009 runs on 5 V, so the hands do not share the 12 V arm bus). Grip force is not published (data gap).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerIn, Ground, USB } from "@deltarobotics/uhd";
import { part } from "./lib/jj";

export const POLLEN_AMAZINGHAND_KIT: ModuleDef = part({
  id: "pollen-amazinghand-kit", name: "Pollen AmazingHand (Seeed kit)", manufacturer: "Pollen Robotics / Seeed Studio", part_number: "AmazingHand kit",
  description: "Open-source humanoid hand: four two-jointed fingers driven by eight micro serial servos in the palm.",
  categories: ["robotics"], tags: ["hand", "humanoid", "open-source"],
  sources: [{ id: "src_repo", name: "pollen-robotics/AmazingHand", url: "https://github.com/pollen-robotics/AmazingHand" }, { id: "src_seeed", name: "Seeed Amazing Hand kit", url: "https://www.seeedstudio.com/" }],
  interfaces: [PowerIn({ id: "v5", name: "5 V servo supply", voltageV: 5, minSupplyCurrentA: 2 }), Ground({ id: "gnd", name: "GND" }), ...USB({ id: "usb", role: "device", speeds: ["full"] })],
  traits: [
    { type: "data_gap", params: { field: "grip force", note: "Not published by Pollen or Seeed." } },
    { type: "data_gap", params: { field: "kit contents", note: "Seeed does not list them; CNX Software (2025-12-02) says printed structure, 8x SCS0009 and a XIAO controller." } },
  ],
  mass_g: 400,
});
