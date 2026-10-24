"""Static checks for the three tiers, from the CAD (out/cad/tier-<t>/rig.json).

    python3 cad/analysis.py      (plain Python; reads the rigs, writes out/cad/analysis.json
                                  and prints a summary)

Checks, each with its assumptions stated in the output:
  1. Shoulder-flex and elbow holding torque with the arm straight out (worst static case),
     against each actuator's rated and stall torque times its reduction.
  2. The counterbalance spring torque that leaves the shoulder actuator at or under its
     rated torque.
  3. Tip-over: the push at shoulder height that tips the figure over the base-disc edge,
     with both arms straight out in front.
  4. Printed-plastic mass per tier (filament to buy).
"""
import json
import os

G = 9.81
ROOT = os.path.join(os.path.dirname(__file__), "..", "out", "cad")

# actuator torque in kg*cm: (rated or continuous, stall), with the source of each figure
ACT = {
    "ds3235": {"rated": None, "stall": 32.0, "src": "DS3235 datasheet via DIYmall listing: 32 kg.cm @ 6 V (research/sourcing/20261024-bom.json)"},
    "ds3225": {"rated": None, "stall": 24.5, "src": "DS3225 datasheet (catalog part): 24.5 kg.cm @ 6.8 V"},
    "mg996r": {"rated": None, "stall": None, "src": "not sourced (grip only)"},
    "sts3215": {"rated": 10.0, "stall": 30.0, "src": "Feetech ST3215-C047 12 V: rated 10, stall 30 kg.cm (Seeed/Waveshare, BOM)"},
    "sts3250": {"rated": 16.0, "stall": 50.0, "src": "Feetech STS3250 12 V: rated 16, stall 50 kg.cm (listing, BOM)"},
}
# hobby servos publish no continuous rating: assume one third of stall for holding (stated)
HOBBY_RATED_FRACTION = 1 / 3
TIERS = {
    "a": {"shoulder": ("ds3235", 1.0), "elbow": ("ds3225", 1.0)},
    "b": {"shoulder": ("sts3215", 60 / 22), "elbow": ("sts3215", 60 / 22)},
    "c": {"shoulder": ("sts3250", 60 / 22), "elbow": ("sts3250", 60 / 22)},
}
PAYLOAD_KG = 0.25            # assumption (research/questions.md Q5)
HEAD_KG = 2.0                # assumption: the head is not weighed (research/questions.md Q1)
PUSH_HEIGHT_M = 1.2          # shoulder height of a person leaning on Jack
BASE_RADIUS_M = 0.305        # 24 in disc


def chain_z(rig):
    """Absolute z of each link origin along the hanging arm (mm), and parents."""
    L = {l["name"]: l for l in rig["links"]}
    out = {}

    def z(name):
        if name in out:
            return out[name]
        l = L[name]
        par = l["parent"]
        base = 0.0 if par in (None, "torso") else z(par)
        out[name] = base + (l["origin"][2] if par not in (None, "torso") else 0.0)
        return out[name]

    for n in L:
        z(n)
    return out, L


def downstream(L, start):
    names = {start}
    changed = True
    while changed:
        changed = False
        for n, l in L.items():
            if l["parent"] in names and n not in names:
                names.add(n)
                changed = True
    return names


def arm_moment(rig, side, joint_link):
    """Moment (N*m) about the joint with the arm straight out, plus the hand point distance (m)."""
    zabs, L = chain_z(rig)
    jz = zabs[joint_link]
    names = downstream(L, joint_link)
    m_tot, mom = 0.0, 0.0
    hand_r = 0.0
    for p in rig["parts"]:
        if p["link"] not in names:
            continue
        cz = (p["bbox"][0][2] + p["bbox"][1][2]) / 2 + zabs[p["link"]]
        r = abs(cz - jz) / 1000.0
        m = p["mass_g"] / 1000.0
        mom += m * G * r
        m_tot += m
        hand_r = max(hand_r, abs(p["bbox"][0][2] + zabs[p["link"]] - jz) / 1000.0)
    grip_r = hand_r - 0.05
    mom += PAYLOAD_KG * G * grip_r
    return mom, m_tot, grip_r


