from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import baseplate, hardware, optics, thorlabs
from PyOpticL.types import Dimension as dim
from PyOpticL.types import cardinal_angle, turn_angle

# define and place the baseplate object
baseplate = Component(
    label="Example Baseplate",
    definition=baseplate(
        dimensions=(dim(100, "mm"), dim(100, "mm"), dim(1, "in")),
        optical_height=dim(0.5, "in"),
    ),
)

# add a beam path to the baseplate
beam = baseplate.add(
    BeamPath(label="Beam"),
    position=(0, 30, 0),
    rotation=cardinal_angle["right"],
)

# add a waveplate along the beam, 30 mm from the beam start
beam.add(
    Component(
        label="Waveplate",
        definition=optics.circular_waveplate(
            mount_definition=thorlabs.rotation_mount_rsp05(),
        ),
    ),
    beam_index=0b1,
    distance=30,
    rotation=cardinal_angle["right"],
)

# add a cube beamsplitter along the beam, 40 mm from the waveplate
beam.add(
    Component(
        label="Beam Splitter",
        definition=optics.beamsplitter_cube_on_surface_adapter(),
    ),
    beam_index=0b1,
    distance=40,
    rotation=cardinal_angle["right"],
)

# add a mirror along the reflected beam, 30 mm from the beamsplitter
beam.add(
    Component(
        label="Mirror",
        definition=optics.circular_mirror(
            mount_definition=thorlabs.mirror_mount_k05s1(),
        ),
    ),
    beam_index=0b11,
    distance=30,
    rotation=turn_angle["up-right"],
)

baseplate.recompute()
