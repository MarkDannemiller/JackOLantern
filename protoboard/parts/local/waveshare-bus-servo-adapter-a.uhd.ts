/**
 * Waveshare Bus Servo Adapter (A), SKU 25514: USB-C or UART to the Feetech ST/SC bus, 9-12.6 V input that must
 * match the servo voltage, up to 253 servos per bus. Sources: research/sourcing/20261024-bom.json (vendor page).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerIn, PowerOut, Ground, USB } from "@deltarobotics/uhd";
import { part, feetechBus } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const WAVESHARE_BUS_SERVO_ADAPTER_A_ELECTRICAL: ModuleDef = part({
  id: "waveshare-bus-servo-adapter-a", name: "Waveshare Bus Servo Adapter (A)", manufacturer: "Waveshare", part_number: "25514",
  description: "Bridges a computer's USB to the Feetech servo bus and passes the servo supply onto the bus.",
  categories: ["actuator.servo_controller", "expansion.breakout"], tags: ["feetech", "usb"], sources: [{ id: "src_waveshare", name: "Waveshare Bus Servo Adapter (A)", url: "https://www.waveshare.com/wiki/Bus_Servo_Adapter_(A)" }],
  interfaces: [PowerIn({ id: "vin", name: "DC in", voltageV: [9, 12.6] }), Ground({ id: "gnd", name: "GND" }),
    PowerOut({ id: "bus_vplus", name: "Bus V+", voltageV: [9, 12.6] }), feetechBus("bus", "host"),
    ...USB({ id: "usb", role: "device", speeds: ["full"] })],
  traits: [{ type: "supplied_from", params: { interfaceId: "bus_vplus", via: "board", source: "vin" } }],
  dims: [42, 33, 12],
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const WAVESHARE_BUS_SERVO_ADAPTER_A: ModuleDef = withMech(WAVESHARE_BUS_SERVO_ADAPTER_A_ELECTRICAL as ModuleDef, "jj-body-bus");
