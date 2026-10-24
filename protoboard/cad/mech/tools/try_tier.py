"""Assemble a whole tier, solve, report issues, write a preview GLB."""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from jj.assemble import build_tier  # noqa: E402
from jj.export import preview_glb  # noqa: E402
tier, out = sys.argv[1], sys.argv[2]
t0 = time.time()
asm, info = build_tier(tier, costume="--costume" in sys.argv)
print(f"{len(asm.instances)} instances, {len(asm.mates)} mates, solved in {time.time() - t0:.1f} s")
for i in info["issues"][:40]:
    print("ISSUE", i)
print("issues", len(info["issues"]))
hw = asm.hardware()
print("hardware", len(hw))
bad = [r for r in asm.stack_checks() if not r["ok"]]
for r in bad[:20]:
    print("STACK", r)
print("stack failures", len(bad))
preview_glb(asm, hw, out, skip_links=())
print("wrote", out, round(time.time() - t0, 1))
