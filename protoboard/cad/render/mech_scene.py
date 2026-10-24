"""Blender scene for the full-hardware model (Blender 4.5, headless): every placed part and fastener of a tier.

    blender -b --python cad/render/mech_scene.py -- <job.json>

Same job format as jj_scene.py (stills and keyed animations), but the geometry is the detailed model:
out/mech/tier-<t>/scene.json (instances, fasteners, joints, made by cad/mech/build.py), part meshes from the parts
folders (body.glb), fasteners and costume from cad/mech/tools/export_costume.py, the head from the received facade
GLB. Each joint's child link is an empty at the joint origin, so a pose is a set of joint angles.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jj_scene as S  # noqa: E402  (materials, studio, camera, render settings, head import)

JOB = S.JOB
ROOT = S.ROOT
MECH = os.path.join(ROOT, "out", "mech")
PARTS = json.load(open(os.path.join(ROOT, "src", "mech", "mech.json")))["parts"]
MM = 0.001

# scene colour key -> render material (jj_scene names; two added here)
COLOR = {"printed_cf": "printed_cf", "glove_white": "glove_white", "orange_shell": "head_orange", "plastic_yellow": "plastic_yellow",
         "metal_steel": "metal_steel", "metal_alu": "metal_alu", "brass": "brass", "servo_dark": "servo_dark", "rubber": "rubber",
         "pcb_blue": "pcb_blue", "pcb_green": "pcb_green", "plastic_black": "plastic_black", "wood_ply": "wood_ply",
         "battery_red": "battery_red", "bucket": "bucket", "concrete": "concrete", "fabric_shirt": "fabric_shirt",
         "fabric_vest": "fabric_vest", "leather_brown": "leather_brown", "hat_tan": "hat_tan", "bandana_green": "bandana_green"}


def materials():
    M = S.build_materials()
    M["printed_cf"] = S.noisy("printed_cf", (0.075, 0.075, 0.08), (0.04, 0.04, 0.045), 60.0, (0.55, 0.75), bump=0.08)
    M["plastic_yellow"] = S.principled("plastic_yellow", (0.95, 0.72, 0.03), 0.4)
    M["bucket"] = S.principled("bucket_orange", (0.85, 0.32, 0.03), 0.5)
    return M


MESH = {}


def mesh_from(path, key, scale=1.0):
    """One shared mesh per part: import once, join, drop the importer's objects."""
    if key in MESH:
        return MESH[key]
    before = set(bpy.data.objects)
    if path.endswith(".glb"):
        bpy.ops.import_scene.gltf(filepath=path)
    else:
        bpy.ops.wm.stl_import(filepath=path, global_scale=scale)
    new = [o for o in bpy.data.objects if o not in before]
    names = [o.name for o in new]
    meshes = [o for o in new if o.type == "MESH"]
    for o in meshes:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
    if len(meshes) > 1:
        ctx = {"active_object": meshes[0], "selected_editable_objects": meshes}
        with bpy.context.temp_override(**ctx):
            bpy.ops.object.join()
    me = meshes[0].data if meshes else None
    for n in names:  # the join removed the others
        o = bpy.data.objects.get(n)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
    if me is not None:
        me.name = key
        me.materials.clear()
        for p in me.polygons:
            p.use_smooth = True
        if hasattr(me, "set_sharp_from_angle"):
            me.set_sharp_from_angle(angle=math.radians(35))
    MESH[key] = me
    return me


def part_mesh(pid, tier):
    p = PARTS.get(pid, {})
    if p.get("category") == "hardware":
        return mesh_from(os.path.join(MECH, "hw", f"{pid}.stl"), "hw:" + pid, MM)
    if p.get("category") == "costume":
        return mesh_from(os.path.join(MECH, f"tier-{tier}", "costume", f"{pid}.stl"), f"{tier}:{pid}", MM)
    body = p.get("body") or {}
    if body.get("glb") and os.path.exists(os.path.join(ROOT, body["glb"])):
        return mesh_from(os.path.join(ROOT, body["glb"]), pid)
    return None


