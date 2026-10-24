"""Quick look at a preview GLB in Blender (Eevee): four views on one sheet.

    blender -b --python cad/mech/tools/preview.py -- <preview.glb> <out.png> [focus x y z] [size mm]
"""
import bpy
import math
import sys
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
glb, out = args[0], args[1]
focus = Vector([float(v) for v in args[2:5]]) * 0.001 if len(args) >= 5 else None
size = float(args[5]) * 0.001 if len(args) >= 6 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)

COL = {"orange_shell": (0.95, 0.42, 0.05), "servo_dark": (0.08, 0.08, 0.09), "servo_black": (0.05, 0.05, 0.05),
       "metal_steel": (0.6, 0.6, 0.62), "metal_alu": (0.75, 0.76, 0.78), "brass": (0.8, 0.6, 0.25), "rubber": (0.12, 0.12, 0.12),
       "printed_grey": (0.35, 0.36, 0.38), "printed_cf": (0.9, 0.5, 0.2), "glove_white": (0.92, 0.92, 0.9),
       "wood_ply": (0.78, 0.62, 0.42), "pcb_green": (0.1, 0.45, 0.2), "pcb_blue": (0.1, 0.25, 0.6), "battery_red": (0.75, 0.05, 0.05),
       "plastic_black": (0.07, 0.07, 0.07), "plastic_red": (0.8, 0.05, 0.05), "plastic_yellow": (0.95, 0.8, 0.05), "concrete": (0.6, 0.6, 0.58), "bucket": (0.9, 0.5, 0.1)}
mats = {}
for ob in list(bpy.data.objects):
    if ob.type != "MESH":
        continue
    key = ob.name.split(".")[0]
    if key not in COL and ob.parent is not None:
        key = ob.parent.name.split(".")[0]
    c = COL.get(key, (0.5, 0.5, 0.5))
    m = mats.get(key)
    if m is None:
        m = bpy.data.materials.new(key)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*c, 1)
        b.inputs["Roughness"].default_value = 0.5
        b.inputs["Metallic"].default_value = 0.8 if key in ("metal_steel", "metal_alu", "brass") else 0.0
        mats[key] = m
    ob.data.materials.clear()
    ob.data.materials.append(m)

meshes = [o for o in bpy.data.objects if o.type == "MESH"]
mn = Vector((1e9, 1e9, 1e9))
mx = Vector((-1e9, -1e9, -1e9))
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mn = Vector(map(min, mn, w))
        mx = Vector(map(max, mx, w))
center = focus if focus is not None else (mn + mx) / 2
extent = size if size is not None else max(mx - mn)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 900
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.82, 0.84, 0.88, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
scene.world = world
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 3.0
so = bpy.data.objects.new("sun", sun)
so.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
scene.collection.objects.link(so)
cam = bpy.data.cameras.new("cam")
cam.type = "ORTHO"
cam.ortho_scale = extent * 1.15
co = bpy.data.objects.new("cam", cam)
scene.collection.objects.link(co)
scene.camera = co

views = {"front": (0, -1, 0), "side": (-1, 0, 0), "top": (0, 0, 1), "iso": (-1, -1.2, 0.8)}
import os
tiles = []
for name, d in views.items():
    v = Vector(d).normalized()
    co.location = center + v * extent * 3
    co.rotation_euler = (center - co.location).to_track_quat("-Z", "Y" if name != "top" else "Y").to_euler()
    if name == "top":
        co.rotation_euler = (0, 0, 0)
    scene.render.filepath = out.replace(".png", f"-{name}.png")
    bpy.ops.render.render(write_still=True)
    tiles.append(scene.render.filepath)
print("PREVIEW", tiles)
