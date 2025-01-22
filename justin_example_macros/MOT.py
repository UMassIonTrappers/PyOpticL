import numpy as np

from PyOpticL import layout
from PyOpticL.laser import Beam
from PyOpticL.layout import Baseplate, Origin, optomech

INCH = 25.4

origin = Origin("origin")

beam = origin.place(Beam("beam", (0, 0, 0), (0, 1, 0)))

beam.placeAlong(
    optomech.CircularMirror("input_mirror_1", radius=INCH),
    10,
    layout.NORMALS["up-right"],
)

beam.placeAlong(
    optomech.CircularMirror("input_mirror_2", radius=INCH),
    4 * INCH,
    layout.NORMALS["right-up"],
)

beam.placeAlong(
    optomech.CircularTransmission("waveplate_1", radius=INCH), 3 * INCH, (0, -1, 0)
)

beam.placeAlong(
    optomech.CubeSplitter("splitter1", cube_size=2 * INCH),
    4 * INCH,
    layout.NORMALS["up-left"],
)

beam.placeAlong(
    optomech.CircularMirror("vert_mirror1", radius=INCH),
    13 * INCH,
    (1, 0, -1),
    beam_index=0b11,
)

beam.placeAlong(
    optomech.CircularMirror("vert_mirror2", radius=INCH),
    9 * INCH,
    (0, 1, 1),
    beam_index=0b11,
)

beam.placeAlong(
    optomech.CircularMirror("vert_mirror3", radius=INCH),
    13 * INCH,
    (0, -1, 1),
    beam_index=0b11,
)

beam.placeAlong(
    optomech.CircularTransmission("vert_waveplate", radius=INCH),
    18 * INCH,
    (0, 0, -1),
    beam_index=0b11,
)

beam.placeAlong(
    optomech.CircularMirror("vert_retromirror", radius=INCH),
    2 * INCH,
    (0, 0, -1),
    beam_index=0b11,
)

beam.placeAlong(
    optomech.CircularStopper("vert_stop", radius=0), 1 * INCH, beam_index=0b11
)

beam.placeAlong(
    optomech.CircularTransmission("waveplate_2", radius=INCH),
    4 * INCH,
    (0, -1, 0),
    0b10,
)

beam.placeAlong(
    optomech.CubeSplitter("splitter2", cube_size=2 * INCH),
    4 * INCH,
    layout.NORMALS["up-left"],
    0b10,
)

beam.placeAlong(
    optomech.CircularMirror("x_mirror1", radius=INCH),
    4 * INCH,
    layout.NORMALS["left-up"],
    beam_index=0b101,
)

beam.placeAlong(
    optomech.CircularMirror("x_mirror2", radius=INCH),
    5 * INCH,
    layout.NORMALS["up-left"],
    beam_index=0b101,
)

beam.placeAlong(
    optomech.CircularTransmission("x_waveplate", radius=INCH),
    18 * INCH,
    (1, 0, 0),
    beam_index=0b101,
)

beam.placeAlong(
    optomech.CircularMirror("x_retromirror", radius=INCH),
    2 * INCH,
    (1, 0, 0),
    beam_index=0b101,
)

beam.placeAlong(optomech.CircularStopper("x_stopper", radius=0), 0)

beam.placeAlong(
    optomech.CircularMirror("y_mirror1", radius=INCH),
    14 * INCH,
    layout.NORMALS["up-left"],
    beam_index=0b100,
)

beam.placeAlong(
    optomech.CircularMirror("y_mirror2", radius=INCH),
    13 * INCH,
    layout.NORMALS["left-down"],
    beam_index=0b100,
)

beam.placeAlong(
    optomech.CircularTransmission("y_waveplate", radius=INCH),
    18 * INCH,
    (0, 1, 0),
    beam_index=0b100,
)
beam.placeAlong(
    optomech.CircularMirror("y_retromirror", radius=INCH),
    2 * INCH,
    (0, 1, 0),
    beam_index=0b100,
)
beam.placeAlong(optomech.CircularStopper("y_stopper", radius=0), 0, beam_index=0b100)


origin.calculate()