def mm_matrix(m16):
    m = Matrix([m16[0:4], m16[4:8], m16[8:12], m16[12:16]])
    m.translation = m.translation * MM
    return m


def build(tier, M, offset=(0, 0, 0), prefix=""):
    sc = json.load(open(os.path.join(MECH, f"tier-{tier}", "scene.json")))
    root = bpy.data.objects.new(f"{prefix}tier_{tier}", None)
    bpy.context.scene.collection.objects.link(root)
    root.location = Vector(offset)
    links, origin = {}, {}
    joints = {j["child"]: j for j in sc["joints"]}
    order = []
    # a link with no joint (tier A's wrist, the balancer posts) rides on the link it is mated to
    link_of = {i["id"]: i["link"] for i in sc["instances"]}
    fixed = {}
    for m in sc["mates"]:
        la, lb = link_of.get(m["a"][0]), link_of.get(m["b"][0])
        for x, y in ((la, lb), (lb, la)):
            if x and y and x != y and x not in joints and x not in ("base", "torso") and x not in fixed and fixed.get(y) != x:
                fixed[x] = y

    def need(name):
        if name in links:
            return links[name]
        j = joints.get(name)
        if j is None and name in fixed:
            j = {"parent": fixed[name], "origin": [0, 0, 0], "fixed": True}
        parent = need(j["parent"]) if j else root
        e = bpy.data.objects.new(f"{prefix}{tier}:{name}", None)
        e.empty_display_size = 0.02
        bpy.context.scene.collection.objects.link(e)
        e.parent = parent
        o = Vector(j["origin"]) * MM if j else Vector((0, 0, 0))
        e.location = o - (origin[j["parent"]] if j and j["parent"] in origin else Vector((0, 0, 0)))
        if j and not j.get("fixed"):
            e["axis"] = j["axis"]
            e["joint"] = j["id"]
        origin[name] = o
        links[name] = e
        order.append(name)
        return e

    for j in sc["joints"]:
        need(j["child"])
    objs = {}
    inst_explode = {}

    def place(name, me, link, world, mat, explode, kind):
        need(link)
        o = bpy.data.objects.new(f"{prefix}{tier}:{name}", me)
        bpy.context.scene.collection.objects.link(o)
        o.parent = links[link]
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = Matrix.Translation(-origin[link]) @ world
        if not o.data.materials:
            o.data.materials.append(mat)
        o["explode"] = list(explode)
        o["kind"] = kind
        o["link"] = link
        o["base_loc"] = list(o.location)
        objs[o.name] = o
        return o

    for i in sc["instances"]:
        if i["matrix"] is None:
            continue
        W = mm_matrix(i["matrix"])
        if i["part"] == "jj-head-assembly":
            head = S.import_head(M)
            meta = PARTS[i["part"]].get("meta", {})
            rot = Matrix.Rotation(math.radians(meta.get("glb_rot_z_deg", 180)), 4, "Z")
            off = Matrix.Translation(Vector(meta.get("glb_offset_mm", [0, 0, 236])) * MM)
            for k, (h, wm) in enumerate(zip(head, S.HEAD_CACHE["mw"])):
                need(i["link"])
                h.parent = links[i["link"]]
                h.matrix_parent_inverse = Matrix.Identity(4)
                h.matrix_basis = Matrix.Translation(-origin[i["link"]]) @ W @ rot @ off @ wm
                h.name = f"{prefix}{tier}:head__{k}"
                h["explode"] = [0, 0, 260] if "0:1:1:135" not in h.name else [0, 0, 420]
                h["kind"] = "head"
                h["link"] = i["link"]
                h["base_loc"] = list(h.location)
                objs[h.name] = h
            rig = json.load(open(os.path.join(S.CAD, "tier-b", "rig.json")))["head"]
            for k, (x, y, z) in enumerate(rig["eyes_mm"]):
                p = W @ rot @ Vector((x * MM, y * MM, (z + rig["offset_mm"][2]) * MM))
                bpy.ops.mesh.primitive_uv_sphere_add(radius=13 * MM, segments=32, ring_count=16)
                eye = bpy.context.active_object
                eye.data.materials.append(M["eye_blue"])
                bpy.ops.object.shade_smooth()
                eye.name = f"{prefix}{tier}:head__eye_{k}"
                eye.parent = links[i["link"]]
                eye.location = p - origin[i["link"]]
                eye["explode"], eye["kind"], eye["link"], eye["base_loc"] = [0, 0, 260], "head", i["link"], list(eye.location)
                objs[eye.name] = eye
                lt = bpy.data.lights.new(f"eyeglow{k}", "POINT")
                lt.energy, lt.color, lt.shadow_soft_size = 0.6, (0.2, 0.45, 1.0), 0.01
                lo = bpy.data.objects.new(f"{prefix}{tier}:eyelight{k}", lt)
                bpy.context.scene.collection.objects.link(lo)
                lo.parent = eye
                lo.location = (0, -0.03, 0)
            continue
        me = part_mesh(i["part"], tier)
        if me is None:
            print("NO MESH", i["part"])
            continue
        mat = M.get(COLOR.get(i["color"], ""), M["plastic_dark"])
        kind = "costume" if i["id"].startswith("costume/") else i["category"]
        o = place(i["id"], me, i["link"], W, mat, i["explode"], kind)
        if o.data.materials and o.data.materials[0] != mat:
            o.material_slots[0].link = "OBJECT"
            o.material_slots[0].material = mat
        inst_explode[i["id"]] = i["explode"]
    for k, h in enumerate(sc["hardware"]):
        me = part_mesh(h["part"], tier)
        mat = M["brass"] if "insert" in h["part"] else M["metal_steel"]
        W = mm_matrix(h["matrix"])
        # a fastener lifts with the part it holds, and out of its hole along its own axis
        ax = W.to_3x3() @ Vector((0, 0, 1))
        ex = Vector(inst_explode.get(h["mounted"], [0, 0, 0])) + ax * (0 if "insert" in h["part"] else 45)
        o = place(f"hw{k}_{h['part']}", me, h["link"], W, mat, ex, "hardware")
        if o.data.materials and o.data.materials[0] != mat:
            o.material_slots[0].link = "OBJECT"
            o.material_slots[0].material = mat
    return {"root": root, "links": links, "objs": objs, "joints": {j["id"]: j for j in sc["joints"]}, "tier": tier}


