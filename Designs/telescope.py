from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import Baseplate, optics, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import cardinal_angle, fix_relative_imports

fix_relative_imports()

base_dx = dim(4, "in")
base_dy = dim(3, "in")
base_dz = dim(1, "in")

input_y = dim(2, "in")
lens_separation = dim(50, "mm")
lens_offset = dim(1.5, "in")


def lens(label: str = "Lens") -> Component:
    return Component(
        label=label,
        definition=optics.Spherical_Lens(
            focal_length=dim(50, "mm"),
            thickness=dim(3, "mm"),
            diameter=dim(0.5, "in"),
            mount_definition=thorlabs.Lens_Mount_L05G(),
        ),
    )


def telescope():
    baseplate = Component(
        label="Telescope",
        definition=Baseplate(
            dimensions=(base_dx, base_dy, base_dz),
            optical_height=dim(0.5, "in"),
            mount_holes=[(1, 1), (4, 1), (4, 3),(1,3)]#, (0, 2), (2, 0), (2, 2)],
        ),
    )

    beam = baseplate.add(
        BeamPath(label="Beam"),
        position=(0, input_y, 0),
        rotation=cardinal_angle["right"],
    )

    beam.add(
        lens("Lens 1"),
        beam_index=0b1,
        distance=lens_offset,
        rotation=cardinal_angle["right"],
    )

    beam.add(
        lens("Lens 2"),
        beam_index=0b1,
        distance=lens_separation,
        rotation=cardinal_angle["left"],
    )

    return baseplate


if __name__ == "__main__":
    telescope().recompute()
