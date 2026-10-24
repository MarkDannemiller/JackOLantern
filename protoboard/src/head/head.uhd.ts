/**
 * Joyful Jack's head, as built in 2023 (Fusion "Head Assembly" v79 and "Facade" v61).
 *
 * Sources:
 *   - inbox/20261024-head-assembly.f3z / .stp: ENDO_SKULL, ENDO_JAW, two DS3225MG (jaw),
 *     Raspberry Pi 4 Model B, Neck Design 3, Simplified 3D Printed Animatronic Dual Eye
 *     Mechanism, OV5647 IR-Cut Camera. User parameters HEAD_DIAM 180 mm, JAW_WIDTH 140 mm.
 *   - inbox/20261024-facade.f3z / .stp: FACE, LEFT, RIGHT, HEAD BACK and CAP facade panels.
 *   - protoboard/software/head/motion_controller.py: the PCA9685 channel map and Pi GPIO.
 *
 * PCA9685 channels: 0 eye_y, 1 eye_x, 2-5 lids (tl, tr, bl, br), 6 jaw_l, 7 jaw_r,
 * 8 neck_l, 9 neck_r; 10-15 free. Pi GPIO (BCM): 26 STEP, 19 DIR, 13 EN, 22 home,
 * 23 / 24 eye LEDs.
 *
 * Boundary (what the torso must supply): 5 V for the Pi, the servo V+ supply and
 * ground. The yaw driver's motor supply is a data gap until head power is designed.
 */
import type { ModuleDef } from "@deltarobotics/uhd";

const servoLinks: [number, { child: string; interfaceId: string }][] = [
  [0, { child: "eyes", interfaceId: "eye_y_servo" }],
  [1, { child: "eyes", interfaceId: "eye_x_servo" }],
  [2, { child: "eyes", interfaceId: "lid_tl_servo" }],
  [3, { child: "eyes", interfaceId: "lid_tr_servo" }],
  [4, { child: "eyes", interfaceId: "lid_bl_servo" }],
  [5, { child: "eyes", interfaceId: "lid_br_servo" }],
  [6, { child: "jaw_l", interfaceId: "rc_servo_3wire" }],
  [7, { child: "jaw_r", interfaceId: "rc_servo_3wire" }],
  [8, { child: "neck", interfaceId: "pitch_l_servo" }],
  [9, { child: "neck", interfaceId: "pitch_r_servo" }],
];

export const HEAD: ModuleDef = {
  id: "jj-head",
  name: "Head",
  kind: "module",
  description:
    "Pumpkin head: printed endoskeleton (180 mm head diameter) with a servo jaw, a six-servo eye mechanism, a two-axis neck, a face-tracking camera and LED eyes, run by a Raspberry Pi 4 and a PCA9685 servo driver, under printed facade panels.",
  tags: ["head", "animatronic"],
  categories: ["robotics"],
  interfaces: [],
  children: [
    { id: "computer", moduleDefId: "raspberry-pi-4-model-b", name: "Head computer" },
    { id: "servo_driver", moduleDefId: "pca9685-16ch-servo-driver", name: "Servo driver" },
    { id: "camera", moduleDefId: "ov5647-ir-cut-camera", name: "Camera" },
    { id: "eyes", moduleDefId: "jj-eye-mechanism", name: "Eye mechanism" },
    { id: "jaw_l", moduleDefId: "dsservo-ds3225mg-270", name: "Jaw servo, left" },
    { id: "jaw_r", moduleDefId: "dsservo-ds3225mg-270", name: "Jaw servo, right" },
    { id: "neck", moduleDefId: "jj-neck", name: "Neck" },
  ],
  links: [
    { id: "i2c_servo_driver", name: "I2C to servo driver", a: { child: "computer", interfaceId: "i2c1" }, b: { child: "servo_driver", interfaceId: "i2c" } },
    { id: "servo_driver_logic", name: "Servo driver logic supply", a: { child: "computer", interfaceId: "rail_3v3" }, b: { child: "servo_driver", interfaceId: "vcc" } },
    { id: "servo_driver_gnd", name: "Servo driver ground", a: { child: "computer", interfaceId: "gnd" }, b: { child: "servo_driver", interfaceId: "gnd" } },
    { id: "camera_csi", name: "Camera FFC", a: { child: "computer", interfaceId: "csi" }, b: { child: "camera", interfaceId: "csi" } },
    ...servoLinks.map(([ch, to]) => ({ id: `servo_ch${ch}`, name: `PCA9685 channel ${ch}`, a: { child: "servo_driver", interfaceId: `ch${ch}` }, b: to })),
    {
      id: "yaw_step_dir",
      name: "Yaw STEP/DIR/EN (BCM26/19/13)",
      a: { child: "computer", interfaceId: "yaw_gpio", compose: { step: "gpio26", dir: "gpio19", enable: "gpio13" } },
      b: { child: "neck", interfaceId: "yaw_step_dir" },
    },
    { id: "yaw_driver_gnd", name: "Yaw driver logic ground", a: { child: "computer", interfaceId: "gnd" }, b: { child: "neck", interfaceId: "yaw_driver_gnd" } },
    { id: "yaw_home", name: "Yaw home switch (BCM22)", a: { child: "neck", interfaceId: "yaw_home_signal" }, b: { child: "computer", interfaceId: "gpio22" } },
  ],
  exports: [
    { id: "pi_5v_in", name: "Pi 5 V in", from: { child: "computer", interfaceId: "usbc_5v" } },
    { id: "servo_vplus_in", name: "Servo V+ in", from: { child: "servo_driver", interfaceId: "vplus_in" } },
    { id: "gnd", name: "GND", from: { child: "computer", interfaceId: "gnd" } },
    { id: "i2c", name: "Pi I2C1 (shared bus)", from: { child: "computer", interfaceId: "i2c1" } },
    { id: "logic_3v3", name: "Pi 3V3", from: { child: "computer", interfaceId: "rail_3v3" } },
    { id: "usb_a", name: "Pi USB 2.0 port 1", from: { child: "computer", interfaceId: "usb2_0" } },
    { id: "usb_b", name: "Pi USB 2.0 port 2", from: { child: "computer", interfaceId: "usb2_1" } },
  ],
  traits: [
    { type: "data_gap", params: { field: "eye LEDs", note: "GPIO23 and GPIO24 switch the left and right eye LEDs (gpiozero LED, active high). The LED type and any drive transistor or resistor are not in the code or the CAD, so no part is modelled." } },
    { type: "data_gap", params: { field: "home switch supply", note: "The code drives channel 31 high as the switch's 3.3 V source in BCM mode, which is not a header GPIO (header pin 31 is GPIO6). The switch COM is left unlinked until the wiring is confirmed." } },
    { type: "data_gap", params: { field: "audio", note: "Voice lines play through pygame; the audio output, amplifier and speaker are not documented." } },
    { type: "usage_note", params: { note: "Jaw: closed -3 deg, open 22 deg, max 100 deg/s, 270 deg actuation range on channels 6 and 7.", source: "protoboard/software/head/motion_controller.py" } },
  ],
};
