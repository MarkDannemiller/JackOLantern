"""Joint library shared by the arm and hand builders: generic printed parts (hubs, caps, pulleys, discs),
bought parts that belong to joints (dowels, belts, torsion springs), and the builder mixin that lays out
a belt joint, a direct (coaxial-servo) joint and the servo cradles.

Direct joint: the hub turns in two 6806 bearings back to back in the housing; a disc screwed to the servo
horn is pulled onto the upper bearing's inner ring by three M3 x 30 through the hub wall. Laid out in a
joint frame whose +Z points from the hub toward the servo; the output is the hub flange's underside.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Box, Cylinder, Pos, Rot, Torus, Polygon, extrude

from . import bought, hw
from . import joints as JT
from .common import box_in, cyl_in, frame_of, horn_stack, insert_stack, torque, choose_len
from .export import to_location
from .geom import Frame, translate
from .model import PartDef, StackItem
from .printed import Design, block, cyl

DISC_T = 8.0
DIAG = (1.0, 1.0, 0.0)
Z = np.array([0, 0, 1.0])
STAGES = {
    "j1": dict(z_driven=60, z_driver=20, belt=240),
    "j2": dict(z_driven=60, z_driver=20, belt=240),
    "j4": dict(z_driven=48, z_driver=16, belt=210),
}
for _s in STAGES.values():
    _s["c"] = JT.center_for(JT.gt3_pd(_s["z_driver"]), JT.gt3_pd(_s["z_driven"]), _s["belt"])
    _s["ratio"] = _s["z_driven"] / _s["z_driver"]

TORSION = dict(pid="spring-to5220rcs", name="Century Spring TO-5220RCS torsion spring (180 deg legs, right hand wind)",
               od=26.37, id=21.54, wire=2.41, body=19.3, legs=76.2, rate_nmm_deg=9.83, max_nmm=2078.83, max_deg=211,
               price_usd=6.43, source="Century Spring TO-5220RCS listing (research/sourcing/20261025-hardware-sourcing.json)")


def F(o, n, x):
    return frame_of(o, n, x)


def belt_cavity(bf, r1, r2, c, hz):
    """Convex hull of the driven (r1, at the origin) and driver (r2, at +c on x) circles, in belt frame bf, z in hz."""
    beta = math.asin((r1 - r2) / c) if c > abs(r1 - r2) else 0.0
    from build123d import Cylinder as _C
    hull = Pos(0, 0, (hz[0] + hz[1]) / 2) * _C(r1, hz[1] - hz[0])
    hull = hull + Pos(c, 0, (hz[0] + hz[1]) / 2) * _C(r2, hz[1] - hz[0])
    sa = math.sin(beta)
    ca = math.cos(beta)
    quad = [(-r1 * sa, r1 * ca), (c - r2 * sa, r2 * ca), (c - r2 * sa, -r2 * ca), (-r1 * sa, -r1 * ca)]
    hull = hull + Pos(0, 0, hz[0]) * extrude(Polygon(*quad, align=None), hz[1] - hz[0])
    return to_location(bf) * hull


# ---------------------------------------------------------------------------- generic parts
_generic: dict[str, PartDef] = {}


def hub_part(teeth):
    """Belt-joint hub: journals for two 6806, GT3 pulley between them, 14 mm bore, M3 inserts on both faces.
    Own frame = joint frame (axis +Z, origin at the hub mid-plane)."""
    pid = f"jj-hub-{teeth}t-gt3"
    if pid in _generic:
        return _generic[pid]
    d = Design(pid, f"Belt-joint hub with {teeth}T GT3 pulley (hollow, 14 mm bore)", "petg-cf", "printed", "printed_cf")
    d.add(JT.hub_shape(teeth))
    h = JT.HUB_LEN / 2
    for fid, z, n in (("face_a", -h, -1), ("face_b", h, 1)):
        d.insert_pattern(fid, f"Hub {fid.replace('_', ' ')}", F((0, 0, z), (0, 0, n), DIAG), [], 3, shape="circle",
                         spacing=JT.HUB_INSERT_BCD, count=4, symmetry=90)
    d.feature("journal_1", "Journal in bearing 1", F((0, 0, -JT.HALF), (0, 0, 1), (1, 0, 0)), "shaft", gender="shaft", diameter=30.0)
    d.feature("journal_2", "Journal in bearing 2", F((0, 0, JT.HALF), (0, 0, -1), (1, 0, 0)), "shaft", gender="shaft", diameter=30.0)
    d.meta["teeth"] = teeth
    p = d.part((0, 0, 0))
    _generic[pid] = p
    return p


def cap_part(teeth):
    """Bolt-on bearing cap of a belt joint (bearing 2 seat and lip). Own frame = joint frame."""
    pid = f"jj-cap-{teeth}t"
    if pid in _generic:
        return _generic[pid]
    d = Design(pid, f"Belt-joint bearing cap ({teeth}T housing)", "petg-cf", "printed", "printed_cf")
    d.add(JT.cap_shape(teeth))
    d.feature("seat", "Bearing 2 seat", F((0, 0, JT.GAP + 2.0), (0, 0, 1), (1, 0, 0)), "bearing_seat", od=42.0, depth=7.0,
              retention="shoulder")
    d.feature("to_drum", "Cap on the drum (4 x M3)", F((0, 0, JT.GAP), (0, 0, -1), DIAG, ), "bolt_pattern", role="component",
              shape="circle", spacing=2 * JT.cap_screw_r(teeth), count=4, fastener="M3", threaded=False)
    p = d.part((0, 0, 0))
    p.features["to_drum"].frame.symmetry_deg = 90
    _generic[pid] = p
    return p


def driver_pulley_part(teeth):
    """Driver: GT3 pulley screwed to the STS horn (4 x M3 x 14 through it), 5 mm dowel pressed into its outer
    end. Own frame: origin on the horn-side face, +Z away from the horn; belt plane at z = 5.75."""
    pid = f"jj-pulley-{teeth}t-gt3-horn"
    if pid in _generic:
        return _generic[pid]
    d = Design(pid, f"Driver pulley, {teeth}T GT3, on the STS horn", "petg-cf", "printed", "printed_cf")
    od = JT.gt3_od(teeth)
    d.add(Pos(0, 0, 5.75) * JT.gt3_pulley(teeth, flange_od=od + 3))
    d.cut(Pos(0, 0, 1.5) * Cylinder(3.0, 3.2))             # horn centre screw head
    d.clear_pattern("horn", "On the servo horn (4 x M3 x 14)", F((0, 0, 0), (0, 0, -1), DIAG), [], d=3, depth=11.5,
                    shape="circle", spacing=14.0, count=4, symmetry=90)
    d.cut(Pos(0, 0, 11.5 - 3) * Cylinder(2.45, 6.1))      # dowel: 5 mm press fit, 6 deep from the outer face
    d.feature("dowel", "Dowel bore", F((0, 0, 11.5), (0, 0, 1), (1, 0, 0)), "shaft", gender="bore", diameter=5.0)
    d.feature("belt", "Belt plane", F((0, 0, 5.75), (0, 0, 1), (1, 0, 0)), "belt", teeth=teeth, profile="GT3", pitch=3.0)
    d.meta["teeth"] = teeth
    p = d.part((0, 0, 0))
    _generic[pid] = p
    return p


def dowel_part():
    pid = "dowel-5x16"
    if pid in _generic:
        return _generic[pid]
    p = PartDef(pid, "5 mm x 16 mm hardened steel dowel pin (ISO 8734)", "bought", "metal_steel", Pos(0, 0, 8) * Cylinder(2.5, 16),
                mass_g=2.4, source="ISO 8734 m6 dowel pin", meta={"kind": "pin", "diameter": 5.0, "length": 16.0})
    p.add("end", "Pressed end", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "shaft", gender="shaft", diameter=5.0)
    _generic[pid] = p
    return p


def twist_hub_part():
    """Twist hub: journal through two 6806 (back to back), shoulder on the lower inner ring, flange with M3
    inserts underneath (the output face), three M3 x 30 up through its wall into the horn disc.
    Own frame: origin on the axis at the lip mid-plane, +Z up."""
    pid = "jj-twist-hub"
    if pid in _generic:
        return _generic[pid]
    d = Design(pid, "Twist-joint hub (6806 pair)", "petg-cf", "printed", "printed_cf")
    s = Cylinder(15.0, 17.0)                                       # journal z -8.5 .. 8.5
    s = s + Pos(0, 0, -10.0) * Cylinder(16.5, 3.0)                 # shoulder on the lower inner ring, z -11.5 .. -8.5
    s = s + Pos(0, 0, -15.0) * Cylinder(26.0, 7.0)                 # flange z -18.5 .. -11.5
    s = s - Cylinder(7.0, 60)
    d.add(s)
    for k in range(3):                                             # 3 x M3 x 30 up through the wall, counterbored 4 deep
        a = math.pi / 2 + k * 2 * math.pi / 3
        x, y = 11.0 * math.cos(a), 11.0 * math.sin(a)
        d.cut(Pos(x, y, 0) * Cylinder(1.7, 40))
        d.cut(Pos(x, y, -18.5 + 2.0) * Cylinder(2.9, 4.02))
    d.insert_pattern("out", "Output face (under the flange)", F((0, 0, -18.5), (0, 0, -1), (1, 0, 0)), [], 3, shape="circle",
                     spacing=40.0, count=4, symmetry=90)
    d.feature("journal", "Journal in the lower bearing", F((0, 0, -8.5), (0, 0, 1), (1, 0, 0)), "shaft", gender="shaft", diameter=30.0)
    d.feature("top", "Top face (under the horn disc)", F((0, 0, 8.5), (0, 0, 1), (0, 1, 0)), "bolt_pattern", role="component",
              shape="circle", spacing=22.0, count=3, fastener="M3", threaded=False)
    p = d.part((0, 0, 0))
    p.features["top"].frame.symmetry_deg = 120
    _generic[pid] = p
    return p


def twist_disc_part():
    """Horn disc (8 mm): screwed to the STS horn from below (4 x M3 x 6, heads counterbored 4.5), pulled onto
    the upper bearing's inner ring by the hub's three M3 x 30 (inserts). Own frame: origin on the bottom face,
    +Z up toward the horn."""
    pid = "jj-twist-horn-disc"
    if pid in _generic:
        return _generic[pid]
    d = Design(pid, "Twist-joint horn disc", "petg-cf", "printed", "printed_cf")
    d.add(Pos(0, 0, DISC_T / 2) * Cylinder(16.5, DISC_T))
    d.cut(Pos(0, 0, DISC_T / 2) * Cylinder(2.6, DISC_T + 1))
    d.clear_pattern("horn", "On the servo horn (4 x M3 x 6)", F((0, 0, DISC_T), (0, 0, 1), DIAG), [], d=3, depth=DISC_T,
                    shape="circle", spacing=14.0, count=4, symmetry=90)
    for k in range(4):            # counterbore the horn screw heads from below
        a = math.pi / 4 + k * math.pi / 2
        d.cut(Pos(7 * math.cos(a), 7 * math.sin(a), 2.25) * Cylinder(2.9, 4.52))
    d.insert_pattern("hub", "Hub screws (3 x M3 inserts)", F((0, 0, 0), (0, 0, -1), (0, 1, 0)), [], 3, shape="circle",
                     spacing=22.0, count=3, symmetry=120)
    p = d.part((0, 0, 0))
    _generic[pid] = p
    return p


def torsion_spring_part():
    t = TORSION
    pid = t["pid"]
    if pid in _generic:
        return _generic[pid]
    r = (t["od"] - t["wire"]) / 2
    turns = int(t["body"] / t["wire"])
    body = None
    for k in range(turns):
        ring = Pos(0, 0, t["wire"] / 2 + k * (t["body"] - t["wire"]) / (turns - 1)) * Torus(r, t["wire"] / 2)
        body = ring if body is None else body + ring
    leg = 40.0                    # legs cut to 40 mm from the 76 mm supplied
    la = Pos(leg / 2, r, t["wire"] / 2) * Box(leg, t["wire"], t["wire"])
    lb = Pos(leg / 2, r, t["body"] - t["wire"] / 2) * Box(leg, t["wire"], t["wire"])
    mass = math.pi * 2 * r * turns * math.pi * (t["wire"] / 2) ** 2 * 7.85e-3 + 2 * leg * t["wire"] ** 2 * 7.85e-3
    p = PartDef(pid, t["name"], "bought", "metal_steel", body + la + lb, mass_g=round(mass, 1), source=t["source"],
                meta={**{k: v for k, v in t.items() if k not in ("pid", "name")}, "legs_cut_to_mm": leg})
    p.add("bore_a", "Arbor end A", F((0, 0, 0), (0, 0, -1), (1, 0, 0)), "shaft", gender="bore", diameter=t["id"])
    _generic[pid] = p
    return p


def gt3_belt(length, width, d1, d2, c):
    """Closed GT3 belt around two pulleys: own frame at the driver axis on the belt's lower edge, +X toward the
    driven pulley, +Z across the belt width."""
    pid = f"gt3-belt-{int(round(length))}-{width:g}mm"
    if pid in _generic:
        return _generic[pid]
    band = bought.gt2_belt_simple(length, width, d1, d2, c).solid
    p = PartDef(pid, f"GT3 (3 mm pitch) closed belt, {length:g} mm ({int(round(length / 3))} teeth), {width:g} mm wide", "bought", "rubber",
                band, mass_g=round(length * width * 2.4 * 1.25e-3, 1),
                meta={"length": length, "width": width, "teeth": int(round(length / 3)), "profile": "GT3 (2MGT3)",
                      "working_tension_N": JT.BELT_RATING_N, "rating_source": "Gates 17611-T, 507 N per 25.4 mm, computed for 9 mm"})
    p.add("driver", "On the driver pulley", F((0, 0, width / 2), (0, 0, -1), (1, 0, 0)), "belt")
    _generic[pid] = p
    return p


def signed_angle(a, b, n):
    a, b, n = (np.asarray(v, dtype=float) for v in (a, b, n))
    return math.degrees(math.atan2(float(np.dot(np.cross(a, b), n)), float(np.dot(a, b))))



class JointsMixin:
    # ------------------------------------------------------------ a servo in a printed cradle
    def cradle(self, key, host: Design, host_iid, servo, ms, link, step, horn_clear=(11.5, -3.0, 12.0), wall=3.0, open_dir="-x",
               rear_clear=True):
        """STS servo in a printed cradle: walls on the case's top and bottom faces with PA2.0 screws into the case's
        own screw holes; the cradle is open toward `open_dir` (servo-local axis) so the servo slides in."""
        sid = self.add_generic(f"{key}_servo", servo, link, ms)
        host.add(box_in(ms, [-33.95 - 3, 11.45 + 3], [-12.4 - 3, 12.4 + 3], [-33.1 - wall, -1.7 + wall]))
        xr, yr = [-33.95 - 0.4, 11.45 + 0.4], [-12.4 - 0.4, 12.4 + 0.4]
        ax, sgn = "xy".index(open_dir[1]), (1 if open_dir[0] == "+" else -1)
        rr = [xr, yr][ax]
        rr[1 if sgn > 0 else 0] += sgn * 60
        host.cut(box_in(ms, xr, yr, [-33.1, -1.7]))
        host.cut(cyl_in(ms, horn_clear[0], horn_clear[1], horn_clear[2]))
        if rear_clear:
            host.cut(cyl_in(ms, 11.5, -40.0, -30.0))
        for f in ("case_top", "case_bottom"):
            self.screw_into_generic(f"{key}_servo_{f}", sid, f, host, host_iid, f"{key}_servo_{f}",
                                    f"{key.upper()} servo, {f.replace('_', ' ')} screws", wall, step, d=2, kind="servo")
        return sid

    def cradle_std(self, key, host: Design, host_iid, servo, ms, link, step):
        """Standard-size hobby servo held by its flange on a printed plate: 4 x M4 x 10 through the ears into
        M4 heat-set inserts; the case passes through a window in the plate."""
        sid = self.add_generic(f"{key}_servo", servo, link, ms)
        fz = -16.4                                           # flange underside (own z)
        host.add(box_in(ms, [-37.25 - 4, 17.25 + 4], [-13.5, 13.5], [fz - 6, fz]))
        for s in (-1, 1):
            host.add(box_in(ms, [-37.25 - 4, 17.25 + 4], sorted([s * 10.6, s * 13.5]), [fz, 1.0]))
        host.cut(box_in(ms, [-30.5, 10.5], [-10.4, 10.4], [-60.0, 2.0]))
        host.cut(box_in(ms, [-37.6, 17.6], [-10.4, 10.4], [fz, 2.0]))
        host.cut(cyl_in(ms, 11.0, -3.0, 6.0))
        self.screw_generic_into_design(f"{key}_servo_flange", host, host_iid, f"{key}_servo_flange", f"{key.upper()} servo flange (4 x M4 inserts)",
                                       sid, "flange", servo.meta.get("flange_t", 2.5), step, d=4)
        return sid

    # ------------------------------------------------------------ a belt joint
    def belt_joint(self, key, host: Design, host_iid, jf: Frame, driver_dir, case_dir, horn_side, servo, out_link, host_link, step):
        """Housing in `host` (joint frame jf, cap toward +Z of jf), hub on `out_link`.
        horn_side +1: the servo sits on the cap side of the belt plane, -1: on the drum side."""
        st = STAGES[key]
        zt, zd, C = st["z_driven"], st["z_driver"], st["c"]
        ax = np.asarray(jf.basis()[2])
        o = np.asarray(jf.origin, dtype=float)
        dd = np.asarray(driver_dir, dtype=float)
        dd /= np.linalg.norm(dd)
        jm = jf.matrix()
        drum, cut, R = JT.housing_drum(zt)
        drv = o + dd * C
        bf = F(o, ax, dd).matrix()                          # belt frame: x toward the driver, z along the axis
        host.add(to_location(jm) * drum)
        host.add(box_in(bf, [0, C], [-JT.gt3_pd(zd) / 2 - 8, JT.gt3_pd(zd) / 2 + 8], [-JT.HALF, JT.GAP]))
        host.add(cyl_in(F(drv, ax, dd).matrix(), JT.gt3_pd(zd) / 2 + 8, -JT.HALF, JT.HALF))
        host.cut(to_location(jm) * cut)
        host.cut(belt_cavity(bf, JT.gt3_pd(zt) / 2 + 3.0, JT.gt3_pd(zd) / 2 + 3.0, C, (-6.5, 6.5)))
        # servo: horn face 5.75 from the belt plane on its side, own +Z toward the pulley
        horn_c = drv + ax * 5.75 * horn_side
        ms = F(horn_c, -ax * horn_side, -np.asarray(case_dir, dtype=float)).matrix()
        if servo.meta.get("servo") in bought.STD_SERVOS:
            sid = self.cradle_std(key, host, host_iid, servo, ms, host_link, step)
        else:
            sid = self.cradle(key, host, host_iid, servo, ms, host_link, step, horn_clear=(11.5, -3.0, 12.0))
        # driver pulley on the horn (same frame as the servo), dowel, 625 outboard bearing
        pul = driver_pulley_part(zd)
        pid_ = self.add_generic(f"{key}_driver", pul, host_link, ms)
        self.mate(f"{key}_driver_on_horn", (sid, "horn"), (pid_, "horn"), horn_stack(11.5), step)
        did = self.add_generic(f"{key}_dowel", dowel_part(), host_link, ms @ translate(0, 0, 5.5))
        self.mate(f"{key}_dowel_in_pulley", (pid_, "dowel"), (did, "end"), [], step, gap=-6.0)
        b625 = bought.bearing("625-2rs")
        mb = ms @ translate(0, 0, 13.5)
        bid = self.add_generic(f"{key}_driver_bearing", b625, host_link, mb)
        self.receive(host, f"{key}_driver_seat", f"{key.upper()} driver bearing seat (625)", bid, "od_face_top", "bearing_seat",
                     od=16.0, depth=5.0, retention="press")
        host.add(cyl_in(mb, 12.0, -1.0, 7.5))
        host.cut(cyl_in(mb, 8.05, -1.5, 5.0))
        host.cut(cyl_in(mb, 5.0, 5.0, 9.0))
        self.mate(f"{key}_driver_bearing_seat", (host_iid, f"{key}_driver_seat"), (bid, "od_face_top"), [], step)
        # belt on the pulley, its +X toward the driven pulley
        belt = gt3_belt(st["belt"], 9.0, JT.gt3_pd(zd), JT.gt3_pd(zt), C)
        pz = -ax * horn_side
        mbelt = F(drv - pz * 4.5, pz, -dd).matrix()
        self.add_generic(f"{key}_belt", belt, host_link, mbelt)
        rot = signed_angle(self.df(pid_, "belt").basis()[0], -dd, pz)
        self.mate(f"{key}_belt_on_pulley", (pid_, "belt"), (f"{key}_belt", "driver"), [], step, rot=rot)
        # bearings, hub, cap
        brg = bought.bearing("6806-2rs")
        b1 = self.add_generic(f"{key}_bearing_1", brg, host_link, jm @ translate(0, 0, -JT.HALF))
        host.feature(f"{key}_seat_1", f"{key.upper()} bearing 1 seat", self.df(b1, "od_face_top").flipped(), "bearing_seat", od=42.0,
                     depth=7.0, retention="shoulder")
        self.mate(f"{key}_bearing_1_seat", (host_iid, f"{key}_seat_1"), (b1, "od_face_top"), [], step)
        hid = self.add_generic(f"{key}_hub", hub_part(zt), out_link, jm)
        self.mate(f"{key}_hub_in_bearing_1", (b1, "bore"), (hid, "journal_1"), [], step)
        cid = self.add_generic(f"{key}_cap", cap_part(zt), host_link, jm)
        self.screw_generic_into_design(f"{key}_cap_on_drum", host, host_iid, f"{key}_cap_seat", f"{key.upper()} cap screws (4 x M3 inserts)",
                                       cid, "to_drum", JT.HALF - JT.GAP, step)
        b2 = self.add_generic(f"{key}_bearing_2", brg, host_link, jm @ translate(0, 0, JT.HALF) @ np.diag([1, -1, -1, 1]))
        self.mate(f"{key}_bearing_2_in_cap", (cid, "seat"), (b2, "od_face_top"), [], step)
        self.mate(f"{key}_hub_in_bearing_2", (b2, "bore"), (hid, "journal_2"), [], step)
        return dict(ms=ms, sid=sid, hid=hid, cid=cid, R=R, C=C, drv=drv, ax=ax, o=o, jm=jm)

    # ------------------------------------------------------------ a direct joint (housing in `host`)
    def twist_joint(self, key, host: Design, host_iid, z_lip, servo, host_link, out_link, step, case_dir=(0, -1, 0)):
        """Vertical direct joint: axis +Z through x = y = 0, lip mid-plane at z_lip, servo above, horn down."""
        return self.direct_joint(key, host, host_iid, translate(0, 0, z_lip), servo, host_link, out_link, step, case_dir)

    def direct_joint(self, key, host: Design, host_iid, jm, servo, host_link, out_link, step, case_dir):
        """Direct joint in joint frame jm (origin on the axis at the lip mid-plane, +Z toward the servo)."""
        jm = np.asarray(jm, dtype=float)
        o = jm[:3, 3]
        Zj = jm[:3, 2]
        brg = bought.bearing("6806-2rs")
        host.add(cyl_in(jm, 30.0, -8.5, 8.5 + DISC_T))
        host.cut(cyl_in(jm, 21.05, 1.5, 8.51))
        host.cut(cyl_in(jm, 21.05, -8.51, -1.5))
        host.cut(cyl_in(jm, 18.0, -2.0, 2.0))
        host.cut(cyl_in(jm, 21.5, 8.5, 8.5 + DISC_T + 0.5))
        ms = F(o + Zj * (8.5 + DISC_T), -Zj, -np.asarray(case_dir, dtype=float)).matrix()
        if servo.meta.get("servo") in bought.STD_SERVOS:
            sid = self.cradle_std(key, host, host_iid, servo, ms, host_link, step)
        else:
            sid = self.cradle(key, host, host_iid, servo, ms, host_link, step, horn_clear=(11.5, -3.0, 1.0))
        b_up = self.add_generic(f"{key}_bearing_up", brg, host_link, jm @ translate(0, 0, 8.5) @ np.diag([1, -1, -1, 1]))
        b_lo = self.add_generic(f"{key}_bearing_lo", brg, host_link, jm @ translate(0, 0, -8.5))
        for b, nm in ((b_up, "up"), (b_lo, "lo")):
            host.feature(f"{key}_seat_{nm}", f"{key.upper()} {'upper' if nm == 'up' else 'lower'} bearing seat", self.df(b, "od_face_top").flipped(),
                         "bearing_seat", od=42.0, depth=7.0, retention="shoulder")
            self.mate(f"{key}_bearing_{nm}_seat", (host_iid, f"{key}_seat_{nm}"), (b, "od_face_top"), [], step)
        disc = twist_disc_part()
        did = self.add_generic(f"{key}_disc", disc, out_link, jm @ translate(0, 0, 8.5))
        self.mate(f"{key}_disc_on_horn", (sid, "horn"), (did, "horn"), horn_stack(DISC_T - 4.5), step)
        hid = self.add_generic(f"{key}_hub", twist_hub_part(), out_link, jm)
        self.mate(f"{key}_hub_in_bearing", (b_lo, "bore"), (hid, "journal"), [], step)
        t, note = torque(3, "insert")
        # hub top (z 8.5) to the counterbore floor (z -14.5): heads 23 mm below the disc
        self.mate(f"{key}_hub_to_disc", (did, "hub"), (hid, "top"),
                  [StackItem(hw.insert(3), 0.0, -1), StackItem(hw.shcs(3, 30), 23.0, -1, t, note)], step)
        return dict(ms=ms, sid=sid, hid=hid, did=did, o=o)

