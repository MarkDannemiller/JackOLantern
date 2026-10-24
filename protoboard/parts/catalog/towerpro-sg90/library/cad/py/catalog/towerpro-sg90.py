"""TowerPro SG90 (analog) micro servo: representative geometry (PB-865).

TowerPro publishes no CAD. Its SG90 Analog page gives a dimension table
against a generic servo diagram (torqpro.com "small motor dimension" image,
sources.json src_dim_diagram): A 30.3 (base to spline top), B 22.7 (case
length), C 27 (base to gear-housing top), D 12.2 (width), E 32.3 (over the
flange ears), F 17 (base to flange underside); "Dimension: 23x12.2x29mm".

Assumed (`assumption` traits on the part): flange 2.5 mm thick; one Ø2.0 mm
hole per ear, centred in the ear (27.5 mm apart); output spline Ø4.8 mm,
5.6 mm from the case centre along its length (read from the diagram, which is
not to scale); the gear housing is drawn as the full case section.

Coordinates: case centred on the origin in X/Y, base z = 0, spline up +Z at
+X, flange ears along X.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build123d import BuildPart, Box, Cylinder, Locations, Mode, Pos  # noqa: E402

from partkit import MIN, GeneratedPart  # noqa: E402

PART = "towerpro-sg90"
A, B, C, D, E, F = 30.3, 22.7, 27.0, 12.2, 32.3, 17.0
FT = 2.5  # assumption
HOLE_D = 2.0  # assumption
HOLE_X = (E + B) / 4  # 13.75: centred in each ear (assumption)
SPLINE_D, SPLINE_X = 4.8, 5.6  # assumption


def build() -> None:
    a = GeneratedPart(PART, PART, __file__)
    a.describe(
        "catalog script (TowerPro SG90 dimension table A-F)",
        {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "flange_t": FT, "hole_d": HOLE_D, "hole_x": HOLE_X, "spline_d": SPLINE_D, "spline_x": SPLINE_X},
        ["towerpro.com.tw SG90 Analog: product configure table A-F and specifications", "torqpro.com dimension diagram (A-F definitions)"],
    )
    case = a.body(Box(B, D, C, align=MIN), "case")
    with BuildPart() as flange:
        with Locations(Pos(0, 0, F)):
            Box(E, D, FT, align=MIN)
        with Locations((-HOLE_X, 0), (HOLE_X, 0)):
            Cylinder(HOLE_D / 2, F + FT, align=MIN, mode=Mode.SUBTRACT)
    fl = a.body(flange.part, "flange")
    spline = a.body(Pos(SPLINE_X, 0, C) * Cylinder(SPLINE_D / 2, A - C, align=MIN), "spline")
    walls = []
    for x in (-HOLE_X, HOLE_X):
        s = Pos(x, 0, F) * Cylinder(HOLE_D / 2, FT, align=MIN)
        walls += [f for f in s.faces() if f.geom_type.name == "CYLINDER"]
    a.feature("flange_holes", walls, axis=(0, 0, 1))
    a.feature("flange_top", [f for f in fl.faces() if f.geom_type.name == "PLANE" and f.normal_at().Z > 0.9])
    sp = [f for f in spline.faces() if f.geom_type.name == "CYLINDER"]
    a.feature("spline", sp, axis=(0, 0, 1))
    a.feature("spline_top", [f for f in spline.faces() if f.geom_type.name == "PLANE" and f.normal_at().Z > 0.9])
    a.feature("case_top", [f for f in case.faces() if f.geom_type.name == "PLANE" and f.normal_at().Z > 0.9])
    a.assumption("flange", f"{FT} mm thick, one Ø{HOLE_D} mm hole per ear at x = ±{HOLE_X} mm (not dimensioned)")
    a.assumption("spline", f"Ø{SPLINE_D} mm, {SPLINE_X} mm from the case centre (not dimensioned)")
    a.data_gap("details", "the lead, case steps and gear-housing bump are not modelled")
    a.write()


if __name__ == "__main__":
    build()
