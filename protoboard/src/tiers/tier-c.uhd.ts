/**
 * Joyful Jack, tier C "Maxed" (new spend $2,159.44, no cap set; research/sourcing/20261024-bom-final.md).
 *
 * Power: tier B's dual-M18 OR plus a Mean Well 24 V mains supply as a third OR input (all-day indoor running).
 * Fuse block: out1 actuator relay -> arm 12 V bucks and head-servo buck; out2 head Pi 5 V; out3 E-stop chain;
 * out4 torso Pi 5 (5 V). The two AmazingHand 5 V bucks hang off the relay output too, so the E-stop stops
 * the hands as well as the arms. Compute: a Raspberry Pi 5 in the torso runs the arms and hands; the head keeps its Pi 4.
 * The custom power board is the next revision (a block here, not wired).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { dualPackPower, dualPackLinks } from "./tier-b.uhd";

const L = (id: string, a: [string, string], b: [string, string], name = id) => ({ id, name, a: { child: a[0], interfaceId: a[1] }, b: { child: b[0], interfaceId: b[1] } });
const gnd = ["dock_1", "lead_minus"] as [string, string];

export const JOYFUL_JACK_C: ModuleDef = {
  id: "joyful-jack-c",
  name: "Joyful Jack (tier C, Maxed)",
  kind: "module",
  description: "Pumpkin-head cowboy with humanoid hands: six-joint Feetech arms with Pollen AmazingHands, a torso Raspberry Pi 5, dual hot-swap M18 packs plus mains, battery monitoring and a relay E-stop.",
  interfaces: [],
  children: [
    { id: "head", moduleDefId: "jj-head", name: "Head (existing)" },
    { id: "base", moduleDefId: "jj-ballast-base", name: "Ballast base and mast" },
    { id: "torso", moduleDefId: "jj-torso-bc", name: "Torso" },
    ...dualPackPower([
      { id: "mains", moduleDefId: "meanwell-lrs-350-24", name: "Mains supply 24 V" },
      { id: "or_3", moduleDefId: "ideal-diode-40a", name: "Ideal diode, mains" },
      { id: "pi5", moduleDefId: "raspberry-pi-5", name: "Torso computer (Pi 5)" },
      { id: "buck_pi5", moduleDefId: "drok-300w-buck", name: "Buck, torso Pi 5 (set to 5.1 V)" },
      { id: "buck_hand_r", moduleDefId: "pololu-d36v50f5", name: "Buck, right hand (5 V)" },
      { id: "buck_hand_l", moduleDefId: "pololu-d36v50f5", name: "Buck, left hand (5 V)" },
      { id: "power_board", moduleDefId: "jj-power-board-c", name: "Custom power board (next revision)" },
    ]),
    { id: "arm_r", moduleDefId: "jj-arm-c", name: "Right arm" },
    { id: "arm_l", moduleDefId: "jj-arm-c", name: "Left arm" },
  ],
  links: [
    ...dualPackLinks(),
    L("mains_or", ["mains", "v24"], ["or_3", "vin"]), L("or3_bus", ["or_3", "vout"], ["monitor", "shunt_in"], "OR bus (mains)"),
    L("mains_gnd", gnd, ["mains", "gnd"]), L("or_3_gnd", gnd, ["or_3", "gnd"]),
    L("pi_5v", ["buck_pi", "vout"], ["head", "pi_5v_in"], "Head Pi 5 V"),
    L("head_servo_rail", ["buck_head", "vout"], ["head", "servo_vplus_in"], "Head servo rail"),
    L("head_gnd", gnd, ["head", "gnd"]),
    L("monitor_i2c", ["head", "i2c"], ["monitor", "i2c"], "I2C to the pack monitor (0x44)"),
    L("monitor_logic", ["head", "logic_3v3"], ["monitor", "vin"]),
    L("pi5_feed", ["fuses", "out4"], ["buck_pi5", "vin"]), L("pi5_5v", ["buck_pi5", "vout"], ["pi5", "usb_c_power"], "Torso Pi 5 V"),
    L("buck_pi5_gnd", gnd, ["buck_pi5", "gnd"]),
    L("hand_r_feed", ["relay", "contact_87"], ["buck_hand_r", "vin"], "Right hand behind the E-stop relay"), L("hand_l_feed", ["relay", "contact_87"], ["buck_hand_l", "vin"], "Left hand behind the E-stop relay"),
    L("hand_r_5v", ["buck_hand_r", "vout"], ["arm_r", "hand_5v"]), L("hand_l_5v", ["buck_hand_l", "vout"], ["arm_l", "hand_5v"]),
    L("buck_hand_r_gnd", gnd, ["buck_hand_r", "gnd"]), L("buck_hand_l_gnd", gnd, ["buck_hand_l", "gnd"]),
    L("hand_r_gnd", gnd, ["arm_r", "hand_gnd"]), L("hand_l_gnd", gnd, ["arm_l", "hand_gnd"]),
    L("arm_r_12v", ["buck_arm_r", "vout"], ["arm_r", "power_in"]), L("arm_l_12v", ["buck_arm_l", "vout"], ["arm_l", "power_in"]),
    L("arm_r_gnd", gnd, ["arm_r", "gnd"]), L("arm_l_gnd", gnd, ["arm_l", "gnd"]),
    L("arm_r_usb", ["pi5", "usb2_0"], ["arm_r", "usb"], "USB, right arm bus"), L("arm_l_usb", ["pi5", "usb2_1"], ["arm_l", "usb"], "USB, left arm bus"),
    L("hand_r_usb", ["pi5", "usb3_0"], ["arm_r", "hand_usb"], "USB, right hand"), L("hand_l_usb", ["pi5", "usb3_1"], ["arm_l", "hand_usb"], "USB, left hand"),
  ],
};
