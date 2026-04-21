from PyOpticL import settings
from PyOpticL.types import Dimension as dim
from PyOpticL.utils import (
    bolt_shape,
    bolt_slot_shape,
    cylinder_shape,
    default_bolt_length,
)


class bolt:
    """
    Standard bolt

    Args:
        label (str): The label for the component
        types (list): List of all supported bolt types (for example, one metric and one imperial)
        length (float): Length of the bolt including the head
        clear_depth (float): The depth at which the hole threading should start
        drill_depth (float): Depth of the drilled hole after clear_depth, defaults uses default_extra_drill_depth setting
        washer_diameter (float): Diameter of washer to include, None for no washer
        countersink (bool): Whether the bolt head is a countersink
        head_tolerance (float): Tolerance of the bolt head / washer diameter
        from_top (bool): Whether the origin is at the top or bottom of the bolt head
        slot_length (float): Length of slot drilling a slot, None for no slot
    """

    available_bolt_types = {
        "4_40": dict(
            clear_diameter=dim(0.12, "in"),
            tap_diameter=dim(0.089, "in"),
            head_diameter=dim(5.5, "mm"),
            head_height=dim(2.5, "mm"),
            tags=["imperial"],
        ),
        "8_32": dict(
            clear_diameter=dim(0.172, "in"),
            tap_diameter=dim(0.136, "in"),
            head_diameter=dim(7, "mm"),
            head_height=dim(4.4, "mm"),
            tags=["imperial"],
        ),
        "1/4_20": dict(
            clear_diameter=dim(0.26, "in"),
            tap_diameter=dim(0.201, "in"),
            head_diameter=dim(9.8, "mm"),
            head_height=dim(8, "mm"),
            tags=["imperial"],
        ),
        "M3": dict(
            clear_diameter=dim(3.2, "mm"),
            tap_diameter=dim(2.5, "mm"),
            head_diameter=dim(5.5, "mm"),
            head_height=dim(2.4, "mm"),
            tags=["metric"],
        ),
        "M4": dict(
            clear_diameter=dim(4.3, "mm"),
            tap_diameter=dim(3.3, "mm"),
            head_diameter=dim(7, "mm"),
            head_height=dim(3.0, "mm"),
            tags=["metric"],
        ),
        "M6": dict(
            clear_diameter=dim(6.4, "mm"),
            tap_diameter=dim(5.0, "mm"),
            head_diameter=dim(10, "mm"),
            head_height=dim(4.0, "mm"),
            tags=["metric"],
        ),
    }

    object_group = "hardware"
    object_icon = ""
    object_color = (0.8, 0.8, 0.8)

    def __init__(
        self,
        types: list,
        length: dim = None,
        clear_depth: dim = 0,
        drill_depth: dim = None,
        washer_diameter: dim = None,
        countersink: bool = False,
        head_tolerance: dim = dim(1, "mm"),
        from_top: bool = True,
        slot_length: dim = None,
    ):

        self.length = length
        self.clear_depth = clear_depth
        self.drill_depth = drill_depth
        self.washer_diameter = washer_diameter
        self.countersink = countersink
        self.head_tolerance = head_tolerance
        self.from_top = from_top
        self.slot_length = slot_length

        if slot_length and countersink:
            raise ValueError("Bolt does not support both slot and countersink")

        if washer_diameter and countersink:
            raise ValueError("Bolt does not support both washer and countersink")

        if length is None:
            self.length = default_bolt_length(clear_depth, drill_depth)

        if drill_depth is None:
            self.drill_depth = self.length + settings.default_extra_drill_depth

        for bolt_type in types:
            if bolt_type not in self.available_bolt_types:
                raise ValueError(f"Bolt type {bolt_type} is not supported")
            if (
                settings.measurement_system
                in self.available_bolt_types[bolt_type]["tags"]
            ):
                self.type = bolt_type
                break

    def shape(self):
        dims = self.available_bolt_types[self.type]
        length = self.length
        if self.from_top:
            length -= dims["head_height"]
        part = bolt_shape(
            clear_diameter=dims["clear_diameter"],
            tap_diameter=dims["tap_diameter"],
            length=length,
            clear_depth=0,
            head_diameter=dims["head_diameter"],
            head_height=dims["head_height"],
            position=(0, 0, 0),
            countersink=self.countersink,
            from_top=self.from_top,
        )
        return part

    def drill(self):
        dims = self.available_bolt_types[self.type]

        if self.washer_diameter:
            head_diameter = self.washer_diameter
        else:
            head_diameter = dims["head_diameter"]
        head_diameter += self.head_tolerance

        if not self.slot_length:
            part = bolt_shape(
                clear_diameter=dims["clear_diameter"],
                tap_diameter=dims["tap_diameter"],
                length=self.drill_depth,
                clear_depth=self.clear_depth,
                head_diameter=head_diameter,
                head_height=dims["head_height"],
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                countersink=self.countersink,
                from_top=self.from_top,
            )
        else:
            part = bolt_slot_shape(
                clear_diameter=dims["clear_diameter"],
                tap_diameter=dims["tap_diameter"],
                length=self.drill_depth,
                clear_depth=self.clear_depth,
                head_diameter=head_diameter,
                head_height=dims["head_height"],
                slot_length=self.slot_length,
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                from_top=self.from_top,
            )
        return part


class alignment_pin:
    """
    Standard alignment pin

    Args:
        diameter (float): Diameter of the pin
        length (float): Length of the pin
        hole_tolerance (float): Tolerance in the hole diameter
        depth_tolerance (float): Tolerance in the pin depth
    """

    object_group = "hardware"
    object_icon = ""
    object_color = (0.8, 0.8, 0.8)

    def __init__(
        self,
        diameter: dim,
        length: dim,
        hole_tolerance: dim = dim(0.05, "mm"),
        depth_tolerance: dim = dim(1, "mm"),
    ):
        self.diameter = diameter
        self.length = length
        self.hole_tolerance = hole_tolerance
        self.depth_tolerance = depth_tolerance

    def shape(self):
        part = cylinder_shape(
            diameter=self.diameter,
            height=self.length,
            position=(0, 0, -self.depth_tolerance / 2),
            rotation=(180, 0, 0),
        )
        return part

    def drill(self):
        part = cylinder_shape(
            diameter=self.diameter + self.hole_tolerance,
            height=self.length + self.depth_tolerance,
            position=(0, 0, 0),
            rotation=(180, 0, 0),
        )
        return part
