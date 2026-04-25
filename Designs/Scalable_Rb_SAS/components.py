from PyOpticL.beam_path import Interface
from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import hardware
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import bounding_box_shape, box_shape, cylinder_shape, import_model


class rb_cell_holder:
    """
    A surface mount holder for the RB cell
    """

    object_group = "adapters"
    object_color = (0.5, 0.7, 0.5)
    mesh = import_model("rb_cell_holder", "./models")

    def __init__(self, bolt_length: dim = None, drill_depth: dim = None):
        self.bolt_length = bolt_length
        self.drill_depth = drill_depth

    def subcomponents(self):
        components = []
        for x, y in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mounting Bolt",
                        definition=hardware.bolt(
                            types=["8_32", "M4"],
                            length=self.bolt_length,
                            clear_depth=dim(1, "in"),
                            drill_depth=self.drill_depth,
                        ),
                    ),
                    position=(
                        x * dim(45, "mm"),
                        y * dim(15.7, "mm"),
                        dim(1 / 2, "in"),
                    ),
                    rotation=(0, 0, 0),
                )
            )
        return components

    def drill(self):
        part = bounding_box_shape(
            shape=self.mesh, padding=dim(5, "mm"), fillet=dim(5, "mm")
        )
        return part


class rb_cell_tube:
    """
    A model of a cylindrical Rb cell
    """

    object_group = "optics"
    object_color = (0.5, 0.5, 0.7)
    object_transparency = 75

    def __init__(
        self,
        diameter: dim,
        length: dim,
        bolt_length: dim = None,
        drill_depth: dim = None,
    ):
        self.diameter = diameter
        self.length = length
        self.bolt_length = bolt_length
        self.drill_depth = drill_depth

    def interfaces(self):
        return [
            Interface(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.diameter,
            )
        ]

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Rb Cell Holder",
                    definition=rb_cell_holder(
                        bolt_length=self.bolt_length,
                        drill_depth=self.drill_depth,
                    ),
                ),
                position=(0, 0, 0),
                rotation=(0, 0, 0),
            )
        ]

    def shape(self):
        part = cylinder_shape(
            diameter=self.diameter,
            height=self.length,
            rotation=(0, 90, 0),
            center=0,
        )
        # end caps
        for i in [-1, 1]:
            part = part.fuse(
                cylinder_shape(
                    diameter=self.diameter + dim(2, "mm"),
                    height=dim(2, "mm"),
                    center=i,
                    position=(i * self.length / 2, 0, 0),
                    rotation=(0, 90, 0),
                )
            )
        return part


class rb_cell_cube:
    """
    A cube-shaped Rb cell for testing purposes
    """

    object_group = "optics"
    object_color = (0.5, 0.5, 0.7)
    object_transparency = 75

    def __init__(
        self,
        side_length: dim,
        drill_tolerance: dim = dim(0.5, "mm"),
        corner_drill_diameter: dim = dim(3, "mm"),
        bolt_length: dim = None,
        drill_depth: dim = None,
    ):
        self.side_length = side_length
        self.drill_tolerance = drill_tolerance
        self.corner_drill_diameter = corner_drill_diameter
        self.bolt_length = bolt_length
        self.drill_depth = drill_depth

    def interfaces(self):
        return [
            Interface(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.side_length,
            )
        ]

    def shape(self):
        part = box_shape(
            dimensions=(self.side_length, self.side_length, self.side_length),
        )
        return part

    def drill(self):
        part = box_shape(
            dimensions=(
                self.side_length + self.drill_tolerance,
                self.side_length + self.drill_tolerance,
                self.side_length,
            ),
            position=(0, 0, 0),
            center=(0, 0, 0),
        )
        for x, y in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            part = part.fuse(
                cylinder_shape(
                    diameter=self.corner_drill_diameter,
                    height=self.side_length,
                    position=(
                        x * self.side_length / 2,
                        y * self.side_length / 2,
                        -self.side_length / 2,
                    ),
                )
            )
        return part
