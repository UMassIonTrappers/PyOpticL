from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import Baseplate, optics, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import cardinal_angle, fix_relative_imports, turn_angle

fix_relative_imports()

base_dx = dim(6, "in")
base_dy = dim(4.5, "in")
base_dz = dim(1, "in")

input_x = dim(0, "in")
input_y = base_dy - dim(0.5, "in")


def mirror(label: str = "Mirror") -> Component:
    return Component(
        label=label,
        definition=optics.Circular_Mirror(
            mount_definition=thorlabs.Mirror_Mount_KM05(),
        ),
    )


def ecdl_isolator_plate():
    baseplate = Component(
        label="ECDL Isolator Plate",
        definition=Baseplate(
            dimensions=(base_dx, base_dy, base_dz),
            optical_height=dim(0.5, "in"),
            mount_holes=[(1, 1), (6, 4), (1, 4),(6, 1)]#, (1, 3), (4, 3), (4, 2)],
        ),
    )

    beam = baseplate.add(
        BeamPath(label="Beam"),
        position=(input_x, input_y, 0),
        rotation=cardinal_angle["right"],
    )

    beam.add(
        mirror("Input Mirror 1"),
        beam_index=0b1,
        distance=dim(1.5, "in"),
        rotation=turn_angle["right-down"],
    )

    beam.add(
        mirror("Input Mirror 2"),
        beam_index=0b1,
        distance=dim(2, "in"),
        rotation=turn_angle["down-right"],
    )

    beam.add(
        Component(
            label="Lens 1",
            definition=optics.Cylindrical_Lens(
                thickness=dim(4, "mm"),
                width=dim(20, "mm"),
                height=dim(22, "mm"),
                slots=True,
            ),
        ),
        beam_index=0b1,
        x_position=dim(2.5, "in"),
        rotation=cardinal_angle["right"],
    )

    beam.add(
        Component(
            label="Lens 2",
            definition=optics.Cylindrical_Lens(
                thickness=dim(5.1, "mm"),
                width=dim(15, "mm"),
                height=dim(17, "mm"),
                slots=True,
            ),
        ),
        beam_index=0b1,
        distance=dim(35, "mm"),
        rotation=cardinal_angle["left"],
    )

    beam.add(
        Component(
            label="Optical Isolator",
            definition=thorlabs.Isolator_405(),
        ),
        beam_index=0b1,
        distance=dim(40, "mm"),
        rotation=cardinal_angle["left"],
    )

    return baseplate


if __name__ == "__main__":
    ecdl_isolator_plate().recompute()
