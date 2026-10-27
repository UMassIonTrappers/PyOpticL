import Part

from PyOpticL import settings
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import (
    bolt_shape,
    bolt_slot_shape,
    cylinder_shape,
    default_bolt_length,
    hex_prism_shape,
)


class Bolt:
    """
    Standard bolt

    Args:
        types (list): List of all supported bolt types (for example, one metric and one imperial)
        length (float): Length of the bolt including the head
        clear_depth (float): The depth at which the hole threading should start
        drill_depth (float): Depth of the drilled hole after clear_depth, defaults uses default_extra_drill_depth setting
        washer_diameter (float): Diameter of washer to include, None for no washer
        countersink (bool): Whether the bolt head is a countersink
        head_tolerance (float): Tolerance of the bolt head / washer diameter
        from_top (bool): Whether the origin is at the top or bottom of the bolt head
        slot_length (float): Length of slot drilling a slot, None for no slot

    The threaded part of the drilled hole follows settings.set_thread_mode():
        'tapped'      tap drill hole (default)
        'heat_insert' hole for a heat-set threaded insert
        'nut'         clearance hole and a hex nut pocket at the bolt tip, open to the
                      back of the drilled part
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

    # hex nuts (ISO 4032 / ASME B18.2.2): width across flats and height
    nut_dimensions = {
        "4_40": dict(width=dim(1 / 4, "in"), height=dim(3 / 32, "in")),
        "8_32": dict(width=dim(11 / 32, "in"), height=dim(1 / 8, "in")),
        "1/4_20": dict(width=dim(7 / 16, "in"), height=dim(7 / 32, "in")),
        "M3": dict(width=dim(5.5, "mm"), height=dim(2.4, "mm")),
        "M4": dict(width=dim(7, "mm"), height=dim(3.2, "mm")),
        "M6": dict(width=dim(10, "mm"), height=dim(5.2, "mm")),
    }
    nut_tolerance = dim(0.3, "mm")  # added to the pocket width and height

    # heat-set inserts for 3D printed parts: hole diameter and minimum hole depth
    # (CNC Kitchen standard-length inserts; the imperial sizes are taken from the
    # manufacturer's table but have not been test-printed - check before relying on them)
    insert_dimensions = {
        "4_40": dict(diameter=dim(4.0, "mm"), length=dim(5.7, "mm")),
        "8_32": dict(diameter=dim(5.7, "mm"), length=dim(8.2, "mm")),
        "1/4_20": dict(diameter=dim(8.1, "mm"), length=dim(12.7, "mm")),
        "M3": dict(diameter=dim(4.0, "mm"), length=dim(5.7, "mm")),
        "M4": dict(diameter=dim(5.6, "mm"), length=dim(8.1, "mm")),
        "M6": dict(diameter=dim(8.0, "mm"), length=dim(12.7, "mm")),
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

        self.type = types[0]
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

    def back_pocket(self) -> Part.Shape | None:
        """
        Pocket at the bolt tip that a drilled part opens to its back face; only applied
        to the part containing the bolt tip (see Component.compute_shape)

        Returns:
            Part.Shape | None: The nut pocket in 'nut' thread mode, otherwise None
        """

        if settings.get_thread_mode() == "nut":
            return self.nut_pocket()
        return None

    def _thread_dimensions(self, table: dict, kind: str) -> dict:
        if self.type not in table:
            raise ValueError(f"No {kind} dimensions defined for bolt type {self.type}")
        return table[self.type]

    def tip_depth(self) -> float:
        """Distance from the bolt origin to its tip, along -z"""

        if self.from_top:
            return self.length - self.available_bolt_types[self.type]["head_height"]
        return self.length

    def nut_pocket(self, extend: float = 0) -> Part.Shape:
        """
        Hex pocket for a nut threaded fully onto the bolt tip

        Args:
            extend (float): Extra length of the pocket beyond the bolt tip

        Returns:
            Part.Shape: The pocket, in the bolt frame
        """

        nut = self._thread_dimensions(self.nut_dimensions, "nut")
        height = nut["height"] + self.nut_tolerance
        return hex_prism_shape(
            across_flats=nut["width"] + self.nut_tolerance,
            height=height + extend,
            position=(0, 0, -self.tip_depth() - extend),
        )

    def drill(self):
        dims = self.available_bolt_types[self.type]

        if self.washer_diameter:
            head_diameter = self.washer_diameter
        else:
            head_diameter = dims["head_diameter"]
        head_diameter += self.head_tolerance

        thread_mode = settings.get_thread_mode()
        tap_diameter = dims["tap_diameter"]
        drill_depth = self.drill_depth
        if thread_mode == "nut":
            # clearance down to the nut, see back_pocket()
            tap_diameter = dims["clear_diameter"]
            drill_depth = self.tip_depth()
        elif thread_mode == "heat_insert":
            tap_diameter = self._thread_dimensions(
                self.insert_dimensions, "heat insert"
            )["diameter"]

        if not self.slot_length:
            part = bolt_shape(
                clear_diameter=dims["clear_diameter"],
                tap_diameter=tap_diameter,
                length=drill_depth,
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
                tap_diameter=tap_diameter,
                length=drill_depth,
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
