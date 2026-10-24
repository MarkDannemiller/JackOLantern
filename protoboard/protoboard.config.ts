import { defineConfig } from "@protoboardai/core";

// Joyful Jack is designed at three price tiers that share the head, base, torso and power
// core. The stack has one root per project, so the tier is chosen here: JJ_TIER=a|b|c
// (default b). `JJ_TIER=a protoboard check`, `JJ_TIER=c protoboard bom`, ...
const TIER = (process.env.JJ_TIER ?? "b").toLowerCase();
const ROOTS: Record<string, { source: string; export: string }> = {
  a: { source: "src/tiers/tier-a.uhd.ts", export: "JOYFUL_JACK_A" },
  b: { source: "src/tiers/tier-b.uhd.ts", export: "JOYFUL_JACK_B" },
  c: { source: "src/tiers/tier-c.uhd.ts", export: "JOYFUL_JACK_C" },
};
if (!ROOTS[TIER]) throw new Error(`JJ_TIER must be a, b or c (got "${TIER}")`);

export default defineConfig({
  name: "joyful-jack",
  // the root system and every local definition (exported ModuleDefs): parts designed
  // here in src/, purchased parts researched here in parts/local/ (evidence in parts/evidence/<id>/)
  root: ROOTS[TIER],
  sources: ["src/**/*.uhd.ts", "parts/local/**/*.uhd.ts"],
  // catalog parts from the Protoboard Cloud parts service (`protoboard parts add`);
  // provenance and digests in parts/origins.json
  catalog: "parts/catalog",
  // the Protoboard library (`protoboard parts …`, `protoboard login`); PROTOBOARD_CLOUD_URL or --url
  // overrides it, e.g. http://localhost:8787 for a parts service on this machine
  cloud: { url: "https://protoboard-parts-628357308644.us-central1.run.app" },
  // extension packages (`protoboard extensions add <name>` adds one);
  // `protoboard doctor` reports their tools, `protoboard skills` their skills
  extensions: ["@protoboardai/ext-hardware", "@protoboardai/ext-parts", "@protoboardai/ext-sourcing", "@protoboardai/ext-frame-cad", "@protoboardai/ext-enclosure-cad", "@protoboardai/ext-harness-cad", "@protoboardai/ext-docs", "@protoboardai/ext-release"],
});
