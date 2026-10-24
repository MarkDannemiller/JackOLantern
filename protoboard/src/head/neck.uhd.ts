/**
 * Neck: yaw on a lazy-susan turntable driven by a pancake NEMA 17 through a 3:1
 * gear stage, and pitch by two DS3225MG servos pushing through M3 rods.
 *
 * Sources:
 *   - inbox/20261024-head-assembly.f3z → "Neck Design 3" v34: NEMA17 Pancake Stepper,
 *     LazySusan, Articulating Servo, 145 mm M3 Threaded Rod, 8-32 Brass Heat Sert,
 *     M3x5x6 heat-set inserts.
 *   - protoboard/software/head/motion_controller.py: yaw 0-120 deg (neutral 60),
 *     gear ratio 3, 3200 steps/rev, max 5 deg/s; pitch 180-265 deg (neutral 250),
 *     servo channels neck_l 8 (follows neck_r, reversed, -15 deg offset), neck_r 9.
 *
 * Modelling notes:
 *   - The pitch servos are the 270° DS3225MG (local variant; the code sets
 *     actuation_range 270 on channel 9).
 *   - The turntable, gears, rods and inserts are not modelled as parts yet: no
 *     catalog part matches and their sizes come from the STEP at the CAD step.
 */
import type { ModuleDef } from "@deltarobotics/uhd";

export const NECK: ModuleDef = {
  id: "jj-neck",
  name: "Neck",
  kind: "module",
  description:
    "Two-axis neck: stepper-driven yaw on a lazy-susan turntable (3:1 gear, home switch) and servo-driven pitch with two DS3225MG servos on push rods.",
  tags: ["neck", "pan-tilt", "animatronic"],
  categories: ["robotics"],
  interfaces: [],
  children: [
    { id: "yaw_motor", moduleDefId: "nema17-pancake-stepper", name: "Yaw stepper" },
    { id: "yaw_driver", moduleDefId: "stepper-driver-step-dir", name: "Yaw driver" },
    { id: "yaw_home", moduleDefId: "yaw-home-switch", name: "Yaw home switch" },
    { id: "pitch_l", moduleDefId: "dsservo-ds3225mg-270", name: "Pitch servo, left (follower)" },
    { id: "pitch_r", moduleDefId: "dsservo-ds3225mg-270", name: "Pitch servo, right (leader)" },
  ],
  links: [{ id: "yaw_motor_phases", name: "Yaw motor phases", a: { child: "yaw_driver", interfaceId: "motor" }, b: { child: "yaw_motor", interfaceId: "windings" } }],
  exports: [
    { id: "yaw_step_dir", name: "Yaw STEP/DIR/EN", from: { child: "yaw_driver", interfaceId: "step_dir" } },
    { id: "yaw_driver_gnd", name: "Yaw driver GND", from: { child: "yaw_driver", interfaceId: "gnd" } },
    { id: "yaw_home_com", name: "Home switch COM", from: { child: "yaw_home", interfaceId: "com" } },
    { id: "yaw_home_signal", name: "Home switch signal", from: { child: "yaw_home", interfaceId: "no" } },
    { id: "pitch_l_servo", name: "Pitch servo L", from: { child: "pitch_l", interfaceId: "rc_servo_3wire" } },
    { id: "pitch_r_servo", name: "Pitch servo R", from: { child: "pitch_r", interfaceId: "rc_servo_3wire" } },
  ],
  traits: [
    { type: "usage_note", params: { note: "Yaw gear ratio 3:1 (motor:head), 3200 steps per motor revolution, range 0-120 deg, max 5 deg/s.", source: "protoboard/software/head/motion_controller.py" } },
    { type: "data_gap", params: { field: "yaw motor and driver supply", note: "The supply voltage and current for the yaw driver are not documented; to be set when head power moves into the torso." } },
  ],
};
