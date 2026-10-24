"""Body: base, mast, torso frame, neck mount, batteries and electronics, in world coordinates (mm, Z up,
floor z = 0, the character faces -Y).

Base (all tiers): 24 in plywood skirt, 5 US gal bucket screwed to it, concrete fill, a 1 in floor flange
set in the concrete, a 1 in x 30 in black pipe nipple, a second floor flange under the torso.
Torso B/C: 2020 aluminium box 220 x 140 x 340 (uprights, top and bottom rails, 16 cast corner brackets
with M5 screws into roll-in T-nuts) on a 6 mm aluminium base plate. Torso A: 12 mm birch plywood box
(side panels, top and bottom boards, #8 wood screws). On top: two 2020 neck posts and a 6 mm neck plate
for the head. The shoulder housings' feet bolt to the top side rails (x = +-100) with M5 into T-nuts
(tier A: hammer-in tee nuts), at the positions arm_bus.py and arm_std.py use.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Box, Cylinder, Cone, Pos, Rot, Torus, extrude, Polygon, Circle, Rectangle, RectangleRounded

from . import bought, hw
from .builder import Builder
from .common import box_in, cyl_in, frame_of, insert_stack, torque, choose_len
from .geom import Frame, translate, rot_axis
from .model import PartDef, StackItem
from .printed import Design, block, cyl

X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])
DISC_T, DISC_D = 19.0, 610.0
BUCKET_H, BUCKET_DT, BUCKET_DB, BUCKET_WALL = 368.0, 302.0, 262.0, 2.5
CONCRETE_TOP = 330.0
FLANGE_BOT_Z = 90.0            # bottom floor flange's face (top), set on a first 70 mm pour of concrete
PIPE_OD, PIPE_ID, PIPE_L, THREAD_IN = 33.4, 26.6, 762.0, 17.5   # 1 in NPS x 30 in nipple; ~17.5 mm into each flange
FRAME_X, FRAME_Y = 100.0, 60.0  # extrusion centre lines
FRAME_TOP = 1160.0
FRAME_BOT = FRAME_TOP - 340.0
NECK_Z = 1268.0
NECK_T = 6.0


def F(o, n, x, sym=None):
    f = frame_of(o, n, x)
    f.symmetry_deg = sym
    return f


_parts: dict[str, PartDef] = {}


def _p(pid, *a, **k):
    if pid in _parts:
        return _parts[pid]
    p = PartDef(pid, *a, **k)
    _parts[pid] = p
    return p


# ------------------------------------------------------------------------------ bought / cut parts
def extrusion(L, role):
    """Misumi HFS5-2020 cut to L (6 mm slot, M5 end taps). Own frame: axis +Z, from z = 0 to L, square centred."""
    pid = f"hfs5-2020-{int(L)}-{role}"
    if pid in _parts:
        return _parts[pid]
    s = Pos(0, 0, L / 2) * Box(20, 20, L)
    for a in range(4):
        s = s - Rot(0, 0, 90 * a) * (Pos(9.0, 0, L / 2) * Box(4.2, 6.2, L + 1))
        s = s - Rot(0, 0, 90 * a) * (Pos(6.0, 0, L / 2) * Box(3.2, 11.0, L + 1))
    s = s - Pos(0, 0, L / 2) * Cylinder(2.1, L + 1)
    p = _p(pid, f"2020 aluminium extrusion, {L:g} mm ({role}), M5 tapped both ends", "bought", "metal_alu", s, mass_g=round(0.5 * L, 1),
           source="Misumi HFS5-2020 (0.5 kg/m, slot 6 mm, centre hole 4.2 mm: research/sourcing/20261025-hardware-sourcing.json)",
           meta={"kind": "extrusion", "length": L, "part_number": f"HFS5-2020-{int(L)}-TPW"})
    p.add("end_a", "End A (M5 tap)", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "bolt_pattern", role="structure", shape="positions", positions=[[0, 0]],
          fastener="M5", threaded=True)
    p.add("end_b", "End B (M5 tap)", F((0, 0, L), (0, 0, 1), (1, 0, 0)), "bolt_pattern", role="structure", shape="positions", positions=[[0, 0]],
          fastener="M5", threaded=True)
    return p


def slot_face(p: PartDef, fid, side, z, x_dir=(0, 0, 1)):
    """Add a T-slot face feature on an extrusion: side in '+x', '-x', '+y', '-y', at height z (own frame)."""
    n = {"+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0)}[side]
    o = (10 * n[0], 10 * n[1], z)
    if fid not in p.features:
        p.add(fid, f"T-slot {side} at {z:g} mm", F(o, n, x_dir), "bolt_pattern", role="structure", shape="positions", positions=[[0, 0]],
              fastener="M5", threaded=True, t_slot=True)
    return fid


def corner_bracket():
    """Cast 90 deg corner bracket, 20 series (Maker Store BRAC-90CAST): legs 20 x 20, 4 mm thick, one M5 hole
    per leg. Own frame: inner corner at the origin, leg A on the XY plane (z 0..4? no: leg A lies on z = 0
    face, +Z out of the leg), leg B on the XZ plane."""
    pid = "brac-90cast-20"
    if pid in _parts:
        return _parts[pid]
    t = 4.0
    a = Pos(10, 10, t / 2) * Box(20, 20, t)                 # leg A: on the face z = 0, along +X
    b = Pos(-t / 2, 10, 10) * Box(t, 20, 20)                # leg B: on the face x = 0, along +Z
    gus = Pos(2, 10, 2) * (Rot(0, 45, 0) * Box(5, 3, 5))
    s = a + b + gus - Pos(10, 10, t / 2) * Cylinder(2.75, t + 1) - Pos(-t / 2, 10, 10) * (Rot(0, 90, 0) * Cylinder(2.75, t + 1))
    p = _p(pid, "Cast 90 deg corner bracket, 20 series (one M5 per leg)", "bought", "metal_alu", s, mass_g=12.0,
           source="Maker Store USA BRAC-90CAST listing, $1.80 (research/sourcing/20261025-hardware-sourcing.json); dimensions nominal",
           meta={"part_number": "BRAC-90CAST", "price_usd": 1.80})
    p.add("leg_a", "Leg A (M5 hole)", F((10, 10, 0), (0, 0, -1), (1, 0, 0)), "bolt_pattern", role="component", shape="positions",
          positions=[[0, 0]], fastener="M5", threaded=False)
    p.add("leg_b", "Leg B (M5 hole)", F((0, 10, 10), (-1, 0, 0), (0, 0, 1)), "bolt_pattern", role="component", shape="positions",
          positions=[[0, 0]], fastener="M5", threaded=False)
    return p


def floor_flange():
    """1 in malleable iron floor flange (Anvil FIG 1190): 4 in OD, 4 x 1/4 in holes on a 3 in circle.
    Own frame: the mounting face at z = 0, +Z toward the pipe."""
    pid = "floor-flange-1in"
    if pid in _parts:
        return _parts[pid]
    s = Pos(0, 0, 4) * Cylinder(50.8, 8) + Pos(0, 0, 16) * Cylinder(25.0, 18) - Pos(0, 0, 16) * Cylinder(PIPE_OD / 2 - 0.5, 40)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        s = s - Pos(38.1 * math.cos(a), 38.1 * math.sin(a), 4) * Cylinder(3.6, 10)
    p = _p(pid, "1 in floor flange, malleable iron (Anvil FIG 1190)", "bought", "metal_steel", s, mass_g=560.0,
           source="Anvil FIG 1190: 4 in OD, 4 x 1/4 in holes on a 3 in bolt circle (research/sourcing); mass: assumption",
           meta={"part_number": "Anvil 0319900105 (FIG 1190, 1 in)"})
    p.add("face", "Mounting face (4 x 1/4 in)", F((0, 0, 0), (0, 0, -1), (1, 1, 0)), "bolt_pattern", role="component", shape="circle",
          spacing=76.2, count=4, fastener="1/4-20", threaded=False)
    p.features["face"].frame.symmetry_deg = 90
    p.add("socket", "1 in NPT socket", F((0, 0, 25.0), (0, 0, 1), (1, 0, 0)), "shaft", gender="bore", diameter=PIPE_OD, thread="1 in NPT")
    return p


def pipe_nipple():
    pid = "pipe-nipple-1x30"
    if pid in _parts:
        return _parts[pid]
    s = Pos(0, 0, PIPE_L / 2) * (Cylinder(PIPE_OD / 2, PIPE_L) - Cylinder(PIPE_ID / 2, PIPE_L + 1))
    p = _p(pid, "1 in x 30 in black steel pipe nipple (NPS, threaded both ends)", "bought", "metal_steel", s, mass_g=round(2.5 * 762, 0),
           source="ASME B36.10 1 in Sch 40: 33.4 mm OD, 2.50 kg/m", meta={"length": PIPE_L})
    p.add("end_a", "Bottom thread", F((0, 0, THREAD_IN), (0, 0, -1), (1, 0, 0)), "shaft", gender="shaft", diameter=PIPE_OD, thread="1 in NPT")
    p.add("end_b", "Top thread", F((0, 0, PIPE_L - THREAD_IN), (0, 0, 1), (1, 0, 0)), "shaft", gender="shaft", diameter=PIPE_OD, thread="1 in NPT")
    return p


def bolt_14_20(length_in):
    """1/4-20 hex bolt (inch); modelled with the metric helpers' shapes at 6.35 mm."""
    pid = f"hex-bolt-1-4-20x{length_in:g}in"
    if pid in _parts:
        return _parts[pid]
    L = length_in * 25.4
    s = Pos(0, 0, -2.0) * Cylinder(6.4, 4.0) + Pos(0, 0, L / 2) * Cylinder(3.0, L)
    p = _p(pid, f"1/4-20 x {length_in:g} in hex bolt, zinc", "hardware", "metal_steel", s, mass_g=round(0.25 * L, 1),
           meta={"kind": "screw", "diameter": 6.35, "length": L, "head_diameter": 11.1, "head_height": 4.0, "standard": "ASME B18.2.1"})
    return p


