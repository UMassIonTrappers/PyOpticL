from PyOpticL.layout import Component, Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import box_shape, cardinal_angle, fix_relative_imports

fix_relative_imports("../modules")

from beam_pickoff import beam_pickoff
from ecdl.ecdl import ecdl
from periscope import periscope


class Source_Box:
    object_group = "other"
    object_icon = ""
    object_color = (0.5, 0.5, 0.5)

    def __init__(self, dimensions: tuple, optical_height: dim = dim(1.5, "in")):
        """Initialize adjustable parameters"""
        self.dimensions = dimensions
        self.optical_height = optical_height

    def shape(self):
        part = box_shape(
            dimensions=self.dimensions,
            position=(0, 0, -self.optical_height),
            center=(1, 0, -1),
        )
        return part


laser_cooling_subsystem = Layout("Laser Cooling Subsystem")


def photoionization_subsystem_commercial():
    subsystem = Layout("Photoionization Subsystem")

    x = 0
    subsystem.add(
        Component(
            label="Source Box",
            definition=Source_Box(
                dimensions=(dim(8, "in"), dim(4, "in"), dim(4, "in"))
            ),
        ),
        position=(dim(-x, "grid"), 0, 0),
        rotation=cardinal_angle["left"],
    )

    x += 3
    subsystem.add(
        periscope(),
        position=(dim(-x, "grid"), 0, 0),
        rotation=cardinal_angle["left"],
    )

    x += 2
    subsystem.add(
        beam_pickoff(),
        position=(dim(-x, "grid"), dim(1, "in"), 0),
        rotation=cardinal_angle["left"],
    )

    return subsystem


def photoionization_subsystem_ecdl():
    subsystem = Layout("Photoionization Subsystem")

    x = -4
    subsystem.add(
        ecdl(),
        position=(dim(-x, "grid"), dim(1, "in"), 0),
        rotation=cardinal_angle["left"],
    )

    x += 7
    subsystem.add(
        periscope(),
        position=(dim(-x, "grid"), 0, 0),
        rotation=cardinal_angle["left"],
    )

    x += 2
    subsystem.add(
        beam_pickoff(),
        position=(dim(-x, "grid"), dim(1, "in"), 0),
        rotation=cardinal_angle["left"],
    )

    return subsystem


if __name__ == "__main__":
    subsystem = photoionization_subsystem_ecdl()
    subsystem.recompute()
