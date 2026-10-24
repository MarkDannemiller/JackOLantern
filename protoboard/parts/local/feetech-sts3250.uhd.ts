/**
 * Feetech STS3250 (ST-3250-C001) 12 V: 50 kg.cm peak / 16 rated, 4.2 A stall, magnetic encoder (listing).
 * Sources: research/sourcing/20261024-bom.json (listing; no official datasheet or authorised US price found).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerIn, Ground } from "@deltarobotics/uhd";
import { part, feetechBus } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const FEETECH_STS3250_ELECTRICAL: ModuleDef = part({
  id: "feetech-sts3250", name: "Feetech STS3250 12 V serial bus servo", manufacturer: "Feetech", part_number: "ST-3250-C001",
  description: "High-torque 12 V smart servo (tier C shoulders and elbows, through 2.73:1 belt stages).",
  categories: ["actuator.motor.servo"], tags: ["servo", "feetech", "bus"], sources: [{ id: "src_listing", name: "STS3250 listing (BOM row)", url: "https://www.google.com/search?q=feetech+STS3250" }],
  interfaces: [PowerIn({ id: "bus_vplus", name: "V+ (bus)", voltageV: [6, 12], minSupplyCurrentA: 4.2 }), Ground({ id: "bus_gnd", name: "GND (bus)" }), feetechBus("bus", "device")],
  traits: [{ type: "performance", params: { kind: "servo", stall_torque_kgcm: 50, rated_torque_kgcm: 16, voltage_V: 12, source: "research/sourcing/20261024-bom.json" } }],
  dims: [45.22, 24.72, 35], mass_g: 72,
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const FEETECH_STS3250: ModuleDef = withMech(FEETECH_STS3250_ELECTRICAL as ModuleDef, "servo-sts3250");
