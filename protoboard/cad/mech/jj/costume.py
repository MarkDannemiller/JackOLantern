"""Costume and hat: the shapes from the concept-level generator (cad/joyful_jack_cad.py: shirt, vest,
bandana, belt, buckle, holster, cowboy hat), placed in world coordinates. They are sewn or bought, held
on with hook-and-loop tape: placed parts in the build guide, not mated."""
from __future__ import annotations

import importlib.util
import os

from .model import PartDef

HERE = os.path.dirname(os.path.abspath(__file__))
_old = None


def _legacy():
    global _old
    if _old is None:
        spec = importlib.util.spec_from_file_location("jj_legacy_cad", os.path.join(HERE, "..", "..", "joyful_jack_cad.py"))
        _old = importlib.util.module_from_spec(spec)
        import sys
        sys.modules[spec.name] = _old           # dataclasses look the module up while the class is built
        spec.loader.exec_module(_old)
    return _old


NAMES = {"shirt_front": "Flannel shirt, front (on a printed shoulder form)", "shirt_back": "Flannel shirt, back", "hatch_door": "Back hatch flap (hook-and-loop)",
         "vest_left": "Vest, left", "vest_right": "Vest, right", "bandana": "Bandana", "belt": "Belt", "buckle": "Belt buckle", "holster": "Holster",
         "brim": "Cowboy hat, brim", "crown": "Cowboy hat, crown", "band": "Hat band", "concho": "Hat band concho"}


def costume_parts(tier):
    """[(part, world matrix)] for the costume and the hat (the hat rides on the head: link 'head')."""
    old = _legacy()
    root = old.Link("torso", None)
    old.torso_and_costume(root, tier)
    hat = old.Link("hat", "head")
    old.cowboy_hat(hat)
    out = []
    import numpy as np
    for lk, link, z in ((root, "torso", 0.0), (hat, "head", old.NECK_Z)):
        for p in lk.parts:
            key = p.name.split("__", 1)[1]
            pid = f"jj-costume-{key.replace('_', '-')}"
            part = PartDef(pid, NAMES.get(key, key.replace("_", " ")), "costume", p.material, p.shape,
                           source="concept geometry (cad/joyful_jack_cad.py); sewn or bought to fit", meta={"explode": list(p.explode)})
            m = np.eye(4)
            m[2, 3] = z
            out.append((part, m, link, p.explode))
    return out
