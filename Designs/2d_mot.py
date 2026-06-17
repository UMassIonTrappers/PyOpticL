from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import Baseplate
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import cardinal_angle, fix_relative_imports, turn_angle

fix_relative_imports()

from one_inch_library import beamsplitter_cube, mirror, waveplate

base_dx = dim(17, "in")
base_dy = dim(20, "in")
base_dz = dim(1, "in")

input_x = dim(14, "grid")
input_y = dim(0.5, "in")


def mot_2d():

    baseplate = Component(
        label="MOT 2D Routing",
        definition=Baseplate(
            dimensions=(base_dx, base_dy, base_dz),
            optical_height=dim(1, "in"),
        ),
    )

    beam = baseplate.add(
        BeamPath(label="780 nm MOT Beam", wavelength=780.24, waist=dim(0.25, "in")),
        position=(input_x, input_y, 0),
        rotation=cardinal_angle["up"],
    )

    beam.add(
        mirror("Input Mirror 1"),
        beam_index=0b1,
        distance=dim(2, "in"),
        rotation=turn_angle["up-right"],
    )
    beam.add(
        mirror("Input Mirror 2"),
        beam_index=0b1,
        distance=dim(2, "in"),
        rotation=turn_angle["right-up"],
    )

    beam.add(
        waveplate("Input Half Waveplate"),
        beam_index=0b1,
        distance=dim(1, "in"),
        rotation=cardinal_angle["up"],
    )
    beam.add(
        beamsplitter_cube("PBS", rotate_adapter=True),
        beam_index=0b1,
        distance=dim(2, "in"),
        rotation=cardinal_angle["up"],
    )

    beam.add(
        waveplate("Vertical Arm HWP"),
        beam_index=0b11,
        distance=dim(2, "in"),
        rotation=cardinal_angle["left"],
    )
    beam.add(
        mirror("Vertical Turn Mirror"),
        beam_index=0b11,
        distance=dim(4, "in"),
        rotation=turn_angle["left-up"],
    )

    beam.add(
        waveplate("Vertical Arm QWP"),
        beam_index=0b11,
        distance=dim(10, "in"),
        rotation=cardinal_angle["up"],
    )
    beam.add(
        mirror("Vertical Arm Retro Mirror"),
        beam_index=0b11,
        distance=dim(3.5, "in"),
        rotation=cardinal_angle["down"],
    )

    beam.add(
        waveplate("Horizontal Arm QWP"),
        beam_index=0b10,
        distance=dim(2, "in"),
        rotation=cardinal_angle["up"],
    )

    beam.add(
        mirror("Horizontal Turn Mirror"),
        beam_index=0b10,
        distance=dim(4, "in"),
        rotation=turn_angle["up-left"],
    )

    beam.add(
        waveplate("Horizontal Retro QWP"),
        beam_index=0b10,
        distance=dim(10, "in"),
        rotation=cardinal_angle["left"],
    )

    beam.add(
        mirror("Horizontal Retro Mirror"),
        beam_index=0b10,
        distance=dim(3, "in"),
        rotation=cardinal_angle["right"],
    )

    # beam.add(iris("Input Iris"), beam_index=0b1, distance=dim(0.75, "in"), rotation=cardinal_angle["up"])

    # beam.add(iris("Vertical Arm Iris"), beam_index=0b11, distance=dim(0.75, "in"), rotation=cardinal_angle["up"])

    # beam.add(iris("Horizontal Arm Iris"), beam_index=0b10, distance=dim(0.75, "in"), rotation=cardinal_angle["right"])

    return baseplate


if __name__ == "__main__":
    baseplate = mot_2d()
    baseplate.recompute()
