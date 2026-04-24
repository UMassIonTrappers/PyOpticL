from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import baseplate, hardware, optics, thorlabs
from PyOpticL.types import Dimension as dim
from PyOpticL.types import cardinal_angle, turn_angle

baseplate = Component(
    label="Example Baseplate",
    definition=baseplate(
        dimensions=(dim(100, "mm"), dim(100, "mm"), dim(1, "in")),
        optical_height=dim(0.5, "in"),
    ),
)

beam = baseplate.add(
    BeamPath(label="Beam"),
    position=(0, dim(30, "mm"), 0),
    rotation=(0, 0, cardinal_angle["right"]),
)

beam.add(
    Component(
        label="Waveplate",
        definition=optics.circular_waveplate(
            mount_definition=thorlabs.rotation_mount_rsp05(),
        ),
    ),
    beam_index=0b1,
    distance=dim(30, "mm"),
    rotation=(0, 0, cardinal_angle["right"]),
)

beam.add(
    Component(
        label="Beam Splitter",
        definition=optics.beamsplitter_cube_on_surface_adapter(),
    ),
    beam_index=0b1,
    distance=dim(40, "mm"),
    rotation=(0, 0, cardinal_angle["right"]),
)

beam.add(
    Component(
        label="Mirror",
        definition=optics.circular_mirror(
            mount_definition=thorlabs.mirror_mount_k05s1(),
        ),
    ),
    beam_index=0b11,
    distance=dim(30, "mm"),
    rotation=(0, 0, turn_angle["up-right"]),
)

baseplate.recompute()
