import numpy as np

from PyOpticL import layout
from PyOpticL.laser import Beam
from PyOpticL.layout import Baseplate, Origin, optomech

INCH = 25.4


def right_source(name, position=(0, 0, 0), rotation=(0, 0, 0)):
    origin = Origin(name, position, rotation)

    beams = []

    for i in range(13):
        beam = origin.place(
            Beam(f"beam_{i}", (i * np.sqrt(2) * INCH, 0, i * 5), (1, 1, 0))
        )
        beams.append(beam)

    for i in range(len(beams)):
        temp = beams[i].placeAlong(
            optomech.CircularTransmission(
                f"dioder{i}",
                radius=0.25 * INCH,
                thickness=20,
                mount_class=optomech.Km05ForRedstone,
            ),
            0,
            normal=(1, 1, 0),
        )
        if i != 0:
            temp.place(
                Baseplate("pole", (-37.5, -15, -14.7 - i * 5), (0, 0, 0), 30, 30, i * 5)
            )

    for i in range(len(beams)):
        temp = beams[i].placeAlong(
            optomech.CircularMirror(
                f"mirrorr{i}",
                radius=0.25 * INCH,
                thickness=6,
                mount_class=optomech.Km05ForRedstone,
            ),
            (13 - i) * 2 * INCH + 4 * INCH,
            normal=(-1, 0, 0),
        )
        if i != 0:
            temp.place(
                Baseplate("pole", (-37.5+14, -15, -14.7 - i * 5), (0, 0, 0), 30, 30, i * 5)
            )

    for i in range(len(beams)):
        beams[i].placeAlong(
            optomech.CircularMirror(f"mirrorr1{i}", radius=0.75, thickness=0.5),
            i * INCH + 2 * INCH - 2 * (13 - i),
            normal=(1, 0, 0),
        )

    for i in range(len(beams)):
        beams[i].placeAlong(
            optomech.CircularStopper(f"temp{i}", radius=0, thickness=1),
            i * INCH + 28 * INCH,
            normal=(1, 0, 0),
        )
    # beams[0].placeAlong(optomech.CircularStopper("stopper", radius=13*INCH, thickness=1), 5 * INCH,
    #                     (0, -1, 0)
    #                     )

    return origin


def left_source(name, position=(0, 0, 0), rotation=(0, 0, 0), stopper=False):
    origin = Origin(name, position, rotation)

    beams = []
    for i in range(13):
        beam = origin.place(
            Beam(f"beam_{i}", (0, i * np.sqrt(2) * INCH, i * 5), (1, 1, 0))
        )
        beams.append(beam)

    for i in range(len(beams)):
        temp = beams[i].placeAlong(
            optomech.CircularTransmission(
                f"dioder{i}",
                radius=0.25 * INCH,
                thickness=20,
                mount_class=optomech.Km05ForRedstone,
            ),
            0,
            normal=(1, 1, 0),
        )
        if i != 0:
            temp.place(
                Baseplate("pole", (-37.5, -15, -14.7 - i * 5), (0, 0, 0), 30, 30, i * 5)
            )

    for i in range(len(beams)):
        temp = beams[i].placeAlong(
            optomech.CircularMirror(
                f"mirrorl{i}",
                radius=0.25 * INCH,
                thickness=6,
                mount_class=optomech.Km05ForRedstone,
            ),
            (13 - i) * 2 * INCH + 4 * INCH,
            normal=(0, -1, 0),
        )
        if i != 0:
            temp.place(
                Baseplate("pole", (-37.5+14, -15, -14.7 - i * 5), (0, 0, 0), 30, 30, i * 5)
            )

    for i in range(len(beams)):
        beams[i].placeAlong(
            optomech.CircularMirror(f"mirrorl2{i}", radius=0.75, thickness=0.5),
            i * INCH + 2 * INCH - 2 * (13 - i),
            normal=(0, 1, 0),
        )

    for i in range(len(beams)):
        beams[i].placeAlong(
            optomech.CircularStopper(f"temp{i}", radius=0, thickness=1),
            i * INCH + 28 * INCH,
            normal=(1, 0, 0),
        )

    # if stopper:
    #     beams[0].placeAlong(
    #         optomech.CircularStopper("stopper", radius=13 * INCH, thickness=1),
    #         3 * INCH,
    #         (0, -1, 0),
    #     )

    return origin


left_plate = Origin("left_source")

left_plate.place(
    Baseplate(
        "left_baseplate",
        (-(2 * np.sqrt(2) - 1.25) * INCH, -(2 * np.sqrt(2) - 1.25) * INCH, -INCH - 14.7),
        (0, 0, 0),
        (4 * np.sqrt(2) + 2.5 + 13 * np.sqrt(2)) * INCH,
        (4 * np.sqrt(2) + 2.5 + 13 * np.sqrt(2)) * INCH,
        INCH,
    )
)
left_plate.place(
    left_source("left_left_source", (0, 2 * INCH * np.sqrt(2), 0), stopper=True)
)
left_plate.place(right_source("left_right_source", (2 * np.sqrt(2) * INCH, 0, 0)))
left_plate.calculate()


right_plate = Origin("right_source", (1300, 0, 0), (90, 0, 0))

right_plate.place(
    Baseplate(
        "left_baseplate",
        (-(2 * np.sqrt(2) - 1.25) * INCH, -(2 * np.sqrt(2) - 1.25) * INCH, -INCH - 14.7),
        (0, 0, 0),
        (4 * np.sqrt(2) + 2.5 + 13 * np.sqrt(2)) * INCH,
        (4 * np.sqrt(2) + 2.5 + 13 * np.sqrt(2)) * INCH,
        INCH,
    )
)
right_plate.place(left_source("right_left_source", (0, 2 * INCH * np.sqrt(2), 0)))
right_plate.place(right_source("right_right_source", (2 * np.sqrt(2) * INCH, 0, 0)))
right_plate.calculate()
