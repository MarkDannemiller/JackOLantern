"""Shapes and features printed parts are made of: rounded blocks, bores, bearing seats, insert and
clearance holes, servo pockets, GT2 pulleys.

Everything here works in a part's design frame (mm). `Design` collects a part's solid and its
feature frames in one frame, then `Design.part(origin)` re-expresses both about the part's own
origin, so the frames a mate uses are exactly the ones the solid was cut from.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import (Box, Cylinder, Pos, Rot, Location, extrude, Polygon, fillet, Axis, Sphere, Cone,
                       RectangleRounded, Plane, Circle, Ellipse, loft, Torus, Compound)

from .geom import Frame, translate, bolt_holes
from .model import PartDef
from . import hw

PRINT = {   # print settings by material (research/sourcing: PETG, PLA+, CF-PETG)
    "petg-cf": "PETG-CF, 0.6 mm nozzle, 0.3 mm layers, 5 walls, 40 % gyroid",
    "petg": "PETG, 0.4 mm nozzle, 0.2 mm layers, 4 walls, 30 % gyroid",
    "pla": "PLA+, 0.4 mm nozzle, 0.2 mm layers, 3 walls, 15 % infill (cosmetic shells)",
}


def _axis_rot(axis):
    """Rotation taking +Z to the given axis ('x', 'y', 'z', '-x', ...)."""
    return {"z": Rot(0, 0, 0), "-z": Rot(180, 0, 0), "x": Rot(0, 90, 0), "-x": Rot(0, -90, 0),
            "y": Rot(-90, 0, 0), "-y": Rot(90, 0, 0)}[axis]


AXV = {"x": (1, 0, 0), "-x": (-1, 0, 0), "y": (0, 1, 0), "-y": (0, -1, 0), "z": (0, 0, 1), "-z": (0, 0, -1)}


def cyl(axis, center, r, h):
    """Cylinder of radius r and length h, axis along `axis`, centred at `center`."""
    return Pos(*center) * (_axis_rot(axis) * Cylinder(r, h))


def cyl_from(axis, start, r, h):
    """Cylinder starting at `start` running h along `axis`."""
    v = np.asarray(AXV[axis], dtype=float)
    c = np.asarray(start, dtype=float) + v * h / 2
    return cyl(axis.lstrip("-") if False else axis, tuple(c), r, abs(h))


def block(xr, yr, zr, r=0.0):
    """Axis-aligned box over the ranges; vertical edges rounded by r (skipped if the kernel refuses)."""
    sx, sy, sz = xr[1] - xr[0], yr[1] - yr[0], zr[1] - zr[0]
    b = Pos((xr[0] + xr[1]) / 2, (yr[0] + yr[1]) / 2, (zr[0] + zr[1]) / 2) * Box(sx, sy, sz)
    if r > 0:
        try:
            b = fillet(b.edges().filter_by(Axis.Z), min(r, sx / 2 - 0.05, sy / 2 - 0.05))
        except Exception:
            pass
    return b


def round_edges(shape, axis, r):
    try:
        return fillet(shape.edges().filter_by(axis), r)
    except Exception:
        return shape


def gt2_pulley(teeth, width, flange_d=None, flange_t=1.0, axis="z", center=(0, 0, 0)):
    """GT2 pulley: toothed ring (pitch d - 0.508 OD) between two flanges, axis along `axis`, centred on `center`.
    The teeth are cut as 2 mm pitch slots (R0.555 tooth profile simplified to a rounded slot)."""
    pd = teeth * 2.0 / math.pi
    od = pd - 0.508
    body = Cylinder(od / 2, width)
    tooth_depth = 0.75
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        cut = Pos((od / 2) * math.cos(a), (od / 2) * math.sin(a), 0) * Cylinder(0.6, width + 0.2)
        body = body - cut
    fd = flange_d or (od + 4)
    for s in (-1, 1):
        body = body + Pos(0, 0, s * (width / 2 + flange_t / 2)) * Cylinder(fd / 2, flange_t)
    return Pos(*center) * (_axis_rot(axis) * body)


class Design:
    """A part being designed: solid plus features in one design frame."""

    def __init__(self, pid, name, material="petg-cf", category="printed", color="orange_shell"):
        self.pid, self.name, self.material, self.category, self.color = pid, name, material, category, color
        self.solid = None
        self.features = []          # (fid, name, Frame, kind, params)
        self.notes = []
        self.inserts = []           # (d, count) heat-set inserts pressed into this part
        self.meta = {}

    def add(self, shape):
        self.solid = shape if self.solid is None else self.solid + shape
        return self

    def cut(self, shape):
        self.solid = self.solid - shape
        return self

    def feature(self, fid, name, frame, kind, **params):
        self.features.append((fid, name, frame, kind, params))
        return frame

    # -- holes ----------------------------------------------------------------
    def insert_pattern(self, fid, name, frame: Frame, holes, d=3, extra_depth=0.6, shape=None, spacing=None, count=None,
                       spacing_y=None, symmetry=None):
        """Heat-set insert holes into the face at `frame` (normal pointing out of the material)."""
        od, L, hole = hw.INSERT[d]
        if shape and shape != "positions":
            holes = bolt_holes(shape, spacing, count or len(holes), spacing_y)
        m = frame.matrix()
        for (x, y) in holes:
            p = (m @ np.array([x, y, 0, 1.0]))[:3]
            n = np.asarray(frame.basis()[2])
            c = p - n * (L + extra_depth) / 2
            self.cut(_cyl_dir(c, n, hole / 2, L + extra_depth + 0.02))
        self.inserts.append((d, len(holes)))
        params = dict(role="structure", fastener=f"M{d:g}", threaded=True, insert=f"heatset-insert-m{d:g}")
        if shape:
            params.update(shape=shape, spacing=spacing, count=count or len(holes))
            if spacing_y is not None:
                params["spacing_y"] = spacing_y
        else:
            params.update(positions=[list(h) for h in holes], shape="positions")
        f = Frame(frame.origin, frame.normal, frame.x, symmetry)
        return self.feature(fid, name, f, "bolt_pattern", **params)

    def clear_pattern(self, fid, name, frame: Frame, holes, d=3, depth=10.0, cbore=None, shape=None, spacing=None,
                      count=None, spacing_y=None, symmetry=None, role="component"):
        """Clearance holes from the face at `frame` (normal out of the material) `depth` deep; `cbore` =
        (diameter, depth) counterbores them from the far face (the screw head's side)."""
        if shape and shape != "positions":
            holes = bolt_holes(shape, spacing, count or len(holes), spacing_y)
        m = frame.matrix()
        n = np.asarray(frame.basis()[2])
        for (x, y) in holes:
            p = (m @ np.array([x, y, 0, 1.0]))[:3]
            self.cut(_cyl_dir(p - n * depth / 2, n, hw.CLEAR[d] / 2, depth + 0.02))
            if cbore:
                cd, ch = cbore
                self.cut(_cyl_dir(p - n * (depth - ch / 2), n, cd / 2, ch + 0.02))
        params = dict(role=role, fastener=f"M{d:g}", threaded=False)
        if shape:
            params.update(shape=shape, spacing=spacing, count=count or len(holes))
            if spacing_y is not None:
                params["spacing_y"] = spacing_y
        else:
            params.update(positions=[list(h) for h in holes], shape="positions")
        f = Frame(frame.origin, frame.normal, frame.x, symmetry)
        return self.feature(fid, name, f, "bolt_pattern", **params)

    def part(self, origin=(0, 0, 0)) -> PartDef:
        """The PartDef about `origin` (design-frame coordinates of the part's own origin)."""
        o = np.asarray(origin, dtype=float)
        m = translate(*(-o))
        p = PartDef(self.pid, self.name, self.category, self.color, Pos(*(-o)) * self.solid,
                    meta={"material": self.material, "print": PRINT.get(self.material, ""), "inserts": self.inserts,
                          "design_origin": [float(v) for v in o], **self.meta},
                    notes="; ".join(self.notes))
        for fid, name, fr, kind, params in self.features:
            p.add(fid, name, fr.moved(m), kind, **params)
        return p


def _cyl_dir(center, direction, r, h):
    """Cylinder of radius r, length h, centred at `center`, axis along `direction`."""
    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    z = np.array([0, 0, 1.0])
    c = Cylinder(r, h)
    if np.allclose(d, z):
        return Pos(*center) * c
    if np.allclose(d, -z):
        return Pos(*center) * (Rot(180, 0, 0) * c)
    axis = np.cross(z, d)
    ang = math.degrees(math.acos(max(-1, min(1, float(np.dot(z, d))))))
    from build123d import Location
    loc = Location((0, 0, 0), tuple(axis / np.linalg.norm(axis)), ang)
    return Pos(*center) * (loc * c)


def cyl_dir(center, direction, r, h):
    return _cyl_dir(center, direction, r, h)
