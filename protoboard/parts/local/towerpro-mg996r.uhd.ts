/**
 * TowerPro-type MG996R metal-gear servo (Hosyond 4-pack), tier A grip only.
 * Sources: listing (research/sourcing/build_final_bom.py). Supply range per TowerPro's MG996R page (4.8-7.2 V).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { hobbyServo } from "./lib/jj";

export const TOWERPRO_MG996R: ModuleDef = hobbyServo({
  id: "towerpro-mg996r", name: "MG996R metal-gear servo", manufacturer: "Hosyond (TowerPro MG996R type)", part_number: "MG996R",
  description: "Standard-size metal-gear servo used for the tier-A mitt grip (no gravity load).",
  categories: ["actuator.motor.servo"], tags: ["servo", "pwm"], sources: [{ id: "src_towerpro", name: "TowerPro MG996R", url: "https://www.towerpro.com.tw/product/mg996r/" }],
  voltage: [4.8, 7.2], dims: [40.7, 19.7, 42.9], mass_g: 55,
  traits: [{ type: "assumption", params: { field: "clone vs TowerPro", value: "TowerPro ratings", reason: "The bought 4-pack is a clone; its own datasheet was not read." } }],
});
