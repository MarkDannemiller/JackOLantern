/**
 * PCA9685 16-channel servo driver breakout at 0x40: the head's board. Definition in lib/pca9685.ts (sources there).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { pca9685 } from "./lib/pca9685";

export const PCA9685_16CH_SERVO_DRIVER: ModuleDef = pca9685(0x40);