def nut_14_20():
    pid = "nylock-1-4-20"
    if pid in _parts:
        return _parts[pid]
    s = extrude(__import__("build123d").RegularPolygon(11.1 / math.sqrt(3), 6), 7.0) - Pos(0, 0, 3.5) * Cylinder(3.2, 8)
    return _p(pid, "1/4-20 nylon-insert lock nut, zinc", "hardware", "metal_steel", s, mass_g=3.0,
              meta={"kind": "nut", "diameter": 6.35, "length": 7.0, "outer": 11.1})


def wood_screw(n=8, length_in=1.25):
    pid = f"wood-screw-{n}x{length_in:g}in"
    if pid in _parts:
        return _parts[pid]
    L = length_in * 25.4
    s = Pos(0, 0, -1.5) * Cone(4.2, 2.1, 3.0) + Pos(0, 0, L / 2) * Cylinder(2.1, L)
    return _p(pid, f"#{n} x {length_in:g} in flat head wood screw", "hardware", "metal_steel", s, mass_g=2.0,
              meta={"kind": "screw", "diameter": 4.2, "length": L, "head_diameter": 8.4, "head_height": 3.0, "standard": "ASME B18.6.1"})


def tee_nut_m5():
    pid = "tee-nut-m5-hammer-in"
    if pid in _parts:
        return _parts[pid]
    s = Pos(0, 0, 0.75) * Cylinder(9.5, 1.5) + Pos(0, 0, 5) * Cylinder(3.5, 10) - Pos(0, 0, 5) * Cylinder(2.5, 12)
    return _p(pid, "M5 hammer-in tee nut (for plywood)", "hardware", "metal_steel", s, mass_g=3.0,
              meta={"kind": "nut", "diameter": 5.0, "length": 10.0, "outer": 19.0})


def box_part(pid, name, size, material, mass_g, source, holes=None, hole_d=3.0, color=None, meta=None):
    """A bought box-shaped component, own origin at the centre of its bottom face. holes: positions (x, y) on the
    bottom face of its mounting holes (standoff mounting)."""
    if pid in _parts:
        return _parts[pid]
    sx, sy, sz = size
    s = Pos(0, 0, sz / 2) * Box(sx, sy, sz)
    for (x, y) in holes or []:
        s = s - Pos(x, y, sz / 2) * Cylinder(hole_d / 2 + 0.1, sz + 1)
    p = _p(pid, name, "bought", color or material, s, mass_g=mass_g, source=source, meta=meta or {})
    p.add("bottom", "Bottom face", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "face")
    if holes:
        p.add("holes", "Mounting holes", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "bolt_pattern", role="component", shape="positions",
              positions=[list(h) for h in holes], fastener=f"M{hole_d:g}", threaded=False)
    return p


