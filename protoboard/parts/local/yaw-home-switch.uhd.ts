/**
 * Neck yaw home (limit) switch — model TBD.
 *
 * Sources:
 *   - src_code: protoboard/software/head/pid_stepper.py (home switch read on BCM22 with a
 *     pull-down; reads high at home) and motion_controller.py (a GPIO driven high as its 3.3 V source)
 *
 * Modelling notes:
 *   - PARTIAL: switch type unknown. Modelled as a contact between a 3.3 V common
 *     and a signal output read by the Pi.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { defineModule, PowerIn, Pin } from "@deltarobotics/uhd";

export const YAW_HOME_SWITCH = defineModule({
  id: "yaw-home-switch",
  name: "Neck yaw home switch (model TBD)",
  version: "0.1.0",
  kind: "module",
  manufacturer: "TBD",
  part_number: "TBD",
  description: "Limit switch that marks the neck yaw home position: closes 3.3 V onto a Pi input held low by a pull-down.",
  tags: ["limit-switch", "homing"],
  categories: ["component.switch"],
  interfaces: [
    PowerIn({ id: "com", name: "COM (3.3 V)", voltageV: 3.3 }),
    Pin({ id: "no", name: "NO (signal)", voltageV: 3.3 }),
  ],
  traits: [{ type: "data_gap", params: { field: "switch type and mounting", note: "Not in the code or the CAD component list." } }],
}) as ModuleDef;
