"""Tier B and C arm: Feetech STS serial-bus servos, GT3 belt reductions at the shoulder and elbow,
a cable gravity balancer at the shoulder (balancer.py), hollow hubs on 6806 bearings, printed PETG-CF structure.

Design frame (DF): the right arm at its zero pose, hanging straight down, palm toward the body,
thumb forward. Origin at the shoulder centre S, where the shoulder-flex (J1, along X) and
shoulder-out (J2, along Y) axes cross. Axes are the world's (Z up, the character faces -Y, the right
arm is on -X, so +X is inboard). World = DF + (-232, 0, 1185) for the right arm; the left arm is the
same build turned 180 deg about the vertical axis, so both arms use the same printed parts; only the
hands are mirrored (hands.py).

Joints (positive directions):
  J1 shoulder flex   axis -X through S          + swings the arm forward      belt 60:20 GT3, cable gravity balancer
  J2 shoulder out    axis +Y through S          + swings the arm outward      belt 60:20 GT3 (no spring: see balancer.py)
  J3 upper-arm twist axis +Z at x = y = 0       direct (servo on the axis)
  J4 elbow           axis -X at z = -255        + bends the forearm forward   belt 48:16 GT3
  J5 wrist twist     axis +Z                    direct
  J6 wrist pitch     (tier C, hands.py)

Belt joint: the driven pulley is part of a hollow printed hub turning in two 6806 bearings (one in the
housing, one in a bolt-on cap); the driver is a printed GT3 pulley screwed to the servo horn, its outer
end carried by a 5 mm dowel in a 625 bearing so the belt pull does not load the servo's output shaft.
Twist joint: the hub turns in two 6806 bearings back to back in the housing; a disc screwed to the
servo horn is pulled onto the upper bearing's inner ring by three M3 x 30 through the hub wall.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Box, Cylinder, Pos, Rot, Torus, Polygon, extrude

from . import bought, hw
from . import joints as JT
from .builder import Builder
from .common import box_in, cyl_in, frame_of, horn_stack, insert_stack, torque
from .export import to_location
from .geom import Frame, translate
from .model import PartDef, StackItem
from .printed import Design, block, cyl
from .jointlib import (JointsMixin, STAGES, TORSION, DISC_T, DIAG, hub_part, cap_part, driver_pulley_part, dowel_part,
                       twist_hub_part, twist_disc_part, torsion_spring_part, gt3_belt, signed_angle, belt_cavity)

UPPER = 255.0
FORE = 225.0
S_WORLD = (-232.0, 0.0, 1185.0)
WRIST_Z = -UPPER - FORE                  # wrist face: J5 hub flange underside
R60 = JT.drum_radius(60)
R48 = JT.drum_radius(48)
YOKE_T = 6.0
FORK_T = 6.0
J1_FACE_X = R60 + 2.0 + YOKE_T          # J1 hub face A (outboard): the yoke's seat
J1_MID_X = J1_FACE_X + JT.HUB_LEN / 2
TW3 = -150.0                              # J3 twist: the lip mid-plane between its bearings
TW5 = WRIST_Z + 18.5                      # J5 twist: the hub flange underside is the wrist face
J4_Z = -UPPER
TORSO_TOP_Z = -25.0                       # top of the torso frame's top rails in the DF
FRAME_RAIL_X = 132.0                      # centre of the frame's side top rail in the DF (world x = -100)
X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])



def F(o, n, x):
    return frame_of(o, n, x)


# J1 balancer: anchor a above the J1 axis, pin b below it, two Century 90CS in parallel (k 1.12 N/mm, initial tension
# 22.2 N, 86 mm travel, 120 N max: research/sourcing/20261025-hardware-sourcing.json). The cable runs from the pin to the
# anchor sheave and on to the springs, so their stretch is the pin-anchor distance plus a constant: set at assembly so
# the springs carry F0 / k less than that distance (cable length below), they act as a zero-length spring and the torque
# is k a b sin(angle), the shape of gravity's torque on the arm. k a b = 2.24 N/mm x 42 mm x 42 mm = 3.95 N.m.
BAL_K, BAL_A, BAL_B = 2 * 1.12, 42.0, 42.0
BAL_F0 = 2 * 22.2


# ---------------------------------------------------------------------------- the arm
# servos per tier: shoulder (J1, J2), elbow (J4), twist joints (J3, J5); tier A has no twist joints
CFG = {
    "a": dict(heavy="ds3235", elbow="ds3225", light=None, twist=False),
    "b": dict(heavy="sts3215", elbow="sts3215", light="sts3215", twist=True),
    "c": dict(heavy="sts3250", elbow="sts3250", light="sts3215", twist=True),
}


class ArmBus(JointsMixin, Builder):
    def __init__(self, tier: str):
        super().__init__(f"arm-{tier}")
        self.tier = tier
        c = CFG[tier]
        self.sv_heavy = bought.servo(c["heavy"])
        self.sv_elbow = bought.servo(c["elbow"])
        self.sv = bought.servo(c["light"]) if c["light"] else None
        self.twist = c["twist"]
        self.build()

    # tier A's housings hold hobby servos (flange mounts): its printed parts get their own ids
    def _pid(self, pid):
        return pid + "-a" if self.tier == "a" and pid.startswith("jj-arm-") else pid

    def design(self, pid, name, origin, **kw):
        return super().design(self._pid(pid), name, origin, **kw)

    def add_design(self, iid, pid, link, explode=(0, 0, 0)):
        return super().add_design(iid, self._pid(pid), link, explode)

    # ------------------------------------------------------------ J1 gravity balancer
    def j1_balancer(self, h1: Design):
        from .balancer import j1_balancer
        j1_balancer(self, h1, J1_MID_X + JT.HUB_LEN / 2, BAL_A, BAL_B)

    # ------------------------------------------------------------ build
    def build(self):
        # ================= J1 housing (torso link)
        h1 = self.design("jj-arm-j1-housing", "J1 shoulder housing (on the torso)", (J1_MID_X, 0, 0))
        self.add_design("j1_housing", "jj-arm-j1-housing", "torso")
        jf1 = F((J1_MID_X, 0, 0), X, (0, 0, 1))
        self.j1 = self.belt_joint("j1", h1, "j1_housing", jf1, (0, 1, 0), (0, 0, -1), +1, self.sv_heavy, "yoke", "torso", "shoulder")
        # foot on the frame's side top rail: 2 x M5 into T-nuts in its top slot
        h1.add(block((J1_MID_X - 12, FRAME_RAIL_X + 14), (-32, 32), (TORSO_TOP_Z, TORSO_TOP_Z + 8), 6))
        h1.add(block((J1_MID_X - 8, J1_MID_X + 10), (-30, 30), (-40, TORSO_TOP_Z + 8), 4))
        h1.clear_pattern("torso_mount", "Foot on the frame's top rail (2 x M5, T-nuts)", F((FRAME_RAIL_X, 0, TORSO_TOP_Z), (0, 0, -1), (0, 1, 0)),
                         [], d=5, depth=8.0, shape="row", spacing=40.0, count=2, symmetry=180)
        # J1 gravity balancer: a cable from a pin on a lever on hub face B (b below the axis) over two sheaves on a
        # post (the first a above the axis) down to two extension springs on a 2020 column hanging from the foot
        self.j1_balancer(h1)
        self.joint(id="j1", name="Shoulder flex", parent="torso", child="yoke", origin=(J1_MID_X, 0, 0), axis=(-1, 0, 0),
                   limits=(-35, 120), actuator=self.sv_heavy.meta["servo"], ratio=STAGES["j1"]["ratio"], servo="j1_servo",
                   spring=dict(kind="balancer", k_ab_nm=round(BAL_K * BAL_A * BAL_B * 1e-3, 4), a_mm=BAL_A, b_mm=BAL_B,
                               note="zero-length cable balancer: 2 x Century 90CS, torque k a b sin(angle)"))

        # ================= yoke: plate on J1 face A, fork arms on the J2 hub faces
        yk = self.design("jj-arm-yoke", "Shoulder yoke", (J1_FACE_X - YOKE_T / 2, 0, 0))
        self.add_design("yoke", "jj-arm-yoke", "yoke")
        yk.add(block((J1_FACE_X - YOKE_T, J1_FACE_X), (-JT.HUB_LEN / 2 - FORK_T, JT.HUB_LEN / 2 + FORK_T), (-26, 26), 8))
        for s in (-1, 1):
            yk.add(block((-24.0, J1_FACE_X), sorted([s * JT.HUB_LEN / 2, s * (JT.HUB_LEN / 2 + FORK_T)]), (-24, 24), 8))
            yk.cut(cyl("y", (0, s * (JT.HUB_LEN / 2 + FORK_T / 2), 0), 7.0, FORK_T + 2))
        yk.cut(cyl("x", (J1_FACE_X - YOKE_T / 2, 0, 0), 7.0, YOKE_T + 2))
        self.screw_into_generic("yoke_on_j1_hub", "j1_hub", "face_a", yk, "yoke", "on_j1_hub", "Yoke on J1 hub face A", YOKE_T, "shoulder")

        # ================= upper-arm head: J2 drum (axis Y), J2 servo below the axis, J3 twist housing
        ua = self.design("jj-arm-upper-head", "Upper arm (J2 housing, J2 and J3 servos)", (0, 0, -60))
        self.add_design("upper", "jj-arm-upper-head", "upper")
        jf2 = F((0, 0, 0), Y, (1, 0, 0))
        self.j2 = self.belt_joint("j2", ua, "upper", jf2, (0, 0, -1), (0, 0, -1), -1, self.sv_heavy, "yoke", "upper", "upper")
        for face in ("face_a", "face_b"):
            self.screw_into_generic(f"yoke_fork_{face}", "j2_hub", face, yk, "yoke", f"fork_{face}",
                                    f"Yoke fork on J2 hub {face.replace('_', ' ')}", FORK_T, "upper")
        self.joint(id="j2", name="Shoulder out", parent="yoke", child="upper", origin=(0, 0, 0), axis=(0, 1, 0), limits=(-10, 110),
                   actuator=self.sv_heavy.meta["servo"], ratio=STAGES["j2"]["ratio"], servo="j2_servo")
        lower = "upper_lower" if self.twist else "upper"
        if self.twist:
            ua.add(block((-28, 28), (-46, 17), (TW3 + 8.5 + DISC_T, -60.0), 8))
            self.tw3 = self.twist_joint("j3", ua, "upper", TW3, self.sv, "upper", "upper_lower", "upper", case_dir=(0, -1, 0))
            self.joint(id="j3", name="Upper-arm twist", parent="upper", child="upper_lower", origin=(0, 0, TW3), axis=(0, 0, 1),
                       limits=(-90, 90), actuator=self.sv.meta["servo"], ratio=1.0, servo="j3_servo")
        else:
            ua.add(block((-28, 28), (-46, 17), (TW3 - 18.5, -60.0), 8))
        # ================= elbow housing (upper_lower): on the J3 flange, J4 drum, J4 servo above
        top = TW3 - 18.5
        el = self.design("jj-arm-elbow-housing", "Elbow housing (J4 drum and servo)", (0, 0, J4_Z))
        self.add_design("elbow_housing", "jj-arm-elbow-housing", lower)
        top = TW3 - 18.5
        el.add(cyl("z", (0, 0, top - 4), 27.0, 8.0))
        el.add(block((-18, 18), (-40, 22), (J4_Z + STAGES["j4"]["c"] - 16, top - 4), 6))
        jf4 = F((0, 0, J4_Z), X, (0, 1, 0))
        self.j4 = self.belt_joint("j4", el, "elbow_housing", jf4, (0, 0, 1), (0, -1, 0), +1, self.sv_elbow, "fore", lower, "elbow")
        if self.twist:
            self.screw_into_generic("elbow_on_j3_hub", "j3_hub", "out", el, "elbow_housing", "on_j3", "Elbow housing on the J3 hub", 8.0, "elbow")
        else:
            self.screw_design_pair("elbow_on_upper", ua, "upper", "elbow_seat", el, "elbow_housing", "on_upper", F((0, 0, top), -Z, (1, 0, 0)), [],
                                   8.0, "elbow", name_a="Elbow housing seat (4 x M3 inserts)", name_b="Elbow housing on the upper arm",
                                   shape="circle", spacing=40.0, count=4, symmetry=90)
        self.joint(id="j4", name="Elbow", parent=lower, child="fore", origin=(0, 0, J4_Z), axis=(-1, 0, 0), limits=(0, 135),
                   actuator=self.sv_elbow.meta["servo"], ratio=STAGES["j4"]["ratio"], servo="j4_servo")

        # ================= forearm: fork plates on the J4 hub faces, body with the J5 twist housing
        fa = self.design("jj-arm-fore-fork-in", "Forearm fork plate (inboard)", (JT.HUB_LEN / 2 + FORK_T / 2, 0, J4_Z))
        fb = self.design("jj-arm-fore-fork-out", "Forearm fork plate (outboard)", (-JT.HUB_LEN / 2 - FORK_T / 2, 0, J4_Z))
        self.add_design("fork_in", "jj-arm-fore-fork-in", "fore")
        self.add_design("fork_out", "jj-arm-fore-fork-out", "fore")
        for d_, s in ((fa, 1), (fb, -1)):
            d_.add(block(sorted([s * JT.HUB_LEN / 2, s * (JT.HUB_LEN / 2 + FORK_T)]), (-22, 22), (J4_Z - 72, J4_Z + 22), 6))
            d_.cut(cyl("x", (s * (JT.HUB_LEN / 2 + FORK_T / 2), 0, J4_Z), 7.0, FORK_T + 2))
        self.screw_into_generic("fork_in_on_j4", "j4_hub", "face_b", fa, "fork_in", "on_hub", "Fork plate on J4 hub face B", FORK_T, "forearm")
        self.screw_into_generic("fork_out_on_j4", "j4_hub", "face_a", fb, "fork_out", "on_hub", "Fork plate on J4 hub face A", FORK_T, "forearm")
        fo = self.design("jj-arm-fore-body", "Forearm body" + (" (J5 servo and twist bearings)" if self.twist else " (mitt on its wrist face)"),
                         (0, 0, TW5))
        self.add_design("fore", "jj-arm-fore-body", "fore")
        if self.twist:
            fo.add(block((-JT.HUB_LEN / 2, JT.HUB_LEN / 2), (-38, 24), (TW5 + 8.5 + DISC_T, J4_Z - 48), 6))
            self.tw5 = self.twist_joint("j5", fo, "fore", TW5, self.sv, "fore", "wrist", "forearm", case_dir=(0, -1, 0))
        else:
            fo.add(block((-JT.HUB_LEN / 2, JT.HUB_LEN / 2), (-22, 22), (WRIST_Z, J4_Z - 48), 6))
            fo.insert_pattern("wrist_face", "Wrist face (mitt, 4 x M3 inserts)", F((0, 0, WRIST_Z), -Z, (1, 0, 0)), [], 3, shape="rectangle",
                              spacing=24.0, spacing_y=24.0, count=4, symmetry=90)
        for d_, iid, s in ((fa, "fork_in", 1), (fb, "fork_out", -1)):
            frm = F((s * JT.HUB_LEN / 2, 0, J4_Z - 60), (s, 0, 0), (0, 1, 0))
            self.screw_design_pair(f"{iid}_to_body", fo, "fore", f"to_{iid}", d_, iid, "to_body", frm, [], FORK_T, "forearm",
                                   name_a=f"Forearm body, {iid.replace('_', ' ')} screws (2 x M3 inserts)", name_b="Fork plate to the forearm body",
                                   shape="row", spacing=24.0, count=2, symmetry=180)
        if self.twist:
            self.joint(id="j5", name="Wrist twist", parent="fore", child="wrist", origin=(0, 0, TW5), axis=(0, 0, 1), limits=(-120, 120),
                       actuator=self.sv.meta["servo"], ratio=1.0, servo="j5_servo")
