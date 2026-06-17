from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import Baseplate
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import cardinal_angle, fix_relative_imports, turn_angle

fix_relative_imports()

from half_inch_library import mirror

base_dx = dim(4, "in")
base_dy = dim(6, "in")
base_dz = dim(1, "in")

input_x = dim(2, "grid")


def ecdl_isolator():

    baseplate = Component(
        label="ECDL Isolator",
        definition=Baseplate(
            dimensions=(base_dx, base_dy, base_dz),
            optical_height=dim(0.5, "in"),
            mount_holes=[(1, 1), (4, 1), (1, 6), (4, 6)],
        ),
    )

    beam = baseplate.add(
        BeamPath(label="Beam"),
        position=(input_x, 0, 0),
        rotation=cardinal_angle["up"],
    )

    beam.add(
        mirror(),
        beam_index=0b1,
        distance=dim(35, "mm"),
        rotation=turn_angle["up-right"],
    )

    beam.add(
        mirror(),
        beam_index=0b1,
        distance=dim(1, "grid"),
        rotation=turn_angle["right-up"],
    )

    return baseplate


if __name__ == "__main__":
    baseplate = ecdl_isolator()
    baseplate.recompute()
