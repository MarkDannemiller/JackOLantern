"""Helpers shared by the arm and torso builders: placing bought parts in a design frame, the host
features that receive them, fastener stacks and screw-length choice."""
from __future__ import annotations

import math

import numpy as np
from build123d import Box, Pos, Cylinder

from .geom import Frame
from .model import StackItem
from . import hw

# torque values: maker tables derated for plastic (assumptions, with the table rows they came from)
TORQUE_REF = {
    2: (0.2, "ISO 898-1 8.8 into steel 0.35 N.m (Bossard table)"),
    3: (0.6, "ISO 898-1 8.8 into steel 1.2 N.m (Bossard table)"),
    4: (1.2, "ISO 898-1 8.8 into steel 2.8 N.m (Bossard table)"),
    5: (2.5, "ISO 898-1 8.8 into steel 5.5 N.m (Bossard table)"),
}
STD_LEN = {2: [4, 5, 6, 8, 10, 12], 2.5: [6, 8, 10, 12, 16], 3: [6, 8, 10, 12, 14, 16, 20, 25, 30, 35, 40],
           4: [8, 10, 12, 16, 20, 25, 30, 35, 40], 5: [8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50], 6: [12, 16, 20, 25, 30]}


def torque(d, into="insert"):
    t, ref = TORQUE_REF[int(d) if d >= 3 else 2]
    if into == "insert":
        return t * 0.6, f"assumption: brass heat-set insert in printed PETG-CF, snug; derated from {ref}"
    if into == "servo":
        return 0.15, "assumption: self-tapping into the servo's glass-filled case; hand tight, derated from 0.35 N.m (M2 8.8 into steel)"
    if into == "horn":
        return 0.5, "assumption: M3 into the aluminium horn's thread; derated from 1.2 N.m (M3 8.8 into steel)"
    if into == "nut":
        return t, f"assumption: through a printed part into a nyloc nut; derated from {ref}"
    if into == "tnut":
        return 2.5, "assumption: M5 into a steel T-nut in 6061 extrusion; derated from 5.5 N.m (M5 8.8 into steel)"
    return t, ref


def choose_len(d, grip, engage_min, engage_max):
    """Shortest standard length whose thread past the grip lies in [engage_min, engage_max]."""
    for L in STD_LEN[d]:
        e = L - grip
        if engage_min - 1e-6 <= e <= engage_max + 1e-6:
            return L
    raise ValueError(f"no M{d} length for grip {grip} engage {engage_min}..{engage_max}")


def insert_stack(d, plate_t, step_torque_into="insert"):
    """Screw through a plate of thickness `plate_t` into a heat-set insert in the structure.
    Measured along the structure face's normal (out of the structure): insert 0 .. -L, screw head at +plate_t."""
    od, L, hole = hw.INSERT[d]
    sl = choose_len(d, plate_t, min(1.5 * d, L - 0.5), L + 0.5)
    t, note = torque(d, step_torque_into)
    return [StackItem(hw.insert(d), 0.0, -1),
            StackItem(hw.shcs(d, sl), plate_t, -1, t, note)]


def nut_stack(d, plate_a, plate_b, washer=True):
    """Through-bolt: screw head on the far side of plate_b (component), nyloc nut under plate_a (structure)."""
    w = hw.WASHER[d][1] if washer else 0
    grip = plate_a + plate_b + 2 * w + hw.NYLOC_H[d]
    sl = choose_len(d, grip, 0.8, 6)
    t, note = torque(d, "nut")
    items = []
    if washer:
        items.append(StackItem(hw.washer(d), plate_b, 1))
        items.append(StackItem(hw.washer(d), -plate_a, -1))
    items.append(StackItem(hw.nut(d, True), -plate_a - w, -1, t, note))
    items.append(StackItem(hw.shcs(d, sl), plate_b + w, -1))
    return items


def servo_screw_stack(wall_t, screw_len=None):
    """PA2.0 self-tapping screws through a printed cradle wall into the STS servo's case screw holes
    (about 4.5 mm into the case)."""
    s = pa2_screw(screw_len or (6 if wall_t <= 2.0 else 8))
    t, note = torque(2, "servo")
    return [StackItem(s, wall_t, -1, t, note)]


def horn_stack(plate_t, d=3):
    """M3 screws through a printed part into the servo horn's threaded holes (horn 2.5 mm thick)."""
    sl = choose_len(d, plate_t, 1.8, 2.6)
    t, note = torque(d, "horn")
    return [StackItem(hw.shcs(d, sl), plate_t, -1, t, note)]


def pa2_screw(length):
    key = f"pa2x{length}"
    if key in hw._cache:
        return hw._cache[key]
    from .model import PartDef
    head = Pos(0, 0, -0.8) * Cylinder(1.9, 1.6)
    shank = Pos(0, 0, length / 2) * Cylinder(0.95, length)
    p = PartDef(key, f"PA2.0 x {length} pan head self-tapping screw (for plastic)", "hardware", "metal_steel", head + shank,
                source="Feetech ST-3215-C047 sheet: case screws are PA2.0 self-tapping; longer ones fix the case to a bracket",
                meta={"kind": "screw", "diameter": 2.0, "length": float(length), "head_diameter": 3.8, "head_height": 1.6,
                      "standard": "PA (self-tapping for plastic), pan head"})
    hw._cache[key] = p
    return p


def host_feature(part_feature_frame: Frame, part_matrix) -> Frame:
    """The host's mating frame for a bought part's feature: the part's frame in the design frame, flipped."""
    return part_feature_frame.moved(part_matrix).flipped()


def frame_of(origin, normal, x):
    return Frame(tuple(map(float, origin)), tuple(map(float, normal)), tuple(map(float, x)))


def box_in(m, xr, yr, zr):
    """Box over local ranges, placed by the 4x4 m."""
    from .export import to_location
    b = Pos((xr[0] + xr[1]) / 2, (yr[0] + yr[1]) / 2, (zr[0] + zr[1]) / 2) * Box(xr[1] - xr[0], yr[1] - yr[0], zr[1] - zr[0])
    return to_location(m) * b


def cyl_in(m, r, z0, z1, x=0.0, y=0.0):
    from .export import to_location
    return to_location(m) * (Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0))
