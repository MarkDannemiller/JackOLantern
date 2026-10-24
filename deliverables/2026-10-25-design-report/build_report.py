"""Build the Joyful Jack design report (HTML) from the project's own data.

    python3 deliverables/2026-10-25-design-report/build_report.py [--assets assets.json]

Reads research/sourcing/20261025-bom-v2.json (prices from the model's quantities), protoboard/docs/sim-results.json
(Isaac Sim), the full-hardware model (protoboard/src/mech, out/mech/tier-<t>/scene.json), the harness lists
(protoboard/docs/wiring) and writes index.html next to this file. Media are referenced as media/<name> (local
copy); with --assets, a JSON map {name: url} from the published artifact's asset store replaces them (published
copy: published.html).
"""
import html
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
PB = os.path.join(PROJ, "protoboard")
BOM = json.load(open(os.path.join(PROJ, "research", "sourcing", "20261025-bom-v2.json")))
SIM = {(r["tier"], r["scenario"]): r for r in json.load(open(os.path.join(PB, "docs", "sim-results.json")))}
PARTS = json.load(open(os.path.join(PB, "src", "mech", "mech.json")))["parts"]
ASSETS = json.load(open(sys.argv[sys.argv.index("--assets") + 1])) if "--assets" in sys.argv else None
BELT_RATED = 179.6


def model_counts(t):
    sc = json.load(open(os.path.join(PB, "out", "mech", f"tier-{t}", "scene.json")))
    inst = [i for i in sc["instances"] if not i["id"].startswith("costume/")]
    cats = Counter(PARTS.get(i["part"], {}).get("category") for i in inst)
    printed_g = sum(PARTS[i["part"]].get("mass_g") or 0 for i in inst if PARTS.get(i["part"], {}).get("category") == "printed")
    harness = json.load(open(os.path.join(PB, "docs", "wiring", f"harness-{t}.json")))
    return {"parts": len(inst), "printed": cats["printed"], "bought": cats["bought"], "fasteners": len(sc["hardware"]),
            "printed_kg": printed_g / 1000, "cables": len(harness["cables"]), "joints": len(sc["joints"])}


MC = {t: model_counts(t) for t in "abc"}
GUIDES = os.path.join(PROJ, "deliverables", "2026-10-25-build-guides")


def _pages(f):
    import subprocess
    out = subprocess.run(["pdfinfo", f], capture_output=True, text=True).stdout
    return int(next(l.split()[-1] for l in out.splitlines() if l.startswith("Pages:")))


GUIDE_PAGES = {t: _pages(os.path.join(GUIDES, f"joyful-jack-tier-{t}-build-guide.pdf")) for t in "abc"}
TIP = {t: (SIM[(t, "push-bal")]["tip_force_N"], SIM[(t + "+sandbags2", "push-bal")]["tip_force_N"]) for t in "abc"}


def m(name):
    if ASSETS is not None:
        return ASSETS[name]
    return f"media/{name}"


def money(x):
    return f"${x:,.0f}" if x >= 100 else f"${x:,.2f}"


T = {k.lower(): v for k, v in BOM["tiers"].items()}
GROUP_NAMES = {"arm": "Arms, motors, belts", "power": "Power and safety", "base": "Base and pole", "torso": "Torso frame",
               "costume": "Costume", "fasteners": "Screws and fittings", "control": "Controllers and computer", "hand": "Hands",
               "print": "3D-printing filament", "wiring": "Wiring", "tools": "Tools"}
GROUP_ORDER = ["arm", "hand", "power", "control", "torso", "base", "fasteners", "print", "wiring", "costume", "tools"]


def groups(t):
    g = {}
    for l in T[t]["lines"]:
        g[l["group"]] = g.get(l["group"], 0) + (l["line_usd"] or 0)
    return g


def cost_bars(t):
    g = groups(t)
    total = T[t]["total_usd"]
    rows = []
    for k in GROUP_ORDER:
        if k not in g:
            continue
        pct = g[k] / total * 100
        rows.append(f'<div class="bar"><span class="bar-label">{GROUP_NAMES.get(k, k)}</span>'
                    f'<span class="bar-track"><span class="bar-fill" style="width:{pct:.1f}%"></span></span>'
                    f'<span class="bar-val">{money(g[k]) if g[k] else "TBD"}</span></div>')
    return "\n".join(rows)


