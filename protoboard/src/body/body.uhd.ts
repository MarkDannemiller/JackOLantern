/**
 * Joyful Jack's body structure: designed here, no electrical interfaces. Geometry: cad/joyful_jack_cad.py.
 * Parts and prices: research/sourcing/20261024-bom-final.md (the stack BOM covers the electrical parts only).
 */
import type { ModuleDef } from "@deltarobotics/uhd";

export const BALLAST_BASE: ModuleDef = {
  id: "jj-ballast-base", name: "Ballast base and mast", kind: "module", categories: ["mechanical.structure"], tags: ["base"],
  description: "5 US gal bucket of concrete (~44 kg) on a 24 in birch plywood skirt, with a 1 in black-iron pipe mast threaded into a floor flange cast in the concrete.",
  interfaces: [], children: [], links: [],
};

export const TORSO_A: ModuleDef = {
  id: "jj-torso-a", name: "Torso, tier A (plywood ribs)", kind: "module", categories: ["mechanical.structure"], tags: ["torso"],
  description: "Laser-cut 1/4 in plywood ribs and spines on the mast, a shoulder beam, the M18 dock behind a rear hatch and an electronics plate; flannel shirt, vest, bandana and hat over it.",
  interfaces: [], children: [], links: [],
};

export const TORSO_BC: ModuleDef = {
  id: "jj-torso-bc", name: "Torso, tiers B and C (2020 aluminium frame)", kind: "module", categories: ["mechanical.structure"], tags: ["torso"],
  description: "2020 V-slot box frame on the mast collar, a shoulder beam, two M18 docks behind a rear hatch and an electronics plate; costume over it.",
  interfaces: [], children: [], links: [],
};

export const POWER_BOARD_C: ModuleDef = {
  id: "jj-power-board-c", name: "Custom power board (tier C, next revision)", kind: "module", categories: ["power.distribution"], tags: ["pcb", "designed-here"],
  description: "Planned board: three LM74700-Q1 ideal-diode inputs (two M18, one 24 V mains), TPS25982 eFuses per branch and INA226 monitors on I2C. Replaces the ideal-diode modules, fuse block and INA228 after bring-up. Not yet designed (stack level 2 block).",
  interfaces: [], children: [], links: [],
};
