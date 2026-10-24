"""Joyful Jack body, arms and hands: parametric CAD for the three tiers (build123d).

Run with the stack's CAD runtime from the protoboard/ folder:
    .protoboard/tools/cad/bin/python cad/joyful_jack_cad.py [a|b|c|all]

Writes, per tier, to out/cad/tier-<t>/:
    parts/<name>.stl     one mesh per part, in its link's local frame (mm)
    rig.json             links (parent, joint origin, axis, limits), parts (file, material,
                         mass, explode offset), and the scene placement of the head
    mass.json            mass roll-up and the shoulder / tip checks

Frame: mm, Z up, floor at z = 0, the character faces -Y. The character's right arm is on -X.
Every link is modelled hanging straight down (-Z) from its joint at the link origin.
The head is the received STEP (out/cad/head-*.glb, made by cad/tools/step2glb.py) and is
placed by rig.json, not modelled here.

Dimensions that come from research are marked SRC; sizes chosen here for the design are
plain numbers; actuator and battery bodies are envelopes (box + flange + horn), not
manufacturer models.
"""
from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import dataclass, field

from build123d import (
    Box, Cylinder, Cone, Sphere, Torus, Pos, Rot, Plane, Ellipse, Polygon, Circle, Rectangle,
    RectangleRounded, Location, Compound, Solid, Part, loft, extrude, export_stl, Axis, Align,
)

OUT = os.path.join(os.path.dirname(__file__), "..", "out", "cad")

# ---------------------------------------------------------------- densities (g/cm3)
DENSITY = {
    "orange_shell": 1.27 * 0.6,   # PETG, thin printed shells at ~60 % fill of the modelled solid
    "leather_brown": 0.9,
    "fabric_vest": 0.35, "fabric_shirt": 0.25, "bandana_green": 0.2, "hat_tan": 0.35,
    "metal_steel": 7.85, "metal_alu": 2.7, "brass": 8.5,
    "plastic_black": 1.2 * 0.5, "plastic_dark": 1.2 * 0.5, "plastic_red": 1.1, "rubber": 1.2,
    "pcb_green": 1.85, "pcb_blue": 1.85, "wood_ply": 0.65, "concrete": 2.3, "bucket": 0.95,
    "glove_white": 0.3, "metal_print": 1.24 * 0.5,   # printed parts painted metallic (tier C hand) "battery_red": None, "servo_black": None, "servo_dark": None,
}

# ---------------------------------------------------------------- actuator envelopes
# L along the output axis' perpendicular (length), W (width), H (height, output axis), mass g
@dataclass
class ServoSpec:
    name: str
    L: float
    W: float
    H: float
    flange_L: float
    flange_z: float      # flange underside above the case bottom
    spline_off: float    # spline axis from the case end
    horn_d: float
    mass_g: float
    material: str = "servo_black"

SERVOS = {
    # SRC: DSSERVO DS3225 datasheet drawing (catalog part dsservo-ds3225mg-180): 40 x 20 x 40.5, 54.5 flange, 27.7 to flange, 60 g
    "ds3225": ServoSpec("DS3225MG", 40.0, 20.0, 40.5, 54.5, 27.7, 10.0, 24.0, 60),
    # DS3235 / DS3218 share the standard case (to confirm against research/sourcing)
    "ds3235": ServoSpec("DS3235", 40.0, 20.0, 40.5, 54.5, 27.7, 10.0, 24.0, 66),
    "ds3218": ServoSpec("DS3218MG", 40.0, 20.0, 40.5, 54.5, 27.7, 10.0, 24.0, 60),
    # Feetech STS series envelope (to confirm against research/sourcing)
    "sts3215": ServoSpec("STS3215", 45.2, 24.7, 35.0, 45.2, 35.0, 11.0, 20.0, 55, "servo_dark"),
    "sts3250": ServoSpec("STS3250", 45.2, 24.7, 35.0, 45.2, 35.0, 11.0, 20.0, 72, "servo_dark"),
    # MG996R standard-size envelope (hand grip, tier A)
    "mg996r": ServoSpec("MG996R", 40.7, 19.7, 42.9, 54.0, 28.0, 10.0, 22.0, 55),
    "scs0009": ServoSpec("SCS0009", 23.2, 12.1, 25.25, 32.0, 16.0, 6.0, 8.0, 13, "servo_dark"),
}


# ---------------------------------------------------------------- model containers
@dataclass
class PartRec:
    name: str
    shape: object
    material: str
    explode: tuple = (0, 0, 0)
    mass_g: float | None = None     # fixed mass (bought parts); else volume x density


@dataclass
class Link:
    name: str
    parent: str | None
    origin: tuple = (0, 0, 0)        # joint origin in the parent link frame (mm)
    axis: tuple | None = None        # rotation axis in the parent frame (None = fixed)
    limits: tuple = (-90, 90)
    role: str = ""
    parts: list = field(default_factory=list)

    def add(self, name, shape, material, explode=(0, 0, 0), mass_g=None):
        self.parts.append(PartRec(f"{self.name}__{name}", shape, material, explode, mass_g))
        return shape


