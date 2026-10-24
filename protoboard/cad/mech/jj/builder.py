"""Builder: designs printed parts in a design frame (DF), places bought and generic parts in it, and
records the mates between them, so that every pair of mating frames is computed from one place.

Printed parts are `Design`s whose solids and features are in DF coordinates; a design becomes a
PartDef about its own origin. Generic parts (bought parts, hubs used at several joints) keep their own
coordinates and are placed by a DF matrix. A host's receiving feature is the generic part's feature,
moved into the DF and flipped, so the mate closes exactly.

`emit(asm, prefix, world)` adds the instances and mates to an Assembly; `world` maps DF to world for
the instance whose placement anchors the build (the solver places everything else through mates).
"""
from __future__ import annotations

import math

import numpy as np

from .geom import Frame, translate, bolt_holes
from .model import Assembly, PartDef, StackItem
from .printed import Design
from .common import insert_stack, horn_stack, servo_screw_stack

MY = np.diag([1.0, -1.0, 1.0, 1.0])


def mirror_frame(f: Frame) -> Frame:
    """Mirror a frame across the DF plane y = 0 (origin, normal and x axis)."""
    o = (f.origin[0], -f.origin[1], f.origin[2])
    x, _, z = f.basis()
    return Frame(o, (z[0], -z[1], z[2]), (x[0], -x[1], x[2]), f.symmetry_deg)


