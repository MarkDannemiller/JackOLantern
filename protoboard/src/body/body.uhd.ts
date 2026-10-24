/**
 * Joyful Jack's tier C power board (planned). The body itself (base, mast, torso, neck, electronics board) is
 * generated from the mechanical model: src/mech/body.gen.uhd.ts (cad/mech/build.py, cad/mech/gen_uhd.py).
 */
import type { ModuleDef } from "@deltarobotics/uhd";

export const POWER_BOARD_C: ModuleDef = {
  id: "jj-power-board-c", name: "Custom power board (tier C, next revision)", kind: "module", categories: ["power.distribution"], tags: ["pcb", "designed-here"],
  description: "Planned board: three LM74700-Q1 ideal-diode inputs (two M18, one 24 V mains), TPS25982 eFuses per branch and INA226 monitors on I2C. Replaces the ideal-diode modules, fuse block and INA228 after bring-up. Not yet designed (stack level 2 block).",
  interfaces: [], children: [], links: [],
};
