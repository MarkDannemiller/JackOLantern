"""Render meshes the parts folders do not hold: the costume (no UHD body) to out/mech/tier-<t>/costume/<part id>.stl and
the fasteners in the frames the stacks place them in (hardware-cad's frames are its own) to out/mech/hw/<id>.stl.
In mm, in the part's own frame (the scene places each by its matrix).

    ~/.local/opt/jj-mech/bin/python cad/mech/tools/export_costume.py [a b c]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from build123d import export_stl  # noqa: E402
from jj.assemble import build_tier  # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "out", "mech"))
for t in sys.argv[1:] or ["a", "b", "c"]:
    asm, _ = build_tier(t, costume=True)
    d = os.path.join(OUT, f"tier-{t}", "costume")
    os.makedirs(d, exist_ok=True)
    done = set()
    for i in asm.instances.values():
        p = i.part
        if p.category == "costume" and p.solid is not None and p.id not in done:
            export_stl(p.solid, os.path.join(d, f"{p.id}.stl"), tolerance=0.2, angular_tolerance=0.3)
            done.add(p.id)
    hd = os.path.join(OUT, "hw")
    os.makedirs(hd, exist_ok=True)
    for m in asm.mates:
        for it in m.stack:
            if it.hw.id not in done:
                export_stl(it.hw.solid, os.path.join(hd, f"{it.hw.id}.stl"), tolerance=0.02, angular_tolerance=0.3)
                done.add(it.hw.id)
    print(t, len(done))
