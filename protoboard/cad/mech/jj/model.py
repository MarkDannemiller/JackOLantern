"""Part definitions, instances, mates and joints: the mechanical model one tier is built from.

PartDef      one physical part design (printed, bought, cut), its solid in its own frame (mm, Z up)
             and its features: named frames the part mates on (bolt patterns, bearing seats, shafts...)
Instance     a PartDef placed in the assembly, on one kinematic link
Mate         two instances' features brought together (UHD mate: origins meet, normals oppose),
             optionally carried by a fastener stack (the screws, inserts, nuts, spacers that hold it)
Joint        a revolute axis between two links (servo-driven, belt-driven, or passive)

The assembly is solved the way UHD `assemble()` solves it: from the root, every mate places the
unplaced side. Hardware sits at every hole of the structure side's bolt pattern, along its normal.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .geom import Frame, bolt_holes, mate_transform, translate

FLIP = np.diag([1.0, -1.0, -1.0, 1.0])


@dataclass
class Feature:
    id: str
    name: str
    frame: Frame
    kind: str                     # bolt_pattern | bearing_seat | bearing | shaft | face | belt | anchor | t_slot
    params: dict = field(default_factory=dict)

    def holes(self):
        p = self.params
        if self.kind != "bolt_pattern" or "positions" in p:
            return [tuple(h) for h in p.get("positions", [])]
        return bolt_holes(p["shape"], p["spacing"], p.get("count", 4), p.get("spacing_y"), p.get("pitch"))


@dataclass
class PartDef:
    id: str
    name: str
    category: str                 # printed | bought | cut | vendor | costume | hardware
    material: str                 # render / density key
    solid: Any = None             # build123d shape in part coordinates
    features: dict = field(default_factory=dict)
    mass_g: float | None = None   # bought parts: maker's mass; else volume x density
    source: str = ""              # where the design numbers come from
    notes: str = ""
    vendor_file: str | None = None  # vendor STEP used as the body
    meta: dict = field(default_factory=dict)  # part number, print settings, supplier, hardware sizes

    def add(self, fid, name, frame, kind, **params):
        self.features[fid] = Feature(fid, name, frame, kind, params)
        return self.features[fid]


@dataclass
class Instance:
    id: str
    part: PartDef
    link: str
    matrix: np.ndarray | None = None   # world placement at the zero pose
    explode: tuple = (0.0, 0.0, 0.0)


@dataclass
class StackItem:
    hw: PartDef                   # hardware part (screw, insert, nut, washer, spacer)
    at: float                     # along the structure frame's normal (mm)
    direction: int = 1
    torque_nm: float | None = None
    torque_note: str = ""
    positions: list | None = None  # override the pattern's holes


@dataclass
class Mate:
    id: str
    a: tuple                      # (instance id, feature id) -- the structure side when bolted
    b: tuple
    gap: float = 0.0
    rot: float = 0.0
    stack: list = field(default_factory=list)   # StackItem list
    step: str = ""                # build-guide step this mate belongs to
    note: str = ""


@dataclass
class Joint:
    id: str
    name: str
    parent: str                   # link names
    child: str
    origin: tuple                 # world, zero pose (mm)
    axis: tuple                   # world unit vector
    limits: tuple                 # degrees
    actuator: str | None = None   # servo key
    ratio: float = 1.0            # output turns per servo turn^-1 (belt reduction)
    spring: dict | None = None    # {k_N_per_mm, drum_r_mm, preload_N, ...}
    servo_instance: str | None = None
    home_deg: float = 0.0


class Assembly:
    def __init__(self, name: str, root: str):
        self.name = name
        self.root = root
        self.instances: dict[str, Instance] = {}
        self.mates: list[Mate] = []
        self.joints: list[Joint] = []
        self.links: dict[str, dict] = {}
        self.fixed: dict[str, np.ndarray] = {}

    # -- building
    def link(self, name, parent=None, role=""):
        self.links[name] = {"name": name, "parent": parent, "role": role}
        return name

    def add(self, iid, part: PartDef, link: str, explode=(0, 0, 0), at=None):
        assert iid not in self.instances, iid
        inst = Instance(iid, part, link, None, tuple(explode))
        self.instances[iid] = inst
        if at is not None:
            self.fixed[iid] = np.asarray(at, dtype=float)
        return inst

    def mate(self, mid, a, b, gap=0.0, rot=0.0, stack=None, step="", note=""):
        for iid, fid in (a, b):
            assert iid in self.instances, f"{mid}: no instance {iid}"
            assert fid in self.instances[iid].part.features, f"{mid}: {iid} ({self.instances[iid].part.id}) has no feature {fid}"
        m = Mate(mid, a, b, gap, rot, stack or [], step, note)
        self.mates.append(m)
        return m

    def joint(self, *args, **kw):
        j = Joint(*args, **kw)
        self.joints.append(j)
        return j

    def feature(self, iid, fid) -> Feature:
        return self.instances[iid].part.features[fid]

    def world_frame(self, iid, fid) -> Frame:
        inst = self.instances[iid]
        return inst.part.features[fid].frame.moved(inst.matrix)

    # -- solving (UHD assemble)
    def solve(self):
        placed = {self.root: np.eye(4)} if self.root not in self.fixed else {}
        placed.update(self.fixed)
        issues = []
        used = set()
        progress = True
        while progress:
            progress = False
            for m in self.mates:
                if m.id in used:
                    continue
                (ia, fa), (ib, fb) = m.a, m.b
                A, B = self.feature(ia, fa).frame, self.feature(ib, fb).frame
                pa, pb = placed.get(ia), placed.get(ib)
                if pa is not None and pb is None:
                    placed[ib] = pa @ mate_transform(A, B, m.rot, m.gap)
                elif pb is not None and pa is None:
                    placed[ia] = pb @ mate_transform(B, A, -m.rot, m.gap)
                elif pa is None and pb is None:
                    continue
                else:
                    n = np.asarray(A.basis()[2])
                    exp = (pa @ np.array([*(np.asarray(A.origin) + n * m.gap), 1.0]))[:3]
                    got = (pb @ np.array([*B.origin, 1.0]))[:3]
                    off = float(np.linalg.norm(exp - got))
                    if off > 0.1:
                        issues.append(f"{m.id}: over-constrained, {ib}.{fb} is {off:.2f} mm from where {ia}.{fa} puts it")
                    za = (pa[:3, :3] @ A.basis()[2])
                    zb = (pb[:3, :3] @ B.basis()[2])
                    if float(np.dot(za, zb)) > -0.999:
                        issues.append(f"{m.id}: over-constrained, normals not opposed ({math.degrees(math.acos(max(-1, min(1, -float(np.dot(za, zb)))))):.1f} deg)")
                used.add(m.id)
                progress = True
        for iid, inst in self.instances.items():
            inst.matrix = placed.get(iid)
            if inst.matrix is None:
                issues.append(f"{iid}: not placed (no mate reaches it)")
        return issues

    # -- hardware placement (UHD placeHardware)
    def hardware(self):
        out = []
        for m in self.mates:
            if not m.stack:
                continue
            (ia, fa), (ib, fb) = m.a, m.b
            fs = self.feature(ia, fa)
            base = self.instances[ia].matrix @ fs.frame.matrix()
            holes = fs.holes()
            for k, item in enumerate(m.stack):
                for (x, y) in (item.positions or holes):
                    local = translate(x, y, item.at) @ (np.eye(4) if item.direction == 1 else FLIP)
                    out.append({"mate": m.id, "item": k, "hw": item.hw, "matrix": base @ local, "link": self.instances[ib].link
                                if self._is_child_side(m) else self.instances[ia].link, "step": m.step,
                                "structure": ia, "mounted": ib})
        return out

    def _is_child_side(self, m):
        """Hardware rides with the mounted part's link when the mate crosses no joint (always the case here)."""
        return False

    # -- checks
    def stack_checks(self):
        """Screw length against the stack: thread beyond each nut, engagement in each insert (mm)."""
        rows = []
        for m in self.mates:
            screws = [s for s in m.stack if s.hw.meta.get("kind") == "screw"]
            for s in screws:
                L = s.hw.meta["length"]
                lo, hi = sorted((s.at, s.at + s.direction * L))
                for o in m.stack:
                    kind = o.hw.meta.get("kind")
                    if kind not in ("nut", "insert"):
                        continue
                    h = o.hw.meta["length"]
                    olo, ohi = sorted((o.at, o.at + o.direction * h))
                    if kind == "nut":
                        far = ohi if s.direction == -1 and False else None
                        # the screw must pass the nut's far face (the face away from the head)
                        far = olo if s.direction == -1 else ohi
                        beyond = (far - lo) if s.direction == -1 else (hi - far)
                        rows.append({"mate": m.id, "screw": s.hw.id, "against": o.hw.id, "kind": "beyond nut", "mm": round(beyond, 2), "ok": beyond >= 0})
                    else:
                        engaged = min(hi, ohi) - max(lo, olo)
                        need = 1.5 * s.hw.meta["diameter"]
                        rows.append({"mate": m.id, "screw": s.hw.id, "against": o.hw.id, "kind": "insert engagement", "mm": round(engaged, 2),
                                     "need": round(min(need, h * 0.9), 2), "ok": engaged >= min(need, h * 0.9)})
        return rows
