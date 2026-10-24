/**
 * Eaton Bussmann BK/HHD ATC in-line fuse holder, 12 Ga. leads, 24 A (Waytek listing); fuse value per branch.
 * Sources: https://www.waytekwire.com/product/eaton-s-bussmann-series-bk-hhd-atc-in-line-fuse
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { powerStage } from "./lib/jj";

export const INLINE_ATC_FUSE: ModuleDef = powerStage({
  id: "inline-atc-fuse", name: "Inline ATC fuse holder (24 A)", manufacturer: "Eaton Bussmann", part_number: "BK/HHD",
  description: "Inline ATC blade fuse holder on 12 AWG leads; one per branch, with the fuse sized to the branch.",
  categories: ["component.protection"], tags: ["fuse"], sources: [{ id: "src_waytek", name: "Waytek BK/HHD", url: "https://www.waytekwire.com/product/eaton-s-bussmann-series-bk-hhd-atc-in-line-fuse" }],
  vin: [0, 32], vout: [0, 32], iout: 24, ground: false,
  traits: [{ type: "assumption", params: { field: "voltage rating", value: "32 V DC", reason: "ATC holders are typically 32 V DC rated; this listing states only 24 A." } }],
});