# ---------------------------------------------------------------- primitives
def zcyl(r, h, z0=0.0, x=0.0, y=0.0):
    """Cylinder along Z from z0 to z0+h."""
    return Pos(x, y, z0 + h / 2) * Cylinder(r, h)


def xcyl(r, h, x0=0.0, y=0.0, z=0.0):
    return Pos(x0 + h / 2, y, z) * (Rot(0, 90, 0) * Cylinder(r, h))


def ycyl(r, h, y0=0.0, x=0.0, z=0.0):
    return Pos(x, y0 + h / 2, z) * (Rot(90, 0, 0) * Cylinder(r, h))


def zcone(r0, r1, h, z0=0.0, x=0.0, y=0.0):
    return Pos(x, y, z0 + h / 2) * Cone(r0, r1, h)


def tube(r_out, r_in, h, z0=0.0):
    return zcyl(r_out, h, z0) - zcyl(r_in, h + 2, z0 - 1)


def star(r_out, r_in, n=5, depth=20.0):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi / 2 + i * math.pi / n
        pts.append((r * math.cos(a), r * math.sin(a)))
    return extrude(Polygon(*pts, align=None), depth)


def servo_body(spec: ServoSpec, axis="x"):
    """Servo envelope with its output spline axis on the local origin, pointing +axis.

    The case hangs on the -Z side of the output, so the output sits at the top of the case."""
    s = spec
    case = Pos(s.L / 2 - s.spline_off, 0, -s.H / 2) * Box(s.L, s.W, s.H)
    flange = Pos(s.L / 2 - s.spline_off, 0, -(s.H - s.flange_z) - 1.25) * Box(s.flange_L, s.W, 2.5)
    horn = zcyl(s.horn_d / 2, 4.0, 0.0)
    body = case + flange
    shape_horn = horn
    rot = {"z": Rot(0, 0, 0), "x": Rot(0, 90, 0), "y": Rot(-90, 0, 0), "-x": Rot(0, -90, 0), "-y": Rot(90, 0, 0)}[axis]
    return rot * body, rot * shape_horn


def u_bracket(width, depth, height, t=2.5):
    """Aluminium U bracket (servo bracket) opening downward, centred on the origin top."""
    top = Pos(0, 0, -t / 2) * Box(width, depth, t)
    side_a = Pos(width / 2 - t / 2, 0, -height / 2) * Box(t, depth, height)
    side_b = Pos(-width / 2 + t / 2, 0, -height / 2) * Box(t, depth, height)
    return top + side_a + side_b


def bracer(r_top, r_bot, length, z_top, wall=2.6, straps=(0.25, 0.75)):
    """Arm shell segment: a tapered tube, split into front and back halves, with strap bands."""
    outer = zcone(r_bot, r_top, length, z_top - length)
    inner = zcone(r_bot - wall, r_top - wall, length + 2, z_top - length - 1)
    shell = outer - inner
    front = shell & (Pos(0, -200, z_top - length / 2) * Box(400, 400, length + 4))
    back = shell - front
    bands = []
    for f in straps:
        z = z_top - f * length
        r = r_top + (r_bot - r_top) * f
        bands.append(Pos(0, 0, z) * Torus(r + 0.5, 2.2))
    return front, back, bands


def rounded_box(L, W, H, r):
    return extrude(RectangleRounded(L, W, min(r, min(L, W) / 2 - 0.01)), H)


# ---------------------------------------------------------------- shared: base and mast
BASE_DISC_D = 610.0          # 24 in plywood skirt
BASE_DISC_T = 19.0           # 3/4 in
BUCKET_H = 368.0             # SRC (to confirm): typical 5 US gal bucket ~14.5 in tall
BUCKET_D_TOP = 302.0         # ~11.9 in
BUCKET_D_BOT = 262.0         # ~10.3 in
CONCRETE_H = 330.0
PIPE_OD = 33.4               # 1 in NPS black iron pipe OD (ASME B36.10)
PIPE_ID = 26.6
MAST_TOP = 1010.0
WAIST_Z = 780.0
SHOULDER_Z = 1185.0
SHOULDER_X = 232.0
NECK_Z = 1268.0              # top of the torso neck plate, where the head's neck base sits


def base_and_mast(root: Link):
    z0 = BASE_DISC_T
    root.add("base_disc", zcyl(BASE_DISC_D / 2, BASE_DISC_T, 0), "wood_ply", (0, 0, -120))
    bucket_outer = zcone(BUCKET_D_BOT / 2, BUCKET_D_TOP / 2, BUCKET_H, z0)
    bucket_inner = zcone(BUCKET_D_BOT / 2 - 2.5, BUCKET_D_TOP / 2 - 2.5, BUCKET_H, z0 + 2.5)
    rim = Pos(0, 0, z0 + BUCKET_H - 6) * Torus(BUCKET_D_TOP / 2 + 2, 4)
    root.add("bucket", bucket_outer - bucket_inner + rim, "bucket", (0, 0, -60))
    r_fill = BUCKET_D_BOT / 2 - 2.5 + (BUCKET_D_TOP - BUCKET_D_BOT) / 2 * (CONCRETE_H / BUCKET_H)
    concrete = zcone(BUCKET_D_BOT / 2 - 2.5, r_fill, CONCRETE_H - 2.5, z0 + 2.5) - zcyl(PIPE_OD / 2, 400, z0)
    root.add("concrete", concrete, "concrete", (0, 0, -60))
    flange = zcyl(55, 9, z0 + 6) + zcyl(25, 20, z0 + 6)
    root.add("floor_flange", flange - zcyl(PIPE_ID / 2, 40, z0), "metal_steel", (0, 0, 0))
    mast_h = MAST_TOP - (z0 + 10)
    root.add("mast_pipe", tube(PIPE_OD / 2, PIPE_ID / 2, mast_h, z0 + 10), "metal_steel", (0, 0, 0))
    collar = tube(26, PIPE_OD / 2, 30, WAIST_Z - 40) + xcyl(4, 22, 20, 0, WAIST_Z - 25)
    root.add("height_collar", collar, "metal_steel", (0, 0, 60))


