"""URDF of one tier for Isaac Sim, from the solved mechanical model.

    ~/.local/opt/jj-mech/bin/python cad/mech/sim/make_urdf.py <tier> [--payload 0.25]

Every kinematic link gathers the parts that ride on it (cad/mech: zero pose, world frame). Its mass,
centre of mass and inertia tensor come from the part solids (build123d/OpenCascade volume properties x
the part's density, or the maker's mass spread over the part's volume) plus every screw, nut and insert as
a point mass where the fastener stack puts it. Link frames sit on the joint that moves them, with the
world's axes at the zero pose, so a joint's axis is the world axis. Writes out/mech/sim/tier-<t>/:
    jack.urdf, meshes/<link>.stl (visual and collision, metres), links.json (mass properties, servo data).
The costume is left out (cloth: a few hundred grams, no stiffness).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from jj.assemble import build_tier  # noqa: E402
from jj.export import part_mass_g  # noqa: E402
from jj import bought  # noqa: E402
from jj import joints as JT  # noqa: E402
from jj.jointlib import STAGES, TORSION  # noqa: E402

from OCP.BRepGProp import BRepGProp  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
import trimesh  # noqa: E402

PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

_props = {}
_mesh = {}


def mass_props(part):
    """(volume mm3, com mm (own frame), inertia about com per unit density (mm^5)) of a part's solid."""
    if part.id in _props:
        return _props[part.id]
    s = part.solid
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(s.wrapped, g)
    v = g.Mass()
    c = g.CentreOfMass()
    m = g.MatrixOfInertia()
    I = np.array([[m.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])
    _props[part.id] = (v, np.array([c.X(), c.Y(), c.Z()]), I)
    return _props[part.id]


def tess(part, tol=0.6):
    if part.id in _mesh:
        return _mesh[part.id]
    try:
        verts, tris = part.solid.tessellate(tol, 0.5)
        v = np.array([[p.X, p.Y, p.Z] for p in verts], dtype=float)
        f = np.array(tris, dtype=np.int64)
    except Exception:
        # some faces (vendor STEP) do not triangulate this way: go through an STL export instead
        import tempfile
        from build123d import export_stl
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "p.stl")
            export_stl(part.solid, path, tolerance=tol, angular_tolerance=0.5)
            m = trimesh.load(path, force="mesh")
        v, f = np.asarray(m.vertices, dtype=float), np.asarray(m.faces, dtype=np.int64)
    _mesh[part.id] = (v, f)
    return _mesh[part.id]


LINK_ALIAS = {"r_torso": "torso", "l_torso": "torso", "base": "torso", "pack": "torso"}


def link_of(i):
    return LINK_ALIAS.get(i.link, i.link)


