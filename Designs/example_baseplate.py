from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import Baseplate
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import cardinal_angle, fix_relative_imports, turn_angle

fix_relative_imports()

from half_inch_library import beamsplitter_cube, mirror, waveplate

# define and place the baseplate object
example_baseplate = Component(
    label="Example Baseplate",
    definition=Baseplate(
        dimensions=(dim(100, "mm"), dim(100, "mm"), dim(1, "in")),
        optical_height=dim(0.5, "in"),
    ),
)
# add a beam path to the baseplate
beam = example_baseplate.add(
    BeamPath(label="Beam"),
    position=(0, 50, 0),
    rotation=cardinal_angle["right"],
)
# add a waveplate along the beam, 30 mm from the beam start
beam.add(
    waveplate(),
    beam_index=0b1,
    distance=40,
    rotation=cardinal_angle["right"],
)
# add a cube beamsplitter along the beam, 40 mm from the waveplate
beam.add(
    beamsplitter_cube(),
    beam_index=0b1,
    distance=40,
    rotation=cardinal_angle["right"],
)
# add a mirror along the reflected beam, 30 mm from the beamsplitter
beam.add(
    mirror(),
    beam_index=0b11,
    distance=30,
    rotation=turn_angle["up-right"],
)

if __name__ == "__main__":
    example_baseplate.recompute()