def bom_table(t):
    rows = []
    for l in sorted(T[t]["lines"], key=lambda l: (GROUP_ORDER.index(l["group"]) if l["group"] in GROUP_ORDER else 99, -(l["line_usd"] or 0))):
        link = f'<a href="{html.escape(l["price_source_url"] or "#")}" rel="noopener">source</a>' if l.get("price_source_url") else ""
        rows.append(f"<tr><td>{GROUP_NAMES.get(l['group'], l['group'])}</td><td>{html.escape(l['item'] or '')}<div class='choice'>{html.escape(l['choice'][:110])}</div></td>"
                    f"<td class='num'>{l['qty']}</td><td class='num'>{money(l['unit_price_usd']) if l['unit_price_usd'] is not None else 'TBD'}</td>"
                    f"<td class='num'>{money(l['line_usd']) if l['line_usd'] is not None else 'TBD'}</td><td>{link}</td></tr>")
    return ("<div class='table-wrap'><table class='bom'><thead><tr><th>Group</th><th>Item</th><th class='num'>Qty</th><th class='num'>Each</th>"
            "<th class='num'>Line</th><th>Price from</th></tr></thead><tbody>" + "\n".join(rows) +
            f"</tbody><tfoot><tr><td colspan='4'>Total{' (TBD rows not included)' if T[t]['unpriced'] else ''}</td><td class='num'>{money(T[t]['total_usd'])}</td><td></td></tr></tfoot></table></div>")


TIERS = [
    {"key": "a", "name": "Beginner", "cap": "was under $500", "tag": "A", "who": "A first build: hobby servos, plywood torso, and still a character people stop for.",
     "can": ["Waves: lifts his arm forward and up and waves from the elbow", "Grips a light candy bag with a one-motor mitt",
             "Shoulder springs carry the arm's weight, so the small motors only move it", "Runs on one M18 pack with a low-battery cut-off", "Big red stop button on his back"],
     "cant": ["Feel when he touches someone (no feedback from the motors)", "Twist his upper arm or wrist", "Swap the battery without switching off"],
     "how": "Eight hobby servos, the kind used in RC cars: at each shoulder two 35 kg·cm servos, at the elbow a 25 kg·cm one, each driving its joint through a 3:1 toothed belt, plus one in each mitt. A second servo board joins the one already in the head, so the head's computer runs everything. The torso is a box of 12 mm birch plywood on the steel pole.",
     "hand": "A cartoon mitt: three fingers as one paddle close against a thumb, driven by one servo on a shoulder-bolt pivot. Rubber pads give it grip.",
     "joints": "3 + grip", "hands": "Mitt, 1 motor", "battery": "1 pack", "feel": "No", "swap": "No", "brains": "Head computer"},
    {"key": "b", "name": "Midrange", "cap": "was up to $1,200", "tag": "B", "who": "The one to build for a season of events: smart motors, safer, and he never has to sleep.",
     "can": ["Waves properly: the upper arm twists, so the hand comes up palm out", "Glove hands that open and close around a cup or a bag handle",
             "Every motor reports its position, load and temperature", "Two battery packs: pull one while the other keeps him going", "Tells you when the battery is getting low"],
     "cant": ["Move individual fingers", "Hold an arm straight out to the side for long (shown in the simulation below)"],
     "how": "Fourteen Feetech STS3215 smart servos, the motors used in popular open-source robot arms. At each shoulder and elbow the servo drives a hollow hub on two thin bearings through a 3:1 toothed belt; the upper-arm and wrist twists are driven directly. A spring-and-cable balancer at each shoulder carries the arm's weight. An aluminium frame in the torso carries two Milwaukee packs, joined so one can be swapped live.",
     "hand": "A glove hand in a big cartoon glove: four fingers linked to close together around an object, and a separately driven thumb.",
     "joints": "5 + 2-motor hand", "hands": "Glove, 2 motors", "battery": "2 packs, hot swap", "feel": "Yes", "swap": "Yes", "brains": "Head computer"},
    {"key": "c", "name": "Maxed", "cap": "no cap set", "tag": "C", "who": "The show piece: real robot hands with fingers that each move on their own.",
     "can": ["Humanoid hands: four fingers, each with two moving joints", "A wrist that bends as well as twists, for a hat-tip like the concept art",
             "Batteries plus wall power, so he can run all day indoors", "His own computer in the chest for the arms and hands"],
     "cant": ["Thumbs (the hand used has four fingers, which suits a cartoon)", "Strong grip: the hand's grip force is not published"],
     "how": "Tier B's arm, upgraded: stronger 50 kg·cm STS3250 motors at both shoulder joints and the elbow (still through belts), plus a wrist that bends. Each hand is a Pollen Robotics AmazingHand: an open-source hand with eight tiny motors in the palm. A Raspberry Pi 5 in the chest runs the arms and hands. A mains supply joins the two battery packs.",
     "hand": "The Pollen AmazingHand: four fingers, two joints each, eight micro servos, 400 g. Open source (designs CC BY 4.0), sold as a kit by Seeed Studio.",
     "joints": "6 + 8-motor hand", "hands": "Humanoid, 8 motors", "battery": "2 packs + wall", "feel": "Yes", "swap": "Yes", "brains": "Own computer"},
]

