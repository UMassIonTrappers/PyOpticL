import FreeCAD as App
import numpy as np
import Part

from PyOpticL import settings
from PyOpticL.beam_path import Lens, Reflection, Waveplate
from PyOpticL.icons import optic_icon, thorlabs_icon
from PyOpticL.layout import Component
from PyOpticL.types import Dimension as dim
from PyOpticL.utils import (
    Subcomponent,
    bolt_shape,
    bolt_slot_shape,
    box_shape,
    cylinder_shape,
    default_bolt_length,
    import_model,
)

##########################
### Example Components ###
##########################


class example_component:
    """
    An example component class for reference on creating new components
    creates a simple cube which mounts using a single bolt

    Args:
        side_length (float): The side length of the cube
        height (float): The height of the cube
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults based on minimum thread engagement settings)
    """

    object_group = "example"
    object_icon = ""
    object_color = (0.5, 0.5, 0.5)

    def __init__(
        self,
        side_length: dim,
        height: dim,
        drill_depth: dim = None,
        bolt_length: dim = None,
    ):
        """Initialize adjustable parameters"""
        self.side_length = side_length
        self.height = height
        self.drill_depth = drill_depth
        self.bolt_length = bolt_length

    def subcomponents(self) -> list[Subcomponent]:
        """Define any sub-components"""
        return [
            Subcomponent(
                component=Component(
                    "Mounting Bolt",
                    bolt(
                        types=["8_32", "M4"],
                        length=self.bolt_length,
                        clear_depth=self.height,
                        drill_depth=self.drill_depth,
                    ),
                ),
                position=(0, 0, self.height),
                rotation=(0, 0, 0),
            )
        ]

    def shape(self) -> Part.Shape:
        """Define the main shape of the component"""
        part = box_shape(
            dimensions=(self.side_length, self.side_length, self.height),
            position=(0, 0, 0),
            center=(0, 0, -1),
            fillet=1,
        )
        return part


############################
### Baseplate Components ###
############################


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


###########################
### Hardware Components ###
###########################


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
            self.drill_depth = (
                self.length - self.clear_depth + settings.default_extra_drill_depth
            )

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


##########################
### Optical Components ###
##########################


