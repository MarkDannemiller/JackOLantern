"""Build the Joyful Jack design report (HTML) from the project's own data.

    python3 deliverables/2026-10-25-design-report/build_report.py [--assets assets.json]

Reads research/sourcing/20261024-bom-final.json (prices), protoboard/out/cad/analysis.json (sizing) and
writes index.html next to this file. Media are referenced as media/<name> (local copy); with --assets, a
JSON map {name: url} from the published artifact's asset store replaces them (published copy: published.html).
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
BOM = json.load(open(os.path.join(PROJ, "research", "sourcing", "20261024-bom-final.json")))
AN = json.load(open(os.path.join(PROJ, "protoboard", "out", "cad", "analysis.json")))
ASSETS = json.load(open(sys.argv[sys.argv.index("--assets") + 1])) if "--assets" in sys.argv else None


def m(name):
    if ASSETS is not None:
        return ASSETS[name]
    return f"media/{name}"


def money(x):
    return f"${x:,.0f}" if x >= 100 else f"${x:,.2f}"


T = {k.lower(): v for k, v in BOM["tiers"].items()}
GROUP_NAMES = {"arm": "Arms and motors", "power": "Power and safety", "base": "Base and pole", "torso": "Torso frame",
               "costume": "Costume", "fasteners": "Screws and fittings", "control": "Controllers and computer", "hand": "Hands"}
GROUP_ORDER = ["arm", "hand", "power", "control", "torso", "base", "costume", "fasteners"]


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
                    f'<span class="bar-val">{money(g[k])}</span></div>')
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
            f"</tbody><tfoot><tr><td colspan='4'>Total</td><td class='num'>{money(T[t]['total_usd'])}</td><td></td></tr></tfoot></table></div>")


A = AN["tiers"]

TIERS = [
    {"key": "a", "name": "Beginner", "cap": "under $500", "tag": "A", "who": "A first build: cheap, quick, and still a character people stop for.",
     "can": ["Waves, points and beckons with both arms", "Grips a light candy bag with a one-motor mitt", "Runs on one M18 pack with a low-battery cut-off", "Big red stop button on his back"],
     "cant": ["Feel when he touches someone (no feedback from the motors)", "Hold a loaded arm straight out for long", "Swap the battery without switching off"],
     "how": "Eight hobby servos, the kind used in RC cars, move the arms. A second servo board joins the one already in the head, so the head's computer runs everything. A spring at each shoulder carries the arm's weight so the small motors only have to move it. The torso is laser-cut plywood ribs.",
     "hand": "A cartoon mitt: three fingers moulded as one paddle close against a thumb, driven by one servo. Rubber pads give it grip.",
     "joints": "3 + grip", "hands": "Mitt, 1 motor", "battery": "1 pack", "feel": "No", "swap": "No", "brains": "Head computer"},
    {"key": "b", "name": "Midrange", "cap": "up to $1,200", "tag": "B", "who": "The one to build for a season of events: smart motors, safer, and he never has to sleep.",
     "can": ["Waves properly: the upper arm twists, so the hand comes up", "Hands that open and close around a cup or a bag handle", "Every motor reports its position, load and temperature", "Two battery packs: pull one while the other keeps him going", "Tells you when the battery is getting low"],
     "cant": ["Move individual fingers", "Run on wall power (batteries only)"],
     "how": "Fourteen Feetech smart servos, the same motors used in popular open-source robot arms. Each reports how hard it is working, so Jack can stop if his hand meets resistance. Belts give the shoulders and elbows 2.7 times more strength. An aluminium frame inside the torso carries two Milwaukee packs, joined so one can be swapped live.",
     "hand": "A glove hand in a big cartoon glove: four fingers linked to close together, so they wrap around an object, and a separately driven thumb.",
     "joints": "5 + 2-motor hand", "hands": "Glove, 2 motors", "battery": "2 packs, hot swap", "feel": "Yes", "swap": "Yes", "brains": "Head computer"},
    {"key": "c", "name": "Maxed", "cap": "no cap set", "tag": "C", "who": "The show piece: real robot hands with fingers that each move on their own.",
     "can": ["Humanoid hands: four fingers, each with two moving joints", "Wrist that bends as well as twists, for a hat-tip like the concept art", "Batteries plus wall power, so he can run all day indoors", "His own computer in the chest for the arms and hands"],
     "cant": ["Thumbs (the hand used has four fingers, which suits a cartoon)", "Strong grip: the hand's grip force is not published"],
     "how": "Tier B's arm, upgraded: stronger STS3250 motors at the shoulders and elbows (still through belts), plus a wrist that bends. Each hand is a Pollen Robotics AmazingHand: an open-source hand with eight tiny motors in the palm. A Raspberry Pi 5 in the chest runs the arms and hands. A mains power supply joins the two battery packs.",
     "hand": "The Pollen AmazingHand: four fingers, two joints each, eight micro servos, 400 g. Open source (designs CC BY 4.0), sold as a kit by Seeed Studio.",
     "joints": "6 + 8-motor hand", "hands": "Humanoid, 8 motors", "battery": "2 packs + wall", "feel": "Yes", "swap": "Yes", "brains": "Own computer"},
]


def tier_section(d):
    t = d["key"]
    a = A[t]
    sh, el = a["shoulder"], a["elbow"]
    can = "".join(f"<li>{x}</li>" for x in d["can"])
    cant = "".join(f"<li>{x}</li>" for x in d["cant"])
    total = T[t]["total_usd"]
    head = T[t]["headroom_usd"]
    budget_line = (f"{money(total)} of a $500 cap: {money(head)} to spare" if t == "a" else
                   f"{money(total)} of a $1,200 cap: {money(head)} to spare" if t == "b" else f"{money(total)}, no cap set")
    return f"""
