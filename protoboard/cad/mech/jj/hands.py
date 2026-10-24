"""Hands for tiers B and C (tier A's mitt is in arm_std.py), built for the right arm in the arm's design
frame and mirrored for the left (Builder.mirrored).

Tier B glove hand: a white printed palm on the J5 hub flange holds two STS3215: one turns the four
fingers together (axis along Y, at the knuckles), the other the thumb (axis along X, in front of the
palm). Fingers and thumb are printed in two plates each, screwed to both of their servo's horns.

Tier C: a wrist-pitch joint (STS3215 between two fork plates, axis along X) and Pollen Robotics'
AmazingHand (8 Feetech SCS0009, sold as a kit; CAD by Pollen Robotics, CC BY 4.0), from the part STEP
files in inbox/vendor-cad/, placed in the hand's own palm frame.
"""
from __future__ import annotations

import math
import os

import numpy as np
from build123d import Box, Cylinder, Pos, Rot, Sphere, import_step, Compound

from . import bought
from .arm_bus import WRIST_Z, TW5
from .builder import Builder
from .common import box_in, cyl_in, frame_of, horn_stack, insert_stack
from .export import to_location
from .geom import Frame, translate
from .jointlib import JointsMixin, twist_hub_part
from .model import PartDef
from .printed import Design, block, cyl

W = WRIST_Z
X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])
VENDOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "inbox", "vendor-cad")


def F(o, n, x):
    return frame_of(o, n, x)