class circular_reflector:
    """
    A circular reflector component

    Args:
        diameter (float): The diameter of the reflector
        thickness (float): The thickness of the reflector
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to reflector origin
                              If None, defaults to (-thickness, 0, 0)
        ref_ratio (float): The ratio of reflected to transmitted light
        ref_polarization (float): The reflected polarization angle
        ref_wavelengths (list): A list of tuples representing the ranges of wavelengths to be reflected
                                 Use None for open-ended ranges
        refractive_index (float): refractive index of the substrate
    """

    object_group = "optic"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)

    def __init__(
        self,
        diameter: dim,
        thickness: dim,
        mount_definition: object = None,
        mount_offset: tuple = None,
        ref_ratio: float = None,
        ref_polarization: float = None,
        ref_wavelengths: list = None,
        refractive_index: float = 1.5,
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset
        self.ref_ratio = ref_ratio
        self.ref_polarization = ref_polarization
        self.ref_wavelengths = ref_wavelengths
        self.refractive_index = refractive_index

        if ref_ratio != None or ref_polarization != None or ref_wavelengths != None:
            self.bidirectional = True
            self.max_angle = 180
        else:
            self.bidirectional = False
            self.max_angle = 90

    def interfaces(self):
        interfaces = [
            Reflection(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.diameter,
                ref_ratio=self.ref_ratio,
                ref_polarization=self.ref_polarization,
                ref_wavelengths=self.ref_wavelengths,
                refractive_index_ratio=1 / self.refractive_index,
                max_angle=self.max_angle,
            ),
        ]

        if self.bidirectional:
            interfaces.append(
                Reflection(
                    position=(-self.thickness, 0, 0),
                    rotation=(0, 0, 180),
                    diameter=self.diameter,
                    ref_ratio=0,
                    refractive_index_ratio=1 / self.refractive_index,
                    max_angle=self.max_angle,
                )
            )

        return interfaces

    def subcomponents(self):
        if self.mount_definition != None:
            mount_offset = self.mount_offset
            if mount_offset is None:
                mount_offset = (-self.thickness, 0, 0)
            return [
                Subcomponent(
                    component=Component(
                        label="Mount",
                        definition=self.mount_definition,
                    ),
                    position=mount_offset,
                    rotation=(0, 0, 0),
                )
            ]
        else:
            return []

    def shape(self):
        part = cylinder_shape(
            diameter=self.diameter,
            height=self.thickness,
            position=(-self.thickness, 0, 0),
            rotation=(0, 90, 0),
        )
        return part


class circular_mirror(circular_reflector):
    """
    A circular mirror component

    Args:
        diameter (float): The diameter of the mirror
        thickness (float): The thickness of the mirror
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to mirror origin
                              If None, defaults to (-thickness, 0, 0)
    """

    def __init__(
        self,
        diameter: dim,
        thickness: dim,
        mount_definition: object = None,
        mount_offset: tuple = None,
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
            mount_definition=mount_definition,
            mount_offset=mount_offset,
        )


class circular_sampler(circular_reflector):
    """
    A circular sampler component

    Args:
        diameter (float): The diameter of the sampler
        thickness (float): The thickness of the sampler
        ref_ratio (float): The ratio of reflected to transmitted light
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to sampler origin
                              If None, defaults to (-thickness, 0, 0)
    """

    def __init__(
        self,
        diameter: dim,
        thickness: dim,
        ref_ratio: float,
        mount_definition: object = None,
        mount_offset: tuple = None,
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
            mount_definition=mount_definition,
            mount_offset=mount_offset,
            ref_ratio=ref_ratio,
        )

        self.object_transparency = int(100 * ref_ratio)


class circular_dichroic_mirror(circular_reflector):
    """
    A circular dichroic mirror component

    Args:
        diameter (float): The diameter of the dichroic mirror
        thickness (float): The thickness of the dichroic mirror
        ref_wavelengths (list): A list of tuples representing the ranges of wavelengths to be reflected
                                 Use None for open-ended ranges
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to the mirror origin
                              If None, defaults to (-thickness, 0, 0)
    """

    object_transparency = 25

    def __init__(
        self,
        diameter: dim,
        thickness: dim,
        ref_wavelengths: list,
        mount_definition: object = None,
        mount_offset: tuple = None,
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
            mount_definition=mount_definition,
            mount_offset=mount_offset,
            ref_wavelengths=ref_wavelengths,
        )


class spherical_lens:
    """
    A spherical lens component

    Args:
        diameter (float): The diameter of the lens
        thickness (float): The thickness of the lens
        focal_length (float): The focal length of the lens
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to lens origin
                              If None, defaults to (0, 0, 0)
    """

    object_group = "optic"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)
    object_transparency = 75

    def __init__(
        self,
        diameter: dim,
        thickness: dim,
        focal_length: dim,
        mount_definition: object = None,
        mount_offset: tuple = None,
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.focal_length = focal_length
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset

    def interfaces(self):
        return [
            Lens(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.diameter,
                focal_length=self.focal_length,
            )
        ]

    def subcomponents(self):
        if self.mount_definition != None:
            mount_offset = self.mount_offset
            if mount_offset is None:
                mount_offset = (0, 0, 0)
            return [
                Subcomponent(
                    component=Component(
                        label="Mount",
                        definition=self.mount_definition,
                    ),
                    position=mount_offset,
                    rotation=(0, 0, 0),
                )
            ]
        else:
            return []

    def shape(self):
        part = cylinder_shape(
            diameter=self.diameter,
            height=self.thickness,
            position=(-self.thickness / 2, 0, 0),
            rotation=(0, 90, 0),
        )
        return part


class circular_waveplate:
    """
    A circular waveplate component

    Args:
        diameter (float): The diameter of the waveplate
        thickness (float): The thickness of the waveplate
        retardance (float): The phase delay in waves (0.25 quarter-wave, 0.5 half-wave)
        fast_axis_angle (float): The angle of the fast axis in degrees
    """

    object_group = "optic"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)
    object_transparency = 75

    def __init__(
        self,
        diameter: dim,
        thickness: dim,
        retardance: float,
        fast_axis_angle: float,
        mount_definition: object = None,
        mount_offset: tuple = None,
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.retardance = retardance
        self.fast_axis_angle = fast_axis_angle
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset

    def interfaces(self):
        return [
            Waveplate(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.diameter,
                retardance=self.retardance,
                fast_axis_angle=self.fast_axis_angle,
            )
        ]

    def subcomponents(self):
        if self.mount_definition != None:
            mount_offset = self.mount_offset
            if mount_offset is None:
                mount_offset = (0, 0, 0)
            return [
                Subcomponent(
                    component=Component(
                        label="Mount",
                        definition=self.mount_definition,
                    ),
                    position=mount_offset,
                    rotation=(0, 0, 0),
                )
            ]
        else:
            return []

    def shape(self):
        part = cylinder_shape(
            diameter=self.diameter,
            height=self.thickness,
            position=(-self.thickness / 2, 0, 0),
            rotation=(0, 90, 0),
        )
        return part


class beamsplitter_cube:
    """
    A generic beamsplitter cube component

    Args:
        size (float): The side length of the cube
        thickness (float): The thickness of the beam splitter interface
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to the cube origin
                              If None, defaults to (0, 0, -size/2)
    """

    object_group = "optic"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)
    object_transparency = 75

    def __init__(
        self,
        side_length: dim,
        ref_polarization: float = None,
        ref_ratio: float = None,
        mount_definition: object = None,
        mount_offset: tuple = None,
        drill_tolerance: dim = dim(0.5, "mm"),
        corner_drill_diameter: dim = dim(3, "mm"),
    ):
        if ref_ratio is None and ref_polarization is None:
            raise ValueError("Either ref_ratio or ref_polarization must be specified")

        self.side_length = side_length
        self.ref_polarization = ref_polarization
        self.ref_ratio = ref_ratio
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset
        self.drill_tolerance = drill_tolerance
        self.corner_drill_diameter = corner_drill_diameter

    def interfaces(self):
        return [
            Reflection(
                position=(0, 0, 0),
                rotation=(0, 0, 45),
                width=self.side_length * np.sqrt(2),
                height=self.side_length * np.sqrt(2),
                ref_polarization=self.ref_polarization,
                ref_ratio=self.ref_ratio,
            )
        ]

    def subcomponents(self):
        if self.mount_definition != None:
            mount_offset = self.mount_offset
            if mount_offset is None:
                mount_offset = (0, 0, -self.side_length / 2)
            return [
                Subcomponent(
                    component=Component(
                        label="Mount",
                        definition=self.mount_definition,
                    ),
                    position=mount_offset,
                    rotation=(0, 0, 0),
                )
            ]
        else:
            return []

    def shape(self):
        part = box_shape(
            dimensions=(self.side_length, self.side_length, self.side_length),
            position=(0, 0, 0),
            center=(0, 0, 0),
        )
        diag = self.side_length * np.sqrt(2)
        part = part.cut(
            box_shape(
                dimensions=(0.1, diag, diag),
                position=(0, 0, 0),
                rotation=(0, 0, 45),
                center=(0, 0, 0),
            )
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


################################
### Custom Adapters / Mounts ###
################################


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

    object_group = "adapter"
    object_color = (0.5, 0.7, 0.5)

    def __init__(
        self,
        height: dim,
        min_length: dim,
        bolt_spacing: dim,
        bolt_types: list = ["8_32", "M4"],
        bolt_length: dim = None,
        drill_depth: dim = None,
        extra_thickness: dim = dim(6, "mm"),
        slot_length: dim = dim(0, "mm"),
        fillet_radius: dim = dim(5, "mm"),
        drill_tolerance: dim = dim(1, "mm"),
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
        width = self.bolt_spacing + 2 * self.extra_thickness + 2 * self.drill_tolerance
        length = (
            max(self.min_length, self.slot_length + 2 * self.extra_thickness)
            + 2 * self.drill_tolerance
        )
        height = self.height
        part = box_shape(
            dimensions=(length, width, height),
            position=(0, 0, 0),
            center=(0, 0, 1),
            fillet=self.fillet_radius,
        )
        return part


###########################
### Thorlabs Components ###
###########################


class mirror_mount_k05s1:
    """
    Mirror mount, model K05S1

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mount"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("polaris-k05s1")
    mount_position = (-8.017, 0.000, -12.700)
    bolt_position = (-8.017, 0.000, -7.112)
    pin_positions = [(-8.017, 5.000, -10.795), (-8.017, -5.000, -10.795)]

    def __init__(self, drill_depth: dim = None, bolt_length: dim = None):
        self.drill_depth = drill_depth
        self.bolt_length = bolt_length

    def subcomponents(self):
        components = [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=bolt(
                        types=["8_32", "M4"],
                        length=self.bolt_length,
                        clear_depth=self.mount_position[2] - self.bolt_position[2],
                        drill_depth=self.drill_depth,
                        from_top=False,
                    ),
                ),
                position=self.bolt_position,
                rotation=(0, 0, 0),
            )
        ]
        for position in self.pin_positions:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Alignment Pin",
                        definition=alignment_pin(
                            diameter=dim(1.9, "mm"), length=dim(4, "mm")
                        ),
                    ),
                    position=position,
                    rotation=(0, 0, 0),
                )
            )
        return components


class rotation_mount_rsp05:
    """
    Rotation mount, model RSP05

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mount"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-rsp05")
    mount_position = (-0.635, -0.000, -13.975)
    mount_hole_end = (-0.635, -0.000, -7.521)

    def __init__(
        self,
        include_bolt: bool = True,
        bolt_distance: dim = dim(10, "mm"),
        bolt_distance_includes_head: bool = True,
        bolt_length: dim = None,
    ):
        self.include_bolt = include_bolt
        self.bolt_distance = bolt_distance
        self.bolt_distance_includes_head = bolt_distance_includes_head
        self.bolt_length = bolt_length

    def subcomponents(self):
        components = []
        if self.include_bolt:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mounting Bolt",
                        definition=bolt(
                            types=["8_32", "M4"],
                            length=self.bolt_length,
                            clear_depth=self.bolt_distance,
                            drill_depth=self.mount_hole_end[2] - self.mount_position[2],
                            from_top=self.bolt_distance_includes_head,
                        ),
                    ),
                    position=(
                        self.mount_position[0],
                        self.mount_position[1],
                        self.mount_position[2] - self.bolt_distance,
                    ),
                    rotation=(180, 0, 0),
                )
            )
        return components


