"""Bought parts other than fasteners: actuators, bearings, belts, springs, power and electronics bodies.

Bodies are the maker's CAD where it may be redistributed (Feetech STS3215 from TheRobotStudio
SO-ARM100, Apache-2.0: inbox/vendor-cad/), else nominal models from datasheet dimensions. A nominal
model is a model of the part for fit and mass, never a drawing of it.

Every servo is modelled in one frame: output axis on +Z through the origin, origin on the output
horn's mounting face. Features:
  horn        bolt pattern on the output horn face (structure: the horn's holes are threaded)
  horn_back   STS only: the rear (idler) horn face, same pattern, normal -Z
  case_top / case_bottom / flange   how the case is held (structure: threaded holes in the case)
"""
from __future__ import annotations

import math
import os

import numpy as np
from build123d import (Box, Cylinder, Pos, Rot, Torus, Sphere, import_step, extrude, Polygon, Circle, Location,
                       Compound, sweep, Plane, Wire, Edge, Line, Helix, Solid, Spline)

from .geom import Frame
from .model import PartDef

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
VENDOR = os.path.join(PROJECT, "inbox", "vendor-cad")


# ---------------------------------------------------------------- servos
SERVO_SPECS = {
    # Feetech STS3215 (C047, 12 V): STEP from SO-ARM100 (Apache-2.0). Stall 30 kg.cm at 12 V (Feetech listing,
    # research/sourcing). Case 45.4 x 24.8 mm; front horn face 18.7 mm, rear horn face -17.7 mm above the case
    # centre plane; output axis 11.25 mm from the case centre. Horn: 4 holes on a 14.0 mm circle, at 45 deg.
    "sts3215": dict(name="Feetech STS3215 (C047, 12 V)", mass_g=55.0, stall_kgcm=30.0, speed_rpm=45.0,
                    vendor="so-arm100-sts3215-03a.step", horn_bcd=14.0, horn_holes=4, horn_screw=3,
                    axis_xy=(11.25, 0.0), horn_front_z=18.7, horn_back_z=-17.7, rated_frac=1 / 3),
    # Feetech STS3250: same STS case (assumption: Feetech lists the same 45.2 x 24.7 x 35 mm envelope), 50 kg.cm stall at 12 V.
    "sts3250": dict(name="Feetech STS3250 (12 V)", mass_g=72.0, stall_kgcm=50.0, speed_rpm=43.0,
                    vendor="so-arm100-sts3215-03a.step", horn_bcd=14.0, horn_holes=4, horn_screw=3,
                    axis_xy=(11.25, 0.0), horn_front_z=18.7, horn_back_z=-17.7, rated_frac=1 / 3),
}

# standard-size hobby servos: nominal model in the catalog's DS3225 frame (case centre x = 0, spline at x = +10,
# case -20.1..20.4 in z, flange underside z = 7.6, holes 49.5 x 10, Ø4.5) then shifted so the horn face is z = 0.
STD_SERVOS = {
    "ds3235": dict(name="DSSERVO DS3235SG (35 kg)", mass_g=66.0, stall_kgcm=32.0, speed_rpm=60 / (0.13 * 6)),
    "ds3225": dict(name="DSSERVO DS3225MG 270 deg", mass_g=60.0, stall_kgcm=24.5, speed_rpm=60 / (0.13 * 6)),
    "mg996r": dict(name="TowerPro MG996R", mass_g=55.0, stall_kgcm=9.4, speed_rpm=60 / (0.17 * 6)),
}
STD_HORN_TOP = 24.0          # 25T aluminium disc horn: top face above the case centre plane (catalog spline top 20.4 + horn)
STD_HORN_D = 20.0            # 25T aluminium disc horn: Ø20, 4 x M3 tapped on a 14 mm circle (research/sourcing 20261025)
STD_HORN_BCD = 14.0

_cache: dict[str, PartDef] = {}


def _sts_body(spec):
    path = os.path.join(VENDOR, spec["vendor"])
    shape = import_step(path)
    ax, ay = spec["axis_xy"]
    return Pos(-ax, -ay, -spec["horn_front_z"]) * shape