# ---------------------------------------------------------------- shared: torso shell and costume
TORSO_SECTIONS = [  # z, half-width x, half-depth y
    (WAIST_Z - 10, 150, 98),
    (900, 168, 108),
    (1040, 192, 118),
    (1150, 205, 118),
    (1225, 175, 104),
    (NECK_Z - 4, 62, 55),
]


def torso_solid(grow=0.0):
    sections = [Plane.XY.offset(z) * Ellipse(rx + grow, ry + grow) for z, rx, ry in TORSO_SECTIONS]
    return loft(sections)


def torso_and_costume(root: Link, tier: str):
    body = torso_solid(0.0)
    shell = body - torso_solid(-3.0)
    front = shell & (Pos(0, -300, 1000) * Box(800, 600, 900))
    back = shell - front
    # the torso shell is the shirt-covered form; an access hatch at the back is cut out
    hatch = Pos(0, 110, 905) * Box(190, 80, 170)
    root.add("shirt_front", front, "fabric_shirt", (0, -260, 0))
    root.add("shirt_back", back - hatch, "fabric_shirt", (0, 260, 0))
    root.add("hatch_door", (shell & hatch), "fabric_shirt", (0, 420, 0))

    # vest: a shell over the shirt, open at the front, jagged hem, star cut-outs (concept art)
    vest = torso_solid(9.0) - torso_solid(5.0)
    vest = vest - (Pos(0, -150, 1060) * Box(70, 200, 600))          # front opening
    vest = vest - (Pos(0, 0, WAIST_Z + 45) * Box(600, 400, 70))      # hem above the belt
    for i in range(9):                                                 # jagged hem
        a = i * 2 * math.pi / 9
        tooth = Pos(240 * math.cos(a), 140 * math.sin(a), WAIST_Z + 95) * (Rot(0, 0, math.degrees(a)) * (Rot(45, 0, 0) * Box(70, 70, 70)))
        vest = vest - tooth
    for (x, z, r) in [(-120, 990, 22), (125, 930, 17), (-60, 1110, 14), (95, 1080, 12)]:
        vest = vest - (Pos(x, -40, z) * (Rot(90, 0, 0) * star(r, r * 0.45, 5, 300)))
    vest_l = vest & (Pos(400, 0, 1000) * Box(800, 800, 900))
    vest_r = vest - vest_l
    root.add("vest_left", vest_l, "fabric_vest", (140, -320, 40))
    root.add("vest_right", vest_r, "fabric_vest", (-140, -320, 40))

    # bandana: a folded triangle at the neck
    tri = extrude(Polygon((-95, 0), (95, 0), (0, -120), align=None), 5)
    bandana = Pos(0, -104, NECK_Z - 40) * (Rot(-78, 0, 0) * tri) + Pos(0, -10, NECK_Z - 26) * Torus(72, 8)
    root.add("bandana", bandana, "bandana_green", (0, -380, 120))

    # belt with buckle and holster
    belt = torso_solid(6.0) & (Pos(0, 0, WAIST_Z + 22) * Box(600, 400, 40))
    belt = belt - torso_solid(1.0)
    buckle = Pos(0, -112, WAIST_Z + 22) * Box(58, 10, 44) - Pos(0, -114, WAIST_Z + 22) * Box(40, 10, 26)
    holster = Pos(-150, -60, WAIST_Z - 40) * (Rot(0, 8, 0) * rounded_box(46, 30, 120, 10))
    root.add("belt", belt, "leather_brown", (0, -200, -60))
    root.add("buckle", buckle, "brass", (0, -280, -60))
    root.add("holster", holster, "leather_brown", (-160, -220, -80))

    # cowboy hat sits on the head; placed by the head's top (rig.json head.hat_z)
    return


HEAD_BASE_DROP = 236.0   # head-facade-v61.glb: the neck base plate's underside is 236 mm below the file origin
HAT_Z = HEAD_BASE_DROP + 62.0   # hat brim height above the neck base (head link frame)