# ------------------------------------------------------------------ poses (anatomical degrees, as jj_scene)
def pose(T, P, frame=None):
    P = S.POSES[P] if isinstance(P, str) else P
    L = T["links"]
    by_joint = {e["joint"]: e for e in L.values() if "joint" in e}

    def setj(jid, deg):
        e = by_joint.get(jid)
        if e is None:
            return
        lo, hi = T["joints"][jid]["limits"]
        deg = max(lo, min(hi, deg))
        e.rotation_mode = "QUATERNION"
        e.rotation_quaternion = Quaternion(Vector(e["axis"]).normalized(), math.radians(deg))
        if frame is not None:
            e.keyframe_insert("rotation_quaternion", frame=frame)

    for side in ("r", "l"):
        s = 1 if side == "r" else -1
        a = P[side]
        g = a.get("grip", 0)
        setj(f"{side}_j1", a.get("flex", 0))
        setj(f"{side}_j2", a.get("abduct", 0))
        setj(f"{side}_j3", -s * a.get("twist", 0))
        setj(f"{side}_j4", a.get("elbow", 0))
        setj(f"{side}_j5", s * a.get("wrist", 0))
        setj(f"{side}_j6", a.get("wrist_pitch", 0))
        setj(f"{side}_grip", 70 * g)
        setj(f"{side}_fingers", 80 * g)
        setj(f"{side}_thumb", 45 * g)
    setj("neck_yaw", P.get("neck", 0))


