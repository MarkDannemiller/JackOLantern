/**
 * Helpers for Joyful Jack's project-researched parts (not a part definition; parts/local/*.uhd.ts import it).
 * Every fact passed in carries its source in the calling file; these only shape the interfaces.
 */
import type { InterfaceDef, ModuleDef, TraitDef } from "@deltarobotics/uhd";
import { defineModule, PowerIn, PowerOut, Ground, ServoPort } from "@deltarobotics/uhd";

export const BOM = "research/sourcing/20261024-bom.json";

/** Feetech SCS/STS half-duplex TTL serial servo bus. UHD has no protocol for it (logged vocabulary gap): `custom` + capability. */
export function feetechBus(id: string, role: "host" | "device", name = "Feetech TTL bus"): InterfaceDef {
  return {
    id,
    name,
    domain: "electrical",
    exposed: true,
    protocols: [{ type: "custom", roles: [role] }],
    capabilities: ["feetech_scs_bus"],
    traits: [{ type: "usage_note", params: { note: "Feetech SCS/STS half-duplex TTL serial bus (signal, V+, GND on a 3-pin cable), 1 Mbps default, daisy-chained; every servo has an ID.", source: "https://www.waveshare.com/wiki/Bus_Servo_Adapter_(A)" } }],
  };
}

export interface PartSpec {
  id: string;
  name: string;
  manufacturer: string;
  part_number: string;
  description: string;
  categories: string[];
  tags?: string[];
  sources: { id: string; name: string; url: string }[];
  interfaces: InterfaceDef[];
  traits?: TraitDef[];
  mass_g?: number;
  dims?: [number, number, number];
}

export function part(p: PartSpec): ModuleDef {
  return defineModule({
    id: p.id,
    name: p.name,
    version: "0.1.0",
    kind: "module",
    manufacturer: p.manufacturer,
    part_number: p.part_number,
    description: p.description,
    tags: p.tags ?? [],
    categories: p.categories,
    artifacts: p.sources.map((s) => ({ id: s.id, name: s.name, type: "documentation", url: s.url })),
    interfaces: p.interfaces,
    traits: p.traits ?? [],
    domains: p.dims || p.mass_g
      ? [{ domain: "mechanical", ...(p.dims ? { dimensions_mm: { length: p.dims[0], width: p.dims[1], height: p.dims[2] } } : {}), ...(p.mass_g ? { weight_g: p.mass_g } : {}) }]
      : [],
  }) as ModuleDef;
}

/** A hobby PWM servo: 3-wire servo port, supply range from its datasheet. */
export function hobbyServo(p: Omit<PartSpec, "interfaces"> & { voltage: [number, number] }): ModuleDef {
  return part({
    ...p,
    interfaces: [
      PowerIn({ id: "lead_vplus", name: "V+ (red)", voltageV: p.voltage }),
      Ground({ id: "lead_gnd", name: "GND (brown)" }),
      ...ServoPort({ id: "rc_servo_3wire", role: "input", signal: { name: "SIG" }, power: "lead_vplus", ground: "lead_gnd", connector: "servo_3pin", gender: "plug" }),
    ],
  });
}

/** A two-terminal power stage (buck, ideal diode, fuse, switch): input, output, ground. */
export function powerStage(p: Omit<PartSpec, "interfaces"> & { vin: number | [number, number]; vout: number | [number, number]; iout?: number; ground?: boolean }): ModuleDef {
  return part({
    ...p,
    interfaces: [
      PowerIn({ id: "vin", name: "IN+", voltageV: p.vin }),
      PowerOut({ id: "vout", name: "OUT+", voltageV: p.vout, ...(p.iout ? { maxCurrentA: p.iout } : {}) }),
      ...(p.ground === false ? [] : [Ground({ id: "gnd", name: "GND" })]),
    ],
  });
}
