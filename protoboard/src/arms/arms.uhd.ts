/**
 * Joyful Jack's arms, one module per tier (designed here; geometry in cad/joyful_jack_cad.py, sizing in cad/analysis.py).
 *
 * Tier A: four hobby PWM servos (shoulder flex, shoulder out, elbow, mitt grip) on tier A's second PCA9685.
 * Tier B: seven Feetech STS3215 on one bus adapter per arm; shoulder flex, shoulder out and elbow through
 *         22:60 GT2 belt stages (2.73:1) with a counterbalance spring at the shoulder; glove hand of fingers + thumb.
 * Tier C: six joints (STS3250 at shoulder flex, shoulder out and elbow through the same belt stages; STS3215 at
 *         upper-arm twist, wrist twist and wrist pitch) and a Pollen AmazingHand with its own 5 V supply and USB.
 */
import type { ModuleDef } from "@deltarobotics/uhd";

const A_JOINTS = [
  ["shoulder_flex", "dsservo-ds3235", "Shoulder flex (DS3235)"],
  ["shoulder_out", "dsservo-ds3235", "Shoulder out (DS3235)"],
  ["elbow", "dsservo-ds3225mg-270", "Elbow (DS3225MG)"],
  ["grip", "towerpro-mg996r", "Mitt grip (MG996R)"],
] as const;

export const ARM_A: ModuleDef = {
  id: "jj-arm-a",
  name: "Arm, tier A (4 hobby servos, mitt hand)",
  kind: "module",
  description: "Four-joint arm on hobby PWM servos with printed brackets and orange shells; a one-servo cartoon mitt. Shoulder spring counterbalance (cad/analysis.py: the servo alone cannot hold the arm straight out).",
  categories: ["robotics"],
  tags: ["arm", "tier-a"],
  interfaces: [],
  children: A_JOINTS.map(([id, def, name]) => ({ id, moduleDefId: def, name })),
  links: [],
  exports: A_JOINTS.map(([id, , name]) => ({ id: `${id}_servo`, name: `${name} servo`, from: { child: id, interfaceId: "rc_servo_3wire" } })),
};

function busArm(id: string, name: string, description: string, joints: [string, string, string][], hand: boolean): ModuleDef {
  return {
    id,
    name,
    kind: "module",
    description,
    categories: ["robotics"],
    tags: ["arm"],
    interfaces: [],
    children: [
      { id: "bus_adapter", moduleDefId: "waveshare-bus-servo-adapter-a", name: "Bus adapter" },
      ...joints.map(([jid, def, jname]) => ({ id: jid, moduleDefId: def, name: jname })),
      ...(hand ? [{ id: "hand", moduleDefId: "pollen-amazinghand-kit", name: "AmazingHand" }] : []),
    ],
    links: joints.flatMap(([jid]) => [
      { id: `${jid}_bus`, name: `${jid} bus`, a: { child: "bus_adapter", interfaceId: "bus" }, b: { child: jid, interfaceId: "bus" } },
      { id: `${jid}_vplus`, name: `${jid} V+`, a: { child: "bus_adapter", interfaceId: "bus_vplus" }, b: { child: jid, interfaceId: "bus_vplus" } },
      { id: `${jid}_gnd`, name: `${jid} GND`, a: { child: "bus_adapter", interfaceId: "gnd" }, b: { child: jid, interfaceId: "bus_gnd" } },
    ]),
    exports: [
      { id: "power_in", name: "12 V in", from: { child: "bus_adapter", interfaceId: "vin" } },
      { id: "gnd", name: "GND", from: { child: "bus_adapter", interfaceId: "gnd" } },
      { id: "usb", name: "USB to the computer", from: { child: "bus_adapter", interfaceId: "usb" } },
      ...(hand
        ? [
            { id: "hand_5v", name: "Hand 5 V in", from: { child: "hand", interfaceId: "v5" } },
            { id: "hand_gnd", name: "Hand GND", from: { child: "hand", interfaceId: "gnd" } },
            { id: "hand_usb", name: "Hand USB", from: { child: "hand", interfaceId: "usb" } },
          ]
        : []),
    ],
  };
}

export const ARM_B: ModuleDef = busArm(
  "jj-arm-b",
  "Arm, tier B (7 Feetech STS3215, glove hand)",
  "Six-joint arm plus a two-actuator glove hand on Feetech STS3215 serial servos (position, load and temperature feedback). Shoulder flex, shoulder out and elbow through 2.73:1 GT2 belt stages; shoulder spring counterbalance.",
  [
    ["shoulder_flex", "feetech-sts3215-c047", "Shoulder flex (STS3215, 2.73:1 belt)"],
    ["shoulder_out", "feetech-sts3215-c047", "Shoulder out (STS3215, 2.73:1 belt)"],
    ["upper_twist", "feetech-sts3215-c047", "Upper-arm twist (STS3215)"],
    ["elbow", "feetech-sts3215-c047", "Elbow (STS3215, 2.73:1 belt)"],
    ["wrist_twist", "feetech-sts3215-c047", "Wrist twist (STS3215)"],
    ["fingers", "feetech-sts3215-c047", "Four linked fingers (STS3215)"],
    ["thumb", "feetech-sts3215-c047", "Thumb (STS3215)"],
  ],
  false,
);

export const ARM_C: ModuleDef = busArm(
  "jj-arm-c",
  "Arm, tier C (6 Feetech joints, AmazingHand)",
  "Six-joint arm (STS3250 through 2.73:1 belts at shoulder flex, shoulder out and elbow; STS3215 at upper-arm twist, wrist twist and wrist pitch) with a Pollen AmazingHand: four two-jointed fingers.",
  [
    ["shoulder_flex", "feetech-sts3250", "Shoulder flex (STS3250, 2.73:1 belt)"],
    ["shoulder_out", "feetech-sts3250", "Shoulder out (STS3250, 2.73:1 belt)"],
    ["upper_twist", "feetech-sts3215-c047", "Upper-arm twist (STS3215)"],
    ["elbow", "feetech-sts3250", "Elbow (STS3250, 2.73:1 belt)"],
    ["wrist_twist", "feetech-sts3215-c047", "Wrist twist (STS3215)"],
    ["wrist_pitch", "feetech-sts3215-c047", "Wrist pitch (STS3215)"],
  ],
  true,
);