def servo(key: str) -> PartDef:
    if key in _cache:
        return _cache[key]
    if key in SERVO_SPECS:
        s = SERVO_SPECS[key]
        body = _sts_body(s)
        p = PartDef(f"servo-{key}", s["name"], "bought", "servo_dark", body, mass_g=s["mass_g"],
                    source="Feetech STS3215 STEP (TheRobotStudio SO-ARM100, Apache-2.0)", vendor_file=s["vendor"],
                    meta={"servo": key, **s})
        fz = s["horn_front_z"]
        bz = s["horn_back_z"] - fz
        ax, _ = s["axis_xy"]
        # horn bolt pattern: holes at 45 deg (the pattern frame's x axis turned 45 deg)
        p.add("horn", "Output horn", Frame((0, 0, 0), (0, 0, 1), (1, 1, 0), 90), "bolt_pattern", role="structure",
              shape="circle", spacing=s["horn_bcd"], count=4, fastener=f"M{s['horn_screw']}", threaded=True)
        p.add("horn_back", "Rear (idler) horn", Frame((0, 0, bz), (0, 0, -1), (1, 1, 0), 90), "bolt_pattern", role="structure",
              shape="circle", spacing=s["horn_bcd"], count=4, fastener=f"M{s['horn_screw']}", threaded=True)
        # case: four M2 thread-forming holes on the top face (z 15.15 above the case centre) and bottom face (-15.15)
        p.add("case_top", "Case top screw holes", Frame((-5.4 - ax, 0, 17.0 - fz), (0, 0, 1), (1, 0, 0), 180), "bolt_pattern",
              role="structure", shape="rectangle", spacing=20.7, spacing_y=20.5, count=4, fastener="M2", threaded=True)
        p.add("case_bottom", "Case bottom screw holes", Frame((-7.3 - ax, 0, -14.4 - fz), (0, 0, -1), (1, 0, 0), 180), "bolt_pattern",
              role="structure", shape="rectangle", spacing=24.5, spacing_y=20.5, count=4, fastener="M2", threaded=True)
        p.meta.update(case=dict(x=(-22.7 - ax, 22.7 - ax), y=(-12.4, 12.4), z=(-14.4 - fz, 17.0 - fz)),
                      horn_d=20.0, stall_nm=s["stall_kgcm"] * 0.0980665)
    else:
        s = STD_SERVOS[key]
        z0 = -STD_HORN_TOP    # shift: horn top -> z = 0
        case = Pos(-10, 0, z0 + 0.15) * Box(40, 20, 40.5)
        flange = Pos(-10, 0, z0 + 7.6 + 1.25) * Box(54.5, 20, 2.5)
        holes = None
        for hx in (-24.75, 24.75):
            for hy in (-5, 5):
                h = Pos(-10 + hx, hy, z0 + 7.6 + 1.25) * Cylinder(2.25, 4)
                holes = h if holes is None else holes + h
        spline = Pos(0, 0, z0 + 20.4 - 2) * Cylinder(3, 4)
        horn = Pos(0, 0, -2) * Cylinder(STD_HORN_D / 2, 4)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            horn = horn - Pos(STD_HORN_BCD / 2 * math.cos(a), STD_HORN_BCD / 2 * math.sin(a), -2) * Cylinder(1.25, 5)
        lead = Pos(-30, 0, z0 - 11.45 + 20.1 - 20.1) * Box(4, 6, 3)
        body = case + flange - holes + spline + horn + lead
        p = PartDef(f"servo-{key}", s["name"], "bought", "servo_black", body, mass_g=s["mass_g"],
                    source="nominal model: standard servo case 40 x 20 x 40.5, flange 54.5 with holes 49.5 x 10 (DSSERVO DS3225 drawing, "
                           "catalog part dsservo-ds3225mg-180); 25T aluminium disc horn assumed Ø25, 4 x M3 on 16 mm",
                    meta={"servo": key, **s, "stall_nm": s["stall_kgcm"] * 0.0980665, "rated_frac": 1 / 3})
        p.add("horn", "Output horn", Frame((0, 0, 0), (0, 0, 1), (1, 1, 0), 90), "bolt_pattern", role="structure",
              shape="circle", spacing=STD_HORN_BCD, count=4, fastener="M3", threaded=True)
        p.add("flange", "Mounting flange (underside)", Frame((-10, 0, z0 + 7.6), (0, 0, -1), (1, 0, 0), 180), "bolt_pattern",
              role="component", shape="rectangle", spacing=49.5, spacing_y=10, count=4, fastener="M4", threaded=False)
        p.meta["flange_t"] = 2.5
        p.add("back", "Case back on the output axis", Frame((0, 0, z0 - 20.1 + 0.15), (0, 0, -1), (1, 0, 0)), "face")
        p.meta.update(case=dict(x=(-30, 10), y=(-10, 10), z=(z0 - 20.1 + 0.15, z0 + 20.4 + 0.15)), horn_d=STD_HORN_D)
    _cache[key] = p
    return p


# ---------------------------------------------------------------- bearings (ISO 15 boundary dimensions)
BEARINGS = {
    "6806-2rs": (30, 42, 7), "6805-2rs": (25, 37, 7), "6800-2rs": (10, 19, 5), "688-2rs": (8, 16, 5),
    "625-2rs": (5, 16, 5), "626-2rs": (6, 19, 6), "624-2rs": (4, 13, 5), "608-2rs": (8, 22, 7), "6704-2rs": (20, 27, 4),
}


