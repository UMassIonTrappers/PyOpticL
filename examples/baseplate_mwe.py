import numpy as np

from PyOpticL import layout
from PyOpticL.laser import Beam
from PyOpticL.layout import Baseplate, Origin, optomech

INCH = 25.4

origin = Origin("origin")

beam = origin.place(Beam("beam", (0.5 * INCH, 0, 1.5 * INCH), (0, 1, -0.3)))
plate_1 = origin.place(Baseplate(
                    "plate1",
                    (0, 0, 0),
                    (0, 0, 0),
                    5 * INCH,
                    5 * INCH,
                    INCH,
                    drill=True,
                    mount_holes=[(2, 2), (8, 2)],
                ))

beam.placeAlong(
    optomech.CircularMirror("input_mirror_1", radius=0.25 * INCH, mount_class=optomech.Km05, drills=plate_1),
    2 * INCH,
    (1, -1, 0.1),
)

beam.placeAlong(optomech.CircularStopper("y_stopper", radius=0), 5 * INCH, beam_index=0b1)
# origin.obj.ParentPlacement = App.Placement(App.Matrix())

origin.calculate()
