"""J1 (shoulder-flex) gravity balancer for the tier B and C arms: a zero-length spring made from extension
springs and a cable.

    pin P on a lever on J1's hub face B, b below the axis (turns with the arm), a printed spool on a shoulder screw
    sheave A on a post on the shoulder housing's foot, a above the axis (fixed)
    the cable: tied at P, up over A, back over sheave B, down to an equaliser and two extension springs that hang
    on a 2020 column below the foot (outside the torso frame)

The springs' stretch is the P-A distance plus a constant set by the cable length, so with the cable cut to
leave the springs F0/k shorter than that distance they act as one zero-length spring between P and A: the
torque about J1 is k a b sin(angle), the same shape as gravity's on the arm, for either direction of swing.
Line plane x = hub face B + 10 mm. All in the arm's design frame (arm_bus.py).
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Axis, Cylinder, Pos, Torus

from . import bought, hw
from .common import frame_of, torque
from .geom import translate
from .model import PartDef, StackItem
from .printed import Design, block, cyl

X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])

SPRING_90CS = dict(pid="spring-century-90cs", name="Century Spring 90CS extension spring (0.625 in OD, 6.4 lb/in, 27 lbf max)",
                   od=15.9, wire=2.03, free=139.7, k=1.12, f0=22.2, travel=86.4, fmax=120.1, price=9.37,
                   source="Century Spring 90CS listing: 0.625 in OD, 0.080 in wire, 5.5 in free length, 6.4 lb/in, 5 lb initial tension, "
                          "3.4 in max deflection, 27 lbf max (research/sourcing/20261025-hardware-sourcing.json)")
SHEAVE_R = 6.5          # line radius on a sheave (groove bottom)
HOOK = 12.0             # hook loop diameter (assumption: the listing gives the free length over the hooks)
_parts: dict[str, PartDef] = {}


def F(o, n, x, sym=None):
    f = frame_of(o, n, x)
    f.symmetry_deg = sym
    return f


def spring_part(extension):
    """An extension spring drawn stretched by `extension` mm. Own frame: the bottom of the bottom hook at the
    origin, +Z up; both hook loops lie in the XZ plane (their holes along Y)."""
    s = SPRING_90CS
    pid = s["pid"]
    if pid in _parts:
        return _parts[pid]
    body_free = s["free"] - 2 * HOOK
    L = body_free + extension
    r = (s["od"] - s["wire"]) / 2
    n = int(body_free / s["wire"])
    body = None
    for k in range(n):
        ring = Pos(0, 0, HOOK + k * L / (n - 1)) * Torus(r, s["wire"] / 2)
        body = ring if body is None else body + ring
    loop = Torus(HOOK / 2, s["wire"] / 2).rotate(Axis.X, 90)
    body = body + Pos(0, 0, HOOK / 2) * loop + Pos(0, 0, HOOK + L + HOOK / 2) * loop
    p = PartDef(pid, s["name"], "bought", "metal_steel", body, mass_g=32.0, source=s["source"],
                meta={**{k: v for k, v in s.items() if k not in ("pid", "name", "source")}, "drawn_extension_mm": round(extension, 1),
                      "part_number": "90CS", "price_usd": s["price"]})
    # the pin goes through the bottom loop along -Y; the top loop hangs in the equaliser's hole
    p.add("hook_a_pin", "Bottom hook (on its pin)", F((0, -s["wire"] / 2, HOOK / 2), (0, -1, 0), (0, 0, 1)), "anchor")
    p.add("hook_b", "Top hook", F((0, 0, 2 * HOOK + L), (0, 0, 1), (1, 0, 0)), "anchor")
    _parts[pid] = p
    return p


def sheave_part():
    """Printed cable sheave around a 624-2RS bearing: Ø22 flanges, groove bottom Ø13. Own frame: origin on the axis
    at its face toward the axle's head, +Z through it (6 mm)."""
    pid = "jj-cable-sheave-22"
    if pid in _parts:
        return _parts[pid]
    d = Design(pid, "Cable sheave for a 624 bearing (printed)", "petg", "printed", "printed_cf")
    d.add(Pos(0, 0, 3) * Cylinder(11.0, 6.0))
    d.cut(Pos(0, 0, 3) * (Cylinder(12.0, 3.0) - Cylinder(SHEAVE_R + 1.0, 3.0)))
    d.cut(Pos(0, 0, 3) * Cylinder(6.5 + 0.05, 6.2))
    d.feature("seat", "Bearing seat (624, pressed in from the far face)", F((0, 0, 0.5), (0, 0, 1), (1, 0, 0)), "bearing_seat", od=13.0,
              depth=5.0, retention="press")
    p = d.part((0, 0, 0))
    _parts[pid] = p
    return p


def dyneema_part(length):
    pid = f"dyneema-2mm-{int(length)}"
    if pid in _parts:
        return _parts[pid]
    p = PartDef(pid, f"2 mm Dyneema (UHMWPE) braided cord, {length:g} mm cut", "bought", "rubber", Pos(0, 0, 15.0) * Cylinder(1.0, 30.0),
                mass_g=round(length * 0.0025, 1),
                source="2 mm SK78 Dyneema single braid, about 250 kgf break (typical listing; assumption until bought)",
                meta={"length": length, "kind": "consumable"})
    p.add("end", "Cord end (knotted to the equaliser)", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "anchor")
    _parts[pid] = p
    return p


