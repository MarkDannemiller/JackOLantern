"""Tier A's mitt hand: an MG996R at the knuckles turns a three-finger paddle against a fixed thumb; built for the
right arm in the arm's design frame (arm_bus.py) and mirrored for the left. Tier A's arm itself is arm_bus.py
with hobby servos (DS3235 at the shoulder, DS3225MG at the elbow) on the same belt joints as tiers B and C.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Cylinder, Pos, Sphere

from . import bought, hw
from .arm_bus import UPPER, FORE, WRIST_Z, TORSO_TOP_Z, FRAME_RAIL_X
from .builder import Builder
from .common import box_in, cyl_in, frame_of, insert_stack, torque
from .geom import Frame, translate
from .jointlib import JointsMixin, TORSION, torsion_spring_part, DISC_T
from .model import StackItem
from .printed import Design, block, cyl

X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])
J1_FLANGE_X = 38.0
J4_Z = -UPPER
W = WRIST_Z


def F(o, n, x):
    return frame_of(o, n, x)


def jframe(origin, zdir, xdir):
    return F(origin, zdir, xdir).matrix()


class MittA(JointsMixin, Builder):
    """Tier A mitt (right): palm with a fixed thumb, MG996R at the knuckles, finger paddle."""

    def __init__(self):
        super().__init__("mitt-a")
        self.sg = bought.servo("mg996r")
        self.build()
        self.finalize()

    def build(self):
        PET = dict(material="petg", color="orange_shell")
        K = W - 72.0
        palm = self.design("jj-mitt-a-palm", "Tier A mitt palm (with thumb)", (0, 0, W - 40), **PET)
        self.add_design("palm", "jj-mitt-a-palm", "wrist")
        palm.add(block((-18, 18), (-40, 40), (K - 20, W), 14))
        # thumb: a fixed rounded stub in front, angled down and in
        from .hands import capsule
        palm.add(capsule((6, -40, W - 30), (14, -58, W - 80), 12.0))
        # MG996R: axis along Y at the knuckles, horn to the front, flange held by 4 x M4 inserts, case up
        ms = F((0, -20.0, K), -Y, -Z).matrix()
        sid = self.cradle_std("grip", palm, "palm", self.sg, ms, "wrist", "hand")
        palm.cut(block((-20, 20), (-27, -19.5), (K - 30, K + 14), 0))     # paddle plate slot at the horn
        palm.cut(block((-20, 20), (31, 39), (K - 30, K + 14), 0))         # paddle plate slot at the back
        # the rear pivot: an M4 insert in a boss on the servo's axis, behind the case
        piv = F((0, 30.0, K), Y, (1, 0, 0))
        palm.insert_pattern("pivot", "Paddle pivot (M4 insert, shoulder screw)", piv, [(0.0, 0.0)], 4)
        # wrist: 4 x M3 up into the forearm's inserts
        self.add_proxy("forearm", self._forearm_proxy(), np.eye(4))
        self.screw_into_generic("palm_on_wrist", "forearm", "wrist_face", palm, "palm", "on_wrist", "Mitt on the forearm (4 x M3)", 8.0, "hand")
        # finger paddle: two plates (horn and pivot) and three fat fingers
        pd = self.design("jj-mitt-a-paddle", "Tier A mitt finger paddle", (0, 0, K - 50), **PET)
        self.add_design("paddle", "jj-mitt-a-paddle", "fingers")
        pd.add(block((-10, 10), (-26.0, -20.0), (K - 40, K + 12), 4))
        pd.add(block((-10, 10), (32.0, 38.0), (K - 40, K + 12), 4))
        pd.add(block((-12, 12), (-36, 36), (K - 52, K - 36), 6))
        for y in (-24.0, 0.0, 24.0):
            pd.add(capsule((2, y, K - 48), (14, y, K - 118), 12.0))
        self.screw_into_generic("paddle_on_horn", sid, "horn", pd, "paddle", "on_horn", "Paddle on the MG996R horn (4 x M3)", 6.0, "hand", kind="horn")
        sb = hw.shoulder_bolt(5, 8)
        t, note = torque(4, "insert")
        pd.clear_pattern("on_pivot", "Paddle on the pivot (5 mm shoulder)", F((0, 32.0, K), -Y, (1, 0, 0)), [(0.0, 0.0)], 5, depth=6.0)
        # shoulder screw 5 x 8: head on the plate's outer face (2 gap + 6 plate from the boss), M4 thread into the insert
        self.mate("paddle_pivot", ("palm", "pivot"), ("paddle", "on_pivot"),
                  [StackItem(hw.insert(4), 0.0, -1), StackItem(sb, 8.0, -1, t, note)], "hand", gap=2.0)
        self.joint(id="grip", name="Mitt grip", parent="wrist", child="fingers", origin=(0, 0, K), axis=(0, -1, 0), limits=(0, 70),
                   actuator="mg996r", ratio=1.0, servo="grip_servo")

    def _forearm_proxy(self):
        """The forearm's wrist face as a generic stand-in (the tier A arm owns the real forearm)."""
        from .model import PartDef
        p = PartDef("jj-arm-a-forearm-proxy", "forearm wrist face", "printed", "printed_cf", None)
        p.add("wrist_face", "Wrist face", F((0, 0, W), -Z, (1, 0, 0), ), "bolt_pattern", role="structure", shape="rectangle", spacing=24.0,
              spacing_y=24.0, count=4, fastener="M3", threaded=True)
        p.features["wrist_face"].frame.symmetry_deg = 90
        return p
