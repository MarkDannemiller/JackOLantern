"""Final per-tier BOM: the researched rows (20261024-bom.json) plus the substitutions made to fit
the caps, with totals computed here, never by hand.

    python3 research/sourcing/build_final_bom.py  ->  20261024-bom-final.json and .md

Each tier lists rows by a unique substring of the researched `choice`, with the quantity this
tier needs. New rows (not in the researched file) carry their own price source and date.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(HERE, "20261024-bom.json")))

DROK = next(r for r in SRC if "DROK 300W" in r["choice"])
NEW = {
    "drok_head": {**DROK, "item": "Buck for the head's servo rail (5-6 V)", "notes": "Same DROK module as researched. Tiers B and C: the head keeps its PCA9685 hobby-servo rail."},
    "drok_pi5": {**DROK, "item": "Buck for the torso Raspberry Pi 5, set to 5.1 V (tier C)", "notes": "Adjustable DROK: the Pi 5 wants 5.1 V and the fixed 5.0 V Pololu does not overlap (protoboard check, UHD_LINK_STATE)."},
    "drok_a": {**DROK, "item": "Bucks (tier A): one 6.8 V rail for both arms, one 5-6 V rail for the head servos, one 5.1 V for the Pi",
               "notes": "Same DROK module as researched (price and source there). One shared arm rail: the arms' worst-case stall sum exceeds 10 A, so the motion code staggers moves and the rail is fused at 10 A; brown-out under a full simultaneous stall is a known tier-A limit."},
    "servo_ext": {"group": "power", "item": "Servo extension leads, 300 mm, 10-pack", "choice": "Generic 300 mm male-female servo extension, 26 AWG, JR/Futaba (10 pcs)",
                  "unit_price_usd": 9.95, "vendor": "eBay (US seller)", "price_source_url": "https://www.ebay.de/itm/335657377415", "price_date": "2026-10-24",
                  "confidence": "from listing/secondary source", "notes": "Search snippet of a listing captured in 2025; replaces the 18 AWG spool for servo runs in tier A."},
    "inline_fuse": {"group": "power", "item": "Inline ATC fuse holder, 12 AWG", "choice": "Eaton Bussmann BK/HHD ATC in-line fuse holder, 12 Ga. leads (24 A)",
                    "unit_price_usd": 2.18, "vendor": "Waytek", "price_source_url": "https://www.waytekwire.com/product/eaton-s-bussmann-series-bk-hhd-atc-in-line-fuse", "price_date": "2026-10-24",
                    "confidence": "from listing/secondary source", "notes": "One per branch (Pi buck, head servo buck, arm servo buck, spare); replaces the 6-way fuse block in tier A. Waytek minimum order may apply."},
    "mg996r": {"group": "arm", "item": "Hand grip servos (tier A), MG996R 4-pack", "choice": "Hosyond MG996R 55 g metal-gear digital servo, 4-pack",
               "unit_price_usd": 16.99, "vendor": "Amazon", "price_source_url": "https://www.amazon.com/s?k=hosyond+mg996r+4+pack", "price_date": "2026-10-24", "amazon_tag": "missing (AMAZON_PARTNER_TAG unset)",
               "confidence": "from listing/secondary source", "notes": "Search-snippet price ($16.99, list $17.99). Grip only: two used, two spares. Torque not sourced; the grip is not a gravity joint."},
    "ply_quarter": {"group": "torso", "item": "1/4 in plywood, 2 x 4 ft project panel (torso ribs, tier A)", "choice": "B/C Sanded Plywood Project Panel 1/4 in x 2 ft x 4 ft (Home Depot Internet # 205748601)",
                    "unit_price_usd": 11.22, "vendor": "Home Depot", "price_source_url": "https://homedepot.com/p/1-4-in-x-2-ft-x-4-ft-B-C-Sanded-Plywood-Project-Panel-00102/205748601", "price_date": "2026-10-24",
                    "confidence": "from listing/secondary source", "notes": "Cached page; store stock showed 0. Replaces the Baltic birch pack in tier A."},
}

SHARED_CORE = [  # every tier
    ("Homer Bucket", 1), ("Quikrete Concrete Mix", 1), ("PLUMBFLEX 1 in. x 36 in.", 1), ("Southland 1 in. Black Malleable", 1),
    ("Falken Design 3/4 in x 2 ft x 2 ft Birch", 1), ("Power Wheel Adapter for Milwaukee M18", 1), ("XH-M609", 1),
    ("22mm NC red mushroom", 1), ("Bussmann ATC fuse assortment", 1), ("BNTECHGO 12 AWG", 1), ("TiaoBug", 1), ("George Men", 1),
]
TIERS = {
    # tier A: the flannel shirt is bring-your-own (any old flannel); buying it adds $11.98
    "A": [r for r in SHARED_CORE if r[0] != "George Men"] + [
        ("NEW:servo_ext", 2), ("NEW:inline_fuse", 4), ("Amass XT60", 2),
        ("DIYmall 2 Sets 35kg DS3235", 2), ("DSSERVO DS3225 MG", 2), ("NEW:mg996r", 1),
        ("Adafruit 16-Channel 12-bit PWM/Servo Driver", 1), ("NEW:drok_a", 3), ("Grainger 1NAE3", 2),
        ("ELEGOO PETG PRO", 2), ("MYWISH 550-Piece M3", 1), ("NEW:ply_quarter", 1),
    ],
    "B": SHARED_CORE + [
        ("Sea-Dog blade style", 1), ("BNTECHGO 18 AWG", 1), ("Amass XT60", 3), ("Pololu D24V50F5", 1), ("NEW:drok_head", 1), ("Adafruit INA228", 1), ("TEMCo 24V 40A", 1),
        ("Kee Klamp 75-6", 1), ("Fun World Adult Giant Cartoon", 1),
        ("ST3215-C047 12V 30 kg.cm, 1:345 (Seeed SKU 108090003); equival", 14), ("Waveshare Bus Servo Adapter (A), SKU 25514", 2),
        ("EKYLIN 24V to 12V 20A", 2), ("GODIYMODULES", 2), ("Power Wheel Adapter for Milwaukee M18", 1),
        ("V-Slot 20x20mm", 10), ("Tee Nuts (25 Pack)", 3), ("Cast 90 Degree Corner", 24), ("M5 Low Profile Screws", 3),
        ("Phidgets GT2 Pulley 8mm bore 22 teeth", 6), ("Phidgets GT2 Pulley 8mm bore 60 teeth", 6), ("closed-loop timing belt 6 mm x 220 mm", 6),
        ("Flanged Rotary Bearing for 8mm shaft", 6), ("precision ground rotary shaft", 1), ("Grainger 1NAE3", 2),
        ("ELEGOO PETG PRO", 3), ("ELEGOO TPU 95A", 1), ("MYWISH 550-Piece M3", 1), ("CNC Kitchen Heat Set", 1),
    ],
    "C": SHARED_CORE + [
        ("Sea-Dog blade style", 1), ("BNTECHGO 18 AWG", 1), ("Amass XT60", 3), ("Pololu D24V50F5", 1), ("NEW:drok_pi5", 1), ("NEW:drok_head", 1), ("Adafruit INA228", 1), ("TEMCo 24V 40A", 1),
        ("Kee Klamp 75-6", 1),
        ("ST-3250-C001", 6), ("ST3215-C047 12V 30 kg.cm, 1:345 (Seeed SKU 108090003); equival", 6),
        ("Seeed Studio Amazing Hand (Right Hand)", 1), ("Seeed Studio Amazing Hand (Left Hand)", 1), ("D36V50F5 5 V 5.5 A step-down, item 4091", 2),
        ("Raspberry Pi 5 8 GB", 1), ("Raspberry Pi Active Cooler", 1), ("Waveshare Bus Servo Adapter (A), SKU 25514", 2),
        ("EKYLIN 24V to 12V 20A", 2), ("GODIYMODULES", 3), ("Power Wheel Adapter for Milwaukee M18", 1), ("Mean Well LRS-350-24", 1),
        ("V-Slot 20x20mm", 10), ("Tee Nuts (25 Pack)", 3), ("Cast 90 Degree Corner", 24), ("M5 Low Profile Screws", 3),
        ("Phidgets GT2 Pulley 8mm bore 22 teeth", 6), ("Phidgets GT2 Pulley 8mm bore 60 teeth", 6), ("closed-loop timing belt 6 mm x 220 mm", 6),
        ("Flanged Rotary Bearing for 8mm shaft", 6), ("precision ground rotary shaft", 1), ("Grainger 1NAE3", 2),
        ("ELEGOO PETG PRO", 3), ("ELEGOO TPU 95A", 1), ("MYWISH 550-Piece M3", 1), ("CNC Kitchen Heat Set", 1),
        ("JLCPCB", 1), ("LM74700QDBVRQ1", 3), ("TPS259824", 2), ("INA226AIDGSR", 3),
    ],
}
CAPS = {"A": 500, "B": 1200, "C": None}


def find(key):
    if key.startswith("NEW:"):
        return dict(NEW[key[4:]])
    hits = [r for r in SRC if key in r["choice"] and (r["unit_price_usd"] or 0) > 0]
    if not hits:
        hits = [r for r in SRC if key in r["choice"]]
    if not hits:
        raise SystemExit(f"no researched row for {key!r}")
    return dict(hits[0])


def main():
    out = {"generated": "2026-10-24", "note": "Prices are point-in-time (2026-10-24) and mostly from listings or search snippets; see each row's confidence.", "tiers": {}}
    md = ["# Joyful Jack: final bills of materials by tier", "",
          "Generated by `build_final_bom.py` from `20261024-bom.json` (researched 2026-10-24) plus the substitutions made to fit the caps. "
          "Prices are point-in-time and mostly from listings or search snippets; each row keeps its source and confidence in the JSON. "
          "The existing head (Raspberry Pi 4, PCA9685, head servos, camera) and the Milwaukee M18 packs are not counted (Mark, 2026-10-24).", ""]
    for t, rows in TIERS.items():
        lines, total, unknown = [], 0.0, []
        for key, qty in rows:
            r = find(key)
            unit = r.get("unit_price_usd")
            lt = None if unit is None else round(unit * qty, 2)
            if lt is None:
                unknown.append(r["choice"])
            else:
                total += lt
            lines.append({"group": r.get("group"), "item": r.get("item"), "choice": r["choice"], "qty": qty, "unit_price_usd": unit, "line_usd": lt,
                          "vendor": r.get("vendor"), "price_source_url": r.get("price_source_url"), "confidence": r.get("confidence"), "notes": r.get("notes")})
        cap = CAPS[t]
        out["tiers"][t] = {"total_usd": round(total, 2), "cap_usd": cap, "headroom_usd": None if cap is None else round(cap - total, 2), "unpriced": unknown, "lines": lines}
        md += [f"## Tier {t}: ${total:,.2f}" + (f" (cap ${cap:,}, headroom ${cap - total:,.2f})" if cap else " (no cap)"), "",
               "| Group | Item | Choice | Qty | Unit | Line |", "|---|---|---|---:|---:|---:|"]
        for l in sorted(lines, key=lambda l: (l["group"] or "", -(l["line_usd"] or 0))):
            md.append(f"| {l['group']} | {l['item']} | {l['choice'][:70]} | {l['qty']} | {'' if l['unit_price_usd'] is None else '$%.2f' % l['unit_price_usd']} | {'TBD' if l['line_usd'] is None else '$%.2f' % l['line_usd']} |")
        if unknown:
            md += ["", "Unpriced: " + "; ".join(unknown)]
        md.append("")
    json.dump(out, open(os.path.join(HERE, "20261024-bom-final.json"), "w"), indent=1)
    open(os.path.join(HERE, "20261024-bom-final.md"), "w").write("\n".join(md))
    for t, v in out["tiers"].items():
        print(t, v["total_usd"], "headroom", v["headroom_usd"], "unpriced", len(v["unpriced"]))


main()
