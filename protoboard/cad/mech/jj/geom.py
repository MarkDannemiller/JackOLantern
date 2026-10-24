"""Frames and mates, the same arithmetic as UHD's `assemble()` (@deltarobotics/uhd src/system/geometry.ts).

A frame is an origin, a normal (+Z of the frame) and an x axis, in a part's own coordinates (mm, Z up).
Two frames mate when their origins coincide (offset by `gap` along A's normal), B's normal opposes A's,
and B's x axis lines up with A's x axis rotated by `rot` degrees about A's normal. Placing B is then
    world(B) = world(A) @ mate_transform(frame_a, frame_b, rot, gap)
exactly as `assemble()` does it, so the placements computed here are the ones the stack computes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

Vec = tuple[float, float, float]


def _norm(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n else v


@dataclass
class Frame:
    origin: Vec
    normal: Vec
    x: Vec | None = None
    symmetry_deg: float | None = None

    def basis(self):
        z = _norm(self.normal)
        if self.x is not None:
            x = _norm(self.x)
        else:
            x = np.array([1.0, 0, 0]) if abs(z[0]) < 0.9 else np.array([0, 1.0, 0])
        x = _norm(x - z * np.dot(x, z))
        y = np.cross(z, x)
        return x, y, z

    def matrix(self):
        x, y, z = self.basis()
        m = np.eye(4)
        m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, self.origin
        return m

    def moved(self, m):
        """This frame expressed after applying the 4x4 transform m (part -> parent coordinates)."""
        x, _, z = self.basis()
        o = (m @ np.array([*self.origin, 1.0]))[:3]
        r = m[:3, :3]
        return Frame(tuple(o), tuple(r @ z), tuple(r @ x), self.symmetry_deg)

    def flipped(self):
        """Same origin, opposite normal (x kept): the face looking the other way."""
        x, _, z = self.basis()
        return Frame(self.origin, tuple(-z), tuple(x), self.symmetry_deg)

    def offset(self, d):
        """Moved d mm along its own normal."""
        _, _, z = self.basis()
        return Frame(tuple(np.asarray(self.origin) + z * d), self.normal, self.x, self.symmetry_deg)

    def as_json(self):
        x, _, z = self.basis()
        out = {"origin": [round(float(v), 4) for v in self.origin], "normal": [round(float(v), 6) for v in z],
               "xAxis": [round(float(v), 6) for v in x]}
        if self.symmetry_deg:
            out["symmetryDeg"] = self.symmetry_deg
        return out


def mate_transform(a: Frame, b: Frame, rot_deg: float = 0.0, gap: float = 0.0):
    """4x4 that places B (in its own coordinates) so that its frame meets A's (UHD mateTransform)."""
    if gap:
        a = a.offset(gap)
    ax, ay, az = a.basis()
    t = math.radians(rot_deg)
    tx = _norm(ax * math.cos(t) + ay * math.sin(t))
    tz = -az
    ty = np.cross(tz, tx)
    bx, by, bz = b.basis()
    T = np.stack([tx, ty, tz])          # rows
    B = np.stack([bx, by, bz])
    R = T.T @ B                           # R[i][j] = sum_k T[k][i] B[k][j]
    tr = np.asarray(a.origin) - R @ np.asarray(b.origin)
    m = np.eye(4)
    m[:3, :3] = R
    m[:3, 3] = tr
    return m


def translate(x, y, z):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def rot_axis(axis, deg):
    """Rotation about a unit axis through the origin (4x4)."""
    a = _norm(axis)
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    x, y, z = a
    r = np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                  [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                  [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])
    m = np.eye(4)
    m[:3, :3] = r
    return m


def rot_about(origin, axis, deg):
    o = np.asarray(origin, dtype=float)
    return translate(*o) @ rot_axis(axis, deg) @ translate(*(-o))


def bolt_holes(shape: str, spacing: float, count: int = 4, spacing_y: float | None = None, pitch: float | None = None):
    """Hole positions in a bolt pattern's frame, as UHD boltPatternHoles computes them."""
    if shape == "row":
        p = pitch if pitch is not None else (spacing / (count - 1) if count > 1 else 0)
        return [(-spacing / 2 + k * p, 0.0) for k in range(count)]
    if shape == "circle":
        return [(math.cos(2 * math.pi * k / count) * spacing / 2, math.sin(2 * math.pi * k / count) * spacing / 2) for k in range(count)]
    sy = spacing_y if spacing_y is not None else spacing
    if shape == "cross":
        return [(-spacing / 2, 0.0), (spacing / 2, 0.0), (0.0, -sy / 2), (0.0, sy / 2)]
    return [(-spacing / 2, -sy / 2), (spacing / 2, -sy / 2), (spacing / 2, sy / 2), (-spacing / 2, sy / 2)]


def mat_to_list(m):
    """Row-major 16 numbers (UHD Mat4)."""
    return [round(float(v), 6) for v in np.asarray(m).reshape(-1)]
