/**
 * TEMCo 24 V 40 A 4-pin Bosch-style relay, SPST-NO (vendor page). Coil current not published.
 * Sources: research/sourcing/20261024-bom.json. Pull-in from a 15-21 V pack is unverified: bench test.
 */
import type { ModuleDef } from "@deltarobotics/uhd";
import { PowerIn, PowerOut, Ground } from "@deltarobotics/uhd";
import { part } from "./lib/jj";
import { withMech } from "../../src/mech/lib";

const TEMCO_RELAY_24V_40A_ELECTRICAL: ModuleDef = part({
  id: "temco-relay-24v-40a", name: "TEMCo 24 V 40 A relay (SPST-NO)", manufacturer: "TEMCo", part_number: "CN0345",
  description: "Automotive relay: the E-stop chain energises the coil, the contacts switch the actuator rail.",
  categories: ["component.relay"], tags: ["relay", "safety"], sources: [{ id: "src_temco", name: "TEMCo CN0345", url: "https://www.temcoindustrialpower.com/" }],
  interfaces: [PowerIn({ id: "coil_86", name: "Coil + (86)", voltageV: [15, 24] }), Ground({ id: "coil_85", name: "Coil - (85)" }),
    PowerIn({ id: "contact_30", name: "Common (30)", voltageV: [0, 32] }), PowerOut({ id: "contact_87", name: "NO (87)", voltageV: [0, 32], maxCurrentA: 40 })],
  traits: [
    { type: "supplied_from", params: { interfaceId: "contact_87", via: "contacts", source: "contact_30" } },
    { type: "assumption", params: { field: "coil range", value: "15-24 V", reason: "24 V coil driven from the 15-21 V pack: pull-in at 15 V is unverified (bench test before relying on it)." } },
  ],
});

/** With its body and mounting faces from the mechanical model (cad/mech, src/mech/mech.json). */
export const TEMCO_RELAY_24V_40A: ModuleDef = withMech(TEMCO_RELAY_24V_40A_ELECTRICAL as ModuleDef, "jj-body-relay");
