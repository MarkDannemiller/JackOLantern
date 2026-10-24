"""Wiring harness cut list per tier: the model's electrical links grouped into physical cables, each with its
conductors, gauge, end terminations and a cut length from where its two ends sit in the assembled model.

    python3 cad/mech/harness.py            (after cad/mech/tools/dump_model.mts has written out/mech/uhd-<t>.json)

Writes docs/wiring/harness-<t>.json and .md (generated). Rules, stated so they can be checked:
  * a supply and its return travel in one cable (a ground link pairs with the supply link to the same part)
  * the Feetech serial bus is daisy-chained along each arm in joint order, through the hollow joint hubs; the
    model draws it as a star from the adapter (each servo linked to the adapter), the build chains it
  * cut length = path between the ends (sum of the x, y and z offsets, routed along the frame) x 1.1, plus
    80 mm for terminations and service loops, plus 120 mm at every arm joint a cable crosses; rounded up to 10 mm
  * gauge from the current the branch can carry (fuse or regulator rating): 12 AWG for the pack trunk (30 A
    fuse), 14 AWG for the 12 V arm feeds (20 A converters), 16 AWG for the head servo rail (DROK, 10 A),
    18 AWG for 5 V logic feeds, 20 AWG for the E-stop chain, 26 AWG signals; ampacity per the silicone-wire
    sellers' tables cited in research/sourcing (assumption: short runs inside the torso, 200 C silicone)
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(PROJECT, "docs", "wiring")
ARM_ORDER = ["shoulder_flex", "shoulder_out", "upper_twist", "elbow", "wrist_twist", "wrist_pitch", "fingers", "thumb", "grip"]
JOINT_CROSSINGS = {"shoulder_flex": 0, "shoulder_out": 1, "upper_twist": 2, "elbow": 3, "wrist_twist": 4, "wrist_pitch": 5, "fingers": 5, "thumb": 5, "grip": 3}

GAUGE_RULES = [  # (link-id pattern pieces, gauge, terminations, note)
    (("pack", "dock_lvc", "dock1_or", "dock2_or", "or1_bus", "or2_bus", "monitor_lvc", "lvc_fuses", "mains_or", "or3"), 12,
     "XT60 / ferrules", "pack trunk, 30 A dock fuse"),
    (("act_relay", "relay_arm", "relay_head", "arm_r_12v", "arm_l_12v", "fuse_buck_arm", "arm_rail", "estop_fuse_arm"), 14,
     "ring terminal / 6.3 mm spade / ferrules", "actuator feeds"),
    (("head_servo_rail", "relay_head", "fuse_buck_head", "estop_fuse_head", "relay_hand"), 16, "ferrules / servo header", "head and hand servo rails"),
    (("pi_5v", "pi5", "pi_feed", "fuse_buck_pi", "lvc_fuse_pi", "buck_pi"), 18, "ferrules / USB-C pigtail", "5 V computer feeds"),
    (("estop",), 20, "ferrules / 6.3 mm spade", "E-stop chain (relay coil)"),
]


def gauge_for(link_id, protocol):
    if protocol in ("i2c",):
        return 26, "STEMMA QT / JST-SH 4-pin", "I2C"
    if protocol in ("usb",):
        return None, "USB-A to USB-C cable (bought)", "USB"
    if protocol in ("rc_servo", "pwm"):
        return 22, "3-pin 0.1 in servo plug (extension lead)", "hobby servo signal + power"
    for keys, g, term, note in GAUGE_RULES:
        if any(k in link_id for k in keys):
            return g, term, note
    return 18, "ferrules", "other power"


EXPORT_AT = {"power_in": "bus_adapter", "gnd": "bus_adapter", "usb": "bus_adapter", "hand_5v": "hand", "hand_gnd": "hand", "hand_usb": "hand"}


def where(placements, path):
    """An end's placed body: an arm's exported port sits on the part that carries it (the bus adapter, a servo, the hand)."""
    if path in placements:
        return path
    return None


def pos(placements, path):
    m = placements.get(path)
    if m is None:
        return None
    return np.array(m).reshape(4, 4)[:3, 3]


def length_mm(a, b, crossings=0):
    d = np.abs(np.asarray(a) - np.asarray(b)).sum() * 1.1 + 80 + 120 * crossings
    return int(math.ceil(d / 10.0) * 10)


def build(tier):
    d = json.load(open(os.path.join(PROJECT, "out", "mech", f"uhd-{tier}.json")))
    P = {p["path"]: p["matrix"] for p in d["placements"]}
    links = [w for w in d["wiring"] if w.get("domain") == "electrical" or w.get("protocol") in ("power", "i2c", "usb", "rc_servo", "pwm", "custom")]
    links = [w for w in links if w.get("protocol") not in ("bolt_pattern", "axial_stop", "bearing_fit", "shaft")]
    end = lambda s: (s.split(":")[0], s.split(":")[1])
    cables = []
    used = set()
    # 1. Feetech buses: chain per arm, adapter -> servos in joint order (from the arm's placed servos)
    for side in ("arm_r", "arm_l"):
        if f"{side}/bus_adapter" not in P:
            continue
        servos = [x for x in ARM_ORDER if f"{side}/{x}" in P and x != "grip"]
        prev = f"{side}/bus_adapter"
        for k, sv in enumerate(servos):
            a_p, b_p = pos(P, prev), pos(P, f"{side}/{sv}")
            cross = JOINT_CROSSINGS.get(sv, 0) - (JOINT_CROSSINGS.get(prev.split("/")[-1], 0) if k else 0)
            cables.append(dict(id=f"{side.replace('_', '-')}-bus-{k + 1}", kind="bus", from_=prev, to=f"{side}/{sv}", conductors=["signal", "V+ 12 V", "GND"],
                               gauge=None, terminations="Molex 5264 3-pin both ends (Feetech servo cable)",
                               length_mm=length_mm(a_p, b_p, max(cross, 0)),
                               note=f"daisy chain {'from the bus adapter' if k == 0 else 'from the previous servo'}; through {max(cross, 0)} joint hub(s)",
                               links=[f"{side}/{sv}_bus", f"{side}/{sv}_vplus", f"{side}/{sv}_gnd"]))
            prev = f"{side}/{sv}"
    # 2. power and signal links: pair each ground with the supply to the same part
    rest = [w for w in links if w["linkId"] not in used]
    supplies = {}
    for w in rest:
        (pa, ia), (pb, ib) = end(w["a"]), end(w["b"])
        is_gnd = ib in ("gnd", "neg_bus", "coil_85", "bus_gnd", "lead_minus", "dock_minus", "pack_minus") or "gnd" in w["linkId"]
        if is_gnd:
            continue
        supplies.setdefault(pb, []).append(w)
    for w in rest:
        (pa, ia), (pb, ib) = end(w["a"]), end(w["b"])
        if w["linkId"].startswith(("pack1_dock", "pack2_dock", "pack_dock", "pack1_neg", "pack2_neg", "pack_dock_neg")):
            continue                                             # the pack's own contacts in the dock
        is_gnd = ib in ("gnd", "neg_bus", "coil_85", "bus_gnd", "lead_minus", "dock_minus", "pack_minus") or "gnd" in w["linkId"]
        if is_gnd:
            continue
        g, term, note = gauge_for(w["linkId"], w["protocol"])
        partner = next((x for x in rest if w["protocol"] == "power" and x is not w and end(x["b"])[0] == pb
                        and ("gnd" in x["linkId"] or end(x["b"])[1] in ("gnd", "coil_85"))), None)
        # an end on an arm's exported port: the part that carries it
        ap_path = pa if pa in P else (f"{pa}/{EXPORT_AT.get(ia, ia.replace('_servo', ''))}" if f"{pa}/{EXPORT_AT.get(ia, ia.replace('_servo', ''))}" in P else pa)
        bp_path = pb if pb in P else (f"{pb}/{EXPORT_AT.get(ib, ib.replace('_servo', ''))}" if f"{pb}/{EXPORT_AT.get(ib, ib.replace('_servo', ''))}" in P else pb)
        a_p, b_p = pos(P, ap_path), pos(P, bp_path)
        L = length_mm(a_p, b_p) if a_p is not None and b_p is not None else None
        cond = ["+", "-"] if (w["protocol"] == "power" and partner) else (["+"] if w["protocol"] == "power" else [w["protocol"]])
        if w["protocol"] in ("rc_servo", "pwm"):
            cond = ["signal", "V+", "GND"]
            L = (L or 0) + 120 * JOINT_CROSSINGS.get(ib.replace("_servo", ""), 0)
        cables.append(dict(id=w["linkId"].replace("_", "-"), kind=w["protocol"], from_=f"{pa}:{ia}", to=f"{pb}:{ib}", conductors=cond, gauge=g,
                           terminations=term, length_mm=L, note=note + (f"; return paired from {end(partner['a'])[0]}" if partner else ""),
                           links=[w["linkId"]] + ([partner["linkId"]] if partner else [])))
    # totals per gauge (each conductor counted; red and black)
    totals = {}
    for c in cables:
        if c["gauge"] and c["length_mm"]:
            n = len([x for x in c["conductors"] if x in ("+", "-")]) or 1
            totals[c["gauge"]] = totals.get(c["gauge"], 0) + n * c["length_mm"]
    out = dict(tier=tier, cables=cables, totals_mm_by_awg=totals, bus_cables=sum(1 for c in cables if c["kind"] == "bus"),
               rules=__doc__.split("Rules, stated so they can be checked:")[1].strip())
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, f"harness-{tier}.json"), "w"), indent=1)
    lines = [f"# Wiring harness, tier {tier.upper()} (generated by cad/mech/harness.py; do not edit)", "",
             f"{len(cables)} cables. Lengths are cut lengths from the assembled model (rules at the end).", "",
             "| Cable | From | To | Conductors | AWG | Ends | Cut (mm) | Note |", "|---|---|---|---|---|---|---:|---|"]
    for c in cables:
        lines.append(f"| {c['id']} | {c['from_']} | {c['to']} | {', '.join(c['conductors'])} | {c['gauge'] or '-'} | {c['terminations']} | "
                     f"{c['length_mm'] or 'TBD'} | {c['note']} |")
    lines += ["", "## Wire to buy (red and black counted separately)", "", "| AWG | Total (m) |", "|---|---:|"]
    lines += [f"| {g} | {v / 1000:.1f} |" for g, v in sorted(totals.items())]
    lines += ["", "## Rules", "", out["rules"]]
    open(os.path.join(OUT, f"harness-{tier}.md"), "w").write("\n".join(lines) + "\n")
    print(f"tier {tier}: {len(cables)} cables, wire by AWG (m): " + ", ".join(f"{g}: {v / 1000:.1f}" for g, v in sorted(totals.items())))
    return out


if __name__ == "__main__":
    for t in "abc":
        build(t)
