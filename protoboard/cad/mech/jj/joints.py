"""Joint building blocks shared by the arms: the belt joint (hollow hub on two 6806 bearings with a
printed GT3 pulley, driven from a servo through a closed GT3 belt) and the twist joint (the same hub
without a pulley, turned directly by a coaxial servo).

Everything is laid out in a joint frame: axis +Z, origin on the axis at the mid-plane of the hub.
`place(shape, frame_matrix)` moves a joint-frame shape into the design frame of the part that holds it.

Belt joint stack along the axis (mm, joint frame):
    -16.5  hub face A (1 mm proud of the housing)       +16.5  hub face B
    -15.5 .. -8.5  bearing 1 (6806, 30 x 42 x 7)          8.5 .. 15.5  bearing 2 (in the bolt-on cap)
    -8.5 .. -6.5   housing lip (ID 36) holds bearing 1    6.5 .. 8.5   cap lip
    -5.75 .. 5.75  pulley: 1 mm flanges, 9.5 mm teeth (9 mm belt)

Belt rating (Gates 17611-T via research/sourcing/20261025-hardware-sourcing.json): 3 mm pitch GT2
("GT3") 9 mm wide, 179.6 N recommended working tension (computed from 507 N per 25.4 mm).
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Cylinder, Pos, Rot, Box, Torus, Cone

from .geom import Frame
from .printed import cyl_dir

BRG = dict(code="6806-2rs", d=30.0, D=42.0, B=7.0)
HUB_LEN = 33.0
HALF = 15.5             # housing half width
GAP = 6.5               # half gap between the lips
LIP_ID = 36.0
HUB_BORE = 14.0
HUB_INSERT_BCD = 22.0
GT3_PITCH = 3.0
BELT_W = 9.0
BELT_RATING_N = 179.6


def gt3_pd(teeth):
    return teeth * GT3_PITCH / math.pi


def gt3_od(teeth):
    return gt3_pd(teeth) - 0.762


def drum_radius(driven_teeth):
    """Outer radius of a belt-joint housing drum around the pulley."""
    flange_r = (gt3_od(driven_teeth) + 4) / 2
    return flange_r + 1.25 + 8.0     # 1.25 clearance, 8 mm wall (room for the cap screws' inserts)


def belt_length(d1, d2, c):
    return 2 * c + math.pi * (d1 + d2) / 2 + (d2 - d1) ** 2 / (4 * c)


def center_for(d1, d2, L):
    lo, hi = abs(d2 - d1) / 2 + 1, L / 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if belt_length(d1, d2, mid) < L:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def m4(frame: Frame):
    """Joint frame -> design frame matrix."""
    return frame.matrix()


def place(shape, frame: Frame):
    """Move a joint-frame build123d shape into the design frame."""
    from .export import to_location
    return to_location(frame.matrix()) * shape


def hub_shape(driven_teeth: int | None, face_len=HUB_LEN, bore=HUB_BORE, top_plate=False):
    """The rotating hub in its joint frame. driven_teeth None: twist hub (no pulley)."""
    h = face_len / 2
    s = Pos(0, 0, 0) * Cylinder(BRG["d"] / 2, face_len)                     # journals end to end
    s = s + Pos(0, 0, 0) * Cylinder(33.0 / 2, 2 * 8.5 - 0.1)                 # shoulders against the inner rings
    if driven_teeth:
        s = s + _gt3_pulley(driven_teeth)
    s = s - Cylinder(bore / 2, face_len + 2)
    return s


def _gt3_pulley(teeth, width=9.5, flange_t=1.0, flange_od=None):
    pd = gt3_pd(teeth)
    od = gt3_od(teeth)
    fd = flange_od or (od + 4)
    body = Cylinder(od / 2, width)
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        body = body - Pos((od / 2 + 0.15) * math.cos(a), (od / 2 + 0.15) * math.sin(a), 0) * Cylinder(0.95, width + 0.2)
    for sgn in (-1, 1):
        body = body + Pos(0, 0, sgn * (width / 2 + flange_t / 2)) * Cylinder(fd / 2, flange_t)
    return body


def gt3_pulley(teeth, width=9.5, flange_t=1.0, flange_od=None):
    return _gt3_pulley(teeth, width, flange_t, flange_od)


def housing_drum(driven_teeth, with_cap_side=False):
    """The fixed housing drum in its joint frame, without cap side (z > GAP): bearing-1 seat, lip,
    pulley cavity, and the solid wall around it. Returns (drum, cut) — `cut` is subtracted from the
    host part after union, so the host's own material is cleared too."""
    R = drum_radius(driven_teeth)
    cav = (gt3_od(driven_teeth) + 4) / 2 + 1.25
    drum = Pos(0, 0, (-HALF + GAP) / 2) * Cylinder(R, HALF + GAP)              # z -15.5 .. +6.5
    cut = (Pos(0, 0, -HALF + BRG["B"] / 2 - 0.01) * Cylinder(BRG["D"] / 2, BRG["B"] + 0.02)       # bearing 1 seat
           + Pos(0, 0, -HALF + BRG["B"] + 1.0) * Cylinder(LIP_ID / 2, 2.2)                         # lip bore
           + Pos(0, 0, 0) * Cylinder(cav, 2 * GAP + 0.02))                                           # pulley cavity
    cut = cut + Pos(0, 0, -HALF - 5) * Cylinder(LIP_ID / 2, 10)
    return drum, cut, R


def cap_screw_r(driven_teeth):
    """Cap screws sit mid-wall: cavity radius + 4.1 (insert hole 4.0 mm, walls about 2 mm each side)."""
    return (gt3_od(driven_teeth) + 4) / 2 + 1.25 + 4.1


def cap_shape(driven_teeth):
    """Bolt-on cap: bearing-2 seat and lip, z = +6.5 .. +15.5 in the joint frame."""
    R = drum_radius(driven_teeth)
    cap = Pos(0, 0, (GAP + HALF) / 2) * Cylinder(R, HALF - GAP)
    cap = cap - Pos(0, 0, HALF - BRG["B"] / 2 + 0.01) * Cylinder(BRG["D"] / 2, BRG["B"] + 0.02)
    cap = cap - Pos(0, 0, GAP + 1.0) * Cylinder(LIP_ID / 2, 2.2)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        cap = cap - Pos(cap_screw_r(driven_teeth) * math.cos(a), cap_screw_r(driven_teeth) * math.sin(a), (GAP + HALF) / 2) * Cylinder(1.7, HALF - GAP + 1)
        cap = cap - Pos(cap_screw_r(driven_teeth) * math.cos(a), cap_screw_r(driven_teeth) * math.sin(a), HALF - 1.5) * Cylinder(2.9, 3.1)
    return cap


def cap_holes(driven_teeth):
    r = cap_screw_r(driven_teeth)
    return [(r * math.cos(math.pi / 4 + k * math.pi / 2), r * math.sin(math.pi / 4 + k * math.pi / 2)) for k in range(4)]


def hub_face_holes():
    r = HUB_INSERT_BCD / 2
    return [(r * math.cos(math.pi / 4 + k * math.pi / 2), r * math.sin(math.pi / 4 + k * math.pi / 2)) for k in range(4)]


def joint_frame(origin, axis, x):
    return Frame(tuple(origin), tuple(axis), tuple(x))