# ------------------------------------------------------------------------------ base and mast
def build_base(b: Builder):
    """Skirt, bucket, concrete, flanges, pipe. Root: the skirt disc on the floor."""
    disc = _p("jj-base-skirt", "Base skirt: 24 in round, 3/4 in birch plywood", "cut", "wood_ply",
              Pos(0, 0, DISC_T / 2) * Cylinder(DISC_D / 2, DISC_T), source="design; 3/4 in plywood (research: a 24 in birch round, Woodpeckers, ~$41.61 snippet)",
              meta={"material": "wood_ply"})
    disc.add("top", "Top face", F((0, 0, DISC_T), (0, 0, 1), (1, 0, 0)), "face")
    b.add_generic("skirt", disc, "base", np.eye(4))
    outer = Pos(0, 0, BUCKET_H / 2) * Cone(BUCKET_DB / 2, BUCKET_DT / 2, BUCKET_H)
    inner = Pos(0, 0, BUCKET_H / 2 + BUCKET_WALL) * Cone(BUCKET_DB / 2 - BUCKET_WALL, BUCKET_DT / 2 - BUCKET_WALL, BUCKET_H)
    rim = Pos(0, 0, BUCKET_H - 6) * Torus(BUCKET_DT / 2 + 2, 4)
    bk = _p("bucket-5gal", "5 US gal HDPE bucket (lid not used)", "bought", "bucket", outer - inner + rim, mass_g=900.0,
            source="typical 5 US gal bucket: 14.5 in tall, 11.9 in top, 10.3 in bottom (assumption: measure yours)")
    bk.add("bottom", "Bottom", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "bolt_pattern", role="component", shape="circle", spacing=180.0, count=4,
           fastener="1/4-20", threaded=False)
    bk.features["bottom"].frame.symmetry_deg = 90
    b.add_generic("bucket", bk, "base", translate(0, 0, DISC_T))
    disc.add("bucket_seat", "Bucket bolts (4 x 1/4-20 through the skirt)", F((0, 0, DISC_T), (0, 0, 1), (1, 0, 0)), "bolt_pattern", role="structure",
             shape="circle", spacing=180.0, count=4, fastener="1/4-20", threaded=False)
    disc.features["bucket_seat"].frame.symmetry_deg = 90
    t, note = 6.0, "assumption: snug through HDPE and plywood with fender washers; derated from 9 N.m (1/4-20 grade 5 dry)"
    b.mate("bucket_on_skirt", ("skirt", "bucket_seat"), ("bucket", "bottom"),
           [StackItem(bolt_14_20(1.25), -DISC_T, 1), StackItem(nut_14_20(), BUCKET_WALL, 1, t, note)], "base")
    # concrete: poured in two lifts, the flange set on the first
    r_fill = BUCKET_DB / 2 - BUCKET_WALL + (BUCKET_DT - BUCKET_DB) / 2 * (CONCRETE_TOP / BUCKET_H)
    conc = Pos(0, 0, (CONCRETE_TOP - BUCKET_WALL) / 2) * Cone(BUCKET_DB / 2 - BUCKET_WALL, r_fill, CONCRETE_TOP - BUCKET_WALL)
    conc = conc - Pos(0, 0, 200) * Cylinder(PIPE_OD / 2, 400) - Pos(0, 0, FLANGE_BOT_Z - DISC_T - BUCKET_WALL + 12) * Cylinder(51, 26)
    cc = _p("concrete-fill", "Concrete fill, about 2 x 50 lb bags of quick-setting concrete", "bought", "concrete", conc,
            mass_g=round(conc.volume / 1000 * 2.3, 0), source="volume from the bucket model x 2.3 g/cm3 (assumption)")
    cc.add("bottom", "Bottom", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "face")
    bk.add("floor", "Inside floor", F((0, 0, BUCKET_WALL), (0, 0, 1), (1, 0, 0)), "face")
    b.add_generic("concrete", cc, "base", translate(0, 0, DISC_T + BUCKET_WALL))
    b.mate("concrete_in_bucket", ("bucket", "floor"), ("concrete", "bottom"), [], "base")
    ff = floor_flange()
    mf = translate(0, 0, FLANGE_BOT_Z) @ np.diag([1, 1, 1, 1])
    cc.add("flange_seat", "Bottom flange bed (first lift)", F((0, 0, FLANGE_BOT_Z - DISC_T - BUCKET_WALL), (0, 0, 1), (1, 1, 0)), "face")
    b.add_generic("flange_bottom", ff, "base", mf)
    b.mate("flange_in_concrete", ("concrete", "flange_seat"), ("flange_bottom", "face"), [], "base")
    pp = pipe_nipple()
    mp = translate(0, 0, FLANGE_BOT_Z + 25.0 - THREAD_IN)
    b.add_generic("mast", pp, "base", mp)
    b.mate("mast_in_flange", ("flange_bottom", "socket"), ("mast", "end_a"), [], "base")
    top = FLANGE_BOT_Z + 25.0 - THREAD_IN + PIPE_L - THREAD_IN + 25.0     # top flange face
    mt = translate(0, 0, top) @ np.diag([1, -1, -1, 1])
    b.add_generic("flange_top", ff, "base", mt)
    b.mate("flange_on_mast", ("mast", "end_b"), ("flange_top", "socket"), [], "base")
    return top