SCEN = [("wave-bal-lim", "Wave", "forearm up, waving for 10 s"), ("wave-lim", "Wave, springs removed", "the same, without the shoulder balancer"), ("reach-bal-lim", "Reach and grip", "arm forward, hand closes"),
        ("hold-bal-lim", "Arm straight out", "to the side, then forward, 7 s each (stress test)"), ("estop-bal-lim", "Emergency stop", "power cut at full reach")]


def sim_verdict(r):
    """One line per scenario: did every gravity joint keep up, and how hard did it work."""
    js = [r[j] for j in ("r_j1", "r_j2", "r_j4") if j in r]
    if r["scenario"].startswith("estop"):
        return "ok", "The arms drop to their rest stops and nothing falls."
    err = max(j["err_deg"] for j in js)
    load = max(j["stall_frac_max"] for j in js)
    belt = max(j["belt_N_max"] for j in js)
    sat = max(j["sat_frac"] for j in js)
    good = err < 5 and sat < 0.05
    detail = (f"worst joint {load * 100:.0f}% of motor max, within {err:.0f}° of target, "
              + ("belt briefly at its limit" if belt >= 0.99 * BELT_RATED else f"belts at {belt / BELT_RATED * 100:.0f}% of rating"))
    if not good:
        detail = f"the shoulder can't hold it: {err:.0f}° short of target, at its limit {sat * 100:.0f}% of the time"
    return ("ok" if good else "no"), detail


def sim_table(t):
    rows = []
    for key, name, what in SCEN:
        r = SIM.get((t, key))
        if not r:
            continue
        v, d = sim_verdict(r)
        rows.append(f"<tr><td><b>{name}</b><div class='choice'>{what}</div></td><td class='{'okc' if v == 'ok' else 'noc'}'>{'Passes' if v == 'ok' else 'Limit'}</td><td>{d}</td></tr>")
    return "<table class='mini sim'>" + "".join(rows) + "</table>"


def tier_section(d):
    t = d["key"]
    can = "".join(f"<li>{x}</li>" for x in d["can"])
    cant = "".join(f"<li>{x}</li>" for x in d["cant"])
    total = T[t]["total_usd"]
    mc = MC[t]
    unpriced = len(T[t]["unpriced"])
    budget_line = f"{money(total)} in new parts" + (f", plus {unpriced} small items not yet priced" if unpriced else "")
    return f"""
<section class="tier" id="tier-{t}">
  <div class="wrap">
    <header class="tier-head">
      <span class="tier-letter">{d['tag']}</span>
      <div><p class="eyebrow">Tier {d['tag']} · {d['cap']}</p><h2>{d['name']}</h2><p class="lede">{d['who']}</p></div>
      <div class="price-tag"><span class="price">{money(total)}</span><span class="price-note">new parts{'; your own flannel shirt' if t == 'a' else ''}</span></div>
    </header>
    <div class="tier-grid">
      <figure class="hero-fig"><img src="{m(f'hero-{t}.jpg')}" alt="Tier {d['tag']} Joyful Jack, rendered" loading="lazy"></figure>
      <div class="tier-text">
        <h3>How he works</h3><p>{d['how']}</p>
        <h3>What he can do</h3><ul class="ticks">{can}</ul>
        <h3>What he can't</h3><ul class="crosses">{cant}</ul>
        <p class="counts"><b>{mc['parts']}</b> parts · <b>{mc['fasteners']}</b> screws, nuts and inserts · <b>{mc['cables']}</b> cables · <b>{mc['printed_kg']:.1f} kg</b> of printed parts</p>
      </div>
    </div>
    <div class="pair">
      <figure><img src="{m(f'arm-{t}.jpg')}" alt="Tier {d['tag']} arm, costume off" loading="lazy"><figcaption><b>The arm, every part modelled.</b> Belt-driven shoulder and elbow hubs on thin bearings, the servos, the screws that hold them, and the {'mitt' if t == 'a' else 'glove hand' if t == 'b' else 'AmazingHand'}.</figcaption></figure>
      <figure><img src="{m(f'shoulder-{t}.jpg')}" alt="Tier {d['tag']} shoulder and balancer" loading="lazy"><figcaption><b>The shoulder.</b> Two extension springs on the torso pull a Dyneema cord over pulleys to a lever on the shoulder hub: a "zero-length spring" balancer that cancels most of the arm's weight at every angle.</figcaption></figure>
    </div>
    <div class="pair">
      <figure><img src="{m(f'hands-{t}.jpg')}" alt="Tier {d['tag']} hands" loading="lazy"><figcaption><b>The hands.</b> {d['hand']}</figcaption></figure>
      <figure><img src="{m(f'internals-back-{t}.jpg')}" alt="Tier {d['tag']} from behind, costume off" loading="lazy"><figcaption><b>From behind.</b> The battery {'pack' if t == 'a' else 'packs'} (red) in {'its dock' if t == 'a' else 'their docks'}, the stop button, and the electronics board.</figcaption></figure>
    </div>
    <div class="pair">
      <figure><img src="{m(f'exploded-{t}.jpg')}" alt="Tier {d['tag']} exploded view" loading="lazy"><figcaption><b>Every part, pulled apart.</b> Base and pole stay put, the torso lifts, the arms move out, the head rises, and every screw lifts out of its hole.</figcaption></figure>
      <div class="facts">
        <h3>Proven in simulation</h3>
        <p class="small">The whole robot in NVIDIA Isaac Sim with real masses from the 3D model, a 0.25 kg bag in the right hand, the shoulder springs on, and each motor limited so no belt is pulled past its rating.</p>
        {sim_table(t)}
        <h3>Where the money goes</h3>
        <p class="budget">{budget_line}</p>
        <div class="bars">{cost_bars(t)}</div>
      </div>
    </div>
    <figure class="diagram"><img src="{m(f'diagram-{t}.jpg')}" alt="Tier {d['tag']} system in Protoboard" loading="lazy"><figcaption><b>The wiring, in Protoboard.</b> Every box is a real part with its voltages; Protoboard checked every connection: {('0 problems' if t != 'c' else '0 errors, 2 notes explained in the decision log')}.</figcaption></figure>
    <div class="guide-row"><a class="guide" href="{m(f'joyful-jack-tier-{t}-build-guide.pdf')}">Build guide, tier {d['tag']} (PDF, {GUIDE_PAGES[t]} pages)</a><span class="small">Step-by-step assembly with every part, screw and torque, made by the Protoboard stack from the same model.</span></div>
    <details><summary>Full parts list for tier {d['tag']} ({len(T[t]['lines'])} lines)</summary>{bom_table(t)}</details>
  </div>
</section>"""


