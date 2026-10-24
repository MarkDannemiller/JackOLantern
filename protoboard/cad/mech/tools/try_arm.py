"""Build both arms (with hands) alone, solve them from their torso mounts and compare with the design placements.

    ~/.local/opt/jj-mech/bin/python cad/mech/tools/try_arm.py [b|c] [out.glb]
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from jj.arm_bus import ArmBus, S_WORLD  # noqa: E402
from jj.hands import HandB, WristC  # noqa: E402
from jj.geom import translate, rot_axis  # noqa: E402
from jj.model import Assembly  # noqa: E402
from jj.export import preview_glb  # noqa: E402

tier = sys.argv[1] if len(sys.argv) > 1 else "b"
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/arm.glb"
t0 = time.time()
arm = ArmBus(tier)
arm.finalize()
hand_r = HandB() if tier == "b" else WristC()
hand_l = hand_r.mirrored()
print(f"built in {time.time() - t0:.1f} s: arm {len(arm.instances)} instances / {len(arm.mates)} mates, hand {len(hand_r.instances)} / {len(hand_r.mates)}")
W_R = translate(*S_WORLD)
W_L = rot_axis((0, 0, 1), 180) @ W_R
asm = Assembly("arms", "r/j1_housing")
for side, W, hand in (("r", W_R, hand_r), ("l", W_L, hand_l)):
    arm.emit(asm, f"{side}/", link_prefix=f"{side}_", anchor="j1_housing", world=W)
    hand.emit(asm, f"{side}/hand/", link_prefix=f"{side}_", alias={"wrist_hub": f"{side}/j5_hub"})
issues = asm.solve()
for i in issues:
    print("ISSUE", i)
worst = 0
for side, W, b in (("r", W_R, arm), ("l", W_L, arm), ("r", W_R, hand_r)):
    pre = f"{side}/" if b is arm else f"{side}/hand/"
    for iid, inst in b.instances.items():
        if iid in b.proxies:
            continue
        got = asm.instances[pre + iid].matrix
        if got is None:
            continue
        err = float(np.abs(W @ inst["M"] - got).max())
        if err > 1e-3:
            print(f"PLACEMENT {pre}{iid}: off by {err:.3f}")
        worst = max(worst, err)
print("worst placement difference", round(worst, 6))
# the left hand must be the mirror image (across world x = 0) of the right hand
MX = np.diag([-1.0, 1, 1, 1])
for iid, inst in hand_r.instances.items():
    if iid in hand_r.proxies:
        continue
    r = asm.instances[f"r/hand/{iid}"].matrix
    l = asm.instances[f"l/hand/{iid}"].matrix
    if r is None or l is None:
        continue
    pr, pl = r[:3, 3], l[:3, 3]
    if np.abs(pl - np.array([-pr[0], pr[1], pr[2]])).max() > 1e-3:
        print(f"MIRROR {iid}: right at {np.round(pr, 1)}, left at {np.round(pl, 1)}")
hw = asm.hardware()
print("hardware placed", len(hw))
for r in asm.stack_checks():
    if not r["ok"]:
        print("STACK", r)
preview_glb(asm, hw, out)
print("wrote", out, f"{time.time() - t0:.1f} s")
