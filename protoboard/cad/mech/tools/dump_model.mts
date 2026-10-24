/**
 * Dump the loaded UHD model of the current tier (JJ_TIER): every link with its endpoint instance paths and
 * domain (for the harness cut list), and assemble()'s placements (to compare with cad/mech's own solve).
 *   JJ_TIER=b node cad/mech/tools/dump_model.mts > out/mech/uhd-b.json
 */
import { loadProject } from "@protoboardai/core";
import { assemble, wiringChecklist } from "@deltarobotics/uhd";

const p = await loadProject(process.cwd(), { checks: false });
const sys = p.rootDef!;
const lookup = p.lookup;
const asm = assemble(sys, lookup as never, { root: ["body", "skirt"] });
let wiring: unknown[] = [];
try {
  wiring = (wiringChecklist as unknown as (s: unknown, l: unknown) => unknown[])(sys, lookup);
} catch (e) {
  wiring = [{ error: String(e) }];
}
const out = {
  placements: asm.placements.map((x) => ({ key: x.key, path: x.path.join("/"), matrix: x.matrix })),
  issues: asm.issues,
  mates: asm.mates.length,
  hardware: asm.hardware.length,
  wiring,
  links: p.links.map((l) => JSON.parse(JSON.stringify(l, (k, v) => (k === "def" || k === "definition" ? undefined : v)))),
};
process.stdout.write(JSON.stringify(out));
