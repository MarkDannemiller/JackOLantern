"""BOM v2 per tier: quantities from the built model, prices from the sourcing files, totals computed here.

    python3 research/sourcing/build_bom_v2.py   ->  20261025-bom-v2.json and .md

Inputs (all generated or researched, nothing typed by hand except the pack choice per line):
  * protoboard/src/mech/tier-<t>.json + mech.json   every placed part, by part id
  * protoboard/out/mech/tier-<t>/scene.json         every fastener the stacks place
  * protoboard/docs/wiring/harness-<t>.json         cables and wire by gauge
  * 20261024-bom-final.json                         electronics, power, costume and base rows (kept)
  * 20261025-hardware-sourcing.json, -2.json        mechanical prices (point-in-time, 2026-10-24)

Rules:
  * packs are bought whole: qty = ceil(need / pack); fasteners get 10 % spare before packing
  * a socket-screw kit's per-size count is not stated by the sellers: assumed pack / sizes (TBD: confirm)
  * filament = printed mass x 1.15 (supports, purge, failed prints; assumption), whole 1 kg spools
  * extrusion is bin-packed into 500 mm bars with 3 mm kerf; ends tapped M5 by the builder
  * an item without a price is a TBD row: it counts as unpriced, never as $0
The old caps (A < $500, B <= $1200) are reported for comparison only: the user lifted them for this round.
"""
import json
import math
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
P = os.path.join(PROJECT, "protoboard")
OLD = json.load(open(os.path.join(HERE, "20261024-bom-final.json")))
SRC = []
for f in ("20261025-hardware-sourcing.json", "20261025-hardware-sourcing-2.json"):
    d = json.load(open(os.path.join(HERE, f)))
    SRC += d["entries"] if isinstance(d, dict) else d
MECH = json.load(open(os.path.join(P, "src", "mech", "mech.json")))["parts"]

# old rows the detailed model replaces (mechanics now come from the model)
DROP = ("PLUMBFLEX", "Kee Klamp", "Fun World", "Phidgets", "Grainger 1NAE3", "MYWISH", "CNC Kitchen", "Maker Store Tee Nuts",
        "M5 Low Profile", "V-Slot", "Cast 90", "ELEGOO PETG PRO")


def src(key):
    hits = [e for e in SRC if key in e["item"]]
    hits = [e for e in hits if e["price_usd"] is not None] or hits     # a priced listing over a TBD duplicate
    if not hits:
        raise KeyError(key)
    return hits[0]


def row(group, item, key, need, pack=None, note="", spare=1.0):
    e = src(key)
    pk = pack or (e["pack_qty"] if isinstance(e["pack_qty"], int) else 1)
    qty = math.ceil(need * spare / pk) if need else 0
    price = e["price_usd"]
    return dict(group=group, item=item, choice=e["item"], need=need, pack=pk, qty=qty, unit_price_usd=price,
                line_usd=round(qty * price, 2) if price is not None else None, vendor=e["vendor"], price_source_url=e["url"],
                confidence=e["price_status"], notes="; ".join(x for x in (note, e.get("notes", "")[:240]) if x))


def tbd(group, item, need, why):
    return dict(group=group, item=item, choice="TBD", need=need, pack=None, qty=need, unit_price_usd=None, line_usd=None,
                vendor="TBD", price_source_url=None, confidence="TBD", notes=why)


def binpack(lengths, bar=500, kerf=3):
    bars = []
    for L in sorted(lengths, reverse=True):
        for i, used in enumerate(bars):
            if used + L + kerf <= bar:
                bars[i] += L + kerf
                break
        else:
            bars.append(L + kerf)
    return len(bars)


def model(t):
    inst = json.load(open(os.path.join(P, "src", "mech", f"tier-{t}.json")))["instances"]
    parts = Counter(v["part"] for v in inst.values())
    hw = Counter(h["part"] for h in json.load(open(os.path.join(P, "out", "mech", f"tier-{t}", "scene.json")))["hardware"])
    harness = json.load(open(os.path.join(P, "docs", "wiring", f"harness-{t}.json")))
    return parts, hw, harness