class photodetector_pda10a2:
    """
    Photodetector, model PDA10A2
    """

    object_group = "detector"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-pda10a2")
    mount_position = (-10.544, 0.000, -25.000)
    mount_hole_end = (-10.544, 0.000, -18.142)

    def __init__(
        self,
        include_bolt: bool = True,
        bolt_distance: dim = dim(10, "mm"),
        bolt_distance_includes_head: bool = True,
        bolt_length: dim = None,
    ):
        self.include_bolt = include_bolt
        self.bolt_distance = bolt_distance
        self.bolt_distance_includes_head = bolt_distance_includes_head
        self.bolt_length = bolt_length

    def subcomponents(self):
        components = []
        if self.include_bolt:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mounting Bolt",
                        definition=bolt(
                            types=["8_32", "M4"],
                            length=self.bolt_length,
                            clear_depth=self.bolt_distance,
                            drill_depth=self.mount_hole_end[2] - self.mount_position[2],
                            from_top=self.bolt_distance_includes_head,
                        ),
                    ),
                    position=(
                        self.mount_position[0],
                        self.mount_position[1],
                        self.mount_position[2] - self.bolt_distance,
                    ),
                    rotation=(180, 0, 0),
                )
            )
        return components


#########################
### Common Assemblies ###
#########################