def cowboy_hat(hat: Link):
    """Cowboy hat sized to the head (facade 242 x 234 mm), in the head link frame (origin at the neck base)."""
    z = HAT_Z
    brim = Pos(0, 0, z) * extrude(Ellipse(255, 222), 5)
    lip = Pos(0, 0, z + 2) * Torus(1, 1)
    curl = None
    for sx in (-1, 1):
        c = Pos(sx * 228, 0, z + 22) * (Rot(90, 0, 0) * Cylinder(26, 300))
        c = c - Pos(sx * 228, 0, z + 22) * (Rot(90, 0, 0) * Cylinder(21, 302))
        c = c & (Pos(sx * 248, 0, z + 18) * Box(44, 330, 50))
        curl = c if curl is None else curl + c
    crown = loft([Plane.XY.offset(z + 5) * Ellipse(126, 110), Plane.XY.offset(z + 95) * Ellipse(118, 100), Plane.XY.offset(z + 140) * Ellipse(92, 74)])
    crown_in = loft([Plane.XY.offset(z + 3) * Ellipse(122, 106), Plane.XY.offset(z + 92) * Ellipse(114, 96), Plane.XY.offset(z + 136) * Ellipse(88, 70)])
    crown = crown - crown_in - Pos(0, 0, z + 150) * Box(60, 170, 40)
    band = Pos(0, 0, z + 5) * extrude(Ellipse(128.5, 112.5), 20) - Pos(0, 0, z + 4) * extrude(Ellipse(125, 109), 22)
    hat.add("brim", brim + curl, "hat_tan", (0, 0, 380))
    hat.add("crown", crown, "hat_tan", (0, 0, 460))
    hat.add("band", band, "leather_brown", (0, 0, 420))
    hat.add("concho", Pos(0, -112, z + 14) * (Rot(90, 0, 0) * Cylinder(9, 4)), "metal_steel", (0, 0, 420))


# ---------------------------------------------------------------- torso internals per tier
def torso_internals(root: Link, tier: str):
    if tier == "a":
        # laser-cut 1/4 in (6 mm) plywood ribs on the mast, two spine plates (one 2 x 4 ft project panel)
        for i, (z, rx, ry) in enumerate(TORSO_SECTIONS[:4]):
            rib = Pos(0, 0, z + 20) * extrude(Ellipse(rx - 12, ry - 12), 6) - zcyl(PIPE_OD / 2 + 0.5, 20, z + 18)
            root.add(f"rib_{i}", rib, "wood_ply", (0, 0, 40 * i))
        for x in (-60, 60):
            root.add(f"spine_{'l' if x > 0 else 'r'}", Pos(x, 0, 1000) * Box(6, 150, 420), "wood_ply", (x * 2, 0, 0))
        shoulder_beam = Pos(0, 0, SHOULDER_Z) * Box(2 * SHOULDER_X - 70, 40, 40)
        root.add("shoulder_beam", shoulder_beam - Pos(0, 0, SHOULDER_Z) * Box(2 * SHOULDER_X, 34, 34), "metal_alu", (0, 0, 60))
    else:
        # 2020 extrusion box frame on the mast collar
        L, W, H, z0 = 220.0, 140.0, 380.0, WAIST_Z + 40
        bars = []
        for x in (-L / 2 + 10, L / 2 - 10):
            for y in (-W / 2 + 10, W / 2 - 10):
                bars.append(Pos(x, y, z0 + H / 2) * Box(20, 20, H))
        for z in (z0 + 10, z0 + H - 10):
            for y in (-W / 2 + 10, W / 2 - 10):
                bars.append(Pos(0, y, z) * Box(L - 40, 20, 20))
            for x in (-L / 2 + 10, L / 2 - 10):
                bars.append(Pos(x, 0, z) * Box(20, W - 40, 20))
        frame = bars[0]
        for b in bars[1:]:
            frame = frame + b
        root.add("frame_2020", frame, "metal_alu", (0, 0, 0))
        root.add("mast_plate", Pos(0, 0, z0 + 20) * Box(L - 40, W - 40, 6) - zcyl(PIPE_OD / 2 + 0.5, 20, z0 + 15), "metal_alu", (0, 0, -40))
        shoulder_beam = Pos(0, 0, SHOULDER_Z) * Box(2 * SHOULDER_X - 70, 40, 40) - Pos(0, 0, SHOULDER_Z) * Box(2 * SHOULDER_X, 34, 34)
        root.add("shoulder_beam", shoulder_beam, "metal_alu", (0, 0, 60))
    # neck plate: the head's neck base sits on it
    root.add("neck_plate", zcyl(70, 8, NECK_Z - 8) - zcyl(14, 20, NECK_Z - 10), "metal_alu", (0, 0, 140))
    root.add("neck_post", zcyl(14, NECK_Z - 8 - SHOULDER_Z, SHOULDER_Z) - zcyl(10, 200, SHOULDER_Z - 10), "metal_steel", (0, 0, 100))

    # power: M18 dock(s) and pack(s) behind the hatch, electronics plate in front of the mast
    n_batt = 1 if tier == "a" else 2
    for i in range(n_batt):
        x = 0 if n_batt == 1 else (-55 + 110 * i)
        dock = Pos(x, 68, 860) * Box(84, 36, 120)
        pack = Pos(x, 68 + 18 + 34, 860) * Box(80, 68, 135)   # M18 12.0 Ah envelope (to confirm)
        root.add(f"m18_dock_{i}", dock, "plastic_black", (0, 280, -40 * i))
        root.add(f"m18_pack_{i}", pack, "battery_red", (0, 420, -40 * i), mass_g=1500)  # SRC to confirm
    plate = Pos(0, -55, 1010) * Box(230, 4, 190)
    root.add("electronics_plate", plate, "plastic_black", (0, -220, 0))
    boards = [("buck_5v", (-75, 960), (45, 38, 14), "pcb_green"), ("servo_buck", (40, 960), (80, 52, 30), "metal_alu"),
              ("fuse_block", (-70, 1060), (70, 40, 22), "plastic_black"), ("estop_relay", (20, 1060), (30, 30, 30), "plastic_black"),
              ("ina226", (75, 1060), (25, 20, 3), "pcb_blue")]
    if tier == "a":
        boards.append(("pca9685_2", (-20, 1100), (62, 25, 6), "pcb_blue"))
    else:
        boards += [("bus_adapter", (-20, 1100), (40, 30, 10), "pcb_blue"), ("ideal_diode_or", (70, 1100), (50, 40, 12), "pcb_green")]
    if tier == "c":
        boards += [("pi5", (-90, 1100), (85, 56, 18), "pcb_green"), ("power_board", (0, 905), (120, 70, 10), "pcb_green")]
    for name, (x, z), (l, w, h), mat in boards:
        root.add(name, Pos(x, -57 - w / 2 + 0 if False else -57 - h / 2, z) * Box(l, h, w), mat, (0, -300, 0))
    # emergency stop on the back, at the belt line (red mushroom on a yellow base)
    estop = Pos(0, 120, WAIST_Z + 75) * (Rot(-90, 0, 0) * (zcyl(20, 18, 0) + zcyl(26, 14, 18)))
    root.add("estop", estop, "plastic_red", (0, 260, 0))