def mech_rows(t):
    parts, hw, harness = model(t)
    R = []
    n = lambda k: parts.get(k, 0)
    # bearings, drives, balancer
    R.append(row("arm", "6806-2RS joint bearings", "6806-2RS bearing 30x42x7, 10-pack (DEEG)", n("bearing-6806-2rs")))
    R.append(row("arm", "625-2RS driver outboard bearings", "625-2RS bearing 5x16x5, 10-pack (C3)", n("bearing-625-2rs")))
    R.append(row("arm", "624-2RS balancer sheave bearings", "624-2RS bearing 4x13x5, 16-pack (uxcell)", n("bearing-624-2rs")))
    R.append(row("arm", "GT3 9 mm belts, 240 mm (shoulder joints)", "3GT (GT2-3M) closed belt 240 mm / 80T", n("gt3-belt-240-9mm"),
                 note="no working tension stated by the seller; the design load is 179.6 N rated, checked in the sim"))
    R.append(row("arm", "GT3 9 mm belts, 210 mm (elbow)", "3GT (GT2-3M) closed belt 210 mm / 70T", n("gt3-belt-210-9mm")))
    R.append(row("arm", "5 x 16 mm driver dowels", "Dowel pin 5x16 mm, 304 stainless, 15 pcs", n("dowel-5x16"),
                 note="NOT hardened: the design calls for ISO 8734 hardened pins (price TBD); stainless is a stand-in, check wear"))
    R.append(row("arm", "Century 90CS balancer springs", "Extension spring 0.625 OD, 27 lbf", n("spring-century-90cs")))
    R.append(row("arm", "2 mm Dyneema balancer cord", "2 mm Dyneema cord, 20 m, 200 kg", 1 if n("dyneema-2mm-260") else 0))
    R.append(row("arm", "Shoulder screws 5 x 8, M4", "Shoulder screw 5 mm x 8 mm shoulder, M4, 16 pcs", hw.get("iso7379-5x8", 0)))
    # fasteners, from the stacks (+10 % spare)
    S = 1.1
    R.append(row("fasteners", "Heat-set inserts M3", "Heat-set insert M3 x 5.7, 100 pcs (Prusa", hw.get("heatset-insert-m3", 0), spare=S))
    R.append(row("fasteners", "Heat-set inserts M4", "Heat-set insert M4 x 8.1, 50 pcs", hw.get("heatset-insert-m4", 0), spare=S,
                 note="3DJake price excludes VAT; US shipping from $32.01 (seller page)"))
    for d, key, sizes, avail in (("m3", "SHCS M3 kit", 8, (6, 8, 10, 12, 16, 20, 25, 30)), ("m4", "SHCS M4 kit", 7, (6, 8, 10, 12, 16, 20, 25)),
                                 ("m5", "SHCS M5 kit", 7, (8, 10, 12, 16, 20, 25, 30))):
        counts = {int(k.split("x")[1]): v for k, v in hw.items() if k.startswith(f"iso4762-{d}x")}
        inkit = {L: c for L, c in counts.items() if L in avail}
        if inkit:
            e = src(key)
            per = e["pack_qty"] // sizes
            R.append(row("fasteners", f"Socket head cap screws {d.upper()} ({', '.join(f'{L} mm x{c}' for L, c in sorted(inkit.items()))})",
                         key, max(inkit.values()), pack=per, spare=S,
                         note=f"kit assumed {per} per size ({e['pack_qty']} pcs / {sizes} sizes; TBD: confirm the per-size count)"))
        for L, c in counts.items():
            if L not in avail:
                R.append(row("fasteners", f"Socket head cap screws {d.upper()} x {L}", f"SHCS {d.upper()} x {L}", c, spare=S))
    for k, key in (("pa2x6", "M2 x 6 self-tapping"), ("pa2x8", "M2 x 8 self-tapping")):
        if hw.get(k):
            R.append(row("fasteners", f"Servo case screws {k.upper()}", key, hw[k], spare=S,
                         note="Feetech case screws are PA2 plastite; listing says self-tapping, thread form not confirmed"))
    for k, key in (("iso10511-m4", "M4 nylon-insert lock nut"), ("iso10511-m5", "M5 nylon-insert lock nut"),
                   ("iso7089-m4", "M4 flat washer"), ("iso7089-m5", "M5 flat washer")):
        if hw.get(k):
            R.append(row("fasteners", k, key, hw[k], spare=S))
    for k, key in (("hex-bolt-1-4-20x1in", "1/4-20 x 1 in hex bolt kit"), ("hex-bolt-1-4-20x1.25in", "1/4-20 x 1-1/4 in hex bolt kit")):
        if hw.get(k):
            R.append(row("base", f"{k} (kit includes the nylock nuts and washers)", key, hw[k]))
    if hw.get("wood-screw-8x1.25in"):
        R.append(row("torso", "#8 x 1-1/4 in wood screws (ply torso)", "#8 x 1-1/4 in flat head wood screw", hw["wood-screw-8x1.25in"]))
    if hw.get("wood-screw-8x0.75in"):
        R.append(tbd("torso", "#8 x 3/4 in wood screw", hw["wood-screw-8x0.75in"], "not priced; any hardware store loose item"))
    if hw.get("wood-screw-4x0.5in"):
        R.append(row("torso", "#4 x 1/2 in wood screws (trays, board)", "#4 x 1/2 in flat head wood screw", hw["wood-screw-4x0.5in"]))
    if hw.get("tee-nut-m5-hammer-in"):
        R.append(row("torso", "M5 hammer-in tee nuts", "M5 hammer-in tee nut", hw["tee-nut-m5-hammer-in"]))
    if hw.get("tnut-2020-m5"):
        R.append(row("torso", "M5 drop-in T-nuts for 2020", "Drop-in tee nut M5, 10-pack", hw["tnut-2020-m5"], spare=S))
    # frame
    if n("brac-90cast-20"):
        R.append(row("torso", "Cast 90 deg corner brackets, 20 series", "Cast 90 deg corner bracket 20 series", n("brac-90cast-20")))
    cuts = []
    for k, v in parts.items():
        if k.startswith("hfs5-2020-"):
            cuts += [int(k.split("-")[2])] * v
    if cuts:
        bars = binpack(cuts)
        old = next(l for l in OLD["tiers"]["B"]["lines"] if "V-Slot" in l["choice"])
        R.append(dict(group="torso", item=f"2020 extrusion, cut list {', '.join(f'{L} mm x{c}' for L, c in sorted(Counter(cuts).items()))}",
                      choice=old["choice"], need=sum(cuts), pack=500, qty=bars, unit_price_usd=old["unit_price_usd"],
                      line_usd=round(bars * old["unit_price_usd"], 2), vendor=old["vendor"], price_source_url=old["price_source_url"],
                      confidence=old["confidence"], notes="bin-packed into 500 mm bars, 3 mm kerf; tap the ends M5 (V-slot centre bore 4.2 mm)"))
        R.append(tbd("tools", "M5 tap and handle", 1, "for the extrusion ends; not priced"))
    # stock
    R.append(row("base", "1 in x 30 in black nipple (mast)", "1 in x 30 in Sch 40 black steel nipple", n("pipe-nipple-1x30")))
    R.append(row("torso", "6 mm 6061 plate for the neck plate (150 x 150)", "6061 aluminium plate 6 mm, 6 x 6 in", n("jj-neck-plate"),
                 note="cut and drill from the drawing in the build guide"))
    if n("jj-torso-base-plate"):
        R.append(row("torso", "Plate for the torso base plate (220 x 140)", "6061 aluminium plate 1/4 in, 6 x 12 in", 1,
                     note="1/4 in is 6.35 mm, not 6.0: the stacks were checked at 6 mm, 0.35 mm less engagement; alloy not confirmed"))
    if any(k.startswith("jj-torso-a-") for k in parts):
        R.append(row("torso", "1/2 in birch plywood for the tier A torso box", "1/2 in birch plywood project panel 2 x 4 ft", 1))
    if t != "a":  # tier A keeps its researched 1/4 in panel row, which covers the board too
        ply = next(l for l in OLD["tiers"]["A"]["lines"] if "B/C Sanded Plywood" in l["choice"])
        R.append({**ply, "item": "1/4 in plywood panel for the electronics board", "qty": 1, "line_usd": ply["unit_price_usd"]})
    # filament
    mass = Counter()
    for k, v in parts.items():
        p = MECH.get(k, {})
        if p.get("category") == "printed":
            mass[p.get("meta", {}).get("material", "petg")] += p.get("mass_g", 0) * v
    R.append(row("print", f"PETG-CF filament ({mass['petg-cf']:.0f} g printed)", "PETG-CF 1 kg (Elegoo)", mass["petg-cf"] * 1.15 / 1000, pack=1))
    R.append(row("print", f"PETG filament ({mass['petg']:.0f} g printed)", "PETG 1 kg (Elegoo Rapid PETG)", mass["petg"] * 1.15 / 1000, pack=1))
    # wiring
    bus = harness["bus_cables"]
    if bus:
        R.append(row("wiring", f"Feetech 5264 3-pin bus cables ({bus} in the chains)", "Feetech 5264 3P servo cable 900 mm, 6 pcs (Waveshare) - recheck", bus,
                     note="900 mm cut to the harness lengths; servos ship with one short cable each"))
    if n("jj-body-estop"):
        R.append(row("power", "E-stop enclosure", "E-stop enclosure, 1-hole yellow (Schneider XALK01H7) - recheck", 1))
    for g, mm in sorted(harness["totals_mm_by_awg"].items(), key=lambda x: int(x[0])):
        g = int(g)
        if g in (12, 18) and t != "a" or (g == 12):
            continue  # the kept 12 and 18 AWG spools cover these (checked below)
        if g == 22 and t == "a":
            continue  # servo extension leads (kept row)
        R.append(tbd("wiring", f"{g} AWG silicone wire, {mm / 1000:.1f} m (red and black counted)", 1, "not priced in the sourcing files"))
    return R