def compare_table():
    rows = [("Price (new parts)", [money(T[d["key"]]["total_usd"]) for d in TIERS]),
            ("Moving joints, each arm", [d["joints"] for d in TIERS]),
            ("Hands", [d["hands"] for d in TIERS]),
            ("Feels resistance", [d["feel"] for d in TIERS]),
            ("Battery", [d["battery"] for d in TIERS]),
            ("Swap a battery while running", [d["swap"] for d in TIERS]),
            ("Runs the arms", [d["brains"] for d in TIERS]),
            ("Parts / screws and fittings", [f"{MC[d['key']]['parts']} / {MC[d['key']]['fasteners']}" for d in TIERS]),
            ("Build guide", [f"{GUIDE_PAGES[d['key']]} pages" for d in TIERS])]
    head = "".join(f"<th>Tier {d['tag']}<span>{d['name']}</span></th>" for d in TIERS)
    body = "".join(f"<tr><th scope='row'>{r}</th>" + "".join(f"<td>{v}</td>" for v in vals) + "</tr>" for r, vals in rows)
    return f"<div class='table-wrap'><table class='compare'><thead><tr><th></th>{head}</tr></thead><tbody>{body}</tbody></table></div>"



CSS = """
<style>
/* Layout: a dusk-lit long read. One pumpkin accent, LED-blue second, bone text on night; paper in light theme. */
:root{
  --bg:#f3eee6; --panel:#fffaf2; --ink:#20160f; --muted:#6c5d50; --line:#e2d6c6;
  --pumpkin:#c8530f; --pumpkin-soft:#f2d2bb; --led:#2563c9; --good:#2f7d43; --bad:#a23a2a;
  --display:"Rye", "Georgia", serif; --head:"Zilla Slab", "Rockwell", Georgia, serif; --body:"Source Sans 3", "Segoe UI", system-ui, sans-serif; --mono:"IBM Plex Mono", ui-monospace, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0f1116; --panel:#171a22; --ink:#efe6d6; --muted:#a39886; --line:#2a2e39; --pumpkin:#ef7a2a; --pumpkin-soft:#3a2416; --led:#6ea2ff; --good:#7ccf8e; --bad:#ef8f7c; color-scheme: dark } }
:root[data-theme="dark"]{ --bg:#0f1116; --panel:#171a22; --ink:#efe6d6; --muted:#a39886; --line:#2a2e39; --pumpkin:#ef7a2a; --pumpkin-soft:#3a2416; --led:#6ea2ff; --good:#7ccf8e; --bad:#ef8f7c; color-scheme: dark }
body{background:var(--bg); color:var(--ink); font-family:var(--body); font-size:17px; line-height:1.6}
.wrap{max-width:1120px; margin:0 auto; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px))}
h1,h2,h3{font-family:var(--head); line-height:1.15; text-wrap:balance; margin:0}
h2{font-size:clamp(28px,4vw,40px)} h3{font-size:20px; margin-top:22px; margin-bottom:6px}
p{margin:0 0 12px} .lede{font-size:19px; color:var(--muted); max-width:62ch}
.eyebrow{font-family:var(--mono); font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--pumpkin); margin-bottom:6px}
a{color:var(--led)} a:focus-visible, summary:focus-visible{outline:2px solid var(--led); outline-offset:3px}
img,video{max-width:100%; display:block; border-radius:6px}
figure{margin:0} figcaption{font-size:15px; color:var(--muted); margin-top:8px; max-width:70ch}
figcaption b{color:var(--ink)}
.small{font-size:14px; color:var(--muted)}
/* masthead */
.mast{background:#0b0c10; color:#efe6d6; padding-block:36px 0}
.mast .wrap{display:grid; gap:20px}
.mast h1{font-family:var(--display); font-weight:400; font-size:clamp(46px,9vw,104px); color:#ef7a2a; letter-spacing:.01em}
.mast .sub{font-size:clamp(18px,2.3vw,23px); max-width:58ch; color:#d9cdb9}
.mast .meta{font-family:var(--mono); font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#a39886}
.mast img{border-radius:0; width:100%}
.mast .mast-strip{display:flex; flex-wrap:wrap; gap:10px 32px; padding-block:16px 28px}
.mast-strip div{display:flex; flex-direction:column} .mast-strip b{font-family:var(--head); font-size:26px; color:#efe6d6}
.mast-strip span{font-size:13px; color:#a39886}
section{padding-block:56px}
section + section{border-top:1px solid var(--line)}
.story{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px; margin-top:22px}
.story figure{background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:10px}
.story img{aspect-ratio:3/4; object-fit:cover; width:100%}
.cards{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px; margin-top:26px}
.card{background:var(--panel); border:1px solid var(--line); border-radius:10px; overflow:hidden; display:flex; flex-direction:column}
.card img{border-radius:0; aspect-ratio:4/5; object-fit:cover; object-position:center 20%}
.card .card-body{padding:16px 18px 20px; display:flex; flex-direction:column; gap:6px; min-width:0}
.card h3{margin:0; font-size:24px} .card .price{font-family:var(--head); font-size:30px; color:var(--pumpkin)}
.card a.more{margin-top:auto; font-weight:600; text-decoration:none}
.rec{margin-top:26px; background:var(--pumpkin-soft); border-left:4px solid var(--pumpkin); padding:16px 20px; border-radius:6px}
.rec b{font-family:var(--head); font-size:19px}
.table-wrap{overflow-x:auto; margin-top:16px}
table{border-collapse:collapse; width:100%; font-size:15px}
th,td{padding:9px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top}
.compare thead th{font-family:var(--head); font-size:20px} .compare thead th span{display:block; font-family:var(--body); font-size:13px; color:var(--muted); font-weight:400}
.compare tbody th{font-weight:600; color:var(--muted); font-size:14px}
.num{text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap}
.tier-head{display:grid; grid-template-columns:auto 1fr auto; gap:20px; align-items:center; margin-bottom:24px}
.tier-letter{font-family:var(--display); font-size:64px; color:var(--pumpkin); line-height:1}
.price-tag{text-align:right} .price-tag .price{font-family:var(--head); font-size:38px; display:block; font-variant-numeric:tabular-nums}
.price-tag .price-note{font-size:13px; color:var(--muted)}
.tier-grid{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:28px; align-items:start}
.hero-fig img{width:100%}
.tier-text{min-width:0}
ul.ticks, ul.crosses{list-style:none; padding:0; margin:0; display:grid; gap:6px}
ul.ticks li::before{content:"✓"; color:var(--good); font-weight:700; margin-right:8px}
ul.crosses li::before{content:"–"; color:var(--bad); font-weight:700; margin-right:10px}
.pair{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:24px; margin-top:28px; align-items:start}
.facts{min-width:0} .facts h3:first-child{margin-top:0}
.budget{font-family:var(--head); font-size:18px}
.bars{display:grid; gap:7px}
.bar{display:grid; grid-template-columns:minmax(0,11em) 1fr auto; gap:10px; align-items:center; font-size:14px}
.bar-track{height:10px; background:var(--line); border-radius:5px; overflow:hidden}
.bar-fill{display:block; height:100%; background:var(--pumpkin)}
.bar-val{font-variant-numeric:tabular-nums; color:var(--muted)}
.mini{font-size:14px} .mini th{color:var(--muted); font-weight:600}
.diagram{margin-top:28px} .diagram img{border:1px solid var(--line)}
details{margin-top:22px; background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px 16px}
summary{cursor:pointer; font-weight:600}
.bom .choice{font-size:12.5px; color:var(--muted)} .bom tfoot td{font-weight:700}
.videos{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:20px}
.feature-video{margin-top:22px}
.grid2{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:28px; margin-top:20px}
.callout{background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px 18px}
.callout h3{margin-top:0}
ol.steps{padding-left:20px; display:grid; gap:8px} ol.steps li{padding-left:4px}
.counts{margin-top:16px; font-size:15px; color:var(--muted)} .counts b{color:var(--ink); font-variant-numeric:tabular-nums}
.sim td{vertical-align:top} .sim .choice{font-size:12.5px; color:var(--muted)}
.okc{color:var(--good); font-weight:700; white-space:nowrap} .noc{color:var(--bad); font-weight:700; white-space:nowrap}
.guide-row{display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; margin-top:22px}
a.guide{display:inline-block; background:var(--pumpkin); color:#fff; text-decoration:none; font-weight:700; padding:10px 16px; border-radius:6px}
a.guide:hover{filter:brightness(1.08)}
.foot{font-size:14px; color:var(--muted); padding-block:40px}
code{font-family:var(--mono); font-size:.88em; background:var(--panel); border:1px solid var(--line); padding:1px 5px; border-radius:4px; overflow-wrap:anywhere}
@media (max-width:820px){
  .story,.cards,.videos{grid-template-columns:1fr}
  .tier-grid,.pair,.grid2{grid-template-columns:1fr}
  .tier-head{grid-template-columns:auto 1fr} .price-tag{grid-column:1/-1; text-align:left}
}
@media (prefers-reduced-motion: reduce){ *{scroll-behavior:auto} }
</style>
"""


