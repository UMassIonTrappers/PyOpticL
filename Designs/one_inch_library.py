from PyOpticL.layout import Component
from PyOpticL.library import optics, thorlabs
from PyOpticL.utils import Dimension as dim


ONE_INCH = dim(1, "in")


def mirror(label: str = "Mirror") -> Component:
    return Component(
        label=label,
        definition=optics.Circular_Mirror(
            diameter=ONE_INCH,
            mount_definition=thorlabs.Mirror_Mount_KM100(),
        ),
    )


def waveplate(label: str = "Waveplate") -> Component:
    return Component(
        label=label,
        definition=optics.Circular_Waveplate(
            diameter=ONE_INCH,
            mount_definition=thorlabs.Rotation_Mount_RSP1(),
        ),
    )


def beamsplitter_cube(
    label: str = "Beamsplitter Cube",
    rotate_adapter=False,
) -> Component:
    return Component(
        label=label,
        definition=optics.Beamsplitter_Cube_on_Surface_Adapter(
            side_length=ONE_INCH,
            rotate_adapter=rotate_adapter,
        ),
    )


def sampler(label: str = "Sampler") -> Component:
    return Component(
        label=label,
        definition=optics.Circular_Sampler(
            diameter=ONE_INCH,
            mount_definition=thorlabs.Beamsplitter_Mount_B1G(),
        ),
    )


def iris(label: str = "Iris") -> Component:
    return Component(
        label=label,
        definition=thorlabs.Iris_IDA25(),
    )


def fiberport(label: str = "Fiberport") -> Component:
    return Component(
        label=label,
        definition=thorlabs.Fiberport_PAF2A4A(),
    )


fiberport_offset = (
    thorlabs.Fiberport_PAF2A4A.mount_offset_x
    - thorlabs.Fiberport_Mount_HCA3.mount_offset_x
)