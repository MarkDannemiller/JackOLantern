"""Render the full-hardware set (cad/render/mech_scene.py): stills in Cycles, animations in Eevee, then encode.

    python3 cad/render/render_mech.py [stills|anims|all] [--only name,name] [--draft]

Outputs to out/renders/mech/ (PNG stills, frames/<name>/, MP4 via encode.py's settings).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render_all import BLENDER, merge, orbit  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "out", "renders", "mech")
DRAFT = "--draft" in sys.argv

# poses in anatomical degrees (mech_scene clamps each joint to its limits)
REST = {"r": dict(flex=6, abduct=6, elbow=20, grip=0.2), "l": dict(flex=6, abduct=6, elbow=20, grip=0.2), "neck": 0}
# the simulated wave (cad/mech/sim/run_sim.py WAVE_BC): the arm rises forward on the balanced shoulder, so the
# shoulder-out joint carries little gravity and every belt stays within its rating
WAVE = {"r": dict(flex=90, abduct=45, twist=0, elbow=90, grip=0.0), "l": dict(flex=20, abduct=8, elbow=55, grip=0.6), "neck": -12}
WAVE_A = {"r": dict(flex=90, elbow=90, grip=0.0), "l": dict(flex=20, abduct=8, elbow=55, grip=0.6), "neck": -12}
TIP_HAT = {"r": dict(flex=118, abduct=30, twist=-30, elbow=125, wrist=20, wrist_pitch=-20, grip=0.7), "l": dict(flex=15, abduct=10, elbow=70, grip=0.9), "neck": 8}
OFFER = {"r": dict(flex=30, abduct=6, elbow=70, grip=0.1), "l": dict(flex=30, abduct=6, elbow=70, grip=0.1), "neck": 0}
GRAB = {"r": dict(flex=30, abduct=6, elbow=70, grip=1.0), "l": dict(flex=30, abduct=6, elbow=70, grip=1.0), "neck": 0}
SHOW = {"r": dict(flex=40, abduct=40, twist=-30, elbow=85, wrist=20, grip=0.1), "l": dict(flex=15, abduct=10, elbow=50, grip=0.9), "neck": -10}
ZERO = {"r": {}, "l": {}, "neck": 0}
HERO = {"a": WAVE_A, "b": WAVE, "c": TIP_HAT}


def still(name, **kw):
    job = {"mode": "still", "engine": "cycles", "samples": 160, "style": "dark", **kw}
    job["out"] = os.path.join(OUT, f"{name}.png")
    if DRAFT:
        job.update(engine="eevee", samples=16, res=[r // 3 for r in job.get("res", [1600, 2000])])
    return name, job


STILLS = [
    *[still(f"hero-{t}", tiers=[t], pose=HERO[t], res=[1600, 2000], camera={"loc": [0.72, -2.15, 1.5], "target": [0, 0, 1.2], "lens": 50}) for t in "abc"],
    still("lineup", tiers=["a", "b", "c"], pose={"a": WAVE_A, "b": SHOW, "c": TIP_HAT}, spacing=1.15, res=[2800, 1500],
          camera={"loc": [0.35, -4.9, 1.55], "target": [0, 0, 1.0], "lens": 42}, samples=128),
    *[still(f"internals-{t}", tiers=[t], pose=REST, style="light", hide_costume=True, res=[1600, 1600],
            camera={"loc": [1.55, -1.55, 1.6], "target": [0, 0, 1.0], "lens": 45}, samples=128) for t in "abc"],
    *[still(f"internals-back-{t}", tiers=[t], pose=REST, style="light", hide_costume=True, res=[1600, 1600],
            camera={"loc": [-1.3, 1.6, 1.5], "target": [0, 0, 1.0], "lens": 45}, samples=128) for t in "abc"],
    *[still(f"exploded-{t}", tiers=[t], pose=ZERO, explode=1.0, style="light", hide_costume=True, res=[1500, 2000],
            camera={"loc": [1.45, -2.45, 1.75], "target": [0, 0, 1.25], "lens": 32}, samples=128) for t in "abc"],
    *[still(f"arm-{t}", tiers=[t], pose=OFFER, style="light", hide_costume=True, res=[1600, 1200],
            camera={"loc": [-1.25, -1.45, 1.35], "target": [-0.2, -0.22, 1.0], "lens": 42}, samples=128) for t in "abc"],
    *[still(f"shoulder-{t}", tiers=[t], pose=REST, style="light", hide_costume=True, res=[1600, 1200],
            camera={"loc": [-0.75, -0.55, 1.35], "target": [-0.2, -0.02, 1.15], "lens": 60}, samples=128) for t in "abc"],
    *[still(f"hands-{t}", tiers=[t], pose=GRAB if t != "c" else OFFER, res=[1600, 1100],
            camera={"loc": [0.35, -1.55, 1.3], "target": [0, -0.28, 0.98], "lens": 40}) for t in "abc"],
]


def anim_explode(t):
    tl = merge(orbit(0, 12, 5.2, 2.2, -35, 55, 24, (0, 0, 1.3)),
               [{"t": 0, "pose": ZERO, "explode": 0.0, "costume": 0}, {"t": 2.0, "explode": 0.0}, {"t": 5.0, "explode": 1.0},
                {"t": 8.0, "explode": 1.0}, {"t": 11.0, "explode": 0.0}, {"t": 12.0, "explode": 0.0}])
    job = {"mode": "anim", "engine": "eevee", "samples": 24, "style": "light", "tiers": [t], "res": [1280, 720], "fps": 30, "hide_costume": True,
           "camera": {"loc": tl[0]["cam"], "target": tl[0]["target"], "lens": 35}, "timeline": tl,
           "out": os.path.join(OUT, "frames", f"explode-{t}", "f_")}
    return f"explode-{t}", job


def anim_walkthrough(t="b"):
    """Costumed wave, the costume comes off, power at the back, electronics, the shoulder and balancer, the arm moves,
    the hand grips, the head turns, the costume returns."""
    wave_lo = {**WAVE, "r": {**WAVE["r"], "wrist": 35}}
    wave_hi = {**WAVE, "r": {**WAVE["r"], "wrist": -35}}
    cams = [
        {"t": 0.0, "cam": [2.6, -3.6, 1.7], "target": [0, 0, 1.2], "lens": 40},
        {"t": 4.0, "cam": [0.9, -2.7, 1.55], "target": [0, 0, 1.25]},
        {"t": 8.0, "cam": [0.9, -2.7, 1.55], "target": [0, 0, 1.2]},
        {"t": 11.0, "cam": [1.2, 1.6, 1.3], "target": [0, 0.02, 0.95], "lens": 45},
        {"t": 15.0, "cam": [0.9, 1.3, 1.2], "target": [0, 0.02, 0.92]},
        {"t": 18.0, "cam": [-0.7, -1.4, 1.35], "target": [0, -0.03, 1.0]},
        {"t": 21.0, "cam": [-0.8, -0.6, 1.4], "target": [-0.2, -0.02, 1.15], "lens": 55},
        {"t": 24.0, "cam": [-1.1, -1.0, 1.3], "target": [-0.25, -0.1, 1.0], "lens": 50},
        {"t": 27.5, "cam": [-0.9, -1.2, 1.2], "target": [-0.2, -0.2, 0.95]},
        {"t": 29.0, "cam": [0.3, -1.2, 1.75], "target": [0, 0, 1.5], "lens": 45},
        {"t": 32.0, "cam": [0.5, -1.4, 1.75], "target": [0, 0, 1.5]},
        {"t": 35.0, "cam": [2.4, -3.8, 1.7], "target": [0, 0, 1.15], "lens": 40},
        {"t": 37.0, "cam": [2.4, -3.8, 1.7], "target": [0, 0, 1.15]},
    ]
    acts = [
        {"t": 0.0, "pose": REST, "costume": 1}, {"t": 2.0, "pose": REST}, {"t": 3.2, "pose": WAVE}, {"t": 3.8, "pose": wave_lo},
        {"t": 4.4, "pose": wave_hi}, {"t": 5.0, "pose": wave_lo}, {"t": 5.6, "pose": wave_hi}, {"t": 6.2, "pose": wave_lo}, {"t": 6.8, "pose": WAVE}, {"t": 8.0, "pose": REST}, {"t": 8.5, "costume": 0},
        {"t": 21.0, "pose": REST}, {"t": 23.0, "pose": SHOW}, {"t": 25.0, "pose": OFFER}, {"t": 26.3, "pose": GRAB},
        {"t": 27.3, "pose": OFFER}, {"t": 28.3, "pose": GRAB}, {"t": 29.0, "pose": REST},
        {"t": 29.5, "pose": {**REST, "neck": -35}}, {"t": 31.0, "pose": {**REST, "neck": 35}}, {"t": 32.5, "pose": REST},
        {"t": 33.0, "costume": 1}, {"t": 35.0, "pose": WAVE}, {"t": 37.0, "pose": WAVE},
    ]
    tl = merge(cams, acts)
    job = {"mode": "anim", "engine": "eevee", "samples": 24, "style": "dark", "tiers": [t], "res": [1280, 720], "fps": 30,
           "camera": {"loc": cams[0]["cam"], "target": cams[0]["target"], "lens": 40}, "timeline": tl,
           "out": os.path.join(OUT, "frames", f"walkthrough-{t}", "f_")}
    return f"walkthrough-{t}", job


ANIMS = [anim_explode("a"), anim_explode("b"), anim_explode("c"), anim_walkthrough("b")]


def run(name, job):
    os.makedirs(os.path.join(OUT, "jobs"), exist_ok=True)
    jp = os.path.join(OUT, "jobs", f"{name}.json")
    json.dump(job, open(jp, "w"), indent=1)
    if job["mode"] == "anim":
        os.makedirs(os.path.dirname(job["out"]), exist_ok=True)
    with open(os.path.join(OUT, "jobs", f"{name}.log"), "w") as log:
        r = subprocess.run([BLENDER, "-b", "--python", os.path.join(HERE, "mech_scene.py"), "--", jp], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    print(f"{name}: exit {r.returncode}", flush=True)
    if job["mode"] == "anim" and r.returncode == 0:
        frames = os.path.dirname(job["out"])
        subprocess.run([sys.executable, os.path.join(HERE, "encode.py"), name], env={**os.environ, "JJ_RENDER_OUT": OUT})  # captions


def main():
    what = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "all"
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
    todo = (STILLS if what in ("stills", "all") else []) + (ANIMS if what in ("anims", "all") else [])
    os.makedirs(OUT, exist_ok=True)
    for name, job in todo:
        if not only or name in only:
            run(name, job)


if __name__ == "__main__":
    main()
