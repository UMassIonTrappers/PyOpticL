from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import hardware, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import bounding_box_shape, box_shape, translate_shape


class surface_adapter:
    """
    A generic surface mount adapter

    Args:
        height (float): The height of the mount
        bolt_spacing (float): The spacing between the two mount holes of the adapter
        bolt_types (list): Supported bolt types used by the mount holes
        bolt_length (float): Length of the mounting bolts
        drill_depth (float): Drill depth for the mounting bolts
        min_length (float): The minimum length of the mount
        extra_thickness (float): Extra wall thickness around bolt spacing
        slot_length (float): The length of the slot for the bolts, 0 for no slot
        fillet_radius (float): Fillet radius for adapter corners
        drill_tolerance (float): The tolerance to add around the drilling
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
                        definition=hardware.bolt(
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


class slide_adapter:
    """
    A simple adapter within single point mounting for elements like irises
    """

    object_group = "adapters"
    object_color = (0.5, 0.7, 0.5)

    def __init__(
        self,
        post_height: dim = dim(20, "mm"),
        post_thickness: dim = dim(8, "mm"),
        mount_height: dim = dim(0.5, "in"),
        rail_height: dim = dim(8, "mm"),
        slot_length: dim = dim(10, "mm"),
        extra_thickness: dim = dim(6, "mm"),
        bolt_types: list = ["8_32", "M4"],
        bolt_length: dim = None,
        drill_depth: dim = None,
    ):
        self.post_height = post_height
        self.post_thickness = post_thickness
        self.mount_height = mount_height
        self.rail_height = rail_height
        self.slot_length = slot_length
        self.extra_thickness = extra_thickness
        self.bolt_types = bolt_types
        self.bolt_length = bolt_length
        self.drill_depth = drill_depth

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=self.bolt_types,
                        length=self.bolt_length,
                        clear_depth=self.mount_height,
                        drill_depth=self.drill_depth,
                        slot_length=self.slot_length,
                    ),
                ),
                position=(
                    -self.post_thickness - self.slot_length / 2 - self.extra_thickness,
                    0,
                    self.rail_height - self.mount_height,
                ),
                rotation=(0, 0, 0),
            ),
        ]

    def shape(self):
        part = box_shape(
            dimensions=(
                self.post_thickness,
                self.extra_thickness * 2,
                self.post_height,
            ),
            position=(0, 0, -self.mount_height),
            center=(1, 0, -1),
        )
        part = part.fuse(
            box_shape(
                dimensions=(
                    self.slot_length + self.extra_thickness * 2 + self.post_thickness,
                    self.extra_thickness * 2,
                    self.rail_height,
                ),
                position=(0, 0, -self.mount_height),
                center=(1, 0, -1),
                fillet=dim(5, "mm"),
            )
        )
        return part