<section class="tier" id="tier-{t}">
  <div class="wrap">
    <header class="tier-head">
      <span class="tier-letter">{d['tag']}</span>
      <div><p class="eyebrow">Tier {d['tag']} · {d['cap']}</p><h2>{d['name']}</h2><p class="lede">{d['who']}</p></div>
      <div class="price-tag"><span class="price">{money(total)}</span><span class="price-note">{'new parts; your own flannel shirt' if t == 'a' else 'new parts'}</span></div>
    </header>
    <div class="tier-grid">
      <figure class="hero-fig"><img src="{m(f'hero-{t}.jpg')}" alt="Tier {d['tag']} Joyful Jack, rendered" loading="lazy"></figure>
      <div class="tier-text">
        <h3>How he works</h3><p>{d['how']}</p>
        <h3>What he can do</h3><ul class="ticks">{can}</ul>
        <h3>What he can't</h3><ul class="crosses">{cant}</ul>
      </div>
    </div>
    <div class="pair">
      <figure><img src="{m(f'hands-{t}.jpg')}" alt="Tier {d['tag']} hands" loading="lazy"><figcaption><b>The hands.</b> {d['hand']}</figcaption></figure>
      <figure><img src="{m(f'internals-{t}.jpg')}" alt="Tier {d['tag']} with the costume off" loading="lazy"><figcaption><b>Costume off.</b> The frame on the pole, the battery {'pack' if t == 'a' else 'packs'} (red) behind the back hatch, and the electronics plate.</figcaption></figure>
    </div>
    <div class="pair">
      <figure><img src="{m(f'exploded-{t}.jpg')}" alt="Tier {d['tag']} exploded view" loading="lazy"><figcaption><b>Every part, pulled apart.</b> Base and pole stay put; torso and costume lift; the arms move out; the head and hat rise above.</figcaption></figure>
      <div class="facts">
        <h3>Where the money goes</h3>
        <p class="budget">{budget_line}</p>
        <div class="bars">{cost_bars(t)}</div>
        <h3>Strength check</h3>
        <p class="small">Arm held straight out with a 0.25 kg bag: the hardest moment for the motors.</p>
        <table class="mini"><tr><th></th><th class="num">Needed</th><th class="num">Motor can give (max)</th></tr>
          <tr><td>Shoulder</td><td class="num">{sh['need_kgcm']:.0f} kg·cm</td><td class="num">{sh['stall_kgcm']:.0f} kg·cm</td></tr>
          <tr><td>Elbow</td><td class="num">{el['need_kgcm']:.0f} kg·cm</td><td class="num">{el['stall_kgcm']:.0f} kg·cm</td></tr></table>
        <p class="small">{'The shoulder spring supplies about ' + str(round(sh.get('spring_kgcm_needed', 0))) + ' kg·cm so the motor works well inside its limit.' if sh.get('spring_kgcm_needed') else ''}
        {' The elbow is close to its limit with a load, so tier A keeps a loaded forearm near vertical.' if t == 'a' else ''}</p>
      </div>
    </div>
    <figure class="diagram"><img src="{m(f'diagram-{t}.jpg')}" alt="Tier {d['tag']} system in Protoboard" loading="lazy"><figcaption><b>The wiring, in Protoboard.</b> Every box is a real part with its voltages; Protoboard checked every connection: {('0 problems' if t != 'c' else '0 errors, 2 notes explained in the decision log')}.</figcaption></figure>
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
            ("Arm weight (each)", [f"{A[d['key']]['arm_mass_kg']:.1f} kg" for d in TIERS])]
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
    ta, tb, tc = A["a"]["tip"], A["b"]["tip"], A["c"]["tip"]
    return f"""<title>Joyful Jack Design Report</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rye&family=Zilla+Slab:wght@500;700&family=Source+Sans+3:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}
<header class="mast">
  <div class="wrap">
    <p class="meta">Delta Robotics · design report · 25 Oct 2026 · draft for Mark's review</p>
    <h1>Joyful Jack</h1>
    <p class="sub">A body and two moving arms for our animatronic pumpkin cowboy, designed three ways: a beginner build under $500, a midrange build up to $1,200, and a maxed-out build with real robot hands.</p>
  </div>
  <img src="{m('lineup-dark.jpg')}" alt="Tiers A, B and C side by side">
  <div class="wrap mast-strip">
    <div><b>{money(T['a']['total_usd'])}</b><span>Tier A, Beginner</span></div>
    <div><b>{money(T['b']['total_usd'])}</b><span>Tier B, Midrange</span></div>
    <div><b>{money(T['c']['total_usd'])}</b><span>Tier C, Maxed</span></div>
    <div><b>~1.7 m</b><span>tall, hat included</span></div>
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
  <div class="rec"><b>Recommendation: build tier B.</b> It is the best value: motors that feel resistance make Jack safer around children, two batteries mean he never has to stop, and it comes in {money(T['b']['headroom_usd'])} under the $1,200 cap. Tier A is a good weekend build but runs at its limits. Tier C's hands are a crowd-pleaser and can be added to a tier B Jack later, since the arms share the same motors and wiring.</p>
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
      <figure><img src="{m('lineup-light.jpg')}" alt="All three tiers at rest" loading="lazy"><figcaption><b>At rest.</b> Arms hang on their stops, so a power cut drops nothing.</figcaption></figure>
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
      <p>With both arms out, a push of about {ta['push_to_tip_kgf']:.0f}–{tb['push_to_tip_kgf']:.0f} kg of force at shoulder height would tip him over. A teenager leaning on his shoulder could do that.</p>
      <p><b>For events:</b> lay sandbags on the plywood disc under the costume, or tie the pole to a post. Two 25 lb bags add about a third more margin; four bring it to about 1.7 times.</p>
    </div>
  </div>
</div></section>

{tiers_html}

<section id="motion"><div class="wrap">
  <p class="eyebrow">See him move</p>
  <h2>Animations</h2>
  <p class="lede">A walkthrough of the recommended build, then each tier taken apart and put back together.</p>
  <div class="feature-video">{vid('walkthrough-b.mp4', 'hero-b.jpg', '<b>System walkthrough, tier B.</b> The wave, the costume coming off, the battery packs and electronics, the arm and glove hand, and the head. 36 seconds.')}</div>
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
        <li>Indoor only, or outdoors too? Rain changes the electronics enclosure.</li>
        <li>Is the overall height (about 1.7 m with the hat) right?</li>
      </ol>
    </div>
    <div>
      <h3>Bench tests before the first event</h3>
      <ol class="steps">
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
      <p>Prices were looked up on 24 Oct 2026, mostly from store listings, and will move. Tier A has only {money(T['a']['headroom_usd'])} to spare. The strength and tip numbers come from the 3D model's weights and published motor ratings. The hobby servos publish no continuous rating, so we assumed a third of their maximum. Nothing has been ordered.</p>
    </div>
  </div>
</div></section>

<footer class="wrap foot">
  <p>Built in the Protoboard stack: the head, body, arms and power systems of all three tiers are modelled and checked in <code>projects/internal/2026-10-24-joyful-jack/protoboard</code> (choose a tier with <code>JJ_TIER=a|b|c</code>). 3D models: <code>protoboard/cad/joyful_jack_cad.py</code>. Renders: Blender. Prices: <code>research/sourcing/20261024-bom-final.md</code>. Decisions and engineering checks: <code>protoboard/docs/decisions.md</code>.</p>
</footer>
"""


out = os.path.join(HERE, "published.html" if ASSETS is not None else "index.html")
open(out, "w").write(page())
print("wrote", out)
