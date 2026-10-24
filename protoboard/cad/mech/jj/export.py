"""Write a solved assembly out: per-part bodies (STEP, GLB, STL, manifest), the placed scene, a preview GLB.

Per part (out/mech/parts/<part id>/):
    body.step, body.glb (metres, Y-up), body.stl (mm), body.manifest.json (volume, features with
    their area/centroid signatures, mass, material)
Per assembly (out/mech/tier-<t>/):
    scene.json      every instance (part, link, world matrix at the zero pose, explode vector), every
                    hardware placement, the mates, the joints and the links
    preview.glb     everything placed, one node per instance, coloured by material (for quick looks)
"""
from __future__ import annotations

import hashlib
import json
import os

import numpy as np
from build123d import export_step, export_stl, export_gltf, Compound, Location, Matrix

from .geom import mat_to_list

DENSITY = {   # g/cm3 of the modelled solid (printed parts: material x the solid fraction the print settings give)
    "petg-cf": 1.30 * 0.62, "petg": 1.27 * 0.55, "pla": 1.24 * 0.35, "metal_steel": 7.85, "metal_alu": 2.70,
    "brass": 8.5, "rubber": 1.2, "wood_ply": 0.65, "concrete": 2.3, "bucket": 0.95, "plastic_black": 1.15,
}


def part_mass_g(part):
    if part.mass_g is not None:
        return float(part.mass_g)
    mat = part.meta.get("material") or part.material
    rho = DENSITY.get(mat) or DENSITY.get(part.material) or 1.0
    return float(part.solid.volume) / 1000.0 * rho


def to_location(m):
    from OCP.gp import gp_Trsf
    m = np.asarray(m, dtype=float)
    t = gp_Trsf()
    t.SetValues(*[float(m[r, c]) for r in range(3) for c in range(4)])
    return Location(t)


def baked(shape):
    """The shape with its location moved into the geometry. build123d 0.13's glTF export writes a located shape's
    translation into the node without the Y-up turn, so a part with a location lands offset and turned."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.TopLoc import TopLoc_Location
    from build123d import Shape
    w = shape.wrapped
    if w.Location().IsIdentity():
        return shape
    return Shape.cast(BRepBuilderAPI_Transform(w.Located(TopLoc_Location()), w.Location().Transformation(), True).Shape())


def export_part(part, out_dir, formats=("glb", "stl", "step")):
    d = os.path.join(out_dir, part.id)
    os.makedirs(d, exist_ok=True)
    solid = part.solid
    if "step" in formats:
        export_step(solid, os.path.join(d, "body.step"))
    if "glb" in formats:
        export_gltf(baked(solid), os.path.join(d, "body.glb"), binary=True, linear_deflection=0.08, angular_deflection=0.3)
    if "stl" in formats:
        export_stl(solid, os.path.join(d, "body.stl"), tolerance=0.05, angular_tolerance=0.2)
    feats = {}
    for fid, f in part.features.items():
        feats[fid] = {"kind": f.kind, "frame": f.frame.as_json(), "params": f.params}
    man = {"artifact": part.id, "units": "mm", "tool": "build123d", "volume_mm3": round(float(solid.volume), 2),
           "mass_g": round(part_mass_g(part), 2), "material": part.meta.get("material") or part.material,
           "category": part.category, "features": feats, "source": part.source, "meta": _jsonable(part.meta)}
    json.dump(man, open(os.path.join(d, "body.manifest.json"), "w"), indent=1)
    return d


def _jsonable(x):
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return str(x)


def scene_json(asm, hardware, path):
    inst = []
    for iid, i in asm.instances.items():
        inst.append({"id": iid, "part": i.part.id, "link": i.link, "matrix": mat_to_list(i.matrix) if i.matrix is not None else None,
                     "explode": list(i.explode), "category": i.part.category, "material": i.part.meta.get("material") or i.part.material,
                     "color": i.part.material, "mass_g": round(part_mass_g(i.part), 2)})
    hws = [{"mate": h["mate"], "part": h["hw"].id, "matrix": mat_to_list(h["matrix"]), "link": asm.instances[h["mounted"]].link,
            "structure": h["structure"], "mounted": h["mounted"], "step": h["step"], "mass_g": round(part_mass_g(h["hw"]), 3)}
           for h in hardware]
    mates = [{"id": m.id, "a": list(m.a), "b": list(m.b), "gap": m.gap, "rot": m.rot, "step": m.step, "note": m.note,
              "stack": [{"part": s.hw.id, "at": s.at, "direction": s.direction, "torque_nm": s.torque_nm, "torque_note": s.torque_note,
                         "positions": s.positions} for s in m.stack]} for m in asm.mates]
    joints = [{"id": j.id, "name": j.name, "parent": j.parent, "child": j.child, "origin": list(map(float, j.origin)),
               "axis": list(map(float, j.axis)), "limits": list(j.limits), "actuator": j.actuator, "ratio": j.ratio,
               "spring": j.spring, "servo_instance": j.servo_instance, "home_deg": j.home_deg} for j in asm.joints]
    json.dump({"name": asm.name, "root": asm.root, "links": list(asm.links.values()), "instances": inst, "hardware": hws,
               "mates": mates, "joints": joints}, open(path, "w"), indent=1)


def preview_glb(asm, hardware, path, include_hw=True, skip_links=()):
    """One GLB with every placed body, one node per material (so a viewer can colour by name)."""
    groups = {}
    for iid, i in asm.instances.items():
        if i.matrix is None or i.part.solid is None or i.link in skip_links:
            continue
        groups.setdefault(i.part.material, []).append(to_location(i.matrix) * i.part.solid)
    if include_hw:
        for h in hardware:
            groups.setdefault(h["hw"].material, []).append(to_location(h["matrix"]) * h["hw"].solid)
    comps = []
    for mat, shapes in groups.items():
        c = Compound(children=shapes)
        c.label = mat
        comps.append(c)
    export_gltf(Compound(children=comps), path, binary=True, linear_deflection=0.2, angular_deflection=0.5)