# ---------------------------------------------------------------- arms
@dataclass
class ArmPlan:
    joints: list            # [(name, servo key, axis, limits)]
    upper: float = 255.0
    fore: float = 225.0
    shell_r: tuple = (44, 36, 34, 27)  # upper top, upper bottom, fore top, fore bottom


ARMS = {
    "a": ArmPlan([("j1_flex", "ds3235", "x", (-60, 150)), ("j2_abduct", "ds3235", "y", (-10, 100)),
                  ("j3_elbow", "ds3225", "x", (0, 130)), ("grip", "mg996r", "x", (0, 70))]),
    # tier B: STS3215 everywhere; shoulder flex, abduction and elbow through 22:60 GT2 belt stages (2.73:1).
    # tier C: STS3250 on the same belt stages (cad/analysis.py: direct drive cannot hold the arm out)
    "b": ArmPlan([("j1_flex", "sts3215", "x", (-60, 160)), ("j2_abduct", "sts3215", "y", (-10, 110)),
                  ("j3_twist", "sts3215", "z", (-90, 90)), ("j4_elbow", "sts3215", "x", (0, 135)),
                  ("j5_wrist_twist", "sts3215", "z", (-120, 120)), ("fingers", "sts3215", "x", (0, 80)), ("thumb", "sts3215", "y", (0, 70))]),
    "c": ArmPlan([("j1_flex", "sts3250", "x", (-60, 160)), ("j2_abduct", "sts3250", "y", (-10, 110)),
                  ("j3_twist", "sts3215", "z", (-90, 90)), ("j4_elbow", "sts3250", "x", (0, 135)),
                  ("j5_wrist_twist", "sts3215", "z", (-120, 120)), ("j6_wrist_pitch", "sts3215", "x", (-60, 60))]),
}


