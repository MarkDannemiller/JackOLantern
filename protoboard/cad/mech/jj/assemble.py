"""One tier, assembled: base, torso, electronics, neck and head, both arms and hands, costume.

    from jj.assemble import build_tier
    asm, info = build_tier("b")

Every instance is placed by solving its mates from the skirt on the floor (the root), the way UHD's
`assemble()` does it; the arms hang on the torso through their shoulder feet, the hands on the wrists.
`info` has the builders, the joints (world frame, zero pose) and the check results.
"""
from __future__ import annotations

import numpy as np

from . import hw
from .arm_bus import ArmBus, S_WORLD, TORSO_TOP_Z, FRAME_RAIL_X
from .arm_std import MittA
from .builder import Builder
from .costume import costume_parts
from .geom import Frame, translate, rot_axis
from .hands import HandB, WristC
from .model import Assembly, StackItem
from .common import torque
from . import torso as TS

W_R = translate(*S_WORLD)
W_L = rot_axis((0, 0, 1), 180) @ W_R


def _foot_mates(body: Builder, tier, side, Wside, arm: Builder):
    """The shoulder housing's foot on the torso: T-slot features on the side top rail (B/C) or tee nuts in the
    shoulder board (A), at the foot's hole row, and the mate between them."""
    foot = arm.df("j1_housing", "torso_mount").moved(Wside)          # foot underside in world
    tq, tq_note = torque(5, "tnut")
    if tier != "a":
        rail = f"rail_y_top_{side}"
        fid = TS._rail_feature(body, rail, f"foot_{side}", foot)
        part = body.generic[body.instances[rail]["part"]]
        f = part.features[fid]
        f.params.update(shape="row", spacing=40.0, count=2)
        f.params.pop("positions", None)
        stack = [StackItem(hw.tnut_2020(5), 0.0, -1), StackItem(hw.shcs(5, 12), 8.0, -1, tq, tq_note)]
        return (rail, fid), stack
    top = body.designs["jj-torso-a-top"]
    top.feature(f"foot_{side}", f"Shoulder foot ({'right' if side == 'r' else 'left'}), 2 x M5 hammer-in tee nuts", foot.flipped(), "bolt_pattern",
                role="structure", shape="row", spacing=40.0, count=2, fastener="M5", threaded=True)
    stack = [StackItem(TS.tee_nut_m5(), -12.0, 1), StackItem(hw.shcs(5, 20), 8.0, -1, 3.0, "assumption: M5 into a hammer-in tee nut in plywood, snug")]
    return ("ply_top", f"foot_{side}"), stack


def build_tier(tier: str, costume=True):
    asm = Assembly(f"joyful-jack-{tier}", "skirt")
    body = Builder(f"body-{tier}")
    top = TS.build_base(body)
    if tier == "a":
        TS.build_torso_ply(body, top)
    else:
        TS.build_torso_2020(body, top)
    plate = TS.build_neck(body, tier)
    TS.build_head(body, plate)
    TS.build_electronics(body, tier)
    # arms and hands
    arm = ArmBus(tier)
    arm.finalize()
    if tier == "a":
        hand_r = MittA()
        alias_key, alias_to = "forearm", "fore"
    else:
        hand_r = HandB() if tier == "b" else WristC()
        alias_key, alias_to = "wrist_hub", "j5_hub"
    hand_l = hand_r.mirrored()
    feet = {}
    for side, Wside in (("r", W_R), ("l", W_L)):
        feet[side] = _foot_mates(body, tier, side, Wside, arm)
    body.finalize()
    body.emit(asm, "", anchor="skirt", world=np.eye(4))
    for side, Wside, hand in (("r", W_R, hand_r), ("l", W_L, hand_l)):
        arm.emit(asm, f"arm_{side}/", link_prefix=f"{side}_")
        hand.emit(asm, f"arm_{side}/hand/", link_prefix=f"{side}_", alias={alias_key: f"arm_{side}/{alias_to}"})
        (a_iid, a_fid), stack = feet[side]
        asm.mate(f"arm_{side}_foot", (a_iid, a_fid), (f"arm_{side}/j1_housing", "torso_mount"), 0.0, 0.0, stack, "arms")
        # the foot's design-placement rotation (UHD rot) between the rail's frame and the foot's
    if costume:
        for k, (part, m, link, ex) in enumerate(costume_parts(tier)):
            asm.add(f"costume/{part.id[len('jj-costume-'):]}", part, link, ex, at=m)
    issues = asm.solve()
    # joints in the world frame (zero pose)
    joints = []
    for side, Wside, hand in (("r", W_R, hand_r), ("l", W_L, hand_l)):
        for b, pre in ((arm, f"arm_{side}/"), (hand, f"arm_{side}/hand/")):
            for j in b.joints:
                o = (Wside @ np.array([*j["origin"], 1.0]))[:3]
                ax = Wside[:3, :3] @ np.asarray(j["axis"], dtype=float)
                if b is hand and side == "l":
                    pass
                joints.append({**j, "id": f"{side}_{j['id']}", "parent": f"{side}_{j['parent']}" if j["parent"] != "torso" else "torso",
                               "child": f"{side}_{j['child']}", "origin": [float(v) for v in o], "axis": [float(v) for v in ax],
                               "servo": pre + j["servo"] if j.get("servo") else None})
    joints.append(dict(id="neck_yaw", name="Neck yaw (head stepper)", parent="torso", child="head", origin=[0.0, 0.0, TS.NECK_Z],
                       axis=[0.0, 0.0, 1.0], limits=(-60, 60), actuator="nema17-pancake", ratio=1.0, servo=None))
    return asm, dict(body=body, arm=arm, hand_r=hand_r, hand_l=hand_l, joints=joints, issues=issues)