def capsule(p0, p1, r):
    """A rounded rod from p0 to p1 (DF), radius r."""
    from .printed import cyl_dir
    p0, p1 = np.asarray(p0, dtype=float), np.asarray(p1, dtype=float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    return cyl_dir(tuple((p0 + p1) / 2), d, r, L) + Pos(*p0) * Sphere(r) + Pos(*p1) * Sphere(r)


class HandB(JointsMixin, Builder):
    """Tier B glove hand (right). Links: 'wrist' (palm), 'fingers', 'thumb'."""

    def __init__(self):
        super().__init__("hand-b")
        self.sv = bought.servo("sts3215")
        self.build()
        self.finalize()

    def build(self):
        self.add_proxy("wrist_hub", twist_hub_part(), translate(0, 0, TW5))
        K = W - 78.0                          # knuckle axis height
        T = np.array([0.0, -45.0, W - 50.0])   # thumb axis point
        palm = self.design("jj-hand-b-palm", "Glove hand palm", (0, 0, W - 40), material="petg", color="glove_white")
        self.add_design("palm", "jj-hand-b-palm", "wrist")
        palm.add(cyl("z", (0, 0, W - 3), 26.0, 6.0))
        palm.add(block((-17, 17), (-62, 30), (W - 92, W - 5), 12))
        self.screw_into_generic("palm_on_wrist", "wrist_hub", "out", palm, "palm", "on_wrist", "Palm on the wrist hub (4 x M3)", 6.0, "hand")
        # finger servo: axis along Y at the knuckles, front horn at y -18.2, case up, slides in from the palm face (+X)
        ms_f = F((0, -18.2, K), -Y, -Z).matrix()
        # slots for the finger plates around the servo horns
        for s in (-1, 1):
            palm.cut(block((-20, 20), sorted([s * 17.4, s * 25.6]), (W - 100, K + 16), 0))
        sf = self.cradle("fingers", palm, "palm", self.sv, ms_f, "wrist", "hand", horn_clear=(11.5, -3.0, 6.0), wall=1.7, open_dir="+y",
                         rear_clear=False)
        palm.cut(cyl_in(ms_f, 11.5, -40.0, -34.0))
        # thumb servo: axis along X, front horn at x +18.2, case up, slides in from the front (-Y)
        ms_t = F(T + X * 18.2, X, -Z).matrix()
        st = self.cradle("thumb", palm, "palm", self.sv, ms_t, "wrist", "hand", horn_clear=(11.5, -3.0, 6.0), wall=1.7, open_dir="-y",
                         rear_clear=False)
        palm.cut(cyl_in(ms_t, 11.5, -40.0, -34.0))

        # ---------------- fingers: two plates on the finger servo's horns, a bar, four curled fingers
        fg = self.design("jj-hand-b-fingers", "Glove fingers (four, on one servo)", (0, 0, K - 40), material="petg", color="glove_white")
        self.add_design("fingers", "jj-hand-b-fingers", "fingers")
        for s in (-1, 1):
            fg.add(block((-10, 10), sorted([s * 18.7, s * 24.2]), (K - 34, K + 12), 4))
            fg.add(cyl("y", (0, s * 18.45, K), 10.0, 0.5))
        fg.add(block((-10, 10), (-41, 41), (K - 44, K - 30), 6))
        for k, y in enumerate((-30.0, -10.0, 10.0, 30.0)):
            ln = (44, 50, 48, 40)[k]
            p0 = np.array([0, y, K - 42])
            p1 = p0 + np.array([math.sin(math.radians(12)), 0, -math.cos(math.radians(12))]) * ln
            p2 = p1 + np.array([math.sin(math.radians(38)), 0, -math.cos(math.radians(38))]) * ln * 0.7
            fg.add(capsule(p0, p1, 8.5) + capsule(p1, p2, 7.8))
        # horn screws: front plate on the front horn, rear plate on the rear horn (4 x M3 x 8 each)
        self.screw_into_generic("fingers_on_horn", sf, "horn", fg, "fingers", "on_horn", "Front plate on the finger servo horn", 6.0, "hand", kind="horn")
        self.screw_into_generic("fingers_on_rear_horn", sf, "horn_back", fg, "fingers", "on_rear_horn", "Rear plate on the finger servo's rear horn",
                                6.0, "hand", kind="horn")

        # ---------------- thumb: two plates on the thumb servo's horns, joined in front of the palm
        th = self.design("jj-hand-b-thumb", "Glove thumb", (0, -70, T[2] - 30), material="petg", color="glove_white")
        self.add_design("thumb", "jj-hand-b-thumb", "thumb")
        for s in (-1, 1):
            th.add(block(sorted([s * 18.7, s * 24.2]), (-80, -36), (T[2] - 26, T[2] + 10), 4))
            th.add(cyl("x", (s * 18.45, T[1], T[2]), 10.0, 0.5))
        th.add(block((-24.2, 24.2), (-82, -66), (T[2] - 26, T[2] - 6), 6))
        q0 = np.array([0, -74, T[2] - 18])
        q1 = q0 + np.array([0, -6, -45])
        q2 = q1 + np.array([0, 16, -30])
        th.add(capsule(q0, q1, 11.0) + capsule(q1, q2, 9.5))
        self.screw_into_generic("thumb_on_horn", st, "horn", th, "thumb", "on_horn", "Thumb plate on the thumb servo horn", 6.0, "hand", kind="horn")
        self.screw_into_generic("thumb_on_rear_horn", st, "horn_back", th, "thumb", "on_rear_horn", "Thumb plate on the thumb servo's rear horn",
                                6.0, "hand", kind="horn")
        self.joint(id="fingers", name="Fingers", parent="wrist", child="fingers", origin=(0, 0, K), axis=(0, -1, 0), limits=(0, 80),
                   actuator="sts3215", ratio=1.0, servo="fingers_servo")
        self.joint(id="thumb", name="Thumb", parent="wrist", child="thumb", origin=tuple(T), axis=(1, 0, 0), limits=(0, 45),
                   actuator="sts3215", ratio=1.0, servo="thumb_servo")


# ------------------------------------------------------------------------------------ tier C
def amazinghand_part(side="r"):
    """Pollen AmazingHand (right): palm parts in their common frame plus four fingers (proximal and distal
    shells) on the hand plate's finger edge. Own frame = Pollen's palm frame (mm): fingers toward +Y, the wrist
    interface's end face at y = -102.2. Finger positions along the edge are spaced across the plate (assumption:
    the part files carry no assembly positions)."""
    pid = f"pollen-amazinghand-{side}"
    s = side.upper()
    parts = []
    for n in (f"{side}-hand-plate", f"{side}-palm-shell", f"{side}-top-shell", f"{side}-wrist-interface"):
        f = os.path.join(VENDOR, f"amazinghand-{n}.step")
        if os.path.exists(f):
            parts.append(import_step(f))
    prox = import_step(os.path.join(VENDOR, "amazinghand-proximal-shell.step"))
    dist = import_step(os.path.join(VENDOR, "amazinghand-distal-shell.step"))
    for k, x in enumerate((0.0, 21.0, 42.0, 63.0)):
        parts.append(Pos(x, 0, 0) * prox)
        parts.append(Pos(x, 0, 0) * dist)
    body = Compound(children=parts)
    p = PartDef(pid, f"Pollen Robotics AmazingHand kit ({'right' if side == 'r' else 'left'}), 8 x Feetech SCS0009", "bought", "glove_white", body,
                mass_g=400.0, source="Pollen Robotics AmazingHand part STEPs (github.com/pollen-robotics/AmazingHand, CC BY 4.0); mass: assumption",
                vendor_file="inbox/vendor-cad/amazinghand-*.step", meta={"licence": "CC BY 4.0 (mechanical design), Apache-2.0 (software)", "chiral": True,
                                                                            "mirror_name": "Pollen Robotics AmazingHand kit (left), 8 x Feetech SCS0009"})
    p.add("wrist", "Wrist interface end face (4 x M3, pattern assumed)", Frame((24.5, -102.2, -12.4), (0, -1, 0), (1, 0, 0), 180), "bolt_pattern",
          role="structure", shape="rectangle", spacing=30.0, spacing_y=20.0, count=4, fastener="M3", threaded=True)
    return p


class WristC(JointsMixin, Builder):
    """Tier C wrist pitch (J6) and AmazingHand (right). Links: 'wrist' (block), 'hand' (forks, adapter, hand)."""

    def __init__(self):
        super().__init__("wrist-c")
        self.sv = bought.servo("sts3215")
        self.build()
        self.finalize()

    def build(self):
        self.add_proxy("wrist_hub", twist_hub_part(), translate(0, 0, TW5))
        P = np.array([0.0, 0.0, W - 42.0])
        blk = self.design("jj-wrist-c-block", "Wrist pitch block (J6 servo)", (0, 0, W - 20))
        self.add_design("wrist_block", "jj-wrist-c-block", "wrist")
        blk.add(cyl("z", (0, 0, W - 3), 26.0, 6.0))
        blk.add(block((-15.5, 15.5), (-17, 17), (W - 58, W - 5), 4))
        self.screw_into_generic("block_on_wrist", "wrist_hub", "out", blk, "wrist_block", "on_wrist", "Wrist block on the J5 hub (4 x M3)", 6.0, "wrist")
        ms = F(P + X * 18.2, X, -Z).matrix()
        sv = self.cradle("j6", blk, "wrist_block", self.sv, ms, "wrist", "wrist", horn_clear=(11.5, -3.0, 6.0), wall=1.7, open_dir="+y",
                         rear_clear=False)
        blk.cut(cyl_in(ms, 11.5, -40.0, -34.0))
        fork = {}
        for s, nm in ((1, "in"), (-1, "out")):
            d = self.design(f"jj-wrist-c-fork-{nm}", f"Wrist pitch fork plate ({'inboard' if s > 0 else 'outboard'})", (s * 21.7, 0, W - 60))
            self.add_design(f"fork_{nm}", f"jj-wrist-c-fork-{nm}", "hand")
            d.add(block(sorted([s * 18.7, s * 24.2]), (-18, 18), (W - 92, W - 30), 6))
            d.add(cyl("x", (s * 18.45, 0, P[2]), 10.0, 0.5))
            fork[nm] = d
        self.screw_into_generic("fork_in_on_horn", sv, "horn", fork["in"], "fork_in", "on_horn", "Fork plate on the J6 horn", 6.0, "wrist", kind="horn")
        self.screw_into_generic("fork_out_on_horn", sv, "horn_back", fork["out"], "fork_out", "on_horn", "Fork plate on the J6 rear horn", 6.0, "wrist",
                                kind="horn")
        ad = self.design("jj-hand-c-adapter", "AmazingHand adapter", (0, 0, W - 86))
        self.add_design("adapter", "jj-hand-c-adapter", "hand")
        ad.add(block((-18.7, 18.7), (-24, 24), (W - 92, W - 78), 4))
        for s, nm in ((1, "in"), (-1, "out")):
            fr = F((s * 18.7, 0, W - 85), (s, 0, 0), (0, 1, 0))
            self.screw_design_pair(f"adapter_to_fork_{nm}", ad, "adapter", f"to_fork_{nm}", fork[nm], f"fork_{nm}", "to_adapter", fr, [], 6.0,
                                   "wrist", name_a=f"Adapter, {nm} fork screws (2 x M3 inserts)", name_b="Fork plate to the adapter",
                                   shape="row", spacing=24.0, count=2, symmetry=180)
        # the hand hangs fingers down, palm toward +X: Pollen +Y -> DF -Z, Pollen +Z -> DF +X
        hand = amazinghand_part("r")
        from .geom import mate_transform
        Mh = mate_transform(F((0, 0, W - 92), -Z, Y), hand.features["wrist"].frame)   # wrist face on the adapter's underside
        hid = self.add_generic("amazinghand", hand, "hand", Mh)
        self.screw_into_generic("hand_on_adapter", hid, "wrist", ad, "adapter", "hand_seat", "AmazingHand on the adapter (4 x M3)", 14.0, "wrist",
                                kind="tap")
        self.joint(id="j6", name="Wrist pitch", parent="wrist", child="hand", origin=tuple(P), axis=(-1, 0, 0), limits=(-60, 60),
                   actuator="sts3215", ratio=1.0, servo="j6_servo")
