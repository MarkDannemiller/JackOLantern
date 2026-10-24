/**
 * Raspberry Pi Ltd Raspberry Pi 4 Model B — Joyful Jack's head computer.
 *
 * Sources:
 *   - src_brief: Raspberry Pi 4 Model B product brief — https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-product-brief.pdf
 *   - src_gpio:  Raspberry Pi documentation, GPIO and the 40-pin header — https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
 *
 * Modelling notes:
 *   - PARTIAL definition, not yet verified (uhd-part-research / uhd-part-verify
 *     are level-4 work). It declares only the header pins and ports the head
 *     uses (protoboard/software/head/*.py), plus power, the camera port and the two USB 2.0 ports (product brief: 2x USB 3.0, 2x USB 2.0).
 *     The other GPIO, USB, Ethernet, HDMI and the radios are left out.
 *   - GPIO leaves are named by BCM number (the code uses GPIO.BCM); `pin` is the
 *     physical header position.
 *   - GPIO5 and GPIO6 (header pins 29 and 31) are declared because the code
 *     drives "29" and "31" high as 3.3 V sources for the yaw driver and the
 *     limit switch, but in BCM mode (see the data_gap trait).
 *   - No CAD bound yet: the board sits in the head STEP
 *     (inbox/20261024-head-assembly.stp, "Raspberry Pi 4 Model B v2").
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { defineModule, PowerIn, PowerOut, Ground, Pin, I2C, CSI2, USB } from "@deltarobotics/uhd";

const SRC = {
  brief: "https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-product-brief.pdf",
  gpio: "https://www.raspberrypi.com/documentation/computers/raspberry-pi.html",
} as const;

const gpio = (bcm: number, pin: number) => Pin({ id: `gpio${bcm}`, name: `GPIO${bcm}`, pin, voltageV: 3.3 });

export const RASPBERRY_PI_4_MODEL_B = defineModule({
  id: "raspberry-pi-4-model-b",
  name: "Raspberry Pi 4 Model B",
  version: "0.1.0",
  kind: "module",
  manufacturer: "Raspberry Pi Ltd",
  part_number: "Raspberry Pi 4 Model B",
  description:
    "Single-board computer, quad-core Cortex-A72, 40-pin GPIO header (3.3 V logic), 2-lane MIPI CSI-2 camera port, 5 V USB-C power (3 A minimum). Partial definition: only what Joyful Jack's head uses.",
  tags: ["sbc", "raspberry-pi", "linux"],
  categories: ["microcontroller.single_board_computer"],
  artifacts: [
    { id: "src_brief", name: "Raspberry Pi 4 Model B product brief", type: "datasheet", url: SRC.brief },
    { id: "src_gpio", name: "Raspberry Pi documentation: GPIO", type: "documentation", url: SRC.gpio },
  ],
  interfaces: [
    PowerIn({ id: "usbc_5v", name: "5 V (USB-C)", voltageV: 5, minSupplyCurrentA: 3 }),
    PowerOut({ id: "rail_3v3", name: "3V3 (header pins 1, 17)", pin: 1, voltageV: 3.3 }),
    Ground({ id: "gnd", name: "GND" }),
    ...I2C({ id: "i2c1", name: "I2C1", roles: ["master"], voltageV: 3.3, sda: { pin: 3, name: "GPIO2 (SDA1)" }, scl: { pin: 5, name: "GPIO3 (SCL1)" } }),
    gpio(5, 29),
    gpio(6, 31),
    gpio(13, 33),
    gpio(19, 35),
    gpio(22, 15),
    gpio(23, 16),
    gpio(24, 18),
    gpio(26, 37),
    ...CSI2({ id: "csi", name: "Camera (CSI-2)", role: "receiver", lanes: 2 }),
    ...USB({ id: "usb2_0", name: "USB 2.0 port 1", role: "host", speeds: ["low", "full", "high"] }),
    ...USB({ id: "usb2_1", name: "USB 2.0 port 2", role: "host", speeds: ["low", "full", "high"] }),
  ],
  traits: [
    { type: "data_gap", params: { field: "audio output", note: "The head plays voice lines through pygame; which output (3.5 mm jack, HDMI or USB) and what amplifier and speaker are not in the code or the CAD." } },
    {
      type: "data_gap",
      params: {
        field: "GPIO5/GPIO6 use",
        note: "motion_controller.py calls GPIO.setmode(GPIO.BCM) and then sets channels 29 and 31 high as 3.3 V sources. In BCM numbering there is no GPIO29 or GPIO31 on the header; header pins 29 and 31 are GPIO5 and GPIO6. Which wiring was meant is unconfirmed.",
      },
    },
  ],
  domains: [{ domain: "electrical", metadata: { logic_voltage: "3.3 V (GPIO)", source: SRC.gpio } }],
}) as ModuleDef;
