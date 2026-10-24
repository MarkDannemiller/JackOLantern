/**
 * Adafruit INA228 85 V 20-bit power monitor breakout (STEMMA QT), 15 mOhm shunt, 10 A.
 * Sources: research/sourcing/20261024-bom.json. Address 0x40 by default: strapped to 0x44 here so it does not
 * collide with the head's PCA9685 at 0x40 (assumption: A0/A1 jumpers).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerIn, PowerOut, Ground, I2C } from "@deltarobotics/uhd";
import { part } from "./lib/jj";

export const ADAFRUIT_INA228: ModuleDef = part({
  id: "adafruit-ina228", name: "Adafruit INA228 power monitor (0x44)", manufacturer: "Adafruit Industries", part_number: "INA228 breakout",
  description: "Measures pack voltage and current on I2C, so Jack can warn before the pack runs out.",
  categories: ["power.monitor", "expansion.breakout"], tags: ["ina228", "i2c"], sources: [{ id: "src_adafruit", name: "Adafruit INA228", url: "https://www.adafruit.com/product/5832" }],
  interfaces: [PowerIn({ id: "vin", name: "VIN (logic)", voltageV: [3.3, 5] }), Ground({ id: "gnd", name: "GND" }),
    PowerIn({ id: "shunt_in", name: "Shunt IN+", voltageV: [0, 85] }), PowerOut({ id: "shunt_out", name: "Shunt IN-", voltageV: [0, 85], maxCurrentA: 10 }),
    ...I2C({ id: "i2c", roles: ["slave"], address: 0x44, sda: { name: "SDA" }, scl: { name: "SCL" } })],
  traits: [
    { type: "supplied_from", params: { interfaceId: "shunt_out", via: "15 mOhm shunt", source: "shunt_in" } },
    { type: "assumption", params: { field: "I2C address", value: "0x44", reason: "Default 0x40 collides with the head PCA9685; set by the address jumpers." } },
  ],
});
