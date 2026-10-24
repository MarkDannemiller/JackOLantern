/**
 * DSSERVO DS3235 35 kg coreless digital servo (DIYmall listing): 5-7.4 V; 29 / 32 / 35 kg.cm at 5 / 6 / 7.4 V.
 * Sources: research/sourcing/20261024-bom.json (datasheet via listing).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { hobbyServo } from "./lib/jj";

export const DSSERVO_DS3235: ModuleDef = hobbyServo({
  id: "dsservo-ds3235", name: "DSSERVO DS3235 35 kg servo", manufacturer: "DSSERVO", part_number: "DS3235",
  description: "Standard-size coreless metal-gear digital servo: 32 kg.cm stall at 6 V, 35 at 7.4 V; 0.12 s/60 deg at 6 V.",
  categories: ["actuator.motor.servo"], tags: ["servo", "pwm"], sources: [{ id: "src_listing", name: "DIYmall DS3235 listing (BOM row)", url: "https://www.amazon.com/s?k=DIYmall+DS3235" }],
  voltage: [5, 7.4], dims: [40, 20, 40.5], mass_g: 66,
});