# ------------------------------------------------------------------------------ torso B/C (2020)
def build_torso_2020(b: Builder, flange_top_z):
    plate_t = 6.0
    bp = b.design("jj-torso-base-plate", "Torso base plate, 6 mm 6061 aluminium, 220 x 140", (0, 0, FRAME_BOT - plate_t / 2),
                  material="metal_alu", color="metal_alu")
    bp.category = "cut"
    b.add_design("base_plate", "jj-torso-base-plate", "torso")
    bp.add(block((-110, 110), (-70, 70), (FRAME_BOT - plate_t, FRAME_BOT), 6))
    # flange to plate: 4 x 1/4-20 bolts, heads under the flange, nylocks on the plate
    fr = b.df("flange_top", "face").flipped()
    bp.clear_pattern("flange_seat", "Top flange (4 x 1/4-20)", fr, [], d=6, depth=plate_t, shape="circle", spacing=76.2, count=4, symmetry=90)
    b.mate("plate_on_flange", ("base_plate", "flange_seat"), ("flange_top", "face"),
           [StackItem(nut_14_20(), plate_t, 1, 8.0, "assumption: 1/4-20 grade 5 into a nylock on 6 mm aluminium, derated from 9 N.m"),
            StackItem(bolt_14_20(1.0), -8.0, 1)], "torso")
    bp.cut(cyl("z", (0, 0, FRAME_BOT - plate_t / 2), 14.0, plate_t + 2))      # cable pass from the mast
    up = extrusion(340, "upright")
    rx = extrusion(180, "rail-x")
    ry = extrusion(100, "rail-y")
    cb = corner_bracket()
    tnut = hw.tnut_2020(5)
    scr = hw.shcs(5, 10)
    tq, tq_note = torque(5, "tnut")
    tnut_stack = lambda: [StackItem(tnut, 0.0, -1), StackItem(scr, 4.0, -1, tq, tq_note)]
    corners = [(sx, sy) for sx in (-1, 1) for sy in (-1, 1)]
    for sx, sy in corners:
        iid = f"upright_{'r' if sx < 0 else 'l'}{'f' if sy < 0 else 'b'}"
        m = translate(sx * FRAME_X, sy * FRAME_Y, FRAME_BOT)
        b.add_generic(iid, up, "torso", m)
        # upright bottom end on the plate: M5 x 12 up through the plate into the end tap
        fid = f"{iid}_seat"
        bp.clear_pattern(fid, f"Upright {iid[-2:]} (M5 into the end tap)", F((sx * FRAME_X, sy * FRAME_Y, FRAME_BOT), (0, 0, 1), (1, 0, 0)),
                         [(0.0, 0.0)], d=5, depth=plate_t)
        b.mate(f"{iid}_on_plate", (iid, "end_a"), ("base_plate", fid),
               [StackItem(hw.shcs(5, 12), plate_t, -1, tq, "assumption: M5 into a 6061 end tap, derated from 5.5 N.m (8.8 into steel)")], "torso")
    # rails: along X at y = +-60 (top and bottom), along Y at x = +-100 (top and bottom)
    for level, zc in (("top", FRAME_TOP - 10.0), ("bot", FRAME_BOT + 10.0)):
        for sy in (-1, 1):
            iid = f"rail_x_{level}_{'f' if sy < 0 else 'b'}"
            m = translate(-90.0, sy * FRAME_Y, zc) @ rot_axis((0, 1, 0), 90)       # own +Z along +X
            b.add_generic(iid, rx, "torso", m)
        for sx in (-1, 1):
            iid = f"rail_y_{level}_{'r' if sx < 0 else 'l'}"
            m = translate(sx * FRAME_X, -50.0, zc) @ rot_axis((1, 0, 0), -90)      # own +Z along +Y
            b.add_generic(iid, ry, "torso", m)
    # each rail end: one corner bracket under (bottom) or under-side (top) the rail, into the upright
    nb = 0
    for level, zc in (("top", FRAME_TOP - 10.0), ("bot", FRAME_BOT + 10.0)):
        for sx, sy in corners:
            upr = f"upright_{'r' if sx < 0 else 'l'}{'f' if sy < 0 else 'b'}"
            for rail, along in ((f"rail_x_{level}_{'f' if sy < 0 else 'b'}", "x"), (f"rail_y_{level}_{'r' if sx < 0 else 'l'}", "y")):
                nb += 1
                bid = f"bracket_{nb:02d}"
                # bracket: leg A on the rail's inner face of its bottom (top level) or top (bottom level), leg B on the upright
                vz = -1 if level == "top" else 1                      # bracket sits below the top rails, above the bottom rails
                if along == "x":
                    face_up = -sx                                       # upright face toward the frame centre (along x)
                    corner = np.array([sx * FRAME_X + face_up * 10, sy * FRAME_Y, zc + vz * 10])
                    ax_a = np.array([face_up, 0, 0])                    # leg A runs along the rail
                    n_a = np.array([0, 0, vz])                          # leg A's face normal (away from the rail)
                else:
                    face_up = -sy
                    corner = np.array([sx * FRAME_X, sy * FRAME_Y + face_up * 10, zc + vz * 10])
                    ax_a = np.array([0, face_up, 0])
                    n_a = np.array([0, 0, vz])
                # bracket own: leg A along +X on z = 0 (face normal -Z into the rail), leg B along +Z on x = 0
                # map: own +X -> ax_a, own +Z -> -n_a ... leg A lies against the rail face: its own -Z points into the rail
                ex = ax_a
                ez = n_a                                                # own +Z away from the rail face (leg B grows that way)
                ey = np.cross(ez, ex)
                m = np.eye(4)
                m[:3, 0], m[:3, 1], m[:3, 2] = ex, ey, ez
                m[:3, 3] = corner - ey * 10                             # bracket width centred on the rail
                b.add_generic(bid, cb, "torso", m)
                # T-slot features on the rail and the upright at the hole positions
                ha = b.df(bid, "leg_a")
                hb = b.df(bid, "leg_b")
                b.generic[cb.id] = cb
                fa_ = _rail_feature(b, rail, f"{bid}_slot", ha)
                fb_ = _rail_feature(b, upr, f"{bid}_slot", hb)
                b.mate(f"{bid}_on_rail", (rail, fa_), (bid, "leg_a"), tnut_stack(), "torso")
                b.mate(f"{bid}_on_upright", (upr, fb_), (bid, "leg_b"), tnut_stack(), "torso")
    return bp


def _rail_feature(b: Builder, iid, fid, bracket_leg_frame: Frame):
    """Give extrusion instance `iid` a T-slot feature where a bracket leg's (or a foot's, a board's) hole lands:
    the leg's frame, flipped, in the extrusion's own frame. Every extrusion of one length shares one definition,
    which carries the T-slot features of all its instances (each instance uses its own)."""
    inst = b.instances[iid]
    part = b.generic[inst["part"]]
    fr = bracket_leg_frame.flipped().moved(np.linalg.inv(inst["M"]))
    if fid in part.features:
        old = part.features[fid].frame
        same = np.allclose(old.origin, fr.origin, atol=1e-6) and np.allclose(old.basis()[2], fr.basis()[2], atol=1e-9) and np.allclose(old.basis()[0], fr.basis()[0], atol=1e-9)
        if same:
            return fid
        fid = f"{fid}__{iid}"
        if fid in part.features:
            return fid
    part.add(fid, f"T-slot ({fid.split('__')[0].replace('_slot', '').replace('_', ' ')})", fr, "bolt_pattern", role="structure", shape="positions",
             positions=[[0, 0]], fastener="M5", threaded=True, t_slot=True)
    return fid


