"""Summarise a simulation log: per joint, over windows of interest, the worst tracking error, servo torque as a
fraction of stall and of the rated third of stall, belt tension, saturation time; the base's tilt and travel.

    python3 cad/mech/sim/summarise.py <tier> <scenario> [t0 t1 ...]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def summary(tier, name, windows=None):
    d = json.load(open(os.path.join(PROJECT, "out", "mech", "sim", f"tier-{tier}", f"{name}.json")))
    log = d["log"]
    joints = [k for k in log[0] if k not in ("t", "base", "push_N")]
    out = {"tier": tier, "scenario": name, "tip_force_N": d.get("tip_force_N"), "joints": {}, "base": {}}
    windows = windows or [(0, log[-1]["t"])]
    for j in joints:
        rows = []
        for (a, b) in windows:
            w = [r for r in log if a <= r["t"] <= b]
            if not w:
                continue
            err = max(abs(r[j]["q"] - r[j]["tgt"]) for r in w)
            stall = max(r[j]["stall"] for r in w)
            rated_mean = sum(r[j]["rated"] for r in w) / len(w)
            belt = max((r[j]["belt"] or 0) for r in w)
            sat = sum(1 for r in w if r[j]["sat"]) / len(w)
            rows.append(dict(window=[a, b], err_deg=round(err, 2), stall_frac_max=round(stall, 3), rated_frac_mean=round(rated_mean, 3),
                             belt_N_max=round(belt, 1), sat_frac=round(sat, 3), q_end=log[-1][j]["q"]))
        out["joints"][j] = rows
    if "base" in log[0]:
        out["base"] = dict(tilt_max_deg=max(r["base"]["tilt"] for r in log), drift_mm=round(1000 * max(abs(r["base"]["x"] - log[0]["base"]["x"]) + abs(r["base"]["y"] - log[0]["base"]["y"]) for r in log), 1))
    return out


if __name__ == "__main__":
    t, n = sys.argv[1], sys.argv[2]
    ws = [(float(a), float(b)) for a, b in zip(sys.argv[3::2], sys.argv[4::2])] or None
    s = summary(t, n, ws)
    print(json.dumps({k: v for k, v in s.items() if k != "joints"}))
    for j, rows in s["joints"].items():
        if any(r["stall_frac_max"] > 0.02 for r in rows):
            print(j, rows)
