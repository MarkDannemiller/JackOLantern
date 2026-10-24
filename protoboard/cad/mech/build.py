"""Build Joyful Jack's mechanical model for all three tiers and write it where the project uses it.

    ~/.local/opt/jj-mech/bin/python cad/mech/build.py [--parts] [a b c]

Writes (generated; never edit by hand):
  src/mech/mech.json                     every part: name, category, material, mass, features (frames and
                                         parameters), body files; read by src/mech/*.uhd.ts
  src/mech/tier-<t>.json                 instances (part, link, module, zero-pose world matrix), mates with
                                         their fastener stacks, joints
  src/mech/parts/<id>/body.{step,glb,manifest.json} (+ body.stl for printed parts)   printed and cut parts
  parts/local/mech/<id>/body.{step,glb,manifest.json}                                bought parts (nominal or maker CAD)
  out/mech/tier-<t>/scene.json, preview.glb                                           renders and simulation (with costume)
Hardware (screws, nuts, inserts, T-nuts, washers) gets its nominal bodies from the stack's hardware-cad.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jj.assemble import build_tier  # noqa: E402
from jj.export import export_part, part_mass_g, preview_glb, _jsonable  # noqa: E402
from jj.geom import mat_to_list  # noqa: E402

PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC_MECH = os.path.join(PROJECT, "src", "mech")
LOCAL_MECH = os.path.join(PROJECT, "parts", "local", "mech")
OUT = os.path.join(PROJECT, "out", "mech")


def part_dir(p):
    if p.category in ("printed", "cut"):
        return os.path.join(SRC_MECH, "parts"), f"src/mech/parts/{p.id}"
    return LOCAL_MECH, f"parts/local/mech/{p.id}"


def module_of(iid):
    """Which UHD module an instance belongs to: the arms' and hands' parts go in the arm module; everything else
    in the body module, except the electronics bodies and the head (root-level parts)."""
    if iid.startswith("arm_"):
        return iid.split("/", 1)[0]
    if iid.startswith("costume/"):
        return "costume"
    if iid == "head" or iid.startswith("body__"):
        return "root"
    return "body"


def main(tiers, write_parts):
    t0 = time.time()
    os.makedirs(SRC_MECH, exist_ok=True)
    os.makedirs(LOCAL_MECH, exist_ok=True)
    db = {}
    built = {}
    for t in tiers:
        asm, info = build_tier(t, costume=True)
        assert not info["issues"], info["issues"]
        bad = [r for r in asm.stack_checks() if not r["ok"]]
        assert not bad, bad
        built[t] = (asm, info)
        print(f"tier {t}: {len(asm.instances)} instances, {len(asm.mates)} mates ({time.time() - t0:.0f} s)")
        for i in asm.instances.values():
            db.setdefault(i.part.id, i.part)
        for m in asm.mates:
            for s in m.stack:
                db.setdefault(s.hw.id, s.hw)
    # parts
    entries = {}
    for pid, p in sorted(db.items()):
        e = {"id": pid, "name": p.name, "category": p.category, "material": p.meta.get("material") or p.material, "color": p.material,
             "mass_g": round(part_mass_g(p), 3) if p.solid is not None or p.mass_g is not None else None,
             "source": p.source, "notes": p.notes, "meta": _jsonable({k: v for k, v in p.meta.items() if k not in ("case",)}),
             "features": {fid: {"name": f.name, "kind": f.kind, "frame": f.frame.as_json(), "params": _jsonable(f.params)} for fid, f in p.features.items()}}
        if p.category in ("hardware",):
            e["hardware"] = _jsonable(p.meta)
        elif p.category == "costume" or p.solid is None:
            e["body"] = None
        else:
            base, rel = part_dir(p)
            e["body"] = {"dir": rel, "step": f"{rel}/body.step", "glb": f"{rel}/body.glb", "manifest": f"{rel}/body.manifest.json",
                         **({"stl": f"{rel}/body.stl"} if p.category == "printed" else {})}
            e["volume_mm3"] = round(float(p.solid.volume), 2)
            if write_parts:
                export_part(p, base, formats=("glb", "step") + (("stl",) if p.category == "printed" else ()))
                os.replace(os.path.join(base, p.id, "body.manifest.json"), os.path.join(base, p.id, "body.manifest.json"))
        entries[pid] = e
    json.dump({"generated_by": "cad/mech/build.py", "parts": entries}, open(os.path.join(SRC_MECH, "mech.json"), "w"), indent=1)
    print(f"{len(entries)} parts ({time.time() - t0:.0f} s)")
    # tiers
    for t, (asm, info) in built.items():
        inst = {iid: {"part": i.part.id, "link": i.link, "module": module_of(iid), "matrix": mat_to_list(i.matrix), "explode": list(i.explode)}
                for iid, i in asm.instances.items()}
        mates = [{"id": m.id, "a": list(m.a), "b": list(m.b), "gap": m.gap, "rot": m.rot, "step": m.step, "note": m.note,
                  "stack": [{"part": s.hw.id, "at": s.at, "direction": s.direction, "torque_nm": s.torque_nm, "torque_note": s.torque_note,
                             **({"positions": [list(p) for p in s.positions]} if s.positions else {})} for s in m.stack]}
                 for m in asm.mates]
        joints = info["joints"]
        json.dump({"tier": t, "root": asm.root, "instances": inst, "mates": mates, "joints": _jsonable(joints)},
                  open(os.path.join(SRC_MECH, f"tier-{t}.json"), "w"), indent=1)
        d = os.path.join(OUT, f"tier-{t}")
        os.makedirs(d, exist_ok=True)
        hwp = asm.hardware()
        from jj.export import scene_json
        scene_json(asm, hwp, os.path.join(d, "scene.json"))
        sc = json.load(open(os.path.join(d, "scene.json")))
        sc["joints"] = _jsonable(joints)
        json.dump(sc, open(os.path.join(d, "scene.json"), "w"), indent=1)
        preview_glb(asm, hwp, os.path.join(d, "preview.glb"))
        print(f"tier {t}: wrote src/mech/tier-{t}.json and out/mech/tier-{t}/ ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args or ["a", "b", "c"], "--parts" in sys.argv)