def explode_vec(o):
    kind, link = o.get("kind"), o.get("link", "")
    own = Vector(o.get("explode", [0, 0, 0])) * MM
    name = o.name.split(":", 1)[-1]
    if link == "base":
        return Vector((0, 0, 0.16)) if "concrete" in name else (own if kind == "hardware" else Vector((0, 0, 0)))
    if kind == "costume":
        lift = Vector((0, 0, 1.25)) if any(k in name for k in ("brim", "crown", "band", "concho")) else Vector((0, -0.55, 0.30))
        return lift + own * 0.5
    if kind == "head" or link == "head":
        return Vector((0, 0, 0.55)) + own
    if link.startswith(("r_", "l_")):
        side = -1 if link.startswith("r_") else 1
        return Vector((side * 0.30, 0, 0.26)) + Vector((own.x * 1.3, own.y, own.z * 0.6))
    return Vector((0, 0, 0.26)) + own


def explode(T, f, frame=None):
    for o in T["objs"].values():
        o.location = Vector(o["base_loc"]) + explode_vec(o) * f
        if frame is not None:
            o.keyframe_insert("location", frame=frame)


def costume(T, show, frame=None):
    for o in T["objs"].values():
        if o.get("kind") == "costume":
            o.hide_render = not show
            if frame is not None:
                o.keyframe_insert("hide_render", frame=frame)


def main():
    S.clear()
    M = materials()
    tiers = JOB["tiers"]
    spacing = JOB.get("spacing", 1.35)
    T = {}
    for i, t in enumerate(tiers):
        x = (i - (len(tiers) - 1) / 2) * spacing
        T[t] = build(t, M, (x, 0, 0), prefix=f"{i}")
        p = JOB.get("pose", "rest")
        p = p.get(t, "rest") if isinstance(p, dict) and "r" not in p else p
        if t == "a" and isinstance(p, str) and p + "_a" in S.POSES:
            p = p + "_a"
        pose(T[t], p)
        if JOB.get("hide_costume"):
            costume(T[t], False)
    S.studio(JOB.get("style", "dark"))
    cam = JOB["camera"]
    c, tgt = S.camera(cam["loc"], cam["target"], cam.get("lens", 50))
    scn = bpy.context.scene
    if JOB["mode"] == "still":
        if JOB.get("explode"):
            for t in tiers:
                explode(T[t], JOB["explode"])
        S.render_settings(JOB.get("engine", "cycles"), JOB.get("res", [1600, 2000]), JOB.get("samples", 160), JOB["out"])
        bpy.ops.render.render(write_still=True)
        return
    fps = JOB.get("fps", 30)
    t = tiers[0]
    for k in JOB["timeline"]:
        f = int(k["t"] * fps) + 1
        if "pose" in k:
            pose(T[t], k["pose"], frame=f)
        if "explode" in k:
            explode(T[t], k["explode"], frame=f)
        if "costume" in k:
            costume(T[t], k["costume"] >= 0.5, frame=f)
        if "cam" in k:
            c.location = k["cam"]
            c.keyframe_insert("location", frame=f)
        if "target" in k:
            tgt.location = k["target"]
            tgt.keyframe_insert("location", frame=f)
        if "lens" in k:
            c.data.lens = k["lens"]
            c.data.keyframe_insert("lens", frame=f)
    for a in bpy.data.actions:
        for fc in a.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER" if fc.data_path != "hide_render" else "CONSTANT"
                kp.easing = "EASE_IN_OUT"
    scn.frame_start = 1
    scn.frame_end = int(JOB["timeline"][-1]["t"] * fps) + 1
    S.render_settings(JOB.get("engine", "eevee"), JOB.get("res", [1280, 720]), JOB.get("samples", 32), JOB["out"], fps)
    scn.render.image_settings.file_format = "PNG"
    if JOB.get("frames"):
        scn.frame_start, scn.frame_end = JOB["frames"]
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
