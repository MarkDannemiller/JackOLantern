/**
 * Documents for the tier chosen by JJ_TIER (a, b, c): the assembly guide and datasheet of that tier's root
 * system (protoboard run tech-docs). Presentation only: the step groups are generated from the mechanical
 * model's mates (cad/mech/gen_uhd.py -> docs/assembly-steps.gen.json), every value is a query into the model.
 */
import type { DocConfig } from "@protoboardai/ext-docs";
import STEPS from "./assembly-steps.gen.json" with { type: "json" };

const TIER = (process.env.JJ_TIER ?? "b").toLowerCase() as "a" | "b" | "c";
const NAME = { a: "Tier A, Beginner", b: "Tier B, Midrange", c: "Tier C, Maxed" }[TIER];

type Step = { id: string; title: string; mates: string[]; notes: { kind: "tip" | "caution" | "warning"; text: string }[]; after?: "test" };
const steps = (STEPS as Record<string, Step[]>)[TIER];

// a three-quarter view from the front right, above (the character faces -Y); arm steps look at the arm from outside
const ISO = { dir: [-0.85, -1.35, 0.75] };
const ARM_R = { dir: [-1.4, -0.9, 0.45] };
const ARM_L = { dir: [1.4, -0.9, 0.45] };

const config: DocConfig = {
  title: `Joyful Jack, ${NAME}`,
  subtitle: "Animatronic pumpkin-head cowboy: body, arms and hands",
  docId: `JJ-${TIER.toUpperCase()}`,
  revision: "A",
  root: ["body", "skirt"],
  camera: ISO,
  assembly: {
    explode: 40,
    steps: [
      ...steps.map((s) => ({
        id: s.id,
        title: s.title,
        mates: s.mates,
        notes: s.notes,
        ...(s.after ? { after: s.after } : {}),
        camera: s.id.startsWith("arm-r") ? ARM_R : s.id.startsWith("arm-l") ? ARM_L : ISO,
      })),
      { id: "wiring-arm-r", title: "Wire the right arm: servo bus and power", wiring: ["arm_r/*", "arm_r_*"], figure: "wiring" as const },
      { id: "wiring-arm-l", title: "Wire the left arm: servo bus and power", wiring: ["arm_l/*", "arm_l_*"], figure: "wiring" as const },
      { id: "wiring-head", title: "Wire the head: computer, servo rail and monitor bus", wiring: ["pi_*", "head_*", "monitor_*", "*head*"], figure: "wiring" as const },
      { id: "wiring-power", title: "Wire the power system: packs, docks, protection, fuses and converters", wiring: ["*"], figure: "wiring" as const },
    ],
  },
};

export default config;