def kgcm(nm):
    return nm / G * 100.0


def main():
    res = {"assumptions": {"payload_kg": PAYLOAD_KG, "head_kg": HEAD_KG, "push_height_m": PUSH_HEIGHT_M,
                           "hobby_servo_holding": "one third of stall (no continuous rating published)",
                           "arm pose": "straight out horizontally, the worst static case; Jack's gestures pass through it briefly"},
           "tiers": {}}
    for t, plan in TIERS.items():
        rig = json.load(open(os.path.join(ROOT, f"tier-{t}", "rig.json")))
        sh, sh_m, grip = arm_moment(rig, "r", "r_shoulder_yoke")
        el_link = "r_forearm"
        el, el_m, _ = arm_moment(rig, "r", el_link)
        out = {"arm_mass_kg": round(sh_m, 3), "shoulder_moment_Nm": round(sh, 2), "shoulder_moment_kgcm": round(kgcm(sh), 1),
               "elbow_moment_Nm": round(el, 2), "elbow_moment_kgcm": round(kgcm(el), 1), "reach_to_grip_m": round(grip, 3)}
        for j, mom in (("shoulder", sh), ("elbow", el)):
            key, ratio = plan[j]
            a = ACT[key]
            stall = a["stall"] * ratio if a["stall"] else None
            rated = (a["rated"] if a["rated"] else (a["stall"] * HOBBY_RATED_FRACTION if a["stall"] else None))
            rated = rated * ratio if rated else None
            need = kgcm(mom)
            out[j] = {"actuator": key, "reduction": round(ratio, 2), "rated_kgcm": round(rated, 1) if rated else None,
                      "stall_kgcm": round(stall, 1) if stall else None, "need_kgcm": round(need, 1),
                      "margin_vs_stall": round(stall / need, 2) if stall else None,
                      "holds_without_spring": bool(rated and rated >= need), "src": a["src"]}
            if j == "shoulder" and rated:
                out[j]["spring_kgcm_needed"] = round(max(0.0, need - rated), 1)
                out[j]["spring_Nm_needed"] = round(max(0.0, need - rated) * G / 100, 2)
        # tip-over: everything but the arms sits on the axis; arms straight out front add an overturning moment
        total_kg = sum(p["mass_g"] for p in rig["parts"]) / 1000.0 + HEAD_KG
        arms_moment = 2 * sh  # both arms out front, about the shoulder ~ the torso axis
        resist = total_kg * G * BASE_RADIUS_M - arms_moment
        out["tip"] = {"total_mass_kg": round(total_kg, 1), "push_to_tip_N": round(resist / PUSH_HEIGHT_M, 0),
                      "push_to_tip_kgf": round(resist / PUSH_HEIGHT_M / G, 1),
                      "note": "push at shoulder height, toward the front, with both arms straight out in front"}
        printed = sum(p["mass_g"] for p in rig["parts"] if p["material"] in ("orange_shell", "plastic_dark", "glove_white", "metal_print"))
        out["printed_mass_kg_est"] = round(printed / 1000.0, 2)
        res["tiers"][t] = out
    json.dump(res, open(os.path.join(ROOT, "analysis.json"), "w"), indent=1)
    for t, o in res["tiers"].items():
        print(f"tier {t}: arm {o['arm_mass_kg']} kg, shoulder needs {o['shoulder']['need_kgcm']} kg.cm "
              f"(rated {o['shoulder']['rated_kgcm']}, stall {o['shoulder']['stall_kgcm']}, spring {o['shoulder'].get('spring_kgcm_needed')}), "
              f"elbow needs {o['elbow']['need_kgcm']} (rated {o['elbow']['rated_kgcm']}, stall {o['elbow']['stall_kgcm']}), "
              f"tip push {o['tip']['push_to_tip_kgf']} kgf, printed {o['printed_mass_kg_est']} kg")


if __name__ == "__main__":
    main()
