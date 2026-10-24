/**
 * Joyful Jack, tier A "Beginner" (new spend $498.05 of a $500 cap; research/sourcing/20261024-bom-final.md).
 *
 * Power: M18 pack -> dock (switch, 30 A fuse) -> XH-M609 low-voltage cutoff -> three inline fuses:
 *   Pi branch      fuse_pi   -> DROK set to 5.1 V   -> head Pi 4 (never through the E-stop)
 *   head servos    E-stop -> fuse_head -> DROK set to 5.0 V -> head PCA9685 V+
 *   arm servos     E-stop -> fuse_arm  -> DROK set to 6.8 V -> arm PCA9685 (0x41) V+
 * The E-stop's 10 A NC contact breaks the 18 V input of both servo bucks (input current stays under 10 A).
 * Control: the head's Pi 4 drives the arm PCA9685 at 0x41 on the same I2C bus as the head's board at 0x40.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { MECH } from "../mech/assembly.gen";

const ARM_CH: [string, string, number][] = [
  ["arm_r", "shoulder_flex_servo", 0], ["arm_r", "shoulder_out_servo", 1], ["arm_r", "elbow_servo", 2], ["arm_r", "grip_servo", 3],
  ["arm_l", "shoulder_flex_servo", 4], ["arm_l", "shoulder_out_servo", 5], ["arm_l", "elbow_servo", 6], ["arm_l", "grip_servo", 7],
];
const L = (id: string, a: [string, string], b: [string, string], name = id) => ({ id, name, a: { child: a[0], interfaceId: a[1] }, b: { child: b[0], interfaceId: b[1] } });

export const JOYFUL_JACK_A: ModuleDef = {
  id: "joyful-jack-a",
  name: "Joyful Jack (tier A, Beginner)",
  kind: "module",
  description: "Pumpkin-head cowboy on a ballasted pole: the existing head plus two four-joint hobby-servo arms with mitt hands, one M18 pack.",
  interfaces: [],
  children: [
    { id: "head", moduleDefId: "jj-head", name: "Head (existing)" },
    { id: "body", moduleDefId: "jj-body-a", name: "Body: base, mast, torso, neck, electronics board" },
    { id: "pack", moduleDefId: "milwaukee-m18-pack", name: "M18 pack (owned)" },
    { id: "dock", moduleDefId: "m18-power-wheel-adapter", name: "M18 dock" },
    { id: "lvc", moduleDefId: "xh-m609-lvc", name: "Low-voltage cutoff" },
    { id: "estop", moduleDefId: "estop-22mm-nc", name: "Emergency stop" },
    { id: "fuse_pi", moduleDefId: "inline-atc-fuse", name: "Fuse, Pi (5 A)" },
    { id: "fuse_head", moduleDefId: "inline-atc-fuse", name: "Fuse, head servos (5 A)" },
    { id: "fuse_arm", moduleDefId: "inline-atc-fuse", name: "Fuse, arm servos (10 A)" },
    { id: "buck_pi", moduleDefId: "drok-300w-buck", name: "Buck, Pi (5.1 V)" },
    { id: "buck_head", moduleDefId: "drok-300w-buck", name: "Buck, head servos (5.0 V)" },
    { id: "buck_arm", moduleDefId: "drok-300w-buck", name: "Buck, arm servos (6.8 V)" },
    { id: "arm_driver", moduleDefId: "pca9685-16ch-servo-driver-0x41", name: "Arm servo driver (0x41)" },
    { id: "arm_r", moduleDefId: "jj-arm-a-r", name: "Right arm" },
    { id: "arm_l", moduleDefId: "jj-arm-a-l", name: "Left arm" },
    ...((MECH.a.root.children as unknown as NonNullable<ModuleDef["children"]>) ?? []),
  ],
  links: [
    L("pack_dock", ["pack", "pack_plus"], ["dock", "dock_plus"]),
    L("pack_dock_neg", ["pack", "pack_minus"], ["dock", "dock_minus"]),
    L("dock_lvc", ["dock", "lead_plus"], ["lvc", "vin"]),
    L("lvc_gnd", ["dock", "lead_minus"], ["lvc", "gnd"]),
    L("lvc_fuse_pi", ["lvc", "vout"], ["fuse_pi", "vin"]),
    L("lvc_estop", ["lvc", "vout"], ["estop", "vin"]),
    L("estop_fuse_head", ["estop", "vout"], ["fuse_head", "vin"]),
    L("estop_fuse_arm", ["estop", "vout"], ["fuse_arm", "vin"]),
    L("fuse_buck_pi", ["fuse_pi", "vout"], ["buck_pi", "vin"]),
    L("fuse_buck_head", ["fuse_head", "vout"], ["buck_head", "vin"]),
    L("fuse_buck_arm", ["fuse_arm", "vout"], ["buck_arm", "vin"]),
    ...["buck_pi", "buck_head", "buck_arm"].map((b) => L(`${b}_gnd`, ["dock", "lead_minus"], [b, "gnd"])),
    L("pi_5v", ["buck_pi", "vout"], ["head", "pi_5v_in"], "Pi 5.1 V"),
    L("head_servo_rail", ["buck_head", "vout"], ["head", "servo_vplus_in"], "Head servo rail"),
    L("head_gnd", ["dock", "lead_minus"], ["head", "gnd"]),
    L("arm_rail", ["buck_arm", "vout"], ["arm_driver", "vplus_in"], "Arm servo rail"),
    L("arm_driver_i2c", ["head", "i2c"], ["arm_driver", "i2c"], "I2C to the arm driver (0x41)"),
    L("arm_driver_logic", ["head", "logic_3v3"], ["arm_driver", "vcc"]),
    L("arm_driver_gnd", ["head", "gnd"], ["arm_driver", "gnd"]),
    ...ARM_CH.map(([arm, port, ch]) => L(`ch${ch}`, ["arm_driver", `ch${ch}`], [arm, port], `Arm driver ch${ch} -> ${arm} ${port}`)),
    ...((MECH.a.root.links as unknown as NonNullable<ModuleDef["links"]>) ?? []),
  ],
};
