from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout
from PyOpticL.utils import box_shape, fix_relative_imports

fix_relative_imports("../modules")


class Source_Box:
    object_group = "other"
    object_icon = ""
    object_color = (0.5, 0.5, 0.5)

    def __init__(self, dimensions: tuple, optical_height: dim = dim(1.5, "in")):
        """Initialize adjustable parameters"""
        self.dimensions = dimensions

    def shape(self):
        part = box_shape(
            dimensions=self.dimensions,
            position=(0, 0, -self.optical_height),
            center=(-1, 0, -1),
        )
        return part


laser_cooling_subsystem = Layout("Laser Cooling Subsystem")
