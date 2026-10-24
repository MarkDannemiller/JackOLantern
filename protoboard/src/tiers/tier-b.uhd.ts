/**
 * Joyful Jack, tier B "Midrange" (new spend $1,174.95 of a $1,200 cap; research/sourcing/20261024-bom-final.md).
 *
 * Power: two M18 packs -> two docks -> two ideal diodes (OR: pull one pack while the other runs) -> INA228
 * monitor (pack voltage and current on I2C 0x44) -> XH-M609 cutoff -> 6-way fuse block:
 *   out1 -> relay contacts (coil held by the E-stop chain) -> 12 V bucks (one per arm) and the head-servo buck
 *   out2 -> Pololu 5 V -> head Pi 4 (never through the E-stop)
 *   out3 -> E-stop NC -> relay coil
 * Control: the head's Pi 4 drives each arm's Feetech bus through its own USB adapter.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { MECH } from "../mech/assembly.gen";

const L = (id: string, a: [string, string], b: [string, string], name = id) => ({ id, name, a: { child: a[0], interfaceId: a[1] }, b: { child: b[0], interfaceId: b[1] } });

export function dualPackPower(extra: { id: string; moduleDefId: string; name: string }[] = []) {
  return [
    { id: "pack_1", moduleDefId: "milwaukee-m18-pack", name: "M18 pack 1 (owned)" },
    { id: "pack_2", moduleDefId: "milwaukee-m18-pack", name: "M18 pack 2 (owned)" },
    { id: "dock_1", moduleDefId: "m18-power-wheel-adapter", name: "M18 dock 1" },
    { id: "dock_2", moduleDefId: "m18-power-wheel-adapter", name: "M18 dock 2" },
    { id: "or_1", moduleDefId: "ideal-diode-40a", name: "Ideal diode, pack 1" },
    { id: "or_2", moduleDefId: "ideal-diode-40a", name: "Ideal diode, pack 2" },
    { id: "monitor", moduleDefId: "adafruit-ina228", name: "Pack monitor (INA228, 0x44)" },
    { id: "lvc", moduleDefId: "xh-m609-lvc", name: "Low-voltage cutoff" },
    { id: "fuses", moduleDefId: "fuse-block-6way", name: "Fuse block" },
    { id: "relay", moduleDefId: "temco-relay-24v-40a", name: "Actuator relay" },
    { id: "estop", moduleDefId: "estop-22mm-nc", name: "Emergency stop" },
    { id: "buck_head", moduleDefId: "drok-300w-buck", name: "Buck, head servos (5.0 V)" },
    { id: "buck_pi", moduleDefId: "pololu-d24v50f5", name: "Buck, head Pi (5 V)" },
    { id: "buck_arm_r", moduleDefId: "ekylin-12v-20a-buck", name: "Buck, right arm (12 V)" },
    { id: "buck_arm_l", moduleDefId: "ekylin-12v-20a-buck", name: "Buck, left arm (12 V)" },
    ...extra,
  ];
}

export function dualPackLinks() {
  const gnd = ["dock_1", "lead_minus"] as [string, string];
  return [
    L("pack1_dock", ["pack_1", "pack_plus"], ["dock_1", "dock_plus"]), L("pack1_neg", ["pack_1", "pack_minus"], ["dock_1", "dock_minus"]),
    L("pack2_dock", ["pack_2", "pack_plus"], ["dock_2", "dock_plus"]), L("pack2_neg", ["pack_2", "pack_minus"], ["dock_2", "dock_minus"]),
    L("dock1_or", ["dock_1", "lead_plus"], ["or_1", "vin"]), L("dock2_or", ["dock_2", "lead_plus"], ["or_2", "vin"]),
    L("gnd_common", ["dock_1", "lead_minus"], ["dock_2", "lead_minus"], "Pack negatives joined"),
    L("or1_bus", ["or_1", "vout"], ["monitor", "shunt_in"], "OR bus (pack 1)"), L("or2_bus", ["or_2", "vout"], ["monitor", "shunt_in"], "OR bus (pack 2)"),
    L("monitor_lvc", ["monitor", "shunt_out"], ["lvc", "vin"]), L("lvc_gnd", gnd, ["lvc", "gnd"]),
    L("lvc_fuses", ["lvc", "vout"], ["fuses", "feed"]), L("fuses_gnd", gnd, ["fuses", "neg_bus"]),
    L("act_relay", ["fuses", "out1"], ["relay", "contact_30"], "Actuator feed to relay contacts"),
    L("estop_feed", ["fuses", "out3"], ["estop", "vin"]), L("estop_coil", ["estop", "vout"], ["relay", "coil_86"], "E-stop chain holds the relay"),
    L("relay_coil_gnd", gnd, ["relay", "coil_85"]),
    L("relay_arm_r", ["relay", "contact_87"], ["buck_arm_r", "vin"]), L("relay_arm_l", ["relay", "contact_87"], ["buck_arm_l", "vin"]),
    L("relay_head", ["relay", "contact_87"], ["buck_head", "vin"]),
    L("pi_feed", ["fuses", "out2"], ["buck_pi", "vin"]),
    ...["buck_head", "buck_pi", "buck_arm_r", "buck_arm_l", "or_1", "or_2"].map((b) => L(`${b}_gnd`, gnd, [b, "gnd"])),
    L("monitor_gnd", gnd, ["monitor", "gnd"]),
  ];
}

export const JOYFUL_JACK_B: ModuleDef = {
  id: "joyful-jack-b",
  name: "Joyful Jack (tier B, Midrange)",
  kind: "module",
  description: "Pumpkin-head cowboy: the existing head plus two seven-actuator Feetech arms with glove hands, two hot-swappable M18 packs, battery monitoring and a relay E-stop.",
  interfaces: [],
  children: [
    { id: "head", moduleDefId: "jj-head", name: "Head (existing)" },
    { id: "body", moduleDefId: "jj-body-b", name: "Body: base, mast, torso, neck, electronics board" },
    ...dualPackPower(),
    { id: "arm_r", moduleDefId: "jj-arm-b-r", name: "Right arm" },
    { id: "arm_l", moduleDefId: "jj-arm-b-l", name: "Left arm" },
    ...((MECH.b.root.children as unknown as NonNullable<ModuleDef["children"]>) ?? []),
  ],
  links: [
    ...dualPackLinks(),
    L("pi_5v", ["buck_pi", "vout"], ["head", "pi_5v_in"], "Pi 5 V"),
    L("head_servo_rail", ["buck_head", "vout"], ["head", "servo_vplus_in"], "Head servo rail"),
    L("head_gnd", ["dock_1", "lead_minus"], ["head", "gnd"]),
    L("monitor_i2c", ["head", "i2c"], ["monitor", "i2c"], "I2C to the pack monitor (0x44)"),
    L("monitor_logic", ["head", "logic_3v3"], ["monitor", "vin"]),
    L("arm_r_12v", ["buck_arm_r", "vout"], ["arm_r", "power_in"]), L("arm_l_12v", ["buck_arm_l", "vout"], ["arm_l", "power_in"]),
    L("arm_r_gnd", ["dock_1", "lead_minus"], ["arm_r", "gnd"]), L("arm_l_gnd", ["dock_1", "lead_minus"], ["arm_l", "gnd"]),
    L("arm_r_usb", ["head", "usb_a"], ["arm_r", "usb"], "USB to the right arm's bus"), L("arm_l_usb", ["head", "usb_b"], ["arm_l", "usb"], "USB to the left arm's bus"),
    ...((MECH.b.root.links as unknown as NonNullable<ModuleDef["links"]>) ?? []),
  ],
};