def bearing(code: str) -> PartDef:
    pid = f"bearing-{code}"
    if pid in _cache:
        return _cache[pid]
    d, D, B = BEARINGS[code]
    outer = Pos(0, 0, B / 2) * (Cylinder(D / 2, B) - Cylinder(D / 2 - (D - d) * 0.18, B + 1))
    inner = Pos(0, 0, B / 2) * (Cylinder(d / 2 + (D - d) * 0.18, B) - Cylinder(d / 2, B + 1))
    seal = Pos(0, 0, B / 2) * (Cylinder(D / 2 - (D - d) * 0.18, B - 0.6) - Cylinder(d / 2 + (D - d) * 0.18, B))
    body = outer + inner + seal
    p = PartDef(pid, f"{code.upper()} ball bearing ({d} x {D} x {B} mm)", "bought", "metal_steel", body,
                source="ISO 15 boundary dimensions", meta={"bore": d, "od": D, "width": B, "code": code})
    # origin on one face; +Z through the bearing
    p.add("od_face", "Outer ring face", Frame((0, 0, 0), (0, 0, -1), (1, 0, 0), 1), "bearing", od=D, bore=d, width=B)
    p.add("od_face_top", "Outer ring far face", Frame((0, 0, B), (0, 0, 1), (1, 0, 0), 1), "bearing", od=D, bore=d, width=B)
    p.add("bore", "Bore", Frame((0, 0, 0), (0, 0, -1), (1, 0, 0), 1), "shaft", gender="bore", diameter=d)
    _cache[pid] = p
    p.mass_g = round(math.pi / 4 * (D * D - d * d) * B * 7.85e-3 * 0.55, 1)
    return p


# ---------------------------------------------------------------- GT2 belts
def gt2_pitch_d(teeth):
    return teeth * 2.0 / math.pi


def gt2_belt_simple(length_mm, width, d1, d2, center):
    """Belt as a solid band: outer loop minus inner loop (pitch line ± 0.7 mm)."""
    pid = f"gt2-belt-{int(round(length_mm))}-{width:g}mm"
    if pid in _cache:
        return _cache[pid]
    r1, r2 = d1 / 2, d2 / 2

    def loop(off):
        a1, a2 = r1 + off, r2 + off
        beta = math.asin((a2 - a1) / center)
        pts = []
        for k in range(48):
            a = math.pi / 2 + beta + k * (math.pi - 2 * beta) / 47
            pts.append((a1 * math.cos(a), a1 * math.sin(a)))
        for k in range(48):
            a = -math.pi / 2 - beta + k * (math.pi + 2 * beta) / 47
            pts.append((center + a2 * math.cos(a), a2 * math.sin(a)))
        return extrude(Polygon(*pts, align=None), width)

    band = loop(0.75) - (Pos(0, 0, -0.5) * _scale_z(loop(-0.65), width + 1, width))
    p = PartDef(pid, f"GT2 closed belt, {length_mm:g} mm ({int(round(length_mm / 2))} teeth), {width:g} mm wide", "bought", "rubber",
                band, mass_g=round(length_mm * width * 1.4 * 1.25e-3, 1),
                meta={"length": length_mm, "width": width, "teeth": int(round(length_mm / 2)), "profile": "GT2"})
    _cache[pid] = p
    return p


def _scale_z(shape, new_h, old_h):
    from build123d import scale
    return scale(shape, by=(1, 1, new_h / old_h))


def belt_length(d1, d2, c):
    """Open-belt length on pitch diameters (mm)."""
    return 2 * c + math.pi * (d1 + d2) / 2 + (d2 - d1) ** 2 / (4 * c)


def center_for_length(d1, d2, L):
    """Centre distance giving belt length L (pitch diameters)."""
    lo, hi = abs(d2 - d1) / 2 + 1, L / 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if belt_length(d1, d2, mid) < L:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- springs
def extension_spring(pid, name, od, wire, body_len, free_len, rate_n_mm, init_n, max_ext, mass_g, source):
    if pid in _cache:
        return _cache[pid]
    coils = max(4, int(body_len / wire))
    r = (od - wire) / 2
    body = Pos(0, 0, body_len / 2) * (Cylinder(od / 2, body_len) - Cylinder(od / 2 - wire, body_len + 1))
    for k in range(coils):      # rings suggest the coils
        body = body + Pos(0, 0, wire / 2 + k * (body_len - wire) / (coils - 1)) * Torus(r, wire / 2)
    hook_l = (free_len - body_len) / 2
    hook_a = Pos(0, 0, -hook_l / 2) * (Rot(90, 0, 0) * Torus(hook_l / 2, wire / 2))
    hook_b = Pos(0, 0, body_len + hook_l / 2) * (Rot(90, 0, 0) * Torus(hook_l / 2, wire / 2))
    p = PartDef(pid, name, "bought", "metal_steel", body + hook_a + hook_b, mass_g=mass_g, source=source,
                meta={"od": od, "wire": wire, "free_length": free_len, "rate_N_per_mm": rate_n_mm, "initial_tension_N": init_n,
                      "max_extension": max_ext})
    p.add("hook_a", "Hook (fixed end)", Frame((0, 0, -hook_l), (0, 0, -1), (1, 0, 0)), "anchor")
    p.add("hook_b", "Hook (line end)", Frame((0, 0, body_len + hook_l), (0, 0, 1), (1, 0, 0)), "anchor")
    _cache[pid] = p
    return p


def all_bought():
    return dict(_cache)