def build_arm(links: list, tier: str, side: str):
    """One arm (side 'r' on -X, 'l' on +X). Links are built for the right arm and mirrored."""
    sgn = -1 if side == "r" else 1
    plan = ARMS[tier]
    J = {j[0]: j for j in plan.joints}
    S = lambda k: SERVOS[J[k][1]]
    out = []

    def L(name, parent, origin, axis, limits, role=""):
        lk = Link(f"{side}_{name}", parent, origin, axis, limits, role)
        out.append(lk)
        return lk

    ex = (sgn * 1, 0, 0)  # explode outward

    # shoulder mount on the torso (fixed): J1 actuator, its bracket and, in A, the 2:1 belt stage
    mount = L("shoulder_mount", "torso", (sgn * (SHOULDER_X - 40), 0, SHOULDER_Z), None, (0, 0))
    s1 = S("j1_flex")
    body, horn = servo_body(s1, "x" if sgn > 0 else "-x")
    mount.add("j1_servo", Pos(0, 0, -12) * body, s1.material, (sgn * 60, 0, 0), s1.mass_g)
    BRK = "plastic_dark" if tier == "a" else "metal_alu"   # tier A prints its brackets
    mount.add("j1_bracket", Pos(sgn * 4, 0, 30) * Box(16, 56, 60) - Pos(sgn * 4, 0, 30) * Box(6, 40, 40), BRK, (sgn * 40, 0, 0))
    if tier == "a":
        # no belt stage: a counterbalance spring from the bracket to the yoke carries the arm's weight
        mount.add("spring", Pos(0, 30, 42) * (Rot(0, 0, 0) * tube(5, 3.5, 60, -30)), "metal_steel", (sgn * 80, 60, 0))
    if tier in ("b", "c"):
        # 22T pinion on the servo, 60T pulley on the joint shaft, closed GT2 belt
        mount.add("belt_small_pulley", xcyl(7, 10, sgn * 22 - 5, 0, 58), "metal_alu", (sgn * 80, 0, 0))
        mount.add("belt", Pos(sgn * 27, 0, 28) * Box(6, 22, 60), "rubber", (sgn * 80, 0, 0))

    # link 1: shoulder yoke, turns about X (flex) at the shoulder pivot
    l1 = L("shoulder_yoke", mount.name, (sgn * 40, 0, 0), (1, 0, 0), J["j1_flex"][3], "shoulder flex")
    if tier in ("b", "c"):
        l1.add("big_pulley", xcyl(19, 10, sgn * 0 - 5, 0, 0), "metal_alu", (sgn * 60, 0, 0))
    l1.add("pivot_cap", Pos(sgn * 6, 0, 0) * Sphere(26), "orange_shell", (sgn * 120, 0, 40))
    s2 = S("j2_abduct")
    body2, horn2 = servo_body(s2, "-y")
    l1.add("j2_servo", Pos(sgn * 22, 0, -28) * (Rot(0, 0, 90) * body2), s2.material, (sgn * 90, 0, 0), s2.mass_g)
    l1.add("yoke_bracket", Pos(sgn * 22, 0, -10) * u_bracket(44, 58, 46), BRK, (sgn * 90, 0, 20))

    # link 2: upper arm, turns about Y (abduction)
    l2 = L("upper_arm", l1.name, (sgn * 22, 0, -40), (0, 1, 0), J["j2_abduct"][3], "shoulder abduction")
    ru_t, ru_b, rf_t, rf_b = plan.shell_r
    z_elbow = -plan.upper
    f, b_, bands = bracer(ru_t, ru_b, plan.upper - 70, -30)
    l2.add("shell_front", f, "orange_shell", (sgn * 60, -140, 0))
    l2.add("shell_back", b_, "orange_shell", (sgn * 60, 140, 0))
    for i, band in enumerate(bands):
        l2.add(f"strap_{i}", band, "leather_brown", (sgn * 60, -200, 0))
    l2.add("bone", zcyl(8, plan.upper - 40, z_elbow + 20), "metal_alu", (sgn * 140, 0, 0))
    parent_for_elbow = l2
    if "j3_twist" in J:
        s3 = S("j3_twist")
        body3, _ = servo_body(s3, "z")
        l2.add("j3_servo", Pos(0, 0, -50) * (Rot(180, 0, 0) * body3), s3.material, (sgn * 140, 0, 30), s3.mass_g)
        l3 = L("upper_arm_twist", l2.name, (0, 0, -52), (0, 0, 1), J["j3_twist"][3], "upper-arm twist")
        l3.add("twist_disc", zcyl(22, 6, -6), "metal_alu", (sgn * 160, 0, 0))
        parent_for_elbow = l3
        z_elbow_local = z_elbow + 52
    else:
        z_elbow_local = z_elbow

    ek = "j4_elbow" if "j4_elbow" in J else "j3_elbow"
    se = S(ek)
    bodye, _ = servo_body(se, "x" if sgn > 0 else "-x")
    parent_for_elbow.add("elbow_servo", Pos(-sgn * 6, 0, z_elbow_local + 18) * (Rot(0, 0, 180) * bodye), se.material, (sgn * 160, 0, 0), se.mass_g)
    parent_for_elbow.add("elbow_fork", Pos(0, 0, z_elbow_local + 10) * u_bracket(64, 46, 38), BRK, (sgn * 180, 0, 0))
    if tier in ("b", "c"):
        parent_for_elbow.add("elbow_belt", Pos(sgn * 36, 0, z_elbow_local + 30) * Box(6, 22, 52), "rubber", (sgn * 200, 0, 0))

    # forearm, turns about X (elbow)
    l4 = L("forearm", parent_for_elbow.name, (0, 0, z_elbow_local), (1, 0, 0), J[ek][3], "elbow")
    l4.add("elbow_ball", Sphere(24), "metal_steel", (sgn * 200, 0, 0))
    f, b_, bands = bracer(rf_t, rf_b, plan.fore - 60, -26)
    l4.add("shell_front", f, "orange_shell", (sgn * 200, -150, -40))
    l4.add("shell_back", b_, "orange_shell", (sgn * 200, 150, -40))
    for i, band in enumerate(bands):
        l4.add(f"strap_{i}", band, "leather_brown", (sgn * 200, -210, -40))
    l4.add("bone", zcyl(7, plan.fore - 30, -plan.fore + 10), "metal_alu", (sgn * 240, 0, -40))
    wrist_parent = l4
    z_wrist = -plan.fore
    if "j5_wrist_twist" in J:
        s5 = S("j5_wrist_twist")
        body5, _ = servo_body(s5, "z")
        l4.add("wrist_servo", Pos(0, 0, z_wrist + 48) * (Rot(180, 0, 0) * body5), s5.material, (sgn * 240, 0, -60), s5.mass_g)
        l5 = L("wrist", l4.name, (0, 0, z_wrist + 10), (0, 0, 1), J["j5_wrist_twist"][3], "wrist twist")
        l5.add("cuff", tube(30, 24, 16, -14), "leather_brown", (sgn * 260, 0, -80))
        wrist_parent, z_wrist = l5, -10
        if "j6_wrist_pitch" in J:
            s6 = S("j6_wrist_pitch")
            body6, _ = servo_body(s6, "x" if sgn > 0 else "-x")
            l5.add("pitch_servo", Pos(-sgn * 6, 0, -22) * (Rot(0, 0, 180) * body6), s6.material, (sgn * 260, 0, -100), s6.mass_g)
            l6 = L("wrist_pitch", l5.name, (0, 0, -40), (1, 0, 0), J["j6_wrist_pitch"][3], "wrist pitch")
            wrist_parent, z_wrist = l6, 0
    build_hand(out, tier, side, sgn, wrist_parent, z_wrist, J)
    links.extend(out)


