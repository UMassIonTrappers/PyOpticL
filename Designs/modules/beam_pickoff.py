from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import Baseplate, optics, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import cardinal_angle

base_dx = dim(4, "in")
base_dy = dim(4, "in")
base_dz = dim(1, "in")

input_y = dim(1, "in")
mirror_angle = 60


def mirror(label: str = "Mirror") -> Component:
    return Component(
        label=label,
        definition=optics.Circular_Mirror(
            mount_definition=thorlabs.Mirror_Mount_KM05(),
        ),
    )


def fiberport(label: str = "Fiberport") -> Component:
    return Component(
        label=label,
        definition=thorlabs.Fiberport_Mount_KS1T(),
    )


def beam_pickoff():
    baseplate = Component(
        label="Beam Pickoff",
        definition=Baseplate(
            dimensions=(base_dx, base_dy, base_dz),
            optical_height=dim(0.5, "in"),
            mount_holes=[(1, 2), (2, 2), (2, 3)],
        ),
    )

    beam = baseplate.add(
        BeamPath(label="Beam"),
        position=(0, input_y, 0),
        rotation=cardinal_angle["right"],
    )

    beam.add(
        mirror("Input Mirror 1"),
        beam_index=0b1,
        distance=2 * dim(1, "in") + dim(5, "mm"),
        rotation=mirror_angle + 90,
    )

    beam.add(
        mirror("Input Mirror 2"),
        beam_index=0b1,
        distance=2 * dim(1, "in") - dim(5, "mm"),
        rotation=mirror_angle - 90,
    )

    beam.add(
        fiberport(),
        beam_index=0b1,
        distance=dim(53, "mm"),
        rotation=cardinal_angle["left"],
    )

    return baseplate


if __name__ == "__main__":
    beam_pickoff().recompute()
