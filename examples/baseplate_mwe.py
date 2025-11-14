import numpy as np

from PyOpticL import layout
from PyOpticL.old.laser import Beam
from PyOpticL.layout import Baseplate, Origin, optomech

INCH = 25.4

origin = Origin("origin")

beam = origin.place(Beam("beam", (0.5 * INCH, 0, 1.5 * INCH), (0, 1, 0)))
origin.place(
    optomech.Chamber_with_chip(
        "chamber", (-2 * INCH, -2 * INCH, 2.2 * INCH), (1, 1, 0)
    ),
)
plate_1 = Baseplate(
    "plate1",
    (0, 0, 0),
    (0, 0, 0),
    5 * INCH,
    5 * INCH,
    INCH,
    drill=True,
    mount_holes=[(2, 2), (8, 2)],
)
plate_1.place(
    optomech.Bolt(
        "bolt",
        optomech.BOLT_14_20,
        1 * INCH,
        "clear_dia",
        [plate_1],
        (50, 50, 0),
        (0, 0, 0),
        True,
    )
)
input_mirror_1 = beam.placeAlong(
    optomech.CircularMirror(
        "input_mirror_1", radius=0.25 * INCH, mount_class=optomech.Km05, drills=plate_1
    ),
    2 * INCH,
    (1, -1, 0),
)

beam.placeAlong(
    optomech.CircularStopper("y_stopper", radius=0), 5 * INCH, beam_index=0b1
)
# origin.obj.ParentPlacement = App.Placement(App.Matrix())

origin.calculate()