def page():
    tiers_html = "".join(tier_section(d) for d in TIERS)
    cards = "".join(f"""<article class="card"><img src="{m(f'hero-{d['key']}.jpg')}" alt="Tier {d['tag']}" loading="lazy">
      <div class="card-body"><p class="eyebrow">Tier {d['tag']} · {d['cap']}</p><h3>{d['name']}</h3><span class="price">{money(T[d['key']]['total_usd'])}</span>
      <p>{d['who']}</p><a class="more" href="#tier-{d['key']}">See tier {d['tag']} →</a></div></article>""" for d in TIERS)
    vid = lambda name, poster, label: f"""<figure><video controls muted playsinline preload="metadata" poster="{m(poster)}"><source src="{m(name)}" type="video/mp4"></video><figcaption>{label}</figcaption></figure>"""
    tip_lo, tip_hi = min(v[0] for v in TIP.values()), max(v[0] for v in TIP.values())
    sb_lo, sb_hi = min(v[1] for v in TIP.values()), max(v[1] for v in TIP.values())
    nparts = MC["b"]["parts"] + MC["b"]["fasteners"]
    return f"""<title>Joyful Jack Design Report</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rye&family=Zilla+Slab:wght@500;700&family=Source+Sans+3:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}
<header class="mast">
  <div class="wrap">
    <p class="meta">Delta Robotics · design report, revision 2 · 25 Oct 2026 · draft for Mark's review</p>
    <h1>Joyful Jack</h1>
    <p class="sub">A body and two moving arms for our animatronic pumpkin cowboy, designed three ways, every screw modelled, each with a step-by-step build guide, and tested in a physics simulation before anything is bought.</p>
  </div>
  <img src="{m('lineup.jpg')}" alt="Tiers A, B and C side by side">
  <div class="wrap mast-strip">
    <div><b>{money(T['a']['total_usd'])}</b><span>Tier A, Beginner</span></div>
    <div><b>{money(T['b']['total_usd'])}</b><span>Tier B, Midrange</span></div>
    <div><b>{money(T['c']['total_usd'])}</b><span>Tier C, Maxed</span></div>
    <div><b>{nparts}</b><span>parts and fasteners in tier B</span></div>
    <div><b>Milwaukee M18</b><span>battery packs</span></div>
  </div>
</header>

<section id="story"><div class="wrap">
  <p class="eyebrow">Where Jack comes from</p>
  <h2>A head that already works, looking for a body</h2>
  <p class="lede">Jack's head was built in 2023: printed orange face, glowing blue eyes, blinking eyelids, a talking jaw, and a neck that turns and nods. A camera in his nose finds faces so he can look at whoever walks up, and he has a few dozen cowboy voice lines. This project gives him a torso, two arms and hands, and a battery so he can stand on his own all evening.</p>
  <div class="story">
    <figure><img src="{m('concept-sketch.jpg')}" alt="Original notebook sketch" loading="lazy"><figcaption><b>The first sketch.</b> A scarecrow on a pole, no legs, a heavy base.</figcaption></figure>
    <figure><img src="{m('head-real.jpg')}" alt="The real head" loading="lazy"><figcaption><b>The real head.</b> Reused as-is in every tier.</figcaption></figure>
    <figure><img src="{m('concept-art.jpg')}" alt="Concept art" loading="lazy"><figcaption><b>The character.</b> Hat, bandana, tattered vest, weathered orange arm shells.</figcaption></figure>
  </div>
</div></section>

<section id="choices"><div class="wrap">
  <p class="eyebrow">The three versions</p>
  <h2>Pick how much Jack can do</h2>
  <p class="lede">All three share the same head, base, costume and battery system. They differ in the arms, the hands and how much they can sense.</p>
  <div class="cards">{cards}</div>
  {compare_table()}
  <div class="rec"><b>Recommendation: build tier B.</b> It is still the best value: motors that feel resistance make Jack safer around children, and two batteries mean he never has to stop. Modelling every part raised all three prices: proper bearings, belts, shoulder springs and about 600 screws and inserts replace the rough first-pass joints, so tier B is now {money(T['b']['total_usd'])} against the old $1,200 cap and tier A {money(T['a']['total_usd'])} against $500. Tier C's hands can be added to a tier B Jack later, since the arms share the same frame, belts and wiring.</div>
</div></section>

<section id="shared"><div class="wrap">
  <p class="eyebrow">What every Jack has</p>
  <h2>How he stands, and what powers him</h2>
  <div class="grid2">
    <div>
      <h3>A bucket of concrete for feet</h3>
      <p>Jack has no legs. He stands on a steel pipe set into a 5-gallon bucket filled with concrete, about 44 kg, sitting on a 24-inch plywood disc that hides under his costume. The pipe screws into a floor flange cast into the concrete.</p>
      <h3>One battery system</h3>
      <p>He runs on the Milwaukee M18 packs we already own. A dock with a switch and a fuse takes the pack. A cut-off module switches everything off before the pack runs flat, because an M18 pack can't be relied on to protect itself without a Milwaukee tool attached. Converters then make the voltages each part needs.</p>
      <h3>A big red stop button</h3>
      <p>A latching emergency stop on his back cuts power to every motor at once, while the computer stays on. In tiers B and C the button holds a heavy-duty relay, so it also stops the hands.</p>
    </div>
    <div>
      <figure><img src="{m('internals-b.jpg')}" alt="Tier B with the costume off" loading="lazy"><figcaption><b>Costume off (tier B).</b> The aluminium frame on the steel pole, the shoulder springs either side, and the electronics board. Arms hang on their stops, so a power cut drops nothing.</figcaption></figure>
    </div>
  </div>
  <div class="grid2">
    <div class="callout">
      <h3>How long he runs</h3>
      <p>A 12 Ah pack holds about 216 watt-hours. We will measure Jack's real power draw on the bench. Until then, here are planning figures (assumed draws, 85% converter efficiency):</p>
      <table class="mini"><tr><th>If Jack averages</th><th class="num">12 Ah pack</th><th class="num">8 Ah pack</th></tr>
      <tr><td>30 W (mostly idle)</td><td class="num">~6 h</td><td class="num">~4 h</td></tr>
      <tr><td>50 W (regular gestures)</td><td class="num">~3.7 h</td><td class="num">~2.4 h</td></tr>
      <tr><td>80 W (busy all evening)</td><td class="num">~2.3 h</td><td class="num">~1.5 h</td></tr></table>
      <p class="small">Tiers B and C swap packs without stopping, and tier C can also run from the wall.</p>
    </div>
    <div class="callout">
      <h3>Keeping him upright</h3>
      <p>In the simulation, a push at shoulder height with both arms out tips him at {tip_lo:.0f}–{tip_hi:.0f} N (about {tip_lo / 9.81:.0f}–{tip_hi / 9.81:.0f} kg of force). A teenager leaning on his shoulder could do that.</p>
      <p><b>For events:</b> lay two 25 lb sandbags on the plywood disc under the costume: the simulation then needs {sb_lo:.0f}–{sb_hi:.0f} N, about a third more. Or tie the pole to a post.</p>
    </div>
  </div>
</div></section>

{tiers_html}

<section id="motion"><div class="wrap">
  <p class="eyebrow">See him move</p>
  <h2>Animations</h2>
  <p class="lede">A walkthrough of the recommended build, the physics simulation of its wave, then each tier taken apart and put back together.</p>
  <div class="feature-video">{vid('walkthrough-b.mp4', 'hero-b.jpg', '<b>System walkthrough, tier B.</b> The wave, the costume coming off, the battery packs and electronics, the shoulder springs, the arm and glove hand, and the head. 37 seconds.')}</div>
  <div class="feature-video">{vid('sim-wave-b.mp4', 'hero-b.jpg', '<b>Isaac Sim, tier B wave.</b> The physics simulation: real masses, a 0.25 kg bag in the hand, motors with their real torque and speed limits, shoulder springs on. Every joint keeps up and no belt passes its rating.')}</div>
  <div class="videos">
    {vid('explode-a.mp4', 'exploded-a.jpg', '<b>Tier A</b> exploded view')}
    {vid('explode-b.mp4', 'exploded-b.jpg', '<b>Tier B</b> exploded view')}
    {vid('explode-c.mp4', 'exploded-c.jpg', '<b>Tier C</b> exploded view')}
  </div>
</div></section>

<section id="next"><div class="wrap">
  <p class="eyebrow">Before we build</p>
  <h2>What still needs a decision or a test</h2>
  <div class="grid2">
    <div>
      <h3>Decisions for Mark</h3>
      <ol class="steps">
        <li>Which tier to build. Recommended: B, with C's hands as a later upgrade.</li>
        <li>Sign the design brief (it sets what "done" means: runtime per pack, tip test, gesture list).</li>
        <li>What Jack should hold: we assumed a 0.25 kg candy bag.</li>
        <li>Gestures: keep arms raised forward rather than straight out sideways (the simulation's one limit), or add a second spring at the shoulder-out joint.</li>
        <li>Indoor only, or outdoors too? Rain changes the electronics enclosure.</li>
        <li>Is the overall height (about 1.7 m with the hat) right?</li>
      </ol>
    </div>
    <div>
      <h3>Bench tests before the first event</h3>
      <ol class="steps">
        <li>Set each shoulder and elbow servo's torque limit (the simulation's belt limit) before the first power-up.</li>
        <li>Weigh the head (assumed 2 kg in the tip check).</li>
        <li>Measure average power with the arms moving, which sets the real runtime.</li>
        <li>Check the stop relay switches on reliably from a part-drained pack (tiers B and C).</li>
        <li>Set the low-battery cut-off from the cell datasheet (about 15–16 V).</li>
        <li>Tip test with sandbags, and a pinch check at every joint.</li>
      </ol>
    </div>
  </div>
  <div class="grid2">
    <div class="callout">
      <h3>Things we found in the existing head</h3>
      <p>Its code sets two pins by physical number while using the chip's own pin numbering, so the "power" pins for the neck limit switch may not exist. One file imports a misspelled library name, and voice lines use paths from the old computer. None of this affects the body design, but they are worth fixing when the software is next opened.</p>
    </div>
    <div class="callout">
      <h3>How sure are these numbers?</h3>
      <p>Prices were looked up on 24 Oct 2026, mostly from store listings, and will move; quantities come straight from the 3D model, packs bought whole. A few items (some wire gauges, an M5 tap) are not priced yet. The simulation uses the model's weights and the makers' motor ratings; the hobby servos publish no continuous rating, so we assumed a third of their maximum. The belt rating is the belt maker's figure. The head's 2 kg is an assumption until weighed. Nothing has been ordered.</p>
    </div>
  </div>
</div></section>

<footer class="wrap foot">
  <p>Built in the Protoboard stack: the head, body, arms and power systems of all three tiers are modelled and checked in <code>projects/internal/2026-10-24-joyful-jack/protoboard</code> (choose a tier with <code>JJ_TIER=a|b|c</code>). Mechanical model, every part and fastener: <code>protoboard/cad/mech</code>. Build guides: <code>protoboard release</code> 0.2.0-a/b/c. Simulation: NVIDIA Isaac Sim 6.2, <code>protoboard/cad/mech/sim</code>, results in <code>protoboard/docs/sim-results.md</code>. Wiring cut lists: <code>protoboard/docs/wiring</code>. Renders: Blender. Prices: <code>research/sourcing/20261025-bom-v2.md</code>. Decisions: <code>protoboard/docs/decisions.md</code>.</p>
</footer>
"""


out = os.path.join(HERE, "published.html" if ASSETS is not None else "index.html")
open(out, "w").write(page())
print("wrote", out)
