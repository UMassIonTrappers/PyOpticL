from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import baseplate, hardware, optics, thorlabs
from PyOpticL.types import Dimension as dim
from PyOpticL.types import cardinal_angle, turn_angle


def mirror(label: str = "Mirror") -> Component:
    return Component(
        label=label,
        definition=optics.circular_mirror(
            mount_definition=thorlabs.mirror_mount_k05s1(),
        ),
    )


def waveplate(label: str = "Waveplate") -> Component:
    return Component(
        label=label,
        definition=optics.circular_waveplate(
            mount_definition=thorlabs.rotation_mount_rsp05(),
        ),
    )


def beamsplitter_cube(label: str = "Beamsplitter Cube") -> Component:
    return Component(
        label=label,
        definition=optics.beamsplitter_cube_on_surface_adapter(),
    )