# ------------------------------------------------------------------------------ torso A (plywood)
def build_torso_ply(b: Builder, flange_top_z):
    """12 mm birch plywood box: side panels at x = +-100 (their centres), top board (the shoulder board) and
    bottom board, joined with #8 x 1-1/4 in wood screws; the top flange under the bottom board."""
    T = 12.0
    parts = {
        "bottom": ((-112, 112), (-70, 70), (FRAME_BOT - T, FRAME_BOT)),
        "top": ((-112, 112), (-70, 70), (FRAME_TOP - T, FRAME_TOP)),
        "side_r": ((-FRAME_X - 6, -FRAME_X + 6), (-70, 70), (FRAME_BOT, FRAME_TOP - T)),
        "side_l": ((FRAME_X - 6, FRAME_X + 6), (-70, 70), (FRAME_BOT, FRAME_TOP - T)),
    }
    ds = {}
    for k, (xr, yr, zr) in parts.items():
        c = ((xr[0] + xr[1]) / 2, (yr[0] + yr[1]) / 2, (zr[0] + zr[1]) / 2)
        d = b.design(f"jj-torso-a-{k.replace('_', '-')}", f"Torso A {k.replace('_', ' ')} (12 mm birch plywood)", c, material="wood_ply", color="wood_ply")
        d.category = "cut"
        d.add(block(xr, yr, zr, 0))
        b.add_design(f"ply_{k}", f"jj-torso-a-{k.replace('_', '-')}", "torso")
        ds[k] = d
    fr = b.df("flange_top", "face").flipped()
    ds["bottom"].clear_pattern("flange_seat", "Top flange (4 x 1/4-20)", fr, [], d=6, depth=T, shape="circle", spacing=76.2, count=4, symmetry=90)
    b.mate("board_on_flange", ("ply_bottom", "flange_seat"), ("flange_top", "face"),
           [StackItem(nut_14_20(), T, 1, 5.0, "assumption: 1/4-20 into a nylock through 12 mm plywood with a washer, snug"),
            StackItem(bolt_14_20(1.25), -8.0, 1)], "torso")
    ds["bottom"].cut(cyl("z", (0, 0, FRAME_BOT - T / 2), 14.0, T + 2))
    ws = wood_screw(8, 1.25)
    for k, sx in (("side_r", -1), ("side_l", 1)):
        for level, zf, n in (("bottom", FRAME_BOT, -1), ("top", FRAME_TOP - T, 1)):
            # screws from the board's outer face into the side panel's end grain: 3 per joint along y
            o = (sx * FRAME_X, 0.0, zf)
            frame_side = F(o, (0, 0, -n), (0, 1, 0))      # on the panel's end, normal out of the panel into the board
            ds[k].feature(f"{level}_joint", f"{level.title()} board joint", frame_side, "bolt_pattern", role="structure", shape="row",
                          spacing=100.0, count=3, fastener="#8 wood screw", threaded=True)
            ds[level].feature(f"{k}_joint", f"{k.replace('_', ' ').title()} panel joint (3 x #8)", frame_side.flipped(), "bolt_pattern", role="component",
                              shape="row", spacing=100.0, count=3, fastener="#8 wood screw", threaded=False)
            b.mate(f"{k}_{level}_joint", (f"ply_{k}", f"{level}_joint"), (f"ply_{level}", f"{k}_joint"),
                   [StackItem(ws, T, -1, 2.0, "assumption: #8 wood screw into plywood end grain, hand tight with a pilot hole")], "torso")
    return ds


# ------------------------------------------------------------------------------ neck, head
def build_neck(b: Builder, tier):
    """Two 2020 posts on the front and back top rails (B/C) or on the top board (A), a 6 mm neck plate on them."""
    post_l = NECK_Z - NECK_T - FRAME_TOP
    plate = b.design("jj-neck-plate", "Neck plate, 6 mm 6061 aluminium", (0, 0, NECK_Z - NECK_T / 2), material="metal_alu", color="metal_alu")
    plate.category = "cut"
    b.add_design("neck_plate", "jj-neck-plate", "torso")
    plate.add(block((-75, 75), (-75, 75), (NECK_Z - NECK_T, NECK_Z), 20))
    plate.cut(cyl("z", (0, 0, NECK_Z - NECK_T / 2), 16.0, NECK_T + 2))
    post = extrusion(post_l, "neck-post")
    cb = corner_bracket()
    tnut, scr = hw.tnut_2020(5), hw.shcs(5, 10)
    tq, tq_note = torque(5, "tnut")
    for sy in (-1, 1):
        pid = f"neck_post_{'f' if sy < 0 else 'b'}"
        b.add_generic(pid, post, "torso", translate(0, sy * FRAME_Y, FRAME_TOP))
        # post top: M5 x 12 down through the plate into the end tap
        fid = f"{pid}_seat"
        plate.clear_pattern(fid, f"Neck post {'front' if sy < 0 else 'back'} (M5 into the end tap)", F((0, sy * FRAME_Y, NECK_Z - NECK_T), (0, 0, -1), (1, 0, 0)),
                            [(0.0, 0.0)], d=5, depth=NECK_T)
        b.mate(f"neck_plate_on_{pid}", (pid, "end_b"), ("neck_plate", fid),
               [StackItem(hw.shcs(5, 12), NECK_T, -1, tq, "assumption: M5 into a 6061 end tap, derated from 5.5 N.m")], "neck")
        # post bottom: two brackets (on its +-x faces) onto the rail below
        rail = f"rail_x_top_{'f' if sy < 0 else 'b'}" if tier != "a" else None
        for k, sx in enumerate((-1, 1)):
            bid = f"{pid}_bracket_{k}"
            corner = np.array([sx * 10.0, sy * FRAME_Y, FRAME_TOP])
            ex, ez = np.array([sx, 0, 0]), np.array([0, 0, 1.0])
            ey = np.cross(ez, ex)
            m = np.eye(4)
            m[:3, 0], m[:3, 1], m[:3, 2] = ex, ey, ez
            m[:3, 3] = corner - ey * 10
            b.add_generic(bid, cb, "torso", m)
            if rail:
                fa_ = _rail_feature(b, rail, f"{bid}_slot", b.df(bid, "leg_a"))
                b.mate(f"{bid}_on_rail", (rail, fa_), (bid, "leg_a"), [StackItem(tnut, 0.0, -1), StackItem(scr, 4.0, -1, tq, tq_note)], "neck")
            else:
                top = b.designs["jj-torso-a-top"]
                fr = b.df(bid, "leg_a").flipped()
                # a hammer-in tee nut from under the 12 mm board, its barrel up; M5 x 16 down through the bracket leg
                top.clear_pattern(f"{bid}_seat", "Neck bracket (M5 hammer-in tee nut from below)", fr, [(0.0, 0.0)], d=6, depth=12.0, role="structure")
                b.mate(f"{bid}_on_board", ("ply_top", f"{bid}_seat"), (bid, "leg_a"),
                       [StackItem(tee_nut_m5(), -12.0, 1), StackItem(hw.shcs(5, 16), 4.0, -1, 3.0, "assumption: M5 into a hammer-in tee nut in plywood, snug")],
                       "neck")
            fb_ = _rail_feature(b, pid, f"{bid}_slot", b.df(bid, "leg_b"))
            b.mate(f"{bid}_on_post", (pid, fb_), (bid, "leg_b"), [StackItem(tnut, 0.0, -1), StackItem(scr, 4.0, -1, tq, tq_note)], "neck")
    return plate


