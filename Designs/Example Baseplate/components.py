from PyOpticL.beam_path import Interface
from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import hardware, optics, thorlabs
from PyOpticL.types import Dimension as dim
from PyOpticL.utils import bounding_box_shape, box_shape, cylinder_shape, import_model


def mirror():
    return Component(
        label="Mirror",
        definition=optics.circular_mirror(
            mount_definition=thorlabs.mirror_mount_k05s1(),
        ),
    )