def build_hand(out, tier, side, sgn, parent, z0, J):
    ex = lambda k: (sgn * (300 + 30 * k), 0, -140 - 30 * k)

    def L(name, par, origin, axis, limits, role=""):
        lk = Link(f"{side}_{name}", par, origin, axis, limits, role)
        out.append(lk)
        return lk

    if tier == "a":
        # cartoon mitt: palm with the thumb, one ganged three-finger paddle on a hinge, one servo
        sg = SERVOS["mg996r"]
        body, _ = servo_body(sg, "x" if sgn > 0 else "-x")
        parent.add("grip_servo", Pos(0, 0, z0 + 10) * (Rot(0, 0, 180) * body), sg.material, ex(0), sg.mass_g)
        palm = Pos(0, 0, z0 - 30) * rounded_box(78, 34, 70, 14)
        palm = Pos(0, 0, -70) * palm
        parent.add("palm", palm, "orange_shell", ex(1))
        thumb = Pos(-sgn * 44, -18, z0 - 70) * (Rot(-30, 0, 0) * zcyl(13, 55, -55)) + Pos(-sgn * 44, -18 - 24, z0 - 118) * Sphere(13)
        parent.add("thumb", thumb, "orange_shell", ex(2))
        fingers = L("mitt_fingers", parent.name, (0, 4, z0 - 100), (1, 0, 0), J["grip"][3], "grip")
        paddle = None
        for i, x in enumerate((-25, 0, 25)):
            f = zcyl(12.5, 80, -80, x, 0) + Pos(x, 0, -80) * Sphere(12.5)
            paddle = f if paddle is None else paddle + f
        fingers.add("paddle", paddle + Pos(0, 0, -6) * Box(70, 22, 12), "orange_shell", ex(3))
        fingers.add("grip_pad", Pos(0, -12, -45) * Box(66, 3, 70), "rubber", ex(4))
        return

    if tier == "b":
        # glove hand: four linked fingers on one actuator, a thumb on another (fingers + thumb servos)
        sf, st = SERVOS[J["fingers"][1]], SERVOS[J["thumb"][1]]
        bf, _ = servo_body(sf, "x" if sgn > 0 else "-x")
        parent.add("finger_servo", Pos(0, 6, z0 - 18) * (Rot(0, 0, 180) * bf), sf.material, ex(0), sf.mass_g)
        bt, _ = servo_body(st, "y")
        parent.add("thumb_servo", Pos(-sgn * 30, 0, z0 - 40) * (Rot(0, 0, 90) * bt), st.material, ex(0), st.mass_g)
        parent.add("palm", Pos(0, 0, z0 - 125) * rounded_box(84, 32, 70, 12), "glove_white", ex(1))
        parent.add("cuff_flare", zcone(42, 32, 26, z0 - 56), "glove_white", ex(1))
        fingers = L("glove_fingers", parent.name, (0, 0, z0 - 128), (1, 0, 0), J["fingers"][3], "fingers")
        for i, x in enumerate((-30, -10, 10, 30)):
            ln = [32, 36, 34, 28][i]
            seg = zcyl(9, ln, -ln, x) + Pos(x, 0, -ln) * Sphere(9.5) + zcyl(8.5, ln * 0.8, -ln - ln * 0.8, x) + Pos(x, 0, -ln - ln * 0.8) * Sphere(8.5)
            fingers.add(f"finger_{i}", seg, "glove_white", ex(2 + i * 0.3))
        thumb = L("glove_thumb", parent.name, (-sgn * 44, -6, z0 - 85), (0, 1, 0), J["thumb"][3], "thumb")
        thumb.add("thumb", (Rot(0, -sgn * 35, 0) * (zcyl(10, 34, -34) + Pos(0, 0, -34) * Sphere(10) + zcyl(9, 26, -60) + Pos(0, 0, -60) * Sphere(9))), "glove_white", ex(4))
        return

    # tier c: humanoid robotic hand, four fingers of two driven joints and an opposable thumb
    # (AmazingHand-style: eight micro bus servos in the palm, two per finger)
    sm = SERVOS["scs0009"]
    palm_z = z0 - 20
    parent.add("palm_frame", Pos(0, 0, palm_z - 85) * rounded_box(88, 28, 85, 8), "metal_print", ex(1))
    for i in range(8):
        x = -33 + (i % 4) * 22
        y = -9 if i < 4 else 9
        parent.add(f"finger_servo_{i}", Pos(x, y, palm_z - 40) * Box(sm.W, 10, sm.H), sm.material, ex(0.5), sm.mass_g)
    for i, x in enumerate((-33, -11, 11, 33)):
        ln = [36, 42, 40, 32][i]
        prox = L(f"finger{i}_proximal", parent.name, (x, 0, palm_z - 88), (1, 0, 0), (0, 95), "finger")
        prox.add("phalanx", zcyl(7.5, ln, -ln) + Pos(0, 0, 0) * Sphere(8.5), "metal_print", ex(2 + i * 0.2))
        prox.add("tendon_plate", Pos(0, 6, -ln / 2) * Box(10, 2, ln), "metal_print", ex(2 + i * 0.2))
        dist = L(f"finger{i}_distal", prox.name, (0, 0, -ln), (1, 0, 0), (0, 95), "finger")
        dist.add("phalanx", zcyl(6.5, ln * 0.8, -ln * 0.8) + Sphere(7.5) + Pos(0, 0, -ln * 0.8) * Sphere(6.5), "metal_print", ex(3 + i * 0.2))
        dist.add("tip_pad", Pos(0, -5, -ln * 0.6) * Box(10, 3, ln * 0.5), "rubber", ex(3.4 + i * 0.2))
    th = L("thumb_base", parent.name, (-sgn * 46, -10, palm_z - 40), (0, 0, 1), (0, 90), "thumb")
    th.add("metacarpal", Rot(0, -sgn * 40, 0) * (zcyl(8, 36, -36) + Sphere(9)), "metal_print", ex(4))
    th2 = L("thumb_tip", th.name, (-sgn * 23, 0, -28), (1, 0, 0), (0, 80), "thumb")
    th2.add("phalanx", Rot(0, -sgn * 40, 0) * (zcyl(7, 30, -30) + Sphere(8) + Pos(0, 0, -30) * Sphere(7)), "metal_print", ex(5))


