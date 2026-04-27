from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import hardware
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import box_shape


class baseplate:
    """
    Standard optical baseplate

    Args:
        dimensions (tuple): The (x, y, z) dimensions of the baseplate
    """

    object_group = "baseplate"
    object_icon = ""
    object_color = (0.5, 0.5, 0.5)

    def __init__(self, dimensions: tuple, optical_height: dim, mount_holes=[]):
        """Initialize adjustable parameters"""
        self.dimensions = dimensions
        self.optical_height = optical_height
        self.mount_holes = mount_holes

    def subcomponents(self):
        components = []
        for x, y in self.mount_holes:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mount Hole",
                        definition=hardware.bolt(
                            types=["1/4_20", "M6"],
                            clear_depth=self.dimensions[2],
                        ),
                    ),
                    position=(dim(x, "grid"), dim(y, "grid"), -self.optical_height),
                    rotation=(0, 0, 0),
                )
            )
        return components

    def shape(self):
        part = box_shape(
            dimensions=self.dimensions,
            position=(0, 0, -self.optical_height),
            center=(-1, -1, 1),
        )
        return part