def head_part():
    """The existing head (received CAD, inbox/20261024-facade.stp): its mesh is out/cad/head-facade-v61.glb; mass 2 kg (assumption, D7)."""
    p = _p("jj-head-assembly", "Head (existing): facade, eyes, jaw, neck yaw and nod", "vendor", "orange_shell", None, mass_g=2000.0,
           source="inbox/20261024-facade.stp (Facade v61) and 20261024-head-assembly.stp (v79); mass 2 kg is an assumption (D7)",
           vendor_file="out/cad/head-facade-v61.glb", meta={"glb": "out/cad/head-facade-v61.glb", "glb_offset_mm": [0, 0, 236.0], "glb_rot_z_deg": 180})
    p.add("base", "Neck base (4 x M5, pattern to match the head: data gap)", F((0, 0, 0), (0, 0, -1), (1, 0, 0), 90), "bolt_pattern", role="component",
          shape="rectangle", spacing=60.0, spacing_y=60.0, count=4, fastener="M5", threaded=False)
    return p


def build_head(b: Builder, plate: Design):
    hp = head_part()
    b.add_generic("head", hp, "head", translate(0, 0, NECK_Z))
    fr = b.df("head", "base").flipped()
    plate.clear_pattern("head_seat", "Head base (4 x M5, drill to match the head)", fr, [], d=5, depth=NECK_T, shape="rectangle", spacing=60.0,
                        spacing_y=60.0, count=4, symmetry=90)
    plate.features[-1] = (plate.features[-1][0], plate.features[-1][1], plate.features[-1][2], plate.features[-1][3],
                          {**plate.features[-1][4], "role": "structure"})
    tq, _ = torque(5, "nut")
    b.mate("head_on_neck_plate", ("neck_plate", "head_seat"), ("head", "base"),
           [StackItem(hw.washer(5), -NECK_T, -1), StackItem(hw.nut(5, True), -NECK_T - 1.0, -1, tq, "assumption: M5 nyloc under the 6 mm plate, snug"),
            StackItem(hw.shcs(5, 20), 8.0, -1)], "head", note="The head's base screw pattern is not in the received CAD: drill the plate to match (data gap).")


# ------------------------------------------------------------------------------ batteries and electronics
COMPONENTS = {
    # id: (name, size x y z mm, mass g, colour, source)
    "pack": ("Milwaukee M18 REDLITHIUM HIGH OUTPUT 12.0 Ah pack (owned)", (80, 150, 95), 1500, "battery_red", "envelope and mass: assumption (D7), measure yours"),
    "dock": ("M18 power-wheel adapter (dock)", (84, 90, 45), 120, "plastic_black", "nominal envelope (assumption)"),
    "ideal_diode": ("Ideal diode module, 40 A", (60, 45, 20), 40, "pcb_green", "nominal envelope (assumption)"),
    "monitor": ("Adafruit INA228 breakout", (25.4, 17.8, 3), 2, "pcb_blue", "Adafruit 5832: 1.0 x 0.7 in"),
    "lvc": ("XH-M609 low-voltage cutoff", (82, 58, 20), 40, "pcb_blue", "nominal envelope (assumption)"),
    "fuses": ("6-way ATC fuse block with negative bus", (110, 75, 30), 150, "plastic_black", "nominal envelope (assumption)"),
    "relay": ("Temco 24 V 40 A automotive relay", (28, 28, 28), 35, "plastic_black", "ISO mini relay envelope"),
    "drok": ("DROK 300 W buck converter", (65, 50, 25), 60, "metal_alu", "nominal envelope (assumption)"),
    "pololu": ("Pololu D24V50F5 / D36V50F5 5 V regulator", (33, 43, 10), 9, "pcb_green", "Pololu: 1.3 x 1.7 in"),
    "ekylin": ("EKYLIN 12 V 20 A buck converter (potted)", (92, 52, 30), 180, "metal_alu", "nominal envelope (assumption)"),
    "bus": ("Waveshare Bus Servo Adapter (A)", (42, 42, 12), 20, "pcb_blue", "nominal envelope (assumption)"),
    "pca": ("PCA9685 16-channel servo driver", (62.5, 25.4, 8), 9, "pcb_blue", "Adafruit 815: 2.5 x 1.0 in"),
    "pi5": ("Raspberry Pi 5 (torso computer)", (85, 56, 20), 46, "pcb_green", "Raspberry Pi 5 mechanical drawing"),
    "lrs": ("Mean Well LRS-350-24 supply", (215, 115, 30), 760, "metal_alu", "Mean Well LRS-350 datasheet: 215 x 115 x 30 mm"),
    "power_board": ("Custom power board (next revision)", (100, 80, 20), 60, "pcb_green", "placeholder envelope"),
    "fuse_inline": ("Inline ATC fuse holder (14 AWG leads)", (40, 15, 12), 12, "plastic_black", "nominal envelope (assumption)"),
}

LAYOUT = {
    # instance id: (component key, board slot (x, z) centre on the board's back face)
    "b": {"or_1": ("ideal_diode", (-55, 1105)), "or_2": ("ideal_diode", (5, 1105)), "monitor": ("monitor", (60, 1110)),
          "lvc": ("lvc", (-45, 1050)), "fuses": ("fuses", (35, 1040)), "relay": ("relay", (65, 1090)),
          "buck_head": ("drok", (-50, 990)), "buck_pi": ("pololu", (20, 980)), "buck_arm_r": ("ekylin", (-45, 930)),
          "buck_arm_l": ("ekylin", (45, 930)), "arm_r/bus_adapter": ("bus", (-55, 875)), "arm_l/bus_adapter": ("bus", (55, 875))},
    "c": {"or_1": ("ideal_diode", (-55, 1105)), "or_2": ("ideal_diode", (5, 1105)), "monitor": ("monitor", (60, 1110)),
          "lvc": ("lvc", (-45, 1050)), "fuses": ("fuses", (35, 1040)), "relay": ("relay", (65, 1090)),
          "buck_head": ("drok", (-50, 990)), "buck_pi": ("pololu", (20, 985)), "buck_arm_r": ("ekylin", (-45, 930)),
          "buck_arm_l": ("ekylin", (45, 930)), "arm_r/bus_adapter": ("bus", (-60, 870)), "arm_l/bus_adapter": ("bus", (60, 870)),
          "pi5": ("pi5", (0, 870)), "buck_pi5": ("drok", (55, 990)), "buck_hand_r": ("pololu", (-15, 1000)), "buck_hand_l": ("pololu", (-15, 950)),
          "or_3": ("ideal_diode", (60, 1150 - 85))},
    "a": {"lvc": ("lvc", (-45, 1080)), "buck_pi": ("drok", (40, 1085)), "buck_head": ("drok", (-45, 1010)), "buck_arm": ("drok", (40, 1010)),
          "arm_driver": ("pca", (0, 950)), "fuse_pi": ("fuse_inline", (-55, 900)), "fuse_head": ("fuse_inline", (0, 900)),
          "fuse_arm": ("fuse_inline", (55, 900))},
}