# ---------------------------------------------------------------- build, export, mass roll-up
def mirror_shape(shape):
    return shape.mirror(Plane.YZ)


def build(tier: str):
    root = Link("torso", None)
    base_and_mast(root)
    torso_and_costume(root, tier)
    torso_internals(root, tier)
    # the head (received CAD, placed by the renderer) turns with neck yaw; the hat rides on it
    head = Link("head", "torso", (0, 0, NECK_Z), (0, 0, 1), (-60, 60), "neck yaw")
    hat = Link("hat", "head", (0, 0, 0), None, (0, 0))
    cowboy_hat(hat)
    links = [root, head, hat]
    build_arm(links, tier, "r")
    build_arm(links, tier, "l")
    return links


def export(tier: str):
    links = build(tier)
    d = os.path.join(OUT, f"tier-{tier}")
    os.makedirs(os.path.join(d, "parts"), exist_ok=True)
    rig = {"tier": tier, "units": "mm", "frame": "Z up, floor z=0, faces -Y", "neck_z": NECK_Z,
           "head": {"glb": "../head-facade-v61.glb", "link": "head", "offset_mm": [0, 0, HEAD_BASE_DROP], "rot_z_deg": 180,
                    "eyes_mm": [[-38, 64, 26], [38, 64, 26]], "note": "glb frame: face +Y, neck base at z=-236 mm"},
           "shoulder": [SHOULDER_X, SHOULDER_Z], "links": [], "parts": []}
    total = 0.0
    per_link = {}
    for lk in links:
        rig["links"].append({"name": lk.name, "parent": lk.parent, "origin": lk.origin, "axis": lk.axis,
                             "limits": lk.limits, "role": lk.role})
        for p in lk.parts:
            shape = p.shape
            path = os.path.join(d, "parts", f"{p.name}.stl")
            export_stl(shape, path, tolerance=0.25, angular_tolerance=0.25)
            vol_cm3 = shape.volume / 1000.0
            if p.mass_g is not None:
                m = p.mass_g
            else:
                rho = DENSITY.get(p.material) or 1.0
                m = vol_cm3 * rho
            bb = shape.bounding_box()
            rig["parts"].append({"name": p.name, "link": lk.name, "file": f"parts/{p.name}.stl", "material": p.material,
                                 "explode": p.explode, "mass_g": round(m, 1),
                                 "bbox": [[round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z)], [round(v, 1) for v in (bb.max.X, bb.max.Y, bb.max.Z)]]})
            total += m
            per_link[lk.name] = per_link.get(lk.name, 0.0) + m
    with open(os.path.join(d, "rig.json"), "w") as fh:
        json.dump(rig, fh, indent=1)
    with open(os.path.join(d, "mass.json"), "w") as fh:
        json.dump({"total_g_excluding_head": round(total, 1), "per_link_g": {k: round(v, 1) for k, v in per_link.items()}}, fh, indent=1)
    print(f"tier {tier}: {len(rig['parts'])} parts, {len(links)} links, {total/1000:.1f} kg without the head")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for t in (["a", "b", "c"] if which == "all" else [which]):
        export(t)
