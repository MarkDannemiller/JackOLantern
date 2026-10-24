"""Isaac Sim (PhysX) runs of Joyful Jack: can the actuators do the gestures, does it stay standing.

    OMNI_KIT_ACCEPT_EULA=YES ~/.local/opt/isaacsim-6.2/bin/python cad/mech/sim/run_sim.py <tier> <scenario> [--video] [--balancer]

The robot is out/mech/sim/tier-<t>/jack.urdf (make_urdf.py: masses and inertias from the CAD), imported with
Isaac Sim's URDF importer onto a ground plane, base free (it stands on its skirt under gravity, friction 0.8).

Actuator model, per joint (output side): the servo is an implicit PD drive (PhysX) toward the commanded angle
with stiffness ratio^2 x Kp and damping ratio^2 x Kd, where the servo's own loop reaches its stall torque at 3 deg
of motor-side error; its torque is capped every step at the servo's torque-speed line (stall at rest, zero at its
no-load speed, both referred to the output through the belt: x ratio x 0.9 efficiency, speed / ratio). Gravity
balancers (zero-length spring and cable) add k a b sin(theta) when enabled. Logged every 10 ms: angle, target,
servo torque (output and motor side, as a fraction of stall and of the rated third of stall), belt tension
against its 179.6 N rating, base tilt and the base's lift.
Scenarios: hold (arm out sideways then forward, 0.25 kg in the hand, 8 s each), wave, reach, push (tip test),
estop (servos cut at full reach). Results: out/mech/sim/tier-<t>/<scenario>.json (+ frames for --video).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("tier")
ap.add_argument("scenario")
ap.add_argument("--video", action="store_true")
ap.add_argument("--balancer", action="store_true")
ap.add_argument("--belt-limit", action="store_true", help="servo torque limit set so a belt joint never pulls its belt past the rating")
ap.add_argument("--payload", type=float, default=0.25)
ap.add_argument("--width", type=int, default=1280)
ap.add_argument("--height", type=int, default=720)
args = ap.parse_args()

from isaacsim import SimulationApp  # noqa: E402

app = SimulationApp({"headless": True, "width": args.width, "height": args.height})

import omni.usd  # noqa: E402
from pxr import Gf, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics, PhysxSchema  # noqa: E402
from isaacsim.asset.importer.urdf import URDFImporter, URDFImporterConfig  # noqa: E402
from isaacsim.core.api import World  # noqa: E402
from isaacsim.core.experimental.prims import Articulation, RigidPrim  # noqa: E402
from isaacsim.core.utils.stage import add_reference_to_stage  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D = os.path.join(PROJECT, "out", "mech", "sim", f"tier-{args.tier}")     # tier may carry a variant: b+sandbags2
INFO = json.load(open(os.path.join(D, "links.json")))
ACT = {a["joint"]: a for a in INFO["actuators"]}
DT = 1.0 / 240.0


def balancers():
    """Gravity balancer per joint (k a b in N.m) when enabled: from links.json (make_urdf.py writes them)."""
    return INFO.get("balancers", {}) if args.balancer else {}


# ---------------------------------------------------------------- import
usd_dir = os.path.join(D, "usd")
usd_path = os.path.join(usd_dir, "jack.usd")
if not os.path.exists(usd_path) or os.path.getmtime(usd_path) < os.path.getmtime(os.path.join(D, "jack.urdf")):
    cfg = URDFImporterConfig(urdf_path=os.path.join(D, "jack.urdf"), usd_path=usd_dir, merge_fixed_joints=True, fix_base=False,
                             collision_from_visuals=True, collision_type="Convex Hull", allow_self_collision=False,
                             joint_drive_type="force", joint_target_type="position", override_joint_stiffness=100.0,
                             override_joint_damping=5.0, robot_type="Humanoid")
    out = URDFImporter(cfg).import_urdf()
    if out and out != usd_path and os.path.exists(out):
        usd_path = out
    print("imported", usd_path)
cands = [os.path.join(dp, f) for dp, _, fs in os.walk(usd_dir) for f in fs if f.endswith(".usd") or f.endswith(".usda")]
if not os.path.exists(usd_path):
    usd_path = sorted(cands, key=len)[0]

world = World(stage_units_in_meters=1.0, physics_dt=DT, rendering_dt=1.0 / 30.0)
world.scene.add_default_ground_plane(static_friction=0.8, dynamic_friction=0.6, restitution=0.0)
stage = omni.usd.get_context().get_stage()
add_reference_to_stage(usd_path, "/World/jack")
vs = stage.GetPrimAtPath("/World/jack").GetVariantSets()
if vs.HasVariantSet("Physics"):
    vs.GetVariantSet("Physics").SetVariantSelection("physx")
root = None
for p in Usd.PrimRange(stage.GetPrimAtPath("/World/jack")):
    if p.HasAPI(UsdPhysics.ArticulationRootAPI):
        root = p.GetPath().pathString
        break
assert root, "no articulation root"
# lights for video
UsdLux.DomeLight.Define(stage, "/World/dome").CreateIntensityAttr(900)
sun = UsdLux.DistantLight.Define(stage, "/World/sun")
sun.CreateIntensityAttr(2500)
UsdGeom.Xformable(sun).AddRotateXYZOp().Set(Gf.Vec3f(-50, 20, 30))

# base prim (the torso link) for tilt and lift; the push is applied to it at shoulder height
torso_path = None
for p in Usd.PrimRange(stage.GetPrimAtPath(root)):
    if p.GetName() == "torso" and p.HasAPI(UsdPhysics.RigidBodyAPI):
        torso_path = p.GetPath().pathString
        break
torso = RigidPrim(torso_path) if torso_path else None
art = Articulation(root)
world.reset()
names = list(art.dof_names)
idx = {n: i for i, n in enumerate(names)}
nd = len(names)
print("dofs", names)

# drives: implicit PD per joint from the servo model
Kp_motor = {}
for n in names:
    a = ACT.get(n)
    if not a:
        continue
    Kp_motor[n] = a["stall_nm"] / math.radians(3.0)
stiff = np.zeros(nd)
damp = np.zeros(nd)
for n, i in idx.items():
    a = ACT.get(n)
    R = a["ratio"] if a else 1.0
    kp = Kp_motor.get(n, 5.0)
    stiff[i] = R * R * kp * (0.9 if R > 1 else 1.0)
    damp[i] = stiff[i] * 0.04
art.set_dof_gains(stiffnesses=stiff.reshape(1, -1), dampings=damp.reshape(1, -1))
art.set_dof_max_velocities(np.array([[ (ACT[n]["no_load_rad_s"] / ACT[n]["ratio"]) if n in ACT else 5.0 for n in names]]))


def cap(n, qd):
    """Servo torque available at the output at joint speed qd (rad/s)."""
    a = ACT[n]
    R = a["ratio"]
    eta = 0.9 if R > 1 else 1.0
    w = abs(qd) * R
    frac = max(0.0, 1.0 - w / a["no_load_rad_s"])
    c = a["stall_nm"] * R * eta * max(frac, 0.05)
    if args.belt_limit and a.get("belt_r_m"):
        c = min(c, BELT_RATED_N * a["belt_r_m"])   # Feetech torque-limit register (hobby servos: a current limit)
    return c


BELT_RATED_N = 179.6   # GT3 9 mm, research/sourcing (D10)


# ---------------------------------------------------------------- scenarios: targets (deg) per joint over time
T = args.tier[0]
R1, R2 = "r_j1", "r_j2"
ELB = "r_j4"
HAND = {"a": "r_grip", "b": "r_fingers", "c": None}[T]


def smooth(t, t0, t1):
    if t <= t0:
        return 0.0
    if t >= t1:
        return 1.0
    x = (t - t0) / (t1 - t0)
    return x * x * (3 - 2 * x)


# the wave: shoulder flexed 90 and out 45, so the upper arm is level, out and forward, and the forearm (elbow 90)
# stands vertical; the shoulder-out axis (J2) is then vertical and carries no gravity, and the balancer is at its peak
WAVE_BC = json.loads(os.environ.get("JJ_WAVE", '{"r_j1": 90, "r_j2": 45, "r_j3": 0, "r_j4": 90}'))


def targets(t):
    """Gesture targets (deg) at time t: raises over 2.5-3 s (the belt-geared shoulders run at most about 90 deg/s)."""
    q = {n: 0.0 for n in names}
    s = args.scenario
    if s == "hold":
        # arm straight out sideways (shoulder out 90), hold 7 s, down; then straight out forward (shoulder flex 90), hold, down
        q[R2] = 90 * (smooth(t, 0.5, 3.0) - smooth(t, 10.0, 12.5))
        q[R1] = 90 * (smooth(t, 13.0, 15.5) - smooth(t, 21.5, 24.0))
    elif s == "wave":
        # the gesture the renders show (cad/render/render_mech.py WAVE, WAVE_A): forearm vertical, hand up; B and C wave
        # with the wrist twist, A (no wrist twist) with the elbow
        up = smooth(t, 0.5, 3.5) - smooth(t, 14.5, 17.5)
        wv = math.sin(2 * math.pi * 0.8 * (t - 4.0)) * smooth(t, 4.0, 4.6) * (1 - smooth(t, 13.4, 14.0))
        if T == "a":
            q[R1] = 90 * up
            q[ELB] = 90 * up + 15 * wv
        else:
            # the arm rises forward on the balanced shoulder (J1), so the shoulder-out axis (J2) turns near vertical
            # and carries little gravity; WAVE_B in cad/render/render_mech.py is the same pose
            for k, v in WAVE_BC.items():
                q[k] = v * up
            q["r_j5"] = 35 * wv
    elif s == "reach":
        r = smooth(t, 0.5, 3.5) - smooth(t, 9.5, 12.5)
        q[R1] = 70 * r
        q[ELB] = 40 * r
        if HAND:
            q[HAND] = (ACT[HAND]["limits"][1] * 0.8) * (smooth(t, 4.0, 5.0) - smooth(t, 8.0, 9.0))
    elif s in ("push", "estop"):
        q[R2] = 90 * smooth(t, 0.5, 3.0)
        if "l_j2" in q:
            q["l_j2"] = 90 * smooth(t, 0.5, 3.0)
    return q


DUR = {"hold": 25.0, "wave": 18.0, "reach": 13.0, "push": 14.0, "estop": 9.0}[args.scenario]

# payload: a 0.25 kg ball welded into the right hand's grip (hold, wave, reach)
if args.payload and args.scenario in ("hold", "wave", "reach"):
    pass  # the URDF variant with --payload carries it (make_urdf.py --payload)



# camera for video
cam = None
if args.video:
    from isaacsim.sensors.camera import Camera
    eye = np.array([-2.3, -3.1, 1.75])
    tgt = np.array([-0.2, 0.0, 1.2])
    cam = Camera(prim_path="/World/cam", position=eye, frequency=30, resolution=(args.width, args.height),
                 orientation=None)
    cam.initialize()
    from isaacsim.core.utils.viewports import set_camera_view
    set_camera_view(eye=eye, target=tgt, camera_prim_path="/World/cam")
    frames_dir = os.path.join(D, "frames", args.scenario + ("-bal" if args.balancer else "") + ("-lim" if args.belt_limit else ""))
    os.makedirs(frames_dir, exist_ok=True)

log = []
bal = balancers()
t = 0.0
step = 0
estop_t = 4.0
push_force = 0.0
lifted_at = None
z0 = None
from PIL import Image  # noqa: E402

while t < DUR:
    q = art.get_dof_positions().numpy().reshape(-1)
    qd = art.get_dof_velocities().numpy().reshape(-1)
    tg = targets(t)
    live = not (args.scenario == "estop" and t >= estop_t)
    tgt_arr = np.array([[math.radians(tg[n]) for n in names]])
    caps = np.array([[cap(n, qd[i]) if (n in ACT and live) else (0.0 if n in ACT else 50.0) for n, i in idx.items()]])
    art.set_dof_max_efforts(caps)
    if not live:
        art.set_dof_gains(stiffnesses=np.zeros((1, nd)), dampings=np.array([[0.3 * (ACT[n]["ratio"] ** 2) if n in ACT else 0.0 for n in names]]))
    art.set_dof_position_targets(tgt_arr)
    ext = np.zeros((1, nd))
    for n, kab in bal.items():
        if n in idx:
            ext[0, idx[n]] = kab * math.sin(max(-math.pi, min(math.pi, q[idx[n]])))
    art.set_dof_efforts(ext)
    if args.scenario == "push" and torso is not None and t > 4.0:
        push_force = min(400.0, 30.0 * (t - 4.0))          # ramps 30 N/s from the back, at shoulder height
        torso.apply_forces_and_torques_at_pos(forces=np.array([[0.0, -push_force, 0.0]]), positions=np.array([[0.0, 0.0, 1.185]]))
    world.step(render=bool(cam) and step % 8 == 0)
    if step % 2 == 0:
        q = art.get_dof_positions().numpy().reshape(-1)
        qd = art.get_dof_velocities().numpy().reshape(-1)
        stiff_now = stiff if live else np.zeros(nd)
        rec = {"t": round(t, 4)}
        for n, i in idx.items():
            if n not in ACT:
                continue
            a = ACT[n]
            R = a["ratio"]
            tau_cmd = stiff_now[i] * (tgt_arr[0, i] - q[i]) - (damp[i] if live else 0) * qd[i]
            tau = float(np.clip(tau_cmd, -caps[0, i], caps[0, i]))
            tau_m = tau / (R * (0.9 if R > 1 else 1.0))
            rec[n] = dict(q=round(math.degrees(q[i]), 3), tgt=round(math.degrees(tgt_arr[0, i]), 3), tau=round(tau, 4),
                          stall=round(abs(tau_m) / a["stall_nm"], 4), rated=round(abs(tau_m) / (a["stall_nm"] * a["rated_frac"]), 4),
                          sat=bool(abs(tau_cmd) > caps[0, i] * 0.999), bal=round(float(ext[0, i]), 4),
                          belt=round(abs(tau) / a["belt_r_m"], 2) if a.get("belt_r_m") else None)
        if torso is not None:
            pos, quat = torso.get_world_poses()
            pos, quat = pos.numpy().reshape(-1), quat.numpy().reshape(-1)
            w, x, y, z = quat
            up = np.array([2 * (x * z + w * y), 2 * (y * z - w * x), 1 - 2 * (x * x + y * y)])
            tilt = math.degrees(math.acos(max(-1, min(1, up[2]))))
            if z0 is None:
                z0 = pos[2]
            rec["base"] = dict(tilt=round(tilt, 3), x=round(float(pos[0]), 4), y=round(float(pos[1]), 4), z=round(float(pos[2]), 4))
            if args.scenario == "push":
                rec["push_N"] = round(push_force, 1)
                if lifted_at is None and tilt > 2.0:
                    lifted_at = push_force
        log.append(rec)
    if cam is not None and step % 8 == 0 and step > 0:
        rgba = cam.get_rgba()
        if rgba is not None and rgba.size:
            Image.fromarray(np.asarray(rgba)[:, :, :3]).save(os.path.join(frames_dir, f"f_{step // 8:04d}.png"))
    t += DT
    step += 1

res = dict(tier=T, scenario=args.scenario, balancer=args.balancer, payload=INFO.get("payload_kg"), dt=DT, log=log,
           tip_force_N=lifted_at)
name = args.scenario + ("-bal" if args.balancer else "") + ("-lim" if args.belt_limit else "")
json.dump(res, open(os.path.join(D, f"{name}.json"), "w"))
print("done", name, len(log), "samples", "tip at", lifted_at)
app.close()