def component_part(key):
    name, (sx, sy, sz), mass, color, src = COMPONENTS[key]
    p = box_part(f"jj-body-{key}", name, (sx, sy, sz), color, mass, src, color=color, meta={"envelope": [sx, sy, sz]})
    if key == "dock" and "top" not in p.features:
        p.add("top", "Pack rail (the pack slides on from the back)", F((0, 30.0, sz), (0, 0, 1), (1, 0, 0)), "face")
        p.add("mount", "Mounting holes (2 x M4, positions from the dock in hand: data gap)", F((0, 0, 0), (0, 0, -1), (1, 0, 0), 180),
              "bolt_pattern", role="component", shape="row", spacing=60.0, count=2, fastener="M4", threaded=False)
    return p


def tray_part(key):
    """Printed tray for a component without a usable hole pattern: a 3 mm floor and 8 mm walls, two #4 wood
    screws into the board, a zip tie over the component. Own frame: origin at the centre of its floor's underside."""
    pid = f"jj-tray-{key}"
    if pid in _parts:
        return _parts[pid]
    name, (sx, sy, sz), *_ = COMPONENTS[key]
    w = 2.4
    s = Pos(0, 0, 4) * Box(sx + 2 * w, sy + 2 * w, 8) - Pos(0, 0, 3 + 4) * Box(sx + 0.6, sy + 0.6, 8.01)
    s = s - Pos(0, 0, 1.5) * Box(sx * 0.5, 6, 3.2)           # zip-tie slot under the floor
    for x in (-(sx / 2 - 6), sx / 2 - 6):
        s = s - Pos(x, 0, 1.5) * Cylinder(1.6, 3.2)
    p = _p(pid, f"Tray for the {name.split(' (')[0]}", "printed", "printed_cf", s, source="design",
           meta={"material": "petg", "print": "PETG, 0.2 mm layers, 3 walls, 20 % infill"})
    p.add("floor", "Tray floor (component sits here)", F((0, 0, 3), (0, 0, 1), (1, 0, 0)), "face")
    p.add("back", "Tray underside (2 x #4 wood screws)", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "bolt_pattern", role="component", shape="row",
          spacing=sx - 12, count=2, fastener="#4 wood screw", threaded=False)
    return p


