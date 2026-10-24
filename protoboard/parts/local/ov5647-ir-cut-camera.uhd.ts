/**
 * OV5647 IR-cut camera module (5 MP, 2-lane MIPI CSI-2) — Joyful Jack's face-tracking camera.
 *
 * Sources:
 *   - src_rpi_camera: Raspberry Pi camera documentation (Camera Module v1 is the OV5647) —
 *     https://www.raspberrypi.com/documentation/accessories/camera.html
 *   - src_cad: inbox/20261024-head-assembly.f3z, component "OV5647 IR-Cut Camera" (2023-09-21)
 *
 * Modelling notes:
 *   - PARTIAL, unverified. The CAD names the sensor and the IR-cut filter, not the
 *     module vendor. Only the camera port is modelled; mounting comes with the CAD
 *     binding.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { defineModule, CSI2 } from "@deltarobotics/uhd";

export const OV5647_IR_CUT_CAMERA = defineModule({
  id: "ov5647-ir-cut-camera",
  name: "OV5647 IR-cut camera module",
  version: "0.1.0",
  kind: "module",
  manufacturer: "TBD",
  part_number: "OV5647 IR-cut (vendor TBD)",
  description: "5 MP OV5647 camera module with switchable IR-cut filter, 2-lane MIPI CSI-2 over a 15-pin FFC. Partial definition; vendor unconfirmed.",
  tags: ["camera", "ov5647", "csi"],
  categories: ["sensor.camera"],
  artifacts: [{ id: "src_rpi_camera", name: "Raspberry Pi camera documentation", type: "documentation", url: "https://www.raspberrypi.com/documentation/accessories/camera.html" }],
  interfaces: [...CSI2({ id: "csi", name: "CSI-2 (FFC)", role: "transmitter", lanes: 2 })],
  traits: [
    { type: "data_gap", params: { field: "vendor, IR-cut control pin, IR illuminators", note: "Not in the code or the CAD component name." } },
  ],
}) as ModuleDef;
