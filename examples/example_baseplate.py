from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import baseplate, hardware, optics, thorlabs
from PyOpticL.types import Dimension as dim

baseplate = Component(
    label="Example Baseplate",
    definition=baseplate(
        dimensions=(dim(100, "mm"), dim(100, "mm"), dim(1, "in")),
        optical_height=dim(0.5, "in"),
    ),
)

beam = baseplate.add(
    BeamPath(label="Beam", wavelength=640, waist=dim(1, "mm")),
    position=(0, dim(30, "mm"), 0),
    rotation=(0, 0, 0),
)

beam.add(
    Component(
        label="Waveplate",
        definition=optics.circular_waveplate(
            diameter=dim(0.5, "in"),
            retardance=0.5,
            fast_axis_angle=45,
            mount_definition=thorlabs.rotation_mount_rsp05(),
        ),
    ),
    beam_index=0b1,
    distance=dim(30, "mm"),
    rotation=(0, 0, 0),
)

beam.add(
    Component(
        label="Beam Splitter",
        definition=optics.beamsplitter_cube(
            side_length=dim(10, "mm"), optical_height=dim(0.5, "in")
        ),
    ),
    beam_index=0b1,
    distance=dim(40, "mm"),
    rotation=(0, 0, 0),
)

beam.add(
    Component(
        label="Mirror",
        definition=optics.circular_mirror(
            diameter=dim(0.5, "in"),
            mount_definition=thorlabs.mirror_mount_k05s1(),
        ),
    ),
    beam_index=0b11,
    distance=dim(30, "mm"),
    rotation=(0, 0, -45),
)

baseplate.recompute()