def build_electronics(b: Builder, tier):
    """The electronics board (6 mm birch plywood, vertical, inside the front of the torso, facing back) with a
    tray per component; the M18 docks on the base (B/C: base plate; A: bottom board) with the packs behind."""
    T = 6.0
    yb = -FRAME_Y + 10.0                          # board's front face, against the front uprights' inner faces
    board = b.design(f"jj-electronics-board-{tier}", f"Electronics board, tier {tier.upper()}: 6 mm birch plywood 180 x 290", (0, yb + T / 2, 985),
                     material="wood_ply", color="wood_ply")
    board.category = "cut"
    b.add_design("ebd", f"jj-electronics-board-{tier}", "torso")
    board.add(block((-90, 90), (yb, yb + T), (FRAME_BOT + 16 + (12 if tier == "a" else 0), FRAME_TOP - 26), 6))
    ws4 = wood_screw(4, 0.5)
    if tier != "a":
        tnut, scr = hw.tnut_2020(5), hw.shcs(5, 12)
        tq, tq_note = torque(5, "tnut")
        for k, (sx, zc, rail) in enumerate(((-1, FRAME_TOP - 10, "upright_rf"), (1, FRAME_TOP - 10, "upright_lf"), (-1, FRAME_BOT + 30, "upright_rf"),
                                            (1, FRAME_BOT + 30, "upright_lf"))):
            # board corner tabs onto the front uprights' inner (+y) faces
            x = sx * FRAME_X
            board.add(block(sorted([sx * 86, sx * 112]), (yb, yb + T), (zc - 30, zc - 10), 0))
            fr = F((x, -FRAME_Y + 10, zc - 20), (0, 1, 0), (0, 0, 1))
            slot = _rail_feature(b, rail, f"ebd_{k}_slot", fr.flipped())
            board.clear_pattern(f"tab_{k}", "Board tab (M5 into a T-nut)", fr.flipped(), [(0.0, 0.0)], d=5, depth=T)
            b.mate(f"ebd_tab_{k}", (rail, slot), ("ebd", f"tab_{k}"), [StackItem(tnut, 0.0, -1), StackItem(scr, T, -1, tq, tq_note)], "electronics")
    else:
        for k, (sx, zc) in enumerate(((-1, FRAME_TOP - 40), (1, FRAME_TOP - 40), (-1, FRAME_BOT + 40), (1, FRAME_BOT + 40))):
            # cleats: #8 screws through the board's edge tabs into the side panels' inner faces
            board.add(block(sorted([sx * 86, sx * 94]), (yb, yb + 20), (zc - 10, zc + 10), 0))
            fr = F((sx * (FRAME_X - 6), yb + 10, zc), (-sx, 0, 0), (0, 0, 1))
            side = b.designs[f"jj-torso-a-side-{'r' if sx < 0 else 'l'}"]
            side.feature(f"ebd_{k}", "Electronics board cleat", fr, "bolt_pattern", role="structure", shape="positions", positions=[[0, 0]],
                         fastener="#8 wood screw", threaded=True)
            board.feature(f"cleat_{k}", "Board cleat (#8 wood screw)", fr.flipped(), "bolt_pattern", role="component", shape="positions",
                          positions=[[0, 0]], fastener="#8 wood screw", threaded=False)
            b.mate(f"ebd_cleat_{k}", (f"ply_side_{'r' if sx < 0 else 'l'}", f"ebd_{k}"), ("ebd", f"cleat_{k}"),
                   [StackItem(wood_screw(8, 1.25), 8.0, -1, 2.0, "assumption: hand tight with a pilot hole")], "electronics")
    # components on trays
    for iid, (key, (x, z)) in LAYOUT[tier].items():
        tr = tray_part(key)
        safe = iid.replace("/", "__")
        m_tray = F((x, yb + T, z), (0, 1, 0), (1, 0, 0)).matrix()      # tray +Z = board back face normal (+y)
        b.add_generic(f"tray__{safe}", tr, "torso", m_tray)
        fr = b.df(f"tray__{safe}", "back").flipped()
        board.feature(f"tray_{safe}", f"Tray for {iid} (2 x #4 wood screws)", fr, "bolt_pattern", role="structure", shape="row",
                      spacing=tr.features["back"].params["spacing"], count=2, fastener="#4 wood screw", threaded=True)
        b.mate(f"tray_{safe}_on_board", ("ebd", f"tray_{safe}"), (f"tray__{safe}", "back"),
               [StackItem(ws4, 3.0, -1, 0.5, "assumption: #4 x 1/2 in into 6 mm plywood, hand tight")], "electronics")
        body = component_part(key)
        b.add_generic(f"body__{safe}", body, "torso", m_tray @ translate(0, 0, 3.0))
        b.mate(f"body_{safe}_in_tray", (f"tray__{safe}", "floor"), (f"body__{safe}", "bottom"), [], "electronics",
               note="Held by a zip tie through the tray's floor slot.")
    # docks and packs on the base: printed cradle with the dock screwed down, the pack slid in from the back
    docks = {"b": ["dock_1", "dock_2"], "c": ["dock_1", "dock_2"], "a": ["dock"]}[tier]
    packs = {"b": ["pack_1", "pack_2"], "c": ["pack_1", "pack_2"], "a": ["pack"]}[tier]
    xs = [-45.0, 45.0] if len(docks) == 2 else [0.0]
    base_iid = "base_plate" if tier != "a" else "ply_bottom"
    base_d = b.designs["jj-torso-base-plate" if tier != "a" else "jj-torso-a-bottom"]
    z0 = FRAME_BOT
    for k, (d_id, p_id, x) in enumerate(zip(docks, packs, xs)):
        dk = component_part("dock")
        m = translate(x, -10.0, z0)
        b.add_generic(f"body__{d_id}", dk, "torso", m)
        from .common import nut_stack
        plate_t = 6.0 if tier != "a" else 12.0
        # the dock's 5 mm flange on the base: structure = the base (nylocks under it)
        base_frame = b.df(f"body__{d_id}", "mount").flipped()
        base_d.clear_pattern(f"{d_id}_seat", f"{d_id.replace('_', ' ')} (2 x M4, nylocks underneath)", base_frame, [], d=4, depth=plate_t,
                             shape="row", spacing=60.0, count=2, symmetry=180, role="structure")
        b.mate(f"{d_id}_on_base", (base_iid, f"{d_id}_seat"), (f"body__{d_id}", "mount"), nut_stack(4, plate_t, 5.0), "electronics",
               note="Dock screwed down through its own mounting holes: hole positions from the dock in hand (data gap).")
        pk = component_part("pack")
        mp = translate(x, -10.0 + 30.0, z0 + 45.0)
        b.add_generic(f"body__{p_id}", pk, "torso", mp)
        b.mate(f"{p_id}_on_{d_id}", (f"body__{d_id}", "top"), (f"body__{p_id}", "bottom"), [], "battery",
               note="Slide the pack onto the dock from the back hatch until it clicks.")
    # E-stop: 22 mm button in a yellow box on a printed bracket at the back of the shoulders
    es = box_part("jj-body-estop", "22 mm latching E-stop (NC) in a yellow box (Schneider XALK01H7 box)", (68, 68, 95), "plastic_yellow", 260,
                  "box: Schneider XALK01H7 (research/sourcing); button 22 mm (parts/local/estop-22mm-nc)", color="plastic_yellow")
    m_es = F((0, FRAME_Y + 12.0, FRAME_TOP - 50.0), (0, -1, 0), (1, 0, 0)).matrix()     # box bottom against the bracket, button facing back
    b.add_generic("body__estop", es, "torso", m_es)
    br = b.design(f"jj-estop-bracket-{'a' if tier == 'a' else 'bc'}", "E-stop bracket (on the back of the shoulders)", (0, FRAME_Y + 11.0, FRAME_TOP - 45.0),
                  material="petg", color="printed_cf")
    b.add_design("estop_bracket", f"jj-estop-bracket-{'a' if tier == 'a' else 'bc'}", "torso")
    br.add(block((-40, 40), (FRAME_Y + 10.0, FRAME_Y + 12.0), (FRAME_TOP - 90.0, FRAME_TOP), 4))
    br.add(block((-40, 40), (FRAME_Y - 10.0, FRAME_Y + 12.0), (FRAME_TOP, FRAME_TOP + 4.0), 4))
    fr = b.df("body__estop", "bottom").flipped()
    br.feature("estop_seat", "E-stop box (2 x M4 through the box floor, nylocks)", fr, "face")
    b.mate("estop_on_bracket", ("estop_bracket", "estop_seat"), ("body__estop", "bottom"), [], "electronics",
           note="Two M4 x 16 through the box floor and the bracket, nylocks inside the box.")
    if tier != "a":
        rail = "rail_x_top_b"
        tnut, scr = hw.tnut_2020(5), hw.shcs(5, 10)
        tq, tq_note = torque(5, "tnut")
        fr2 = F((0.0, FRAME_Y, FRAME_TOP), (0, 0, 1), (1, 0, 0))
        slot = _rail_feature(b, rail, "estop_bracket_slot", fr2.flipped())
        br.clear_pattern("on_rail", "Bracket on the back top rail (M5 into a T-nut)", fr2.flipped(), [(0.0, 0.0)], d=5, depth=4.0)
        b.mate("estop_bracket_on_rail", (rail, slot), ("estop_bracket", "on_rail"),
               [StackItem(tnut, 0.0, -1), StackItem(scr, 4.0, -1, tq, tq_note)], "electronics")
    else:
        top = b.designs["jj-torso-a-top"]
        fr2 = F((0.0, FRAME_Y, FRAME_TOP), (0, 0, 1), (1, 0, 0))
        top.feature("estop_bracket_seat", "E-stop bracket (#8 wood screw)", fr2, "bolt_pattern", role="structure", shape="positions", positions=[[0, 0]],
                    fastener="#8 wood screw", threaded=True)
        br.feature("on_board", "Bracket on the top board (#8 wood screw)", fr2.flipped(), "bolt_pattern", role="component", shape="positions",
                   positions=[[0, 0]], fastener="#8 wood screw", threaded=False)
        b.mate("estop_bracket_on_board", ("ply_top", "estop_bracket_seat"), ("estop_bracket", "on_board"),
               [StackItem(wood_screw(8, 0.75), 4.0, -1, 2.0, "assumption: hand tight with a pilot hole")], "electronics")
    return board