def build(tier, payload_kg=0.0, sandbags=0):
    asm, info = build_tier(tier, costume=False)
    assert not info["issues"], info["issues"]
    out = os.path.join(PROJECT, "out", "mech", "sim", f"tier-{tier}" + (f"+sandbags{sandbags}" if sandbags else ""))
    os.makedirs(os.path.join(out, "meshes"), exist_ok=True)
    joints = [j for j in info["joints"] if j["id"] != "neck_yaw"]
    # link frames: the child's joint origin; the torso at the world origin
    origin = {"torso": np.zeros(3), "head": np.array([0.0, 0.0, 1268.0])}
    parent = {}
    for j in joints:
        origin[j["child"]] = np.asarray(j["origin"], dtype=float)
        parent[j["child"]] = j["parent"]
    # mass properties and meshes per link
    acc = {}
    meshes = {}
    for iid, i in asm.instances.items():
        if i.part.solid is None and i.part.mass_g is None:
            continue
        L = link_of(i)
        a = acc.setdefault(L, dict(m=0.0, mc=np.zeros(3), parts=[]))
        mass = part_mass_g(i.part) / 1000.0
        R, t = i.matrix[:3, :3], i.matrix[:3, 3]
        if i.part.solid is not None:
            v, c, Iu = mass_props(i.part)
            rho = mass / (v * 1e-9) if v > 0 else 0.0          # kg/m3 so the solid carries the part's mass
            com = R @ c + t
            Ic = R @ (Iu * 1e-15 * rho) @ R.T                  # kg m2 about the part's com, world axes
            vv, ff = tess(i.part)
            meshes.setdefault(L, []).append(((R @ vv.T).T + t, ff))
        else:                                                   # a mass without a solid (the head): its frame origin
            com = t + np.array([0, 0, 120.0])
            Ic = np.eye(3) * mass * 0.1 ** 2 * 0.4
        a["parts"].append((mass, com, Ic))
    for h in asm.hardware():
        L = link_of(asm.instances[h["mounted"]])
        mass = part_mass_g(h["hw"]) / 1000.0
        acc.setdefault(L, dict(m=0.0, mc=np.zeros(3), parts=[]))["parts"].append((mass, h["matrix"][:3, 3], np.zeros((3, 3))))
    for k in range(sandbags):
        # 25 lb (11.34 kg) sandbags lying on the skirt, front and back, 230 mm from the mast
        y = 230.0 if k % 2 == 0 else -230.0
        acc["torso"]["parts"].append((11.34, np.array([0.0, y, 19.0 + 40.0]), np.diag([0.04, 0.02, 0.05]) * 11.34))
    if payload_kg:
        # the payload sits in the right hand's grip, 70 mm below the knuckle line (B/C) or the paddle (A)
        hand = "r_fingers" if tier != "c" else "r_hand"
        grip = np.asarray(origin.get("r_fingers", origin.get("r_hand"))) + np.array([18.0, 0, -70.0])
        acc.setdefault(hand, dict(m=0.0, mc=np.zeros(3), parts=[]))["parts"].append((payload_kg, grip, np.eye(3) * payload_kg * 0.03 ** 2 * 0.4))
    props = {}
    for L, a in acc.items():
        M = sum(p[0] for p in a["parts"])
        C = sum(p[0] * p[1] for p in a["parts"]) / M
        I = np.zeros((3, 3))
        for m, c, Ic in a["parts"]:
            d = (c - C) * 1e-3
            I += Ic + m * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
        props[L] = dict(mass=M, com=C, I=I)
    # links that no joint moves ride on whatever they are mated to (the tier A mitt's palm on the forearm)
    links = set(props) | set(origin)
    fixed = {}
    for L in sorted(links):
        if L in ("torso",) or L in parent:
            continue
        for m in asm.mates:
            la, lb = link_of(asm.instances[m.a[0]]), link_of(asm.instances[m.b[0]])
            other = lb if la == L else la if lb == L else None
            if other and other != L and (other in parent or other == "torso"):
                fixed[L] = other
                origin[L] = origin[other]
                break
        else:
            fixed[L] = "torso"
            origin.setdefault(L, np.zeros(3))
    # meshes in each link's frame (metres)
    for L, parts in meshes.items():
        vs, fs, n = [], [], 0
        for v, f in parts:
            vs.append((v - origin[L]) * 1e-3)
            fs.append(f + n)
            n += len(v)
        trimesh.Trimesh(np.vstack(vs), np.vstack(fs), process=False).export(os.path.join(out, "meshes", f"{L}.stl"))
    # URDF
    def inertial(L):
        p = props.get(L)
        if not p:
            return '<inertial><origin xyz="0 0 0"/><mass value="0.001"/><inertia ixx="1e-7" iyy="1e-7" izz="1e-7" ixy="0" ixz="0" iyz="0"/></inertial>'
        c = (p["com"] - origin[L]) * 1e-3
        I = p["I"]
        return (f'<inertial><origin xyz="{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}" rpy="0 0 0"/><mass value="{p["mass"]:.5f}"/>'
                f'<inertia ixx="{I[0,0]:.7e}" iyy="{I[1,1]:.7e}" izz="{I[2,2]:.7e}" ixy="{I[0,1]:.7e}" ixz="{I[0,2]:.7e}" iyz="{I[1,2]:.7e}"/></inertial>')

    def geom(L):
        if L not in meshes:
            return ""
        m = f'<geometry><mesh filename="meshes/{L}.stl"/></geometry>'
        return f"<visual><origin xyz='0 0 0'/>{m}</visual><collision><origin xyz='0 0 0'/>{m}</collision>"

    xml = ['<?xml version="1.0"?>', f'<robot name="joyful_jack_{tier}">']
    for L in sorted(links):
        xml.append(f'<link name="{L}">{inertial(L)}{geom(L)}</link>')
    for j in joints:
        o = (origin[j["child"]] - origin[j["parent"]]) * 1e-3
        lo, hi = (math.radians(v) for v in j["limits"])
        servo = bought.servo(j["actuator"].replace("feetech-", "").replace("-c047", "")) if j.get("actuator") else None
        effort = (servo.meta["stall_nm"] * j.get("ratio", 1.0)) if servo else 10.0
        xml.append(f'<joint name="{j["id"]}" type="revolute"><parent link="{j["parent"]}"/><child link="{j["child"]}"/>'
                   f'<origin xyz="{o[0]:.6f} {o[1]:.6f} {o[2]:.6f}" rpy="0 0 0"/><axis xyz="{j["axis"][0]:.6f} {j["axis"][1]:.6f} {j["axis"][2]:.6f}"/>'
                   f'<limit lower="{lo:.5f}" upper="{hi:.5f}" effort="{effort * 1.5:.3f}" velocity="20"/><dynamics damping="0.0" friction="0.0"/></joint>')
    for L, P in fixed.items():
        o = (origin[L] - origin[P]) * 1e-3
        xml.append(f'<joint name="fix_{L}" type="fixed"><parent link="{P}"/><child link="{L}"/><origin xyz="{o[0]:.6f} {o[1]:.6f} {o[2]:.6f}"/></joint>')
    if "head" in links and "head" not in parent:
        pass
    xml.append("</robot>")
    open(os.path.join(out, "jack.urdf"), "w").write("\n".join(xml))
    # servo and spring data for the simulation's actuator model
    act = []
    for j in joints:
        key = j["actuator"].replace("feetech-", "").replace("-c047", "")
        s = bought.servo(key)
        st = next((v for k, v in STAGES.items() if abs(v["ratio"] - j.get("ratio", 1.0)) < 1e-9 and j.get("ratio", 1.0) != 1.0), None)
        belt_r = JT.gt3_pd(st["z_driven"]) / 2000.0 if st else None
        act.append(dict(joint=j["id"], name=j["name"], servo=key, stall_nm=s.meta["stall_nm"], rated_frac=s.meta.get("rated_frac", 1 / 3),
                        no_load_rad_s=s.meta["speed_rpm"] * 2 * math.pi / 60, ratio=j.get("ratio", 1.0), belt_r_m=belt_r,
                        belt_rating_n=JT.BELT_RATING_N if st else None, spring=j.get("spring"), limits=j["limits"], axis=j["axis"],
                        origin=list(map(float, origin[j["child"]]))))
    bal = {j["id"]: j["spring"]["k_ab_nm"] for j in joints if j.get("spring") and j["spring"].get("kind") == "balancer"}
    json.dump(dict(tier=tier, payload_kg=payload_kg, balancers=bal, links={L: dict(mass=props[L]["mass"], com=list(map(float, props[L]["com"]))) for L in props},
                   total_mass=sum(p["mass"] for p in props.values()), actuators=act, fixed=fixed),
              open(os.path.join(out, "links.json"), "w"), indent=1)
    print(f"tier {tier}: {len(links)} links, {len(joints)} joints, {sum(p['mass'] for p in props.values()):.1f} kg; "
          + ", ".join(f"{L} {props[L]['mass']:.2f}" for L in sorted(props) if L != "torso") + f"; torso {props['torso']['mass']:.1f} kg")
    return out


if __name__ == "__main__":
    t = sys.argv[1]
    pk = float(sys.argv[sys.argv.index("--payload") + 1]) if "--payload" in sys.argv else 0.0
    sb = int(sys.argv[sys.argv.index("--sandbags") + 1]) if "--sandbags" in sys.argv else 0
    build(t, pk, sb)
