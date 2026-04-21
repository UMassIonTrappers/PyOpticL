from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library.hardware import bolt
from PyOpticL.types import Dimension as dim
from PyOpticL.utils import bounding_box_shape, box_shape


class surface_adapter:
    """
    A generic surface mount adapter

    Args:
        height (float): The height of the mount
        min_width (float): The minimum width of the mount
        bolt_spacing (float): The spacing between the two mount holes of the adapter
        bolt_walls (float): The minimum thickness of the walls around the bolt holes
        slot_length (float): The length of the slot for the bolts, 0 for no slot
        drill_tolerance: (float): The tolerance to add around the drilling
    """

    object_group = "adapters"
    object_color = (0.5, 0.7, 0.5)

    def __init__(
        self,
        height: dim,
        bolt_spacing: dim,
        bolt_types: list = ["8_32", "M4"],
        bolt_length: dim = None,
        drill_depth: dim = None,
        min_length: dim = dim(0, "mm"),
        extra_thickness: dim = dim(6, "mm"),
        slot_length: dim = dim(0, "mm"),
        fillet_radius: dim = dim(5, "mm"),
        drill_tolerance: dim = dim(2, "mm"),
    ):
        self.height = height
        self.min_length = min_length
        self.bolt_spacing = bolt_spacing
        self.bolt_types = bolt_types
        self.bolt_length = bolt_length
        self.drill_depth = drill_depth
        self.extra_thickness = extra_thickness
        self.slot_length = slot_length
        self.drill_depth = drill_depth
        self.fillet_radius = fillet_radius
        self.drill_tolerance = drill_tolerance

    def subcomponents(self):
        components = []
        for x in [-1, 1]:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mounting Bolt",
                        definition=bolt(
                            types=self.bolt_types,
                            length=self.bolt_length,
                            clear_depth=self.height,
                            drill_depth=self.drill_depth,
                            slot_length=self.slot_length,
                        ),
                    ),
                    position=(0, x * self.bolt_spacing / 2, 0),
                    rotation=(0, 0, 0),
                ),
            )
        return components

    def shape(self):
        width = self.bolt_spacing + 2 * self.extra_thickness
        length = max(self.min_length, self.slot_length + 2 * self.extra_thickness)
        height = self.height
        part = box_shape(
            dimensions=(length, width, height),
            position=(0, 0, 0),
            center=(0, 0, 1),
            fillet=self.fillet_radius,
        )
        return part

    def drill(self):
        part = bounding_box_shape(
            shape=self.shape(),
            padding=self.drill_tolerance,
            fillet=self.fillet_radius + self.drill_tolerance,
        )
        return part
