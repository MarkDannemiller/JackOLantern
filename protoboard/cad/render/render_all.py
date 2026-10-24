"""Render the report set: stills (Cycles) and animations (Eevee), then encode the videos.

    python3 cad/render/render_all.py [stills|anims|all] [--only name,name] [--draft]

Outputs to out/renders/ (stills as PNG, animation frames under frames/<name>/, videos as MP4).
Blender: ~/.local/opt/blender-4.5.15-linux-x64/blender (portable 4.5 LTS). ffmpeg from PATH.
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "out", "renders")
BLENDER = os.path.expanduser("~/.local/opt/blender-4.5.15-linux-x64/blender")
DRAFT = "--draft" in sys.argv

HERO_POSE = {"a": "wave", "b": "wave", "c": "tip_hat"}


def still(name, **kw):
    job = {"mode": "still", "engine": "cycles", "samples": 160, "style": "dark", **kw}
    job["out"] = os.path.join(OUT, f"{name}.png")
    if DRAFT:
        job.update(engine="eevee", samples=16, res=[r // 3 for r in job.get("res", [1600, 2000])])
    return name, job


def orbit(t0, t1, r, h, ang0, ang1, steps, target=(0, 0, 1.1)):
    keys = []
    for i in range(steps + 1):
        f = i / steps
        a = math.radians(ang0 + (ang1 - ang0) * f)
        keys.append({"t": round(t0 + (t1 - t0) * f, 3), "cam": [r * math.sin(a), -r * math.cos(a), h], "target": list(target)})
    return keys


def merge(*lists):
    by_t = {}
    for lst in lists:
        for k in lst:
            by_t.setdefault(k["t"], {}).update(k)
    return [dict(v, t=t) for t, v in sorted(by_t.items())]


STILLS = [
    *[still(f"hero-{t}", tiers=[t], pose=HERO_POSE[t], res=[1600, 2000], camera={"loc": [0.72, -2.15, 1.5], "target": [0, 0, 1.2], "lens": 50}) for t in "abc"],
    still("lineup-dark", tiers=["a", "b", "c"], pose={"a": "wave", "b": "showcase", "c": "tip_hat"}, spacing=1.15, res=[2800, 1500],
          camera={"loc": [0.35, -4.9, 1.55], "target": [0, 0, 1.0], "lens": 42}, samples=128),
    still("lineup-light", tiers=["a", "b", "c"], pose="rest", style="light", spacing=1.15, res=[2800, 1500],
          camera={"loc": [0.35, -4.9, 1.45], "target": [0, 0, 0.95], "lens": 42}, samples=128),
    *[still(f"internals-{t}", tiers=[t], pose="rest", style="light", hide_costume=True, res=[1600, 1600],
            camera={"loc": [1.55, 1.55, 1.6], "target": [0, 0, 1.0], "lens": 45}, samples=128) for t in "abc"],
    *[still(f"exploded-{t}", tiers=[t], pose="zero", explode=1.0, style="dark", res=[1500, 2000],
            camera={"loc": [2.35, -3.85, 2.0], "target": [0, 0, 1.66], "lens": 40}, samples=128) for t in "abc"],
    *[still(f"hands-{t}", tiers=[t], pose="grab" if t != "c" else "offer", res=[1600, 1100],
            camera={"loc": [0.35, -1.55, 1.3], "target": [0, -0.28, 0.98], "lens": 40}) for t in "abc"],
]


def anim_explode(t):
    fps = 30
    tl = merge(
        orbit(0, 12, 6.0, 2.3, -35, 55, 24, (0, 0, 1.6)),
        [{"t": 0, "pose": "zero", "explode": 0.0}, {"t": 2.0, "explode": 0.0}, {"t": 5.0, "explode": 1.0}, {"t": 8.0, "explode": 1.0},
         {"t": 11.0, "explode": 0.0}, {"t": 12.0, "explode": 0.0}],
    )
    job = {"mode": "anim", "engine": "eevee", "samples": 24, "style": "dark", "tiers": [t], "res": [1280, 720], "fps": fps,
           "camera": {"loc": tl[0]["cam"], "target": tl[0]["target"], "lens": 35}, "timeline": tl,
           "out": os.path.join(OUT, "frames", f"explode-{t}", "f_")}
    return f"explode-{t}", job


def anim_walkthrough(t="b"):
    """Hero orbit and a wave, the costume comes off, power and electronics, the arm moves,
    the hand grips, the head looks around, the costume returns."""
    cams = [
        {"t": 0.0, "cam": [2.6, -3.6, 1.7], "target": [0, 0, 1.2], "lens": 40},
        {"t": 4.0, "cam": [0.9, -2.7, 1.55], "target": [0, 0, 1.25]},
        {"t": 8.0, "cam": [0.9, -2.7, 1.55], "target": [0, 0, 1.2]},
        {"t": 11.0, "cam": [1.4, 1.5, 1.35], "target": [0, 0.05, 0.95], "lens": 45},           # back: battery and hatch
        {"t": 15.0, "cam": [1.1, 1.2, 1.25], "target": [0, 0.08, 0.9]},
        {"t": 18.0, "cam": [-0.6, -1.5, 1.35], "target": [0, -0.05, 1.03]},                      # front: electronics plate
        {"t": 21.0, "cam": [-1.4, -1.6, 1.35], "target": [-0.3, 0, 1.0], "lens": 45},           # the right arm
        {"t": 25.0, "target_part": "r_glove_fingers__finger_1", "cam_offset": [-0.42, -0.62, 0.2], "track_until": 27.3, "lens": 45},   # the hand, tracked

        {"t": 28.0, "cam": [0.3, -1.2, 1.75], "target": [0, 0, 1.55], "lens": 45},              # the head
        {"t": 31.0, "cam": [0.5, -1.4, 1.75], "target": [0, 0, 1.5]},
        {"t": 34.0, "cam": [2.4, -3.8, 1.7], "target": [0, 0, 1.15], "lens": 40},
        {"t": 36.0, "cam": [2.4, -3.8, 1.7], "target": [0, 0, 1.15]},
    ]
    acts = [
        {"t": 0.0, "pose": "rest", "costume": 1}, {"t": 2.0, "pose": "rest"}, {"t": 3.2, "pose": "wave"}, {"t": 4.0, "pose": {"r": dict(flex=10, abduct=95, twist=90, elbow=70, wrist=0, grip=0.0), "l": dict(flex=20, abduct=10, elbow=60, grip=0.6), "neck": -12}},
        {"t": 4.8, "pose": "wave"}, {"t": 5.6, "pose": {"r": dict(flex=10, abduct=95, twist=90, elbow=70, wrist=0, grip=0.0), "l": dict(flex=20, abduct=10, elbow=60, grip=0.6), "neck": -12}},
        {"t": 6.4, "pose": "wave"}, {"t": 8.0, "pose": "rest"}, {"t": 8.5, "costume": 0}, {"t": 18.5, "pose": "rest"},
        {"t": 21.0, "pose": "showcase"}, {"t": 23.0, "pose": "offer"}, {"t": 24.5, "pose": "grab"},
        {"t": 26.0, "pose": "offer"}, {"t": 27.0, "pose": "grab"}, {"t": 28.2, "pose": "rest"},
        {"t": 28.5, "pose": dict(POSE_NECK, neck=-35)}, {"t": 30.0, "pose": dict(POSE_NECK, neck=35)}, {"t": 31.5, "pose": dict(POSE_NECK, neck=0)},
        {"t": 32.5, "costume": 1}, {"t": 34.0, "pose": "tip_hat"}, {"t": 36.0, "pose": "tip_hat"},
    ]
    tl = merge(cams, acts)
    job = {"mode": "anim", "engine": "eevee", "samples": 24, "style": "dark", "tiers": [t], "res": [1280, 720], "fps": 30,
           "camera": {"loc": cams[0]["cam"], "target": cams[0]["target"], "lens": 40}, "timeline": tl,
           "out": os.path.join(OUT, "frames", f"walkthrough-{t}", "f_")}
    return f"walkthrough-{t}", job


POSE_NECK = {"r": dict(flex=8, abduct=8, elbow=25, grip=0.2), "l": dict(flex=8, abduct=8, elbow=25, grip=0.2)}
ANIMS = [anim_explode("a"), anim_explode("b"), anim_explode("c"), anim_walkthrough("b")]


def run(name, job):
    os.makedirs(os.path.join(OUT, "jobs"), exist_ok=True)
    jp = os.path.join(OUT, "jobs", f"{name}.json")
    json.dump(job, open(jp, "w"), indent=1)
    if job["mode"] == "anim":
        os.makedirs(os.path.dirname(job["out"]), exist_ok=True)
    log = open(os.path.join(OUT, "jobs", f"{name}.log"), "w")
    r = subprocess.run([BLENDER, "-b", "--python", os.path.join(HERE, "jj_scene.py"), "--", jp], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    print(f"{name}: exit {r.returncode}", flush=True)


def main():
    what = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "all"
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    todo = (STILLS if what in ("stills", "all") else []) + (ANIMS if what in ("anims", "all") else [])
    os.makedirs(OUT, exist_ok=True)
    for name, job in todo:
        if only and name not in only:
            continue
        run(name, job)


if __name__ == "__main__":
    main()
