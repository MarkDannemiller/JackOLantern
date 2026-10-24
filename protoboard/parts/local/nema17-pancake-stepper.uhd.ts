/**
 * NEMA 17 pancake stepper motor — Joyful Jack's neck yaw motor.
 *
 * Sources:
 *   - src_cad: inbox/20261024-head-assembly.f3z, Neck Design 3 → component "NEMA17 Pancake Stepper"
 *   - src_code: protoboard/software/head/motion_controller.py (yaw_s_p_rev = 3200, yaw_gear_ratio = 3)
 *
 * Modelling notes:
 *   - PARTIAL, unverified: the motor model is unknown (data_gap). Only the
 *     windings are modelled; the bolt pattern and shaft come with the CAD binding.
 *   - The code counts 3200 steps per motor revolution. For a 200-step (1.8°)
 *     motor that is 1/16 microstepping; the step angle is an assumption.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { defineModule, StepperPhases } from "@deltarobotics/uhd";

export const NEMA17_PANCAKE_STEPPER = defineModule({
  id: "nema17-pancake-stepper",
  name: "NEMA 17 pancake stepper (model TBD)",
  version: "0.1.0",
  kind: "module",
  manufacturer: "TBD",
  part_number: "NEMA 17 pancake (model TBD)",
  description: "Short-body NEMA 17 bipolar stepper driving the neck yaw through a 3:1 gear stage. Partial definition; model unconfirmed.",
  tags: ["stepper", "nema17", "pancake"],
  categories: ["actuator.motor.stepper"],
  interfaces: [...StepperPhases({ id: "windings", name: "Windings", role: "input", winding: "bipolar" })],
  traits: [
    { type: "data_gap", params: { field: "model, rated current, step angle, shaft", note: "Not in the code; the CAD names it only 'NEMA17 Pancake Stepper'." } },
    { type: "assumption", params: { field: "step angle", value: "1.8° (200 full steps)", reason: "3200 counted steps per revolution in the code would then be 1/16 microstepping, a common driver setting." } },
  ],
}) as ModuleDef;
