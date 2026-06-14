from PyOpticL.layout import Component
from PyOpticL.library import optics, thorlabs


def mirror(label: str = "Mirror") -> Component:
    return Component(
        label=label,
        definition=optics.Circular_Mirror(
            mount_definition=thorlabs.Mirror_Mount_K05S1(),
        ),
    )


def waveplate(label: str = "Waveplate") -> Component:
    return Component(
        label=label,
        definition=optics.Circular_Waveplate(
            mount_definition=thorlabs.Rotation_Mount_RSP05(),
        ),
    )


def beamsplitter_cube(
    label: str = "Beamsplitter Cube", rotate_adapter=False
) -> Component:
    return Component(
        label=label,
        definition=optics.Beamsplitter_Cube_on_Surface_Adapter(
            rotate_adapter=rotate_adapter
        ),
    )


def sampler(label: str = "Sampler"):
    return Component(
        label=label,
        definition=optics.Circular_Sampler(
            mount_definition=thorlabs.Beamsplitter_Mount_B05G(),
        ),
    )


def iris(label: str = "Iris") -> Component:
    return Component(
        label=label,
        definition=thorlabs.Iris_IDA12(),
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
