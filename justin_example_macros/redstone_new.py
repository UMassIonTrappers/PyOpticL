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
                        (-i * np.sqrt(2) * INCH),
                        (i * np.sqrt(2) * INCH),
                        (j * 2 * INCH),
                    ),
                    direction=(-1, -1, 0),
                )
            )
        )
    beams.append(row)

for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=0 * INCH,
                normal=(-1, -1, 0),
            )
            plate1 = corner.place(
                Baseplate(
                    "plate1",
                    ( -0.5 * INCH, INCH, -1.5 * INCH),
                    (180, 0, 0),
                    INCH,
                    12 * INCH,
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"input{i}{j}",
                    thickness=25,
                    radius=.25*INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate1,
                ),
                distance=0,
                normal=(-1, -1, 0),
            )
        else:
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"input{i}{j}",
                    thickness=25,
                    radius=.25*INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate1,
                ),
                distance=0,
                normal=(-1, -1, 0),
            )

for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=10 * INCH,
                normal=(-1, -1, 0),
            )
            plate2 = corner.place(
                Baseplate(
                    "plate2",
                    ( +0.5 * INCH, INCH, -1.5 * INCH),
                    (180, 0, 0),
                    INCH,
                    12 * INCH,
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"second_waveplate{i}{j}",
                    thickness=3,
                    radius=.25*INCH,
                    mount_class=optomech.Rsp05ForRedstone,
                    drills=plate2,
                ),
                distance=0,
                normal=(-1, -1, 0),
            )
        else:
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"second_waveplate{i}{j}",
                    thickness=3,
                    radius=.25*INCH,
                    mount_class=optomech.Rsp05ForRedstone,
                    drills=plate2,
                ),
                distance=10 * INCH,
                normal=(-1, -1, 0),
            )

for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=4 * INCH,
                normal=(0, 1, 0),
            )
            plate3 = corner.place(
                Baseplate(
                    "plate3",
                    (-0.5 * INCH, -INCH * np.sqrt(2), -1.5 * INCH),
                    (0, 0, 0),
                    INCH,
                    12 * INCH * np.sqrt(2),
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CubeSplitter(
                    f"first_splitter{i}{j}",
                    mount_class=optomech.PBSForRedstone,
                    drills=plate3,
                ),
                distance=0,
                normal=(0, 1, 0),
            )
        else:
            beams[i][j].placeAlong(
                optomech.CubeSplitter(
                    f"first_splitter{i}{j}",
                    mount_class=optomech.PBSForRedstone,
                    drills=plate3,
                ),
                distance=4 * INCH + (i * (2 * INCH)),
                normal=(0, 1, 0),
            )

for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=25 * INCH,
                normal=(1, 0, 0),
                beam_index=0b10,
            )
            plate4 = corner.place(
                Baseplate(
                    "plate4",
                    (-0.5 * INCH - 7.29 - 6, -1 * INCH * np.sqrt(2), -1.5 * INCH),
                    (0, 0, 0),
                    1 * INCH,
                    12 * INCH * np.sqrt(2),
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CircularMirror(
                    f"first_mirror{i}{j}",
                    thickness=6,
                    radius=0.25 * INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate4,
                ),
                distance=0,
                normal=(1, 0, 0),
                beam_index=0b10,
            )
        else:
            beams[i][j].placeAlong(
                optomech.CircularMirror(
                    f"first_mirror{i}{j}",
                    thickness=6,
                    radius=0.25 * INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate4,
                ),
                distance=25 * INCH - i * (4 * INCH),
                normal=(1, 0, 0),
                beam_index=0b10,
            )

for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=4 * INCH,
                normal=(-1, 1, 0),
                beam_index=0b10,
            )
            plate5 = corner.place(
                Baseplate(
                    "plate5",
                    (+.5 * INCH, +1*INCH, -1.5 * INCH),
                    (180, 0, 0),
                    INCH,
                    12 * INCH,
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"second_waveplate{i}{j}",
                    mount_class=optomech.Rsp05ForRedstone,
                    drills=plate5,
                ),
                distance=0,
                normal=(-1, 1, 0),
                beam_index=0b10,
            )
        else:
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"second_waveplate{i}{j}",
                    mount_class=optomech.Rsp05ForRedstone,
                    drills=plate5,
                ),
                distance=4 * INCH + i * (2 * INCH),
                normal=(-1, 1, 0),
                beam_index=0b10,
            )