class rsp05_on_surface_adapter(rotation_mount_rsp05):
    """
    Rotation mount, model RSP05, on a surface adapter

    Args:
    drill_depth (float): The depth of the mounting hole
    bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    adapter_parameters (dict): A dictionary of parameters to override the default surface adapter parameters
    """

    def __init__(
        self,
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
    ):
        self.adapter_parameters = dict(
            height=dim(10, "mm"),
            min_length=dim(10, "mm"),
            bolt_spacing=dim(25, "mm"),
            bolt_types=["8_32", "M4"],
            bolt_length=bolt_length,
            drill_depth=drill_depth,
            extra_thickness=dim(6, "mm"),
            slot_length=dim(0, "mm"),
            fillet_radius=dim(5, "mm"),
            drill_tolerance=dim(1, "mm"),
        )
        self.adapter_parameters |= adapter_parameters
        super().__init__(
            include_bolt=True,
            bolt_distance=self.adapter_parameters["height"],
        )

    def subcomponents(self):
        components = super().subcomponents()
        components.append(
            Subcomponent(
                component=Component(
                    label="Surface Adapter",
                    definition=surface_adapter(**self.adapter_parameters),
                ),
                position=self.mount_position,
                rotation=(0, 0, 0),
            )
        )
        return components


class beamsplitter_cube_on_surface_adapter(beamsplitter_cube):
    """
    Beamsplitter cube on a surface adapter

    Args:
        size (float): The side length of the cube
        ref_polarization (float): The reflected polarization angle
        ref_ratio (float): The ratio of reflected to transmitted light
        adapter_parameters (dict): A dictionary of parameters to override the default surface adapter parameters
    """

    def __init__(
        self,
        side_length: dim,
        optical_height: dim,
        ref_polarization: float = None,
        ref_ratio: float = None,
        inset_depth: dim = dim(1, "mm"),
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
    ):
        super().__init__(
            side_length=side_length,
            ref_polarization=ref_polarization,
            ref_ratio=ref_ratio,
        )
        self.adapter_parameters = dict(
            height=optical_height - side_length / 2 + inset_depth,
            min_length=side_length + self.corner_drill_diameter + dim(2, "mm"),
            bolt_spacing=dim(25, "mm"),
            bolt_types=["8_32", "M4"],
            bolt_length=bolt_length,
            drill_depth=drill_depth,
            extra_thickness=dim(6, "mm"),
            slot_length=dim(0, "mm"),
            fillet_radius=dim(5, "mm"),
            drill_tolerance=dim(1, "mm"),
        )
        self.adapter_parameters |= adapter_parameters
        self.optical_height = optical_height
        self.inset_depth = inset_depth

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Surface Adapter",
                    definition=surface_adapter(**self.adapter_parameters),
                ),
                position=(0, 0, self.inset_depth - self.side_length / 2),
                rotation=(0, 0, 0),
            )
        ]


class pda10a2_on_surface_adapter(photodetector_pda10a2):
    """
    Photodetector, model PDA10A2, on a surface adapter

    Args:
        adapter_parameters (dict): A dictionary of parameters to override the default surface adapter parameters
    """

    def __init__(
        self,
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
    ):
        self.adapter_parameters = dict(
            height=dim(10, "mm"),
            min_length=dim(20, "mm"),
            bolt_spacing=dim(40, "mm"),
            bolt_types=["8_32", "M4"],
            bolt_length=bolt_length,
            drill_depth=drill_depth,
            extra_thickness=dim(6, "mm"),
            slot_length=dim(0, "mm"),
            fillet_radius=dim(5, "mm"),
            drill_tolerance=dim(1, "mm"),
        )
        self.adapter_parameters |= adapter_parameters
        super().__init__(
            include_bolt=True,
            bolt_distance=self.adapter_parameters["height"],
        )

    def subcomponents(self):
        components = super().subcomponents()
        components.append(
            Subcomponent(
                component=Component(
                    label="Surface Adapter",
                    definition=surface_adapter(**self.adapter_parameters),
                ),
                position=self.mount_position,
                rotation=(0, 0, 0),
            )
        )
        return components
