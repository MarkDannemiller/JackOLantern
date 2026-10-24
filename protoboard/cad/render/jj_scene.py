"""Blender scene builder and renderer for Joyful Jack (Blender 4.5, run headless).

    blender -b --python cad/render/jj_scene.py -- <job.json>

The job file says what to render: {"tiers": ["b"], "mode": "still"|"anim", "pose": ...,
"camera": ..., "out": ..., ...}. Geometry comes from out/cad/tier-<t>/rig.json (made by
cad/joyful_jack_cad.py) and the head from out/cad/head-facade-v61.glb (the received STEP).
Every link of the rig becomes an empty; a joint's angle is that empty's rotation about the
rig axis, so poses and animations are joint angles.
"""
import bpy
import json
import math
import os
import sys
from mathutils import Vector, Euler, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:]
JOB = json.load(open(ARGS[0]))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CAD = os.path.join(ROOT, "out", "cad")
MM = 0.001

# ------------------------------------------------------------------ materials
def principled(name, color, rough=0.5, metal=0.0, emission=None, strength=0.0, alpha=1.0, sheen=0.0, coat=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Sheen Weight" in b.inputs:
        b.inputs["Sheen Weight"].default_value = sheen
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = coat
    if emission:
        b.inputs["Emission Color"].default_value = (*emission, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def noisy(name, c1, c2, scale=8.0, rough=(0.45, 0.8), metal=0.0, detail=6.0, bump=0.15):
    """Two-colour material mixed by noise: weathered paint, leather, concrete, felt."""
    m = principled(name, c1, rough[0], metal)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = detail
    coord = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(coord.outputs["Object"], tex.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.75
    nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough[0]
    rr.inputs["To Max"].default_value = rough[1]
    nt.links.new(tex.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.inputs["Strength"].default_value = bump
    nt.links.new(tex.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    return m


def plaid(name, base, line1, line2, scale=55.0):
    m = principled(name, base, 0.85, sheen=0.4)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
    mix_prev = None
    col = nt.nodes.new("ShaderNodeRGB")
    col.outputs[0].default_value = (*base, 1)
    out = col.outputs[0]
    for axis, colr, fac in (("X", line1, 0.55), ("Z", line1, 0.55), ("X", line2, 0.35), ("Z", line2, 0.35)):
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = axis
        wave.inputs["Scale"].default_value = scale * (1.0 if colr == line1 else 2.3)
        wave.inputs["Distortion"].default_value = 0.0
        nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
        thr = nt.nodes.new("ShaderNodeMath")
        thr.operation = "GREATER_THAN"
        thr.inputs[1].default_value = 0.8 if colr == line1 else 0.9
        nt.links.new(wave.outputs["Fac"], thr.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = fac
        nt.links.new(thr.outputs[0], mul.inputs[0])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(mul.outputs[0], mix.inputs["Factor"])
        nt.links.new(out, mix.inputs[6])
        mix.inputs[7].default_value = (*colr, 1)
        out = mix.outputs[2]
    nt.links.new(out, b.inputs["Base Color"])
    return m


def build_materials():
    M = {}
    M["orange_shell"] = noisy("orange_shell", (0.85, 0.30, 0.03), (0.45, 0.14, 0.02), 6.0, (0.45, 0.85), bump=0.25)
    M["leather_brown"] = noisy("leather_brown", (0.22, 0.10, 0.04), (0.10, 0.045, 0.02), 14.0, (0.5, 0.85), bump=0.3)
    M["fabric_vest"] = noisy("fabric_vest", (0.55, 0.22, 0.05), (0.25, 0.09, 0.03), 9.0, (0.6, 0.95), bump=0.35)
    M["fabric_shirt"] = plaid("fabric_shirt", (0.32, 0.035, 0.03), (0.04, 0.02, 0.02), (0.55, 0.42, 0.18), scale=11.0)
    M["bandana_green"] = noisy("bandana_green", (0.05, 0.16, 0.10), (0.03, 0.10, 0.06), 10.0, (0.7, 0.9))
    M["hat_tan"] = noisy("hat_tan", (0.42, 0.24, 0.10), (0.22, 0.12, 0.05), 7.0, (0.65, 0.95), bump=0.2)
    M["metal_steel"] = noisy("metal_steel", (0.62, 0.62, 0.64), (0.40, 0.40, 0.42), 30.0, (0.25, 0.45), metal=1.0, bump=0.05)
    M["metal_alu"] = principled("metal_alu", (0.80, 0.81, 0.83), 0.3, 1.0)
    M["metal_print"] = noisy("metal_print", (0.70, 0.70, 0.72), (0.45, 0.45, 0.48), 25.0, (0.25, 0.4), metal=1.0, bump=0.05)
    M["brass"] = principled("brass", (0.85, 0.62, 0.25), 0.3, 1.0)
    M["servo_black"] = principled("servo_black", (0.03, 0.03, 0.035), 0.4, coat=0.3)
    M["servo_dark"] = principled("servo_dark", (0.07, 0.08, 0.10), 0.35, coat=0.3)
    M["plastic_black"] = principled("plastic_black", (0.03, 0.03, 0.03), 0.5)
    M["plastic_dark"] = principled("plastic_dark", (0.06, 0.06, 0.06), 0.5)
    M["plastic_red"] = principled("plastic_red", (0.8, 0.03, 0.02), 0.3, coat=0.5)
    M["battery_red"] = principled("battery_red", (0.75, 0.04, 0.03), 0.45)
    M["rubber"] = principled("rubber", (0.04, 0.04, 0.04), 0.9)
    M["pcb_green"] = principled("pcb_green", (0.02, 0.25, 0.08), 0.35, coat=0.5)
    M["pcb_blue"] = principled("pcb_blue", (0.02, 0.08, 0.35), 0.35, coat=0.5)
    M["wood_ply"] = noisy("wood_ply", (0.78, 0.58, 0.36), (0.55, 0.38, 0.20), 3.0, (0.55, 0.7), bump=0.05)
    M["concrete"] = noisy("concrete", (0.30, 0.30, 0.29), (0.18, 0.18, 0.18), 40.0, (0.85, 1.0), bump=0.4)
    M["bucket"] = principled("bucket", (0.05, 0.05, 0.05), 0.55)
    M["glove_white"] = noisy("glove_white", (0.86, 0.84, 0.78), (0.70, 0.66, 0.58), 12.0, (0.7, 0.9), bump=0.15)
    M["eye_blue"] = principled("eye_blue", (0.0, 0.02, 0.35), 0.15, emission=(0.0, 0.12, 1.0), strength=0.45)
    M["head_orange"] = noisy("head_orange", (0.80, 0.22, 0.01), (0.62, 0.15, 0.01), 5.0, (0.4, 0.65), bump=0.1)
    M["head_black"] = principled("head_black", (0.03, 0.03, 0.03), 0.45)
    M["head_white"] = principled("head_white", (0.85, 0.85, 0.82), 0.5)
    M["ghost"] = principled("ghost", (0.6, 0.75, 0.95), 0.2)
    return M


# ------------------------------------------------------------------ scene assembly
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_stl(path):
    bpy.ops.wm.stl_import(filepath=path, global_scale=MM)
    return bpy.context.selected_objects[0]


HEAD_CACHE = {}


def import_head(M):
    """Import the head GLB once; later tiers get linked duplicates."""
    if "objs" in HEAD_CACHE:
        new = []
        for o, mw in zip(HEAD_CACHE["objs"], HEAD_CACHE["mw"]):
            d = o.copy()
            d.parent = None
            d.matrix_parent_inverse = Matrix.Identity(4)
            bpy.context.scene.collection.objects.link(d)
            d.matrix_world = mw
            new.append(d)
        return new
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(CAD, "head-facade-v61.glb"))
    objs = [o for o in bpy.context.scene.objects if o not in before]
    meshes = [o for o in objs if o.type == "MESH"]
    for o in meshes:
        wm = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = wm
        for slot in o.material_slots:
            mt = slot.material
            if mt is None:
                continue
            c = mt.diffuse_color
            if c[0] > 0.8 and c[1] < 0.45 and c[2] < 0.2:
                slot.material = M["head_orange"]
            elif max(c[:3]) < 0.15:
                slot.material = M["head_black"]
            elif c[0] > 0.85 and c[1] > 0.85:
                # the as-built head is printed orange; the neck parts are black (photo, research/concepts)
                slot.material = M["head_black"] if ("Neck" in o.name or "Component" in o.name or "Carriage" in o.name or "Mounting" in o.name) else M["head_orange"]
    for o in objs:
        if o.type != "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    HEAD_CACHE["objs"] = meshes
    HEAD_CACHE["mw"] = [o.matrix_world.copy() for o in meshes]
    return meshes


def build_tier(tier, M, offset=(0, 0, 0), name_prefix=""):
    rig = json.load(open(os.path.join(CAD, f"tier-{tier}", "rig.json")))
    links = {}
    side_sign = {}
    root_empty = bpy.data.objects.new(f"{name_prefix}tier_{tier}", None)
    bpy.context.scene.collection.objects.link(root_empty)
    root_empty.location = Vector(offset)
    for lk in rig["links"]:
        e = bpy.data.objects.new(f"{name_prefix}{tier}:{lk['name']}", None)
        e.empty_display_size = 0.02
        bpy.context.scene.collection.objects.link(e)
        e.parent = links.get(lk["parent"], root_empty)
        e.location = Vector(lk["origin"]) * MM
        e["axis"] = lk["axis"] or [0, 0, 0]
        e["role"] = lk["role"]
        e["limits"] = lk["limits"]
        links[lk["name"]] = e
        side_sign[lk["name"]] = -1 if lk["name"].startswith("r_") else (1 if lk["name"].startswith("l_") else 0)
    parts = {}
    for p in rig["parts"]:
        o = import_stl(os.path.join(CAD, f"tier-{tier}", p["file"]))
        o.name = f"{name_prefix}{tier}:{p['name']}"
        o.data.materials.clear()
        o.data.materials.append(M.get(p["material"], M["plastic_dark"]))
        # stl parts are in their link's local frame
        o.parent = links[p["link"]]
        o["explode"] = p["explode"]
        o["material"] = p["material"]
        o["base_loc"] = list(o.location)
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35)) if False else None
        for poly in o.data.polygons:
            poly.use_smooth = True
        mod = o.modifiers.new("smooth", "SMOOTH_BY_ANGLE") if hasattr(bpy.types, "NodesModifier") and False else None
        parts[p["name"]] = o
    # auto smooth by angle (4.1+): weighted normals keep hard edges crisp
    for o in parts.values():
        o.modifiers.new("wn", "WEIGHTED_NORMAL").keep_sharp = True
        o.data.set_sharp_from_angle(angle=math.radians(35)) if hasattr(o.data, "set_sharp_from_angle") else None
    # head
    head_link = links["head"]
    heads = import_head(M)
    for o, wm in zip(heads, [m.copy() for m in HEAD_CACHE["mw"]]):
        o.parent = head_link
        rot = Matrix.Rotation(math.radians(rig["head"]["rot_z_deg"]), 4, "Z")
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = rot @ Matrix.Translation(Vector(rig["head"]["offset_mm"]) * MM) @ wm
        o.name = f"{name_prefix}{tier}:head__{o.name[:40]}"
        # the facade shell lifts highest, the internals less, so the mechanism shows between them
        o["explode"] = [0, 0, 560] if "0:1:1:135" in o.name else [0, 0, 300]
        o["base_loc"] = list(o.location)
        parts[o.name] = o
    for i, (x, y, z) in enumerate(rig["head"]["eyes_mm"]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=13 * MM, segments=32, ring_count=16)
        eye = bpy.context.active_object
        eye.name = f"{name_prefix}{tier}:head__eye_{i}"
        eye.data.materials.append(M["eye_blue"])
        eye.parent = head_link
        p = Matrix.Rotation(math.pi, 4, "Z") @ Vector((x * MM, y * MM, (z + rig["head"]["offset_mm"][2]) * MM))
        eye.location = p
        eye["explode"] = [0, 0, 300]
        eye["base_loc"] = list(eye.location)
        bpy.ops.object.shade_smooth()
        parts[eye.name] = eye
        lt = bpy.data.lights.new(f"eyeglow{i}", "POINT")
        lt.energy = 0.6
        lt.color = (0.2, 0.45, 1.0)
        lt.shadow_soft_size = 0.01
        lo = bpy.data.objects.new(f"{name_prefix}{tier}:eyelight{i}", lt)
        bpy.context.scene.collection.objects.link(lo)
        lo.parent = head_link
        lo.location = p + Vector((0, -0.03, 0))
    return {"root": root_empty, "links": links, "side": side_sign, "parts": parts, "rig": rig}


# ------------------------------------------------------------------ poses
# anatomical angles (deg): flex = arm forward, abduct = arm out to the side, elbow = forearm
# forward/up, twist, wrist, grip = 0 open .. 1 closed. Converted to rig axes by sign.
POSES = {
    "zero": {"r": dict(), "l": dict(), "neck": 0},
    "rest": {"r": dict(flex=8, abduct=8, elbow=25, grip=0.2), "l": dict(flex=8, abduct=8, elbow=25, grip=0.2), "neck": 0},
    # tier A has no upper-arm twist: it waves with the shoulder forward and the elbow up
    "wave_a": {"r": dict(flex=80, abduct=25, elbow=100, grip=0.0), "l": dict(flex=20, abduct=10, elbow=60, grip=0.6), "neck": -12},
    "wave": {"r": dict(flex=10, abduct=95, twist=90, elbow=95, wrist=0, grip=0.0), "l": dict(flex=20, abduct=10, elbow=60, grip=0.6), "neck": -12},
    "tip_hat": {"r": dict(flex=165, abduct=32, twist=-40, elbow=100, wrist=30, grip=0.7), "l": dict(flex=15, abduct=12, elbow=70, grip=0.9), "neck": 8},
    "offer": {"r": dict(flex=28, abduct=8, elbow=58, wrist=0, grip=0.15), "l": dict(flex=28, abduct=8, elbow=58, wrist=0, grip=0.15), "neck": 0},
    "grab": {"r": dict(flex=28, abduct=8, elbow=58, wrist=0, grip=0.95), "l": dict(flex=28, abduct=8, elbow=58, wrist=0, grip=0.95), "neck": 0},
    "showcase": {"r": dict(flex=35, abduct=40, twist=-30, elbow=80, wrist=20, grip=0.1), "l": dict(flex=15, abduct=10, elbow=50, grip=0.9), "neck": -10},
}


def set_angle(e, deg):
    ax = Vector(e["axis"])
    if ax.length == 0:
        return
    e.rotation_mode = "QUATERNION"
    from mathutils import Quaternion
    e.rotation_quaternion = Quaternion(ax.normalized(), math.radians(deg))


def apply_pose(T, pose, frame=None):
    P = POSES[pose] if isinstance(pose, str) else pose
    L = T["links"]
    for side in ("r", "l"):
        s = -1 if side == "r" else 1
        a = P[side]

        def setj(name, deg):
            k = f"{side}_{name}"
            if k in L:
                set_angle(L[k], deg)
                if frame is not None:
                    L[k].keyframe_insert("rotation_quaternion", frame=frame)

        setj("shoulder_yoke", -a.get("flex", 0))
        setj("upper_arm", -s * a.get("abduct", 0) * -1 if False else (a.get("abduct", 0) * (1 if side == "r" else -1)))
        setj("upper_arm_twist", s * a.get("twist", 0))
        setj("forearm", -a.get("elbow", 0))
        setj("wrist", s * a.get("wrist", 0))
        setj("wrist_pitch", -a.get("wrist_pitch", 0))
        g = a.get("grip", 0)
        setj("mitt_fingers", -70 * g)
        setj("glove_fingers", -80 * g)
        setj("glove_thumb", s * 60 * g)
        for i in range(4):
            setj(f"finger{i}_proximal", -80 * g)
            setj(f"finger{i}_distal", -75 * g)
        setj("thumb_base", s * 70 * g)
        setj("thumb_tip", -60 * g)
    set_angle(L["head"], P.get("neck", 0))
    if frame is not None:
        L["head"].keyframe_insert("rotation_quaternion", frame=frame)


def explode_vec(o):
    """Exploded offset (m) for a part: its own offset plus a layer lift, so the view reads as
    stacked layers: base stays, torso and costume rise, arms move out, head higher, hat on top."""
    n = o.name.split(":", 1)[-1]
    own = Vector(o.get("explode", [0, 0, 0])) * MM
    if any(k in n for k in ("bucket", "base_disc", "floor_flange", "mast_pipe")):
        return Vector((0, 0, 0))
    if "concrete" in n:
        return Vector((0, 0, 0.18))
    if n.startswith("head__"):
        return Vector((0, 0, 0.62)) + own
    if n.startswith("hat__"):
        return Vector((0, 0, 1.45)) + Vector((0, 0, own.z * 0.6))
    if n.startswith("r_") or n.startswith("l_"):
        side = -1 if n.startswith("r_") else 1
        return Vector((side * 0.32, 0, 0.28)) + Vector((own.x * 1.4, own.y, own.z * 0.5))
    return Vector((0, 0, 0.28)) + own


def explode(T, f, frame=None):
    for o in T["parts"].values():
        base = Vector(o["base_loc"])
        o.location = base + explode_vec(o) * f
        if frame is not None:
            o.keyframe_insert("location", frame=frame)


# ------------------------------------------------------------------ studio
def studio(style="dark", floor=True):
    scn = bpy.context.scene
    w = bpy.data.worlds.new("world")
    scn.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    if style == "dark":
        bg.inputs["Color"].default_value = (0.012, 0.012, 0.016, 1)
        bg.inputs["Strength"].default_value = 1.0
    else:
        bg.inputs["Color"].default_value = (0.70, 0.72, 0.76, 1)
        bg.inputs["Strength"].default_value = 0.45

    def area(name, loc, size, energy, color, target=(0, 0, 1.1)):
        L = bpy.data.lights.new(name, "AREA")
        L.size = size
        L.energy = energy
        L.color = color
        o = bpy.data.objects.new(name, L)
        scn.collection.objects.link(o)
        o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return o

    if style == "dark":
        area("key", (-2.2, -2.6, 2.6), 1.6, 260, (1.0, 0.86, 0.72))
        area("rim_blue", (2.4, 1.6, 2.2), 1.2, 320, (0.35, 0.5, 1.0))
        area("rim_orange", (-2.4, 1.8, 1.4), 1.2, 220, (1.0, 0.5, 0.15))
        area("fill", (2.0, -2.8, 0.9), 2.0, 60, (0.8, 0.85, 1.0))
    else:
        area("key", (-2.0, -2.6, 2.8), 2.5, 520, (1.0, 0.97, 0.92))
        area("fill", (2.6, -2.2, 1.6), 2.5, 120, (0.9, 0.95, 1.0))
        area("back", (0.5, 2.6, 2.6), 2.0, 160, (1.0, 1.0, 1.0))
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
        fl = bpy.context.active_object
        fl.name = "floor"
        m = principled("floor", (0.02, 0.02, 0.025) if style == "dark" else (0.55, 0.56, 0.58), 0.35 if style == "dark" else 0.6)
        fl.data.materials.append(m)


def camera(loc, target, lens=50):
    scn = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    c = bpy.data.objects.new("cam", cd)
    scn.collection.objects.link(c)
    c.location = loc
    t = bpy.data.objects.new("cam_target", None)
    scn.collection.objects.link(t)
    t.location = target
    tc = c.constraints.new("TRACK_TO")
    tc.target = t
    tc.track_axis = "TRACK_NEGATIVE_Z"
    tc.up_axis = "UP_Y"
    scn.camera = c
    return c, t


def render_settings(engine, res, samples, path, fps=30):
    scn = bpy.context.scene
    scn.render.resolution_x, scn.render.resolution_y = res
    scn.render.film_transparent = False
    scn.view_settings.view_transform = "AgX"
    scn.view_settings.look = "AgX - Medium High Contrast"
    if engine == "cycles":
        scn.render.engine = "CYCLES"
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for dev_type in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = dev_type
                prefs.get_devices()
                for d in prefs.devices:
                    d.use = d.type == dev_type
                break
            except Exception:
                continue
        scn.cycles.device = "GPU"
        scn.cycles.samples = samples
        scn.cycles.use_denoising = True
        scn.cycles.max_bounces = 8
    else:
        scn.render.engine = "BLENDER_EEVEE_NEXT"
        scn.eevee.taa_render_samples = samples
        scn.eevee.use_shadows = True
        if hasattr(scn.eevee, "use_raytracing"):
            scn.eevee.use_raytracing = True
    scn.render.fps = fps
    scn.render.filepath = path


# ------------------------------------------------------------------ jobs
def main():
    clear()
    M = build_materials()
    tiers = JOB["tiers"]
    spacing = JOB.get("spacing", 1.35)
    T = {}
    for i, t in enumerate(tiers):
        x = (i - (len(tiers) - 1) / 2) * spacing
        T[t] = build_tier(t, M, (x, 0, 0), name_prefix=f"{i}")
        pose = JOB.get("pose", "rest") if not isinstance(JOB.get("pose"), dict) else JOB["pose"].get(t, "rest")
        if t == "a" and isinstance(pose, str) and pose + "_a" in POSES:
            pose = pose + "_a"
        apply_pose(T[t], pose)
    studio(JOB.get("style", "dark"))
    cam = JOB["camera"]
    c, tgt = camera(cam["loc"], cam["target"], cam.get("lens", 50))
    scn = bpy.context.scene
    if JOB["mode"] == "still":
        if JOB.get("explode"):
            for t in tiers:
                explode(T[t], JOB["explode"])
        if JOB.get("hide_costume"):
            for t in tiers:
                for o in T[t]["parts"].values():
                    if o.get("material") in ("fabric_shirt", "fabric_vest", "bandana_green", "leather_brown") and ("shirt" in o.name or "vest" in o.name or "bandana" in o.name or "belt" in o.name or "holster" in o.name or "hatch" in o.name):
                        o.hide_render = True
        render_settings(JOB.get("engine", "cycles"), JOB.get("res", [1600, 2000]), JOB.get("samples", 256), JOB["out"])
        bpy.ops.render.render(write_still=True)
        return
    # animation: a list of keyed segments
    fps = JOB.get("fps", 30)
    tl = JOB["timeline"]
    t = tiers[0]
    for k in tl:
        f = int(k["t"] * fps) + 1
        if "pose" in k:
            apply_pose(T[t], k["pose"], frame=f)
        if "explode" in k:
            explode(T[t], k["explode"], frame=f)
        if "cam" in k:
            c.location = k["cam"]
            c.keyframe_insert("location", frame=f)
        if "target" in k:
            tgt.location = k["target"]
            tgt.keyframe_insert("location", frame=f)
        if "lens" in k:
            c.data.lens = k["lens"]
            c.data.keyframe_insert("lens", frame=f)
        if "costume" in k:
            for o in T[t]["parts"].values():
                if any(s in o.name for s in ("shirt", "vest", "bandana", "belt", "holster", "hatch", "buckle")):
                    o.hide_render = k["costume"] < 0.5
                    o.keyframe_insert("hide_render", frame=f)
    # keys that follow a part: aim at the part's posed world position at that frame (second pass,
    # once every pose key exists), with the camera at an offset from it
    for k in tl:
        if "target_part" in k:
            obj = T[t]["parts"][k["target_part"]]
            f0 = int(k["t"] * fps) + 1
            f1 = int(k.get("track_until", k["t"]) * fps) + 1
            for f in range(f0, f1 + 1):
                scn.frame_set(f)
                p = sum((obj.matrix_world @ Vector(cc) for cc in obj.bound_box), Vector()) / 8
                tgt.location = p
                tgt.keyframe_insert("location", frame=f)
                if "cam_offset" in k:
                    c.location = p + Vector(k["cam_offset"])
                    c.keyframe_insert("location", frame=f)
    for a in bpy.data.actions:
        for fc in a.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER" if fc.data_path != "hide_render" else "CONSTANT"
                kp.easing = "EASE_IN_OUT"
    scn.frame_start = 1
    scn.frame_end = int(tl[-1]["t"] * fps) + 1
    render_settings(JOB.get("engine", "eevee"), JOB.get("res", [1280, 720]), JOB.get("samples", 32), JOB["out"], fps)
    scn.render.image_settings.file_format = "PNG"
    if JOB.get("frames"):
        scn.frame_start, scn.frame_end = JOB["frames"]
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