def j1_balancer(b, h1: Design, xb, A, B):
    """Add the balancer to an ArmBus builder: lever and spool (yoke link); post, sheaves, column, anchor, springs,
    equaliser and cord (torso link)."""
    xl = xb + 10.0                       # cord plane
    k, f0 = 2 * SPRING_90CS["k"], 2 * SPRING_90CS["f0"]
    ext = A + B - f0 / k                 # each spring's stretch with the arm hanging: the cord is cut for this
    assert 0 < ext <= SPRING_90CS["travel"], ext
    ya, yb = -SHEAVE_R, -37.5            # sheave centres (y): the cord goes forward from A to B, then down at y = -44
    ys = yb - SHEAVE_R
    foot_top = -17.0
    t4, n4 = torque(4, "insert")
    # -------- lever on hub face B, spool on a shoulder screw b below the axis (yoke link)
    lv = b.design("jj-arm-j1-bal-lever", "J1 balancer lever (on hub face B)", (xb + 3, 0, -B / 2))
    b.add_design("j1_lever", "jj-arm-j1-bal-lever", "yoke")
    lv.add(cyl("x", (xb + 3, 0, 0), 16.0, 6.0))
    lv.add(block((xb, xb + 6), (-7, 7), (-B - 9, 0), 3))
    lv.add(cyl("x", (xb + 3, 0, -B), 8.0, 6.0))
    lv.cut(cyl("x", (xb + 3, 0, 0), 7.0, 8.0))
    b.screw_into_generic("j1_lever_on_hub", "j1_hub", "face_b", lv, "j1_lever", "on_hub", "Balancer lever on J1 hub face B (4 x M3)", 6.0, "balancer")
    sp_d = b.design("jj-arm-j1-bal-spool", "J1 balancer cord spool (on a shoulder screw)", (xb + 10, 0, -B))
    b.add_design("j1_spool", "jj-arm-j1-bal-spool", "yoke")
    sp_d.add(cyl("x", (xb + 10, 0, -B), 5.0, 8.0) + cyl("x", (xb + 6.75, 0, -B), 7.0, 1.5) + cyl("x", (xb + 13.25, 0, -B), 7.0, 1.5))
    sp_d.cut(cyl("x", (xb + 10, 0, -B), 2.6, 9.0))
    pin = F((xb + 6, 0, -B), X, (0, 1, 0))
    b.screw_design_pair("j1_spool_on_lever", lv, "j1_lever", "pin", sp_d, "j1_spool", "on_pin", pin, [], 8.0, "balancer", d=4,
                        name_a="Cord pin (M4 insert)", name_b="Spool on the pin", shape="circle", spacing=0.0, count=1)
    b.mates[-1]["stack"] = [StackItem(hw.insert(4), 0.0, -1), StackItem(hw.shoulder_bolt(5, 8), 8.0, -1, t4, n4)]
    # -------- post on the foot (torso link): two sheaves on M4 axles along X
    post = b.design("jj-arm-j1-bal-post", "J1 balancer post (on the shoulder housing's foot)", (xl + 7, -20, A / 2))
    b.add_design("j1_post", "jj-arm-j1-bal-post", "torso")
    post.add(block((xl + 4, xl + 10), (yb - 10, 10), (foot_top, A + 12), 3))
    post.add(block((xl + 4, xl + 22), (-8, 10), (foot_top, foot_top + 6), 2))
    b.screw_design_pair("j1_post_on_foot", h1, "j1_housing", "post_seat", post, "j1_post", "on_foot", F((xl + 13, 1.0, foot_top), Z, (0, 1, 0)),
                        [], 6.0, "balancer", d=4, name_a="Balancer post seat (2 x M4 inserts)", name_b="Post on the foot",
                        shape="row", spacing=12.0, count=2, symmetry=180)
    sh = sheave_part()
    brg = bought.bearing("624-2rs")
    for nm, yc in (("a", ya), ("b", yb)):
        m = F((xl - 3, yc, A), X, (0, 1, 0)).matrix()             # sheave from x = xl - 3 to xl + 3
        sid = b.add_generic(f"j1_sheave_{nm}", sh, "torso", m)
        bid = b.add_generic(f"j1_sheave_{nm}_bearing", brg, "torso", m @ translate(0, 0, 5.5) @ np.diag([1, -1, -1, 1]))
        b.mate(f"j1_sheave_{nm}_bearing", (sid, "seat"), (bid, "od_face_top"), [], "balancer")
        sh_axle = b.df(sid, "seat")
        af = F((xl + 4, yc, A), -X, (0, 1, 0))                     # post face, normal toward the sheave
        post.insert_pattern(f"axle_{nm}", f"Sheave {nm.upper()} axle (M4 insert)", af, [(0.0, 0.0)], 4, extra_depth=1.6)
        # washer, sheave (6), washer, M4 x 16 from the far side: clamps the bearing's inner ring
        b.mate(f"j1_sheave_{nm}_axle", ("j1_post", f"axle_{nm}"), (bid, "od_face"),
               [StackItem(hw.insert(4), 0.0, -1), StackItem(hw.washer(4), 0.0, 1), StackItem(hw.washer(4), 6.3, 1),
                StackItem(hw.shcs(4, 16), 7.1, -1, t4, n4)], "balancer", gap=1.5)
    # -------- column (2020, 190 mm) hanging from an extension of the foot
    col_x, col_y = xl + 15.0, -80.0
    h1.add(block((col_x - 12, col_x + 12), (col_y - 12, -32.0), (-25.0, -17.0), 4))
    from .torso import extrusion
    col = extrusion(190, "balancer-column")
    b.add_generic("j1_column", col, "torso", translate(col_x, col_y, -25.0) @ np.diag([1, -1, -1, 1]))
    h1.clear_pattern("column_seat", "Balancer column (M5 into its end tap)", b.df("j1_column", "end_a").flipped(), [(0.0, 0.0)], d=5, depth=8.0)
    b.mate("j1_column_on_foot", ("j1_column", "end_a"), ("j1_housing", "column_seat"),
           [StackItem(hw.shcs(5, 12), 8.0, -1, *torque(5, "tnut"))], "balancer")
    # -------- springs, equaliser, anchor
    sp = spring_part(ext)
    L = sp.features["hook_b"].frame.origin[2]
    z_top = A - 30.0                                           # the equaliser hangs 30 mm below the sheaves
    z_bot = z_top - L                                          # bottom of the bottom hooks
    zbot_col = -25.0 - 190.0
    an = b.design("jj-arm-j1-bal-anchor", "J1 balancer spring anchor (on the column)", (xl, ys - 10, z_bot))
    b.add_design("j1_anchor", "jj-arm-j1-bal-anchor", "torso")
    an.add(block((col_x - 10, col_x + 10), (col_y - 10, col_y + 10), (zbot_col - 6, zbot_col), 3))
    an.add(block((xl - 20, col_x + 10), (col_y + 10 - 2, ys - 6), (zbot_col - 6, z_bot + 14), 3))
    an.clear_pattern("on_column", "Anchor on the column (M5 into its end tap)", b.df("j1_column", "end_b").flipped(), [(0.0, 0.0)], d=5, depth=6.0)
    b.mate("j1_anchor_on_column", ("j1_column", "end_b"), ("j1_anchor", "on_column"), [StackItem(hw.shcs(5, 12), 6.0, -1, *torque(5, "tnut"))],
           "balancer")
    eq = b.design("jj-arm-j1-bal-equalizer", "J1 balancer equaliser (cord to two springs)", (xl, ys, z_top + 6))
    b.add_design("j1_equalizer", "jj-arm-j1-bal-equalizer", "torso")
    eq.add(block((xl - 20, xl + 20), (ys - 3, ys + 3), (z_top, z_top + 12), 2))
    for kk, dx in enumerate((-12.0, 12.0)):
        sid = b.add_generic(f"j1_spring_{kk}", sp, "torso", translate(xl + dx, ys, z_bot))
        hp = b.df(sid, "hook_a_pin")                           # on the loop's -Y side, normal -Y
        web = F((xl + dx, ys - 6, hp.origin[2]), Y, (0, 0, 1))
        an.insert_pattern(f"pin_{kk}", f"Spring {kk + 1} pin (M4 insert)", web, [(0.0, 0.0)], 4)
        b.mate(f"j1_spring_{kk}_on_pin", ("j1_anchor", f"pin_{kk}"), (sid, "hook_a_pin"),
               [StackItem(hw.insert(4), 0.0, -1), StackItem(hw.shcs(4, 16), 8.0, -1, t4, n4)], "balancer", gap=6.0 - SPRING_90CS["wire"] / 2)
        eq.feature(f"hook_{kk}", f"Spring {kk + 1} hook hole", b.df(sid, "hook_b").flipped(), "anchor")
        b.mate(f"j1_spring_{kk}_in_equalizer", ("j1_equalizer", f"hook_{kk}"), (sid, "hook_b"), [], "balancer")
    run = (A + B) + (yb - ya) + 30.0 + math.pi * SHEAVE_R * 1.5
    cord = dyneema_part(round(run + 150, -1))
    b.add_generic("j1_cord", cord, "torso", translate(xl, ys, z_top + 12))
    eq.feature("cord", "Cord eye", F((xl, ys, z_top + 12), Z, (1, 0, 0)), "anchor")
    b.mate("j1_cord_on_equalizer", ("j1_equalizer", "cord"), ("j1_cord", "end"), [], "balancer",
           note=(f"Tie the cord round the spool on the lever, take it up over sheave A and back over sheave B, down to the equaliser; "
                 f"cut it so each spring is stretched {ext:.0f} mm with the arm hanging: that makes the balancer exact."))
    return dict(ext=ext, k=k, A=A, B=B, xl=xl)
