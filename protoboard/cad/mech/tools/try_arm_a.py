"""Build both tier A arms with mitts, solve, check placements and mirror."""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from jj.arm_std import ArmStd, MittA  # noqa: E402
from jj.arm_bus import S_WORLD  # noqa: E402
from jj.geom import translate, rot_axis  # noqa: E402
from jj.model import Assembly  # noqa: E402
from jj.export import preview_glb  # noqa: E402
out = sys.argv[1]
t0 = time.time()
arm = ArmStd(); mitt_r = MittA(); mitt_l = mitt_r.mirrored()
W_R = translate(*S_WORLD); W_L = rot_axis((0, 0, 1), 180) @ W_R
asm = Assembly("arms-a", "r/j1_housing")
for side, W, m in (("r", W_R, mitt_r), ("l", W_L, mitt_l)):
    arm.emit(asm, f"{side}/", link_prefix=f"{side}_", anchor="j1_housing", world=W)
    m.emit(asm, f"{side}/hand/", link_prefix=f"{side}_", alias={"forearm": f"{side}/fore"})
for i in asm.solve(): print("ISSUE", i)
worst = 0
for side, W, b, pre in (("r", W_R, arm, "r/"), ("l", W_L, arm, "l/"), ("r", W_R, mitt_r, "r/hand/")):
    for iid, inst in b.instances.items():
        if iid in b.proxies: continue
        got = asm.instances[pre + iid].matrix
        err = float(np.abs(W @ inst["M"] - got).max()) if got is not None else 1e9
        if err > 1e-3: print("PLACEMENT", pre + iid, round(err, 3))
        worst = max(worst, err)
print("worst", round(worst, 6))
for iid in mitt_r.instances:
    if iid in mitt_r.proxies: continue
    pr = asm.instances["r/hand/" + iid].matrix[:3, 3]; pl = asm.instances["l/hand/" + iid].matrix[:3, 3]
    if np.abs(pl - np.array([-pr[0], pr[1], pr[2]])).max() > 1e-3: print("MIRROR", iid, pr, pl)
hw = asm.hardware(); print("hardware", len(hw))
for r in asm.stack_checks():
    if not r["ok"]: print("STACK", r)
preview_glb(asm, hw, out); print("wrote", out, round(time.time() - t0, 1))
