/**
 * Sea-Dog blade fuse block, 6-way ATC/ATO, with negative bus (tiers B and C).
 * Sources: research/sourcing/20261024-bom.json (listing). Current rating not found (TBD).
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerIn, PowerOut, Ground } from "@deltarobotics/uhd";
import { part } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const FUSE_BLOCK_6WAY_ELECTRICAL: ModuleDef = part({
  id: "fuse-block-6way", name: "6-way ATC fuse block with negative bus", manufacturer: "Sea-Dog", part_number: "blade fuse block, 6-way",
  description: "One feed, six fused outputs and a common negative bus.",
  categories: ["component.protection"], tags: ["fuse"], sources: [{ id: "src_listing", name: "BOM row (listing)", url: "https://www.amazon.com/s?k=sea-dog+fuse+block+6+way" }],
  interfaces: [PowerIn({ id: "feed", name: "Feed +", voltageV: [0, 32] }), Ground({ id: "neg_bus", name: "Negative bus" }),
    ...[1, 2, 3, 4, 5, 6].map((i) => PowerOut({ id: `out${i}`, name: `Fused out ${i}`, voltageV: [0, 32] }))],
  traits: [
    ...[1, 2, 3, 4, 5, 6].map((i) => ({ type: "supplied_from", params: { interfaceId: `out${i}`, via: "ATC fuse", source: "feed" } })),
    { type: "data_gap", params: { field: "block current rating", note: "Not found on the listing." } },
  ],
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const FUSE_BLOCK_6WAY: ModuleDef = withMech(FUSE_BLOCK_6WAY_ELECTRICAL as ModuleDef, "jj-body-fuses");
