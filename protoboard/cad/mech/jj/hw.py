"""Standard hardware: screws, nuts, washers, heat-set inserts, T-nuts, shoulder bolts.

Nominal bodies (no thread form), with the origin conventions of the stack's hardware-cad generator
(@protoboardai/ext-frame-cad py/hardware_cad.py) so the same fastener stacks place them:
  screw   origin under the head, shank along +Z for `length`, head below z = 0
  nut     sits on z = 0 and extends along +Z for its height
  insert  (heat-set) sits on z = 0, extends +Z for its length; modelled by the stack as a `spacer`
  washer  sits on z = 0, extends +Z

Sizes (SRC):
  ISO 4762 socket head cap screws: head diameter / height  M2 3.8/2, M2.5 4.5/2.5, M3 5.5/3, M4 7/4, M5 8.5/5
  ISO 4032 hex nuts (across flats / height): M3 5.5/2.4, M4 7/3.2, M5 8/4.7
  ISO 10511 nyloc nuts (height): M3 4.0, M4 5.0, M5 5.0
  ISO 7089 washers (OD / thickness): M3 7/0.5, M4 9/0.8, M5 10/1.0
  ISO 7379 shoulder screws: shoulder d / thread / head d x h: 5/M4/8x4.5? -> 6/M5/10x4.5
Heat-set inserts follow the CNC Kitchen / Ruthex datasheets (research/sourcing/20261025-hardware-sourcing.json):
  M3 x 5.7: OD 4.6 mm, hole 4.0 mm; M4 x 8.1: OD 6.3 mm, hole 5.6 mm; M2.5 x 4: OD 3.6 mm, hole 3.2 mm.
"""
from __future__ import annotations

import math

from build123d import Box, Cylinder, Pos, RegularPolygon, extrude, Align, Circle

from .model import PartDef

MIN = (Align.CENTER, Align.CENTER, Align.MIN)

SHCS_HEAD = {2: (3.8, 2.0), 2.5: (4.5, 2.5), 3: (5.5, 3.0), 4: (7.0, 4.0), 5: (8.5, 5.0), 6: (10.0, 6.0)}
NUT = {2: (4.0, 1.6), 2.5: (5.0, 2.0), 3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.7), 6: (10.0, 5.2)}
NYLOC_H = {3: 4.0, 4: 5.0, 5: 5.0, 6: 6.0}
WASHER = {3: (7.0, 0.5), 4: (9.0, 0.8), 5: (10.0, 1.0), 6: (12.0, 1.6)}
INSERT = {2.5: (3.6, 4.0, 3.2), 3: (4.6, 5.7, 4.0), 4: (6.3, 8.1, 5.6), 5: (7.1, 9.5, 6.4)}   # OD, length, hole
CLEAR = {2: 2.4, 2.5: 2.9, 3: 3.4, 4: 4.5, 5: 5.5, 6: 6.6}           # clearance hole (ISO 273 medium)
TAP = {2: 1.6, 2.5: 2.05, 3: 2.5, 4: 3.3, 5: 4.2}                     # tap drill / self-tap pilot in plastic
STEEL = "metal_steel"

_cache: dict[str, PartDef] = {}


def _fmt(d):
    return f"{d:g}".replace(".", "p")


def shcs(d: float, length: float, finish: str = "black oxide alloy steel, class 12.9") -> PartDef:
    pid = f"iso4762-m{_fmt(d)}x{length:g}"
    if pid in _cache:
        return _cache[pid]
    hd, hh = SHCS_HEAD[d]
    head = Pos(0, 0, -hh / 2) * Cylinder(hd / 2, hh)
    sock = Pos(0, 0, -hh + hh * 0.3) * extrude(RegularPolygon(d * 0.45, 6), hh * 0.6, both=False)
    shank = Pos(0, 0, length / 2) * Cylinder(d / 2 * 0.95, length)
    p = PartDef(pid, f"M{d:g} x {length:g} socket head cap screw, ISO 4762", "hardware", STEEL, head - sock + shank,
                source="ISO 4762 nominal head sizes", meta={"kind": "screw", "diameter": d, "length": length,
                "head_diameter": hd, "head_height": hh, "standard": "ISO 4762", "finish": finish})
    _cache[pid] = p
    return p


def bhcs(d: float, length: float) -> PartDef:
    """ISO 7380 button head: head 1.75 d diameter, 0.55 d high (M3 5.7 x 1.65)."""
    pid = f"iso7380-m{_fmt(d)}x{length:g}"
    if pid in _cache:
        return _cache[pid]
    hd, hh = {3: (5.7, 1.65), 4: (7.6, 2.2), 5: (9.5, 2.75)}[d]
    head = Pos(0, 0, -hh / 2) * Cylinder(hd / 2, hh)
    shank = Pos(0, 0, length / 2) * Cylinder(d / 2 * 0.95, length)
    p = PartDef(pid, f"M{d:g} x {length:g} button head screw, ISO 7380", "hardware", STEEL, head + shank,
                source="ISO 7380 nominal", meta={"kind": "screw", "diameter": d, "length": length, "head_diameter": hd,
                "head_height": hh, "standard": "ISO 7380"})
    _cache[pid] = p
    return p


