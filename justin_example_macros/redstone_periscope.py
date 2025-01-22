import numpy as np

from PyOpticL import layout
from PyOpticL.laser import Beam
from PyOpticL.layout import Baseplate, Origin, optomech

INCH = 25.4

origin = Origin("left group")

beams = []
corner = 0

for i in range(6):
    row = []
    for j in range(6):
        row.append(
            origin.place(
                Beam(
                    f"beam{i}{j}",
                    position=(
                        (2.5 * np.sqrt(2) * i),
                        (2.5 * np.sqrt(2) * i),
                        (j * 5),
                    ),
                    direction=(-1, 1, 0),
                )
            )
        )
    beams.append(row)


for i in range(len(beams)):
    for j in range(len(beams[i])):
        beams[i][j].placeAlong(
            optomech.CircularTransmission(
                f"input_fiber{i}{j}", thickness=10, radius=0.25 * INCH
            ),
            distance=0,
            normal=(-1, 1, 0),
        )

for i in range(len(beams)):
    for j in range(len(beams[i])):
        beams[i][j].placeAlong(
            optomech.SquareMirror(
                f"periscope_mirror_{i}{j}", side_length=5,
            ),
            distance=5*INCH + 2 * j * INCH,
            normal=(1, -1, 1),
        )


origin.calculate()
