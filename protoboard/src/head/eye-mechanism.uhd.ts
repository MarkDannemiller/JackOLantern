/**
 * Eye mechanism: two eyes on a two-axis gimbal with four eyelids, six SG90 servos.
 *
 * Sources:
 *   - inbox/20261024-head-assembly.f3z → "Simplified 3D Printed Animatronic Dual Eye
 *     Mechanism" v28: Main Base, Sub Base, Servo Block, Eye Holder, Y-Arm,
 *     Three-Point Connector, Fork (x2), Eye Adaptor (x2), PlaceHolder Eye (x2),
 *     Top/Bottom Left Lid (+ mirror), Top/Bottom Lid Link (x2, + mirror), and six
 *     "SG90 - Micro Servo 9g - Tower Pro" with single horns.
 *   - protoboard/software/head/motion_controller.py: servo channels eye_y 0, eye_x 1,
 *     lid_tl 2, lid_tr 3, lid_bl 4, lid_br 5, and the open/closed lid angles.
 *
 * Printed parts are not separate modules yet: they are one designed assembly
 * whose geometry is the received STEP (bound at the CAD step). Each servo is the
 * catalog TowerPro SG90.
 */
import type { ModuleDef } from "@deltarobotics/uhd";

const SERVOS = [
  ["eye_y", "Eye pitch (up/down)"],
  ["eye_x", "Eye yaw (left/right)"],
  ["lid_tl", "Top-left lid"],
  ["lid_tr", "Top-right lid"],
  ["lid_bl", "Bottom-left lid"],
  ["lid_br", "Bottom-right lid"],
] as const;

export const EYE_MECHANISM: ModuleDef = {
  id: "jj-eye-mechanism",
  name: "Eye mechanism",
  kind: "module",
  description:
    "3D-printed dual-eye mechanism: both eyes on one gimbal (pitch and yaw servos) and four linked eyelids, each on its own SG90. Printed parts per the received CAD.",
  tags: ["eyes", "animatronic", "printed"],
  categories: ["robotics"],
  interfaces: [],
  children: SERVOS.map(([id, name]) => ({ id, moduleDefId: "towerpro-sg90", name })),
  links: [],
  exports: SERVOS.map(([id, name]) => ({ id: `${id}_servo`, name: `${name} servo`, from: { child: id, interfaceId: "rc_servo_3wire" } })),
  traits: [
    {
      type: "usage_note",
      params: {
        note: "Lid angles in the code: open lt 0 / lb 80 / rt 85 / rb 0 deg, closed lt 82 / lb 0 / rt 0 / rb 80 deg. Eye limits: y 0-70 (neutral 35), x 0-70 (neutral 30).",
        source: "protoboard/software/head/motion_controller.py",
      },
    },
  ],
};