def kept_rows(t):
    out = []
    for l in OLD["tiers"][t.upper()]["lines"]:
        if any(k in l["choice"] for k in DROP):
            continue
        r = dict(l)
        if "Floor Flange" in l["choice"]:
            r["qty"] = 2  # top and bottom of the mast (model: floor-flange-1in x2)
            r["line_usd"] = round(2 * l["unit_price_usd"], 2)
        out.append(r)
    return out


def main():
    res = {"generated": "2026-10-25", "note": __doc__.split("Rules:")[1].strip(), "tiers": {}}
    caps = {"A": 500, "B": 1200, "C": None}
    for t in "abc":
        _, _, harness = model(t)
        lines = kept_rows(t) + mech_rows(t)
        lines = [l for l in lines if l.get("qty")]
        total = round(sum(l["line_usd"] or 0 for l in lines), 2)
        res["tiers"][t.upper()] = dict(total_usd=total, old_cap_usd=caps[t.upper()],
                                       unpriced=[l["item"] for l in lines if l["line_usd"] is None],
                                       by_group={g: round(sum(l["line_usd"] or 0 for l in lines if l["group"] == g), 2)
                                                 for g in sorted({l["group"] for l in lines})},
                                       wire_m_by_awg={g: round(v / 1000, 1) for g, v in harness["totals_mm_by_awg"].items()},
                                       lines=lines)
    json.dump(res, open(os.path.join(HERE, "20261025-bom-v2.json"), "w"), indent=1)
    md = ["# BOM v2 per tier (generated by build_bom_v2.py; do not edit)", "",
          "Quantities come from the built model; prices are point-in-time (2026-10-24). Rules at the end.", ""]
    for t, v in res["tiers"].items():
        md += [f"## Tier {t}: ${v['total_usd']:,.2f}" + (f" (old cap ${v['old_cap_usd']})" if v["old_cap_usd"] else ""), "",
               "By group: " + ", ".join(f"{g} ${x:,.2f}" for g, x in v["by_group"].items()), ""]
        if v["unpriced"]:
            md += ["Unpriced (TBD): " + "; ".join(v["unpriced"]), ""]
        md += ["| Group | Item | Choice | Need | Qty | Unit $ | Line $ | Vendor | Confidence |", "|---|---|---|---:|---:|---:|---:|---|---|"]
        for l in v["lines"]:
            need = l.get("need", l["qty"])
            need = f"{need:.2f}" if isinstance(need, float) else need
            md.append(f"| {l['group']} | {l['item']} | {l['choice'][:70]} | {need} | {l['qty']} | "
                      f"{'' if l['unit_price_usd'] is None else f'{l['unit_price_usd']:.2f}'} | {'TBD' if l['line_usd'] is None else f'{l['line_usd']:.2f}'} | "
                      f"{l['vendor']} | {l['confidence']} |")
        md.append("")
    md += ["## Rules", "", res["note"], ""]
    open(os.path.join(HERE, "20261025-bom-v2.md"), "w").write("\n".join(md))
    for t, v in res["tiers"].items():
        print(t, v["total_usd"], v["by_group"], "unpriced:", len(v["unpriced"]))


if __name__ == "__main__":
    main()