class Builder:
    def __init__(self, name):
        self.name = name
        self.designs: dict[str, Design] = {}
        self.origins: dict[str, tuple] = {}
        self.generic: dict[str, PartDef] = {}
        self.instances: dict[str, dict] = {}
        self.mates: list[dict] = []
        self.joints: list[dict] = []
        self.parts: dict[str, PartDef] = {}
        self.proxies: set[str] = set()       # instances that stand in for another builder's (not emitted)

    # ---------------------------------------------------------------- parts and instances
    def design(self, pid, name, origin, material="petg-cf", color="printed_cf"):
        d = Design(pid, name, material, "printed", color)
        self.designs[pid] = d
        self.origins[pid] = tuple(origin)
        return d

    def add_design(self, iid, pid, link, explode=(0, 0, 0)):
        self.instances[iid] = dict(part=pid, link=link, M=translate(*self.origins[pid]), kind="design", explode=explode)
        return iid

    def add_generic(self, iid, part: PartDef, link, M, explode=(0, 0, 0)):
        self.generic[part.id] = part
        self.instances[iid] = dict(part=part.id, link=link, M=np.asarray(M, dtype=float), kind="generic", explode=explode)
        return iid

    def add_proxy(self, iid, part: PartDef, M):
        """A stand-in for an instance another builder owns (to compute mating frames); never emitted."""
        self.add_generic(iid, part, "proxy", M)
        self.proxies.add(iid)
        return iid

    def df(self, iid, fid) -> Frame:
        """A feature's frame in the DF."""
        inst = self.instances[iid]
        if inst["kind"] == "design":
            d = self.designs[inst["part"]]
            for f in d.features:
                if f[0] == fid:
                    return f[2]
            raise KeyError(f"{inst['part']} has no feature {fid}")
        return self.generic[inst["part"]].features[fid].frame.moved(inst["M"])

    # ---------------------------------------------------------------- features + mates
    def receive(self, host: Design, fid, name, iid, gfid, kind="face", **params):
        """Host feature that receives generic instance `iid`'s feature `gfid` (flipped DF frame)."""
        fr = self.df(iid, gfid).flipped()
        host.feature(fid, name, fr, kind, **params)
        return fr

    def mate(self, mid, a, b, stack=None, step="", gap=0.0, rot=None, note=""):
        """A mate between two instances' features. `rot` (about A's normal, from A's x axis to B's) defaults
        to the angle the design placements give, so a symmetric pattern can never be solved turned by a
        multiple of its symmetry."""
        if rot is None:
            fa, fb = self.df(*a), self.df(*b)
            xa, _, za = fa.basis()
            xb, _, _ = fb.basis()
            rot = math.degrees(math.atan2(float(np.dot(np.cross(xa, xb), za)), float(np.dot(xa, xb))))
            rot = round(rot, 6) + 0.0
            if abs(rot) < 1e-6:
                rot = 0.0
        self.mates.append(dict(id=mid, a=a, b=b, stack=stack or [], step=step, gap=gap, rot=rot, note=note))

    def screw_into_generic(self, mid, iid, gfid, host: Design, host_iid, fid, name, plate_t, step="", d=3, kind="insert"):
        """Screws through `host` (plate_t thick at the joint) into generic part `iid`'s threaded pattern
        (heat-set inserts, a servo horn, or a servo case)."""
        g = self.generic[self.instances[iid]["part"]]
        gf = g.features[gfid]
        fr = self.df(iid, gfid)
        p = gf.params
        holes = gf.holes()
        host.clear_pattern(fid, name, fr.flipped(), [(x, -y) for (x, y) in holes], d=d, depth=plate_t,
                           shape=p.get("shape") if p.get("shape") != "positions" else None, spacing=p.get("spacing"),
                           spacing_y=p.get("spacing_y"), symmetry=fr.symmetry_deg)
        if kind == "insert":
            stack = insert_stack(d, plate_t)
        elif kind == "horn":
            stack = horn_stack(plate_t, d)
        elif kind == "servo":
            stack = servo_screw_stack(plate_t)
        elif kind == "tap":
            from .common import choose_len, torque
            from . import hw as _hw
            t, note = torque(d, "insert")
            stack = [StackItem(_hw.shcs(d, choose_len(d, plate_t, 4.5, 7.5)), plate_t, -1, t,
                               "assumption: thread-forming into the maker's printed part; " + note)]
        else:
            stack = []
        self.mate(mid, (iid, gfid), (host_iid, fid), stack, step)

    def screw_generic_into_design(self, mid, host: Design, host_iid, fid, name, iid, gfid, plate_t, step="", d=3):
        """Screws through generic part `iid` (its clearance pattern `gfid`, plate_t thick) into heat-set
        inserts the host gets at the matching frame."""
        g = self.generic[self.instances[iid]["part"]]
        p = g.features[gfid].params
        fr = self.df(iid, gfid).flipped()
        host.insert_pattern(fid, name, fr, [], d, shape=p.get("shape"), spacing=p.get("spacing"), count=p.get("count"),
                            spacing_y=p.get("spacing_y"), symmetry=fr.symmetry_deg)
        self.mate(mid, (host_iid, fid), (iid, gfid), insert_stack(d, plate_t), step)

    def screw_design_pair(self, mid, a: Design, a_iid, fa, b: Design, b_iid, fb, frame: Frame, holes, plate_t, step="",
                          d=3, name_a="", name_b="", shape=None, spacing=None, spacing_y=None, symmetry=None, count=None):
        """Inserts in printed part A at `frame` (normal out of A), clearance through printed part B."""
        a.insert_pattern(fa, name_a or fa, frame, holes, d, shape=shape, spacing=spacing, spacing_y=spacing_y, symmetry=symmetry,
                         count=count)
        b.clear_pattern(fb, name_b or fb, frame.flipped(), [(x, -y) for (x, y) in holes], d, depth=plate_t, shape=shape,
                        spacing=spacing, spacing_y=spacing_y, symmetry=symmetry, count=count)
        self.mate(mid, (a_iid, fa), (b_iid, fb), insert_stack(d, plate_t), step)

    def face_pair(self, mid, a: Design, a_iid, fa, b: Design, b_iid, fb, frame: Frame, step="", kind="face", name_a="", name_b="", **params):
        a.feature(fa, name_a or fa, frame, kind, role="structure", **params)
        b.feature(fb, name_b or fb, frame.flipped(), kind, role="component", **params)
        self.mate(mid, (a_iid, fa), (b_iid, fb), [], step)

    def joint(self, **kw):
        self.joints.append(kw)

    # ---------------------------------------------------------------- output
    def finalize(self):
        for pid, d in self.designs.items():
            self.parts[pid] = d.part(self.origins[pid])
        self.parts.update(self.generic)
        return self.parts

    def emit(self, asm: Assembly, prefix: str, link_prefix: str = "", anchor: str | None = None, world=None, parts=None,
             alias: dict | None = None, link_alias: dict | None = None):
        """Add the instances and mates. `alias` maps proxy instance ids to the full ids of the instances they
        stand for; `link_alias` renames links (a hand's 'wrist' is the arm's 'wrist')."""
        parts = parts or self.parts
        alias = alias or {}
        link_alias = link_alias or {}
        full = lambda iid: alias.get(iid, prefix + iid)
        for iid, inst in self.instances.items():
            if iid in self.proxies:
                continue
            ln = link_alias.get(inst["link"], link_prefix + inst["link"])
            asm.add(prefix + iid, parts[inst["part"]], ln, inst["explode"],
                    at=(world @ inst["M"]) if (anchor == iid and world is not None) else None)
        for m in self.mates:
            asm.mate(prefix + m["id"], (full(m["a"][0]), m["a"][1]), (full(m["b"][0]), m["b"][1]), m["gap"], m["rot"],
                     m["stack"], m["step"], m["note"])
        return asm

    def mirrored(self, suffix="-l", name_suffix=" (left)"):
        """The same build mirrored across the DF plane y = 0: printed parts mirrored (new part ids), generic
        parts placed by proper transforms (MY . M . own-Y mirror), so a bought servo stays a real servo."""
        from build123d import Plane
        b = Builder(self.name + suffix)
        b.proxies = set(self.proxies)
        ren = {pid: pid + suffix for pid in self.designs}
        for pid, d in self.designs.items():
            nd = Design(ren[pid], d.name + name_suffix, d.material, d.category, d.color)
            nd.solid = d.solid.mirror(Plane.XZ)
            nd.features = [(fid, nm, mirror_frame(fr), kind, dict(params)) for (fid, nm, fr, kind, params) in d.features]
            nd.notes, nd.inserts, nd.meta = list(d.notes), list(d.inserts), {**d.meta, "mirror_of": pid}
            b.designs[ren[pid]] = nd
            o = self.origins[pid]
            b.origins[ren[pid]] = (o[0], -o[1], o[2])
        b.generic = dict(self.generic)
        # a chiral bought part (a left/right hand kit) becomes its mirror image: solid and features mirrored in its
        # own frame, placed by the same proper transform as every other generic part
        for pid, g in list(self.generic.items()):
            if g.meta.get("chiral") and g.solid is not None:
                from .model import PartDef as _PD
                q = _PD(pid[:-2] + "-l" if pid.endswith("-r") else pid + "-l", g.meta.get("mirror_name", g.name + " (left)"), g.category, g.material,
                        g.solid.mirror(Plane.XZ), {}, g.mass_g, g.source, g.notes, g.vendor_file, {**g.meta, "mirror_of": pid})
                for fid, f in g.features.items():
                    q.features[fid] = type(f)(f.id, f.name, mirror_frame(f.frame), f.kind, dict(f.params))
                b.generic[q.id] = q
                ren[pid] = q.id
        for iid, inst in self.instances.items():
            if inst["kind"] == "design":
                b.instances[iid] = dict(inst, part=ren[inst["part"]], M=translate(*b.origins[ren[inst["part"]]]))
            else:
                b.instances[iid] = dict(inst, part=ren.get(inst["part"], inst["part"]), M=MY @ inst["M"] @ MY)
        b.mates = [dict(m) for m in self.mates]
        b.joints = [dict(j) for j in self.joints]
        # a design feature that mates a generic part is re-derived from the generic's mirrored placement (exact),
        # so the frames agree on the x axis too (a mirrored frame of a 45 deg horn pattern would be off by 90 deg)
        for m in b.mates:
            if m["gap"]:
                continue
            (ia, fa), (ib, fb) = m["a"], m["b"]
            ka, kb = b.instances[ia]["kind"], b.instances[ib]["kind"]
            if ka == "generic" and kb == "design":
                g, d, fd = ia, b.designs[b.instances[ib]["part"]], (ib, fb)
                gf = fa
            elif kb == "generic" and ka == "design":
                g, d, fd = ib, b.designs[b.instances[ia]["part"]], (ia, fa)
                gf = fb
            else:
                continue
            target = b.df(g, gf).flipped()
            d.features = [(fid, nm, (Frame(target.origin, target.normal, target.x, fr.symmetry_deg) if fid == fd[1] else fr), kind, params)
                          for (fid, nm, fr, kind, params) in d.features]
        for m in b.mates:
            fa, fb = b.df(*m["a"]), b.df(*m["b"])
            xa, _, za = fa.basis()
            xb, _, _ = fb.basis()
            r = math.degrees(math.atan2(float(np.dot(np.cross(xa, xb), za)), float(np.dot(xa, xb))))
            m["rot"] = 0.0 if abs(r) < 1e-6 else round(r, 6)
        b.finalize()
        return b
