/**
 * PCA9685 16-channel servo driver breakout at 0x41 (A0 bridged): tier A's arm board (Adafruit 815, BOM).
 * Definition in lib/pca9685.ts (sources there).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { pca9685 } from "./lib/pca9685";

export const PCA9685_16CH_SERVO_DRIVER_0X41: ModuleDef = pca9685(0x41, "-0x41");
