from PyOpticL.laser import Beam
from PyOpticL.layout import optomech
from PyOpticL.layout import Origin
from PyOpticL import layout
from PyOpticL.layout import Baseplate

INCH = 25.4

# for i in range(6):
#     for j in range(6):
#         beam = laser.Beam(
#             "beam{}{}".format(i, j),
#             App.Vector(0, 2 * i * INCH, 2 * j * INCH),
#             App.Vector(1, 0, 0)
#         )
#         beam.placeAlong(optomech.CircularMirror("mirrror{}{}".format(i, j)), 100 + 2 * i * INCH, App.Vector(4, -1, 0))
#         beam.calculate()

# beam = laser.Beam("beam", (0, 0, 0), (1, 0, 0))
# beam1 = laser.Beam("beam", (0, 1, 0), (1, 0, 0))
#
# beam.placeAlong(optomech.CircularMirror("mirror", mount_class=optomech.Km05), 100, layout.NORMALS['right-up'])
#
# beam.placeAlong(optomech.CircularMirror("mirrror"), 100, (-4, +1, 1))
#
# beam.placeAlong(optomech.CircularSplitter("splitter"), 100, (1, 0, 0))
#
# beam.placeAlong(optomech.CircularMirror("mirror1"), 100, (1, 0, 0), 0b10)
# beam.placeAlong(optomech.CircularMirror("mirror2", mount_class=optomech.Km05), 100, (-1, 0, 0), 0b11)
# beam.placeAlong(optomech.CircularMirror('mirror2'), 100, (-1, 0, 0), 0b11)
#
# beam.calculate()
# beam1.calculate()


origin = Origin("origin", (10, 10, 0))

# origin.place(optomech.CircularMirror("mirror", thickness=6, radius=.25 * INCH, mount_class=optomech.Km05ForRedstone))


beam = origin.place(Beam("beam", (0, 0, 0), (1, 0, 0)))
beams = []
for i in range(5):
    for j in range(5):
        beams.append(origin.place(Beam("beam", (0, -4 + 2 * i, -4 + 2 * j), (1, 0, 0))))

beam.placeAlong(optomech.CircularMirror("test", radius=10), 20, layout.NORMALS['right-up'])
beam.placeAlong(optomech.SquareMirror("test", side_length=10), 20, layout.NORMALS['up-left'])
# beam.placeAlong(optomech.CubeSplitter("split"), 25, layout.NORMALS['right-up'])
# beam.placeAlong(optomech.CircularMirror("mirror1"), 25, layout.NORMALS['up-left'], 0b11)
# beam.placeAlong(optomech.CircularMirror("mirror2"), 25, layout.NORMALS['right-up'], 0b10)
#
# origin.place(Baseplate("baseplate", (10, 10, -30), (0, 0, 0), 20, 20, 10))
origin.obj.ParentPlacement = App.Placement(App.Matrix())

beam.calculate()
for beam in beams:
    beam.calculate()


# baseplate = origin.place(Baseplate("baseplate", (0, 0, 0), (0, 0, 0), 100, 100, INCH))
#
# baseplate.place(optomech.Bolt("bolt", optomech.BOLT_4_40, .75*INCH, 'clear_dia', [baseplate], (50, 50, 0), (0, 0, 0), True))

# baseplate = Baseplate("baseplate", (0, 0, 0), (0, 0, 0), 100, 100, 1 * INCH)
# origin = baseplate.place(Origin("origin", (0, 0, .75 * INCH)))
# beam = origin.place(Beam("beam", (20, 20, 0), (1, 0, 0)))
# beam.placeAlong(optomech.CircularTransmission("waveplate", (20, 20, 0), (1, 0, 0), .25 * INCH, 0, mount_class=optomech.Rsp05ForRedstone, drills=baseplate), 10, (-1, 0, 0))
# origin.place(optomech.CubeSplitter("rectangle", (0, 0, 0), (1, 0, 0)))
# origin.place(optomech.CircularTransmission("waveplate", (20, 20, 0), (1, 0, 0), .25 * INCH, 0, mount_class=optomech.Rsp05ForRedstone, drills=[baseplate,]))
# origin.place(optomech.CircularMirror("mirror", (20, 20, 0), (1, 0, 0), .25 * INCH, 6, mount_class=optomech.Km05ForRedstone, drills=baseplate))
# origin.place(optomech.CubeSplitter("splitter", (20, 20, 5), (1, 0, 0), mount_class=optomech.PBSForRedstone, drills=baseplate))
# origin.calculate()

# beam_test = Origin("beam_test", (100, 100, 0))
# beam = beam_test.place(Beam("beam", (0, 0, 0), (1, 0, 0)))
# beam.placeAlong(optomech.SquareMirror("square"), 100, layout.NORMALS['right-up'])
# beam_test.calculate()