for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=4 * INCH,
                normal=(-1, 1, 0),
                beam_index=0b10,
            )
            plate8 = corner.place(
                Baseplate(
                    "plate8",
                    (-.5*INCH + 5 , +INCH, -1.5 * INCH),
                    (180, 0, 0),
                    INCH,
                    12 * INCH,
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"output1{i}{j}",
                    thickness=20,
                    radius=.25*INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate8,
                ),
                distance=0,
                normal=(-1, 1, 0),
                beam_index=0b10,
            )
        else:
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"output1{i}{j}",
                    thickness=20,
                    radius=.25*INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate8,
                ),
                distance=4 * INCH,
                normal=(-1, 1, 0),
                beam_index=0b10,
            )



for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=25 * INCH,
                normal=(1, 0, 0),
                beam_index=0b11,
            )
            plate7 = corner.place(
                Baseplate(
                    "plate7",
                    (0.5 * INCH - 7.29 - 6, +1 * INCH, -1.5 * INCH),
                    (180, 0, 0),
                    1 * INCH,
                    12 * INCH * np.sqrt(2),
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CircularMirror(
                    f"second_mirror{i}{j}",
                    thickness=6,
                    radius=0.25 * INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate7,
                ),
                distance=0,
                normal=(1, 0, 0),
                beam_index=0b11,
            )
        else:
            beams[i][j].placeAlong(
                optomech.CircularMirror(
                    f"second_mirror{i}{j}",
                    thickness=6,
                    radius=0.25 * INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate7,
                ),
                distance=25 * INCH - i * (4 * INCH),
                normal=(1, 0, 0),
                beam_index=0b11,
            )

for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=4 * INCH,
                normal=(-1, -1, 0),
                beam_index=0b11,
            )
            plate8 = corner.place(
                Baseplate(
                    "plate8",
                    (-.5 * INCH, -1*INCH, -1.5 * INCH),
                    (0, 0, 0),
                    INCH,
                    12 * INCH,
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"third_waveplate{i}{j}",
                    mount_class=optomech.Rsp05ForRedstone,
                    drills=plate8,
                ),
                distance=0,
                normal=(-1, -1, 0),
                beam_index=0b11,
            )
        else:
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"third_waveplate{i}{j}",
                    mount_class=optomech.Rsp05ForRedstone,
                    drills=plate8,
                ),
                distance=4 * INCH + i * (2 * INCH),
                normal=(-1, -1, 0),
                beam_index=0b11,
            )

for i in range(len(beams)):
    for j in range(len(beams[i])):
        if i == j == 0:
            corner = beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"corner_ref", radius=0 * INCH, thickness=0
                ),
                distance=4 * INCH,
                normal=(-1, -1, 0),
                beam_index=0b11,
            )
            plate9 = corner.place(
                Baseplate(
                    "plate9",
                    ( -1.5 * INCH + 5, -INCH, -1.5 * INCH),
                    (0, 0, 0),
                    INCH,
                    12 * INCH,
                    13 * INCH,
                )
            )
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"output2{i}{j}",
                    thickness=20,
                    radius=.25*INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate9,
                ),
                distance=0,
                normal=(-1, -1, 0),
                beam_index=0b11,
            )
        else:
            beams[i][j].placeAlong(
                optomech.CircularTransmission(
                    f"output2{i}{j}",
                    thickness=20,
                    radius=.25*INCH,
                    mount_class=optomech.Km05ForRedstone,
                    drills=plate9,
                ),
                distance=4 * INCH,
                normal=(-1, -1, 0),
                beam_index=0b11,
            )

origin.calculate()
