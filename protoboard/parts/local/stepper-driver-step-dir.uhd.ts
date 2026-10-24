/**
 * Step/direction stepper driver (model TBD) — Joyful Jack's neck yaw driver.
 *
 * Sources:
 *   - src_code: protoboard/software/head/motion_controller.py, pid_stepper.py
 *     (STEP on BCM26, DIR on BCM19, ENABLE on BCM13; ENABLE high disables the motor)
 *
 * Modelling notes:
 *   - PARTIAL, unverified: the driver is not named in the code or the CAD. Its
 *     step/dir input and enable polarity come from the code; the motor supply is
 *     a data gap, so no supply interface is declared yet.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { defineModule, StepDir, StepperPhases, Ground } from "@deltarobotics/uhd";

export const STEPPER_DRIVER_STEP_DIR = defineModule({
  id: "stepper-driver-step-dir",
  name: "Step/dir stepper driver (model TBD)",
  version: "0.1.0",
  kind: "module",
  manufacturer: "TBD",
  part_number: "TBD",
  description: "Bipolar stepper driver with STEP, DIR and active-low ENABLE inputs. Partial definition; model unconfirmed.",
  tags: ["stepper-driver", "step-dir"],
  categories: ["actuator.motor_controller"],
  interfaces: [
    ...StepDir({ id: "step_dir", name: "STEP/DIR/EN", role: "input", step: { name: "STEP" }, dir: { name: "DIR" }, enable: { name: "EN" }, voltageV: 3.3, enableActive: "low" }),
    ...StepperPhases({ id: "motor", name: "Motor", role: "output", winding: "bipolar" }),
    Ground({ id: "gnd", name: "GND" }),
  ],
  traits: [
    { type: "data_gap", params: { field: "model, motor supply voltage and current, microstep setting", note: "Not in the code or the CAD. 3200 steps/rev in the code suggests 1/16 microstepping." } },
    { type: "usage_note", params: { note: "ENABLE high disables the outputs (GPIO.output(enable_pin, HIGH) # disable).", source: "protoboard/software/head/pid_stepper.py" } },
  ],
}) as ModuleDef;
