/**
 * PCA9685 16-channel 12-bit PWM / servo driver breakout — Joyful Jack's head servo driver.
 *
 * Sources:
 *   - src_pca9685: NXP PCA9685 datasheet — https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf
 *     (16 channels, 12-bit, I2C, default all-call address 0x70, address pins A0-A5)
 *   - src_servokit: Adafruit CircuitPython ServoKit — https://docs.circuitpython.org/projects/servokit/en/latest/
 *     (ServoKit(channels=16), default address 0x40)
 *   - src_code: protoboard/software/head/motion_controller.py (ServoKit(channels=16), channels 0-9 used)
 *
 * Modelling notes:
 *   - PARTIAL, unverified. The exact breakout is not in the code or the CAD. The
 *     code drives it through Adafruit's ServoKit library, so an Adafruit 815-style
 *     breakout is likely but not confirmed (assumption trait).
 *   - Interfaces: the I2C port, logic VCC, the V+ servo terminal and the 16 servo
 *     headers. Each header's V+ comes from the V+ terminal (supplied_from).
 *   - The V+ voltage is the board's pass-through: it is set to the range both
 *     fitted servo types accept (SG90 4.8 V, DS3225MG 4.8-6.8 V), as an assumption.
 */
import type { ModuleDef, InterfaceDef } from "@deltarobotics/uhd";
import { defineModule, PowerIn, PowerOut, Ground, I2C, ServoPort } from "@deltarobotics/uhd";


const SRC = {
  pca9685: "https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf",
  servokit: "https://docs.circuitpython.org/projects/servokit/en/latest/",
} as const;

const channels: InterfaceDef[] = Array.from({ length: 16 }, (_, ch) =>
  ServoPort({ id: `ch${ch}`, name: `Channel ${ch}`, role: "output", signal: { name: `PWM${ch}` }, power: "servo_vplus", ground: "gnd", connector: "servo_3pin", gender: "header" }),
).flat();

export function pca9685(address: number, idSuffix = ""): ModuleDef {
  return defineModule({
  id: `pca9685-16ch-servo-driver${idSuffix}`,
  name: `PCA9685 16-channel servo driver breakout (0x${address.toString(16)})`,
  version: "0.1.0",
  kind: "module",
  manufacturer: "TBD (Adafruit 815 assumed)",
  part_number: "PCA9685 breakout",
  description:
    "16-channel 12-bit PWM driver on I2C (PCA9685), with a V+ terminal feeding sixteen 3-pin servo headers. Partial definition; the exact breakout is unconfirmed.",
  tags: ["pwm", "servo-driver", "i2c", "pca9685"],
  categories: ["actuator.motor_controller", "expansion.breakout"],
  artifacts: [
    { id: "src_pca9685", name: "NXP PCA9685 datasheet", type: "datasheet", url: SRC.pca9685 },
    { id: "src_servokit", name: "Adafruit CircuitPython ServoKit", type: "documentation", url: SRC.servokit },
  ],
  interfaces: [
    PowerIn({ id: "vcc", name: "VCC (logic)", voltageV: 3.3 }),
    PowerIn({ id: "vplus_in", name: "V+ terminal (servo supply)", voltageV: [4.8, 6.0] }),
    PowerOut({ id: "servo_vplus", name: "V+ to servo headers", voltageV: [4.8, 6.0] }),
    Ground({ id: "gnd", name: "GND" }),
    ...I2C({ id: "i2c", name: "I2C", roles: ["slave"], address, otherAddresses: { all_call: 0x70 }, sda: { name: "SDA" }, scl: { name: "SCL" } }),
    ...channels,
  ],
  traits: [
    { type: "supplied_from", params: { interfaceId: "servo_vplus", via: "board trace", source: "vplus_in" } },
    { type: "assumption", params: { field: "board", value: "Adafruit 815-style PCA9685 breakout", reason: "The code uses Adafruit's ServoKit; no board is named in the code or the CAD." } },
    { type: "assumption", params: { field: "vcc", value: "3.3 V", reason: "Logic fed from the Pi's 3.3 V header rail (the Pi's I2C is 3.3 V); wiring not documented." } },
    { type: "assumption", params: { field: "V+ voltage", value: "4.8-6.0 V", reason: "Pass-through to the servos: the range both fitted servo types accept. The head's actual servo supply is not documented." } },
    { type: "usage_note", params: { note: "I2C address 0x40 is ServoKit's default and the PCA9685 power-on default with A0-A5 low; a second board takes 0x41 (A0 bridged).", source: SRC.servokit } },
  ],
}) as ModuleDef;
}
