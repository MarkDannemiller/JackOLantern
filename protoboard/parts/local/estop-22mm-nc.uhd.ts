/**
 * 22 mm latching mushroom emergency stop, 1 NC contact, rated 600 V 10 A (listing title).
 * Sources: research/sourcing/20261024-bom.json.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { powerStage } from "./lib/jj";

export const ESTOP_22MM_NC: ModuleDef = powerStage({
  id: "estop-22mm-nc", name: "Emergency stop, 22 mm, latching, NC", manufacturer: "Generic", part_number: "22 mm NC mushroom E-stop",
  description: "Red 40 mm mushroom head, latching, one normally-closed contact: pressing it opens the actuator supply.",
  categories: ["component.switch"], tags: ["safety", "estop"], sources: [{ id: "src_listing", name: "BOM row (listing)", url: "https://www.amazon.com/s?k=22mm+emergency+stop+NC" }],
  vin: [0, 600], vout: [0, 600], iout: 10, ground: false,
});