def nut(d: float, nyloc: bool = True) -> PartDef:
    pid = f"iso{'10511' if nyloc else '4032'}-m{_fmt(d)}"
    if pid in _cache:
        return _cache[pid]
    s, m = NUT[d]
    h = NYLOC_H.get(d, m) if nyloc else m
    body = extrude(RegularPolygon(s / math.sqrt(3), 6), h) - Pos(0, 0, h / 2) * Cylinder(d / 2, h + 1)
    p = PartDef(pid, f"M{d:g} {'nyloc ' if nyloc else ''}hex nut, ISO {'10511' if nyloc else '4032'}", "hardware", STEEL, body,
                source="ISO nominal", meta={"kind": "nut", "diameter": d, "length": h, "outer": s,
                "standard": "ISO 10511" if nyloc else "ISO 4032"})
    _cache[pid] = p
    return p


def washer(d: float) -> PartDef:
    pid = f"iso7089-m{_fmt(d)}"
    if pid in _cache:
        return _cache[pid]
    od, t = WASHER[d]
    body = Pos(0, 0, t / 2) * Cylinder(od / 2, t) - Pos(0, 0, t / 2) * Cylinder(d / 2 + 0.2, t + 1)
    p = PartDef(pid, f"M{d:g} flat washer, ISO 7089", "hardware", STEEL, body, source="ISO 7089 nominal",
                meta={"kind": "spacer", "diameter": d, "length": t, "outer": od, "bore": d + 0.4, "standard": "ISO 7089"})
    _cache[pid] = p
    return p


def insert(d: float) -> PartDef:
    pid = f"heatset-insert-m{_fmt(d)}"
    if pid in _cache:
        return _cache[pid]
    od, L, hole = INSERT[d]
    body = Pos(0, 0, L / 2) * Cylinder(od / 2, L) - Pos(0, 0, L / 2) * Cylinder(d * 0.42, L + 1)
    for k in range(3):   # knurl bands
        body = body - Pos(0, 0, L * (0.2 + 0.3 * k)) * (Cylinder(od / 2 + 1, 0.5) - Cylinder(od / 2 - 0.25, 0.6))
    p = PartDef(pid, f"M{d:g} brass heat-set insert ({od:g} mm OD x {L:g} mm)", "hardware", "brass", body,
                source="Ruthex / CNC Kitchen insert datasheets (outer diameter, length, recommended hole)",
                meta={"kind": "insert", "diameter": d, "length": L, "outer": od, "hole": hole, "bore": d * 0.84})
    _cache[pid] = p
    return p


def tnut_2020(d: float = 5) -> PartDef:
    """Drop-in (roll-in) T-nut for 20 mm 6-slot extrusion: origin on the slot face, nut body under it (-Z)."""
    pid = f"tnut-2020-m{_fmt(d)}"
    if pid in _cache:
        return _cache[pid]
    body = Pos(0, 0, 2.0) * Box(10, 6, 4.0) - Pos(0, 0, 2) * Cylinder(d / 2, 6)
    p = PartDef(pid, f"M{d:g} roll-in T-nut for 2020 extrusion", "hardware", STEEL, body,
                source="2020 6-slot roll-in T-nut, nominal (10 x 6 x 4 mm)", meta={"kind": "nut", "diameter": d, "length": 4.0, "outer": 10})
    _cache[pid] = p
    return p


def shoulder_bolt(d_shoulder: float, length: float) -> PartDef:
    """ISO 7379 shoulder screw: shoulder d x length, thread one size down (6 -> M5, 5 -> M4)."""
    pid = f"iso7379-{_fmt(d_shoulder)}x{length:g}"
    if pid in _cache:
        return _cache[pid]
    thread, thread_len, hd, hh = {5: (4, 6.5, 8.0, 3.5), 6: (5, 7.5, 10.0, 4.5), 8: (6, 9.5, 13.0, 5.5)}[d_shoulder]
    head = Pos(0, 0, -hh / 2) * Cylinder(hd / 2, hh)
    sh = Pos(0, 0, length / 2) * Cylinder(d_shoulder / 2, length)
    th = Pos(0, 0, length + thread_len / 2) * Cylinder(thread / 2 * 0.95, thread_len)
    p = PartDef(pid, f"{d_shoulder:g} mm x {length:g} mm shoulder screw (M{thread} thread), ISO 7379", "hardware", STEEL, head + sh + th,
                source="ISO 7379 nominal", meta={"kind": "screw", "diameter": thread, "length": length + thread_len,
                "head_diameter": hd, "head_height": hh, "shoulder": d_shoulder, "standard": "ISO 7379"})
    _cache[pid] = p
    return p


def all_hardware():
    return dict(_cache)
