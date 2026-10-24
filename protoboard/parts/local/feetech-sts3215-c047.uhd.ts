/**
 * Feetech STS3215 12 V (ST3215-C047, Seeed 108090003): 30 kg.cm stall / 10 rated at 12 V, 1:345 metal gears,
 * 12-bit magnetic encoder, 0.222 s/60 deg, 2.7 A stall, 200 mA no load. The SO-100/SO-101 arm's servo.
 * Sources: research/sourcing/20261024-bom.json (Seeed/Waveshare pages, verified).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerIn, Ground } from "@deltarobotics/uhd";
import { part, feetechBus } from "./lib/jj";

export const FEETECH_STS3215_C047: ModuleDef = part({
  id: "feetech-sts3215-c047", name: "Feetech STS3215 12 V serial bus servo", manufacturer: "Feetech", part_number: "ST3215-C047",
  description: "12 V smart servo on a daisy-chained serial bus: reports position, speed, load, voltage and temperature.",
  categories: ["actuator.motor.servo"], tags: ["servo", "feetech", "bus"], sources: [{ id: "src_seeed", name: "Seeed 108090003", url: "https://www.seeedstudio.com/" }, { id: "src_waveshare", name: "Waveshare ST3215", url: "https://www.waveshare.com/wiki/ST3215_Servo" }],
  interfaces: [PowerIn({ id: "bus_vplus", name: "V+ (bus)", voltageV: [6, 12.6], minSupplyCurrentA: 2.7 }), Ground({ id: "bus_gnd", name: "GND (bus)" }), feetechBus("bus", "device")],
  traits: [{ type: "performance", params: { kind: "servo", stall_torque_kgcm: 30, rated_torque_kgcm: 10, voltage_V: 12, gear_ratio: 345, encoder_bits: 12, source: "research/sourcing/20261024-bom.json" } }],
  dims: [45.2, 24.7, 35], mass_g: 55,
});
