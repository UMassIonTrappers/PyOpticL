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

    def __init__(self, dimensions: tuple, optical_height: dim):
        """Initialize adjustable parameters"""
        self.dimensions = dimensions
        self.optical_height = optical_height

    def shape(self):
        part = box_shape(
            dimensions=self.dimensions,
            position=(0, 0, -self.optical_height),
            center=(-1, -1, 1),
        )
        return part
