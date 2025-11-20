import FreeCAD as App
import numpy as np
import Part

from PyOpticL.beam_path import Lens, Reflection
from PyOpticL.icons import optic_icon, thorlabs_icon
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.utils import (
    bolt_shape,
    bolt_slot_shape,
    box_shape,
    cylinder_shape,
    import_model,
    subcomponent,
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
    """

    object_group = "example"
    object_icon = ""
    object_color = (0.5, 0.5, 0.5)

    def __init__(
        self,
        side_length: dim = dim(25, "mm"),
        height: dim = dim(15, "mm"),
        drill_depth: dim = dim(5, "mm"),
    ):
        """Initialize adjustable parameters"""
        self.side_length = side_length
        self.height = height
        self.drill_depth = drill_depth

    def subcomponents(self) -> list[subcomponent]:
        """Define any sub-components"""
        return [
            subcomponent(
                component=Component(
                    "Mounting Bolt",
                    bolt("8_32", length=self.height + self.drill_depth),
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
        type (string): Bolt type, supports "4_40", "8_32", "14_20"
        length (float): Length of the bolt including the head
        washer_diameter (float): Diameter of washer to include, None for no washer
        countersink (bool): Whether the bolt head is a countersink
        head_tol (float): Additional diameter to add to bolt head for clearance
    """

    bolt_dimensions = {
        "4_40": dict(
            clear_diameter=dim(0.12, "in"),
            tap_diameter=dim(0.089, "in"),
            head_diameter=dim(5.5, "mm"),
            head_height=dim(2.5, "mm"),
        ),
        "8_32": dict(
            clear_diameter=dim(0.172, "in"),
            tap_diameter=dim(0.136, "in"),
            head_diameter=dim(7, "mm"),
            head_height=dim(4.4, "mm"),
        ),
        "1/4_20": dict(
            clear_diameter=dim(0.26, "in"),
            tap_diameter=dim(0.201, "in"),
            head_diameter=dim(9.8, "mm"),
            head_height=dim(8, "mm"),
        ),
    }

    object_group = "hardware"
    object_icon = ""
    object_color = (0.8, 0.8, 0.8)

    def __init__(
        self,
        type: str,
        length: dim,
        washer_diameter: dim = None,
        countersink: bool = False,
        head_tol: dim = dim(1, "mm"),
        extra_depth: dim = dim(5, "mm"),
        from_top: bool = True,
    ):

        self.type = type
        self.length = length
        self.washer_diameter = washer_diameter
        self.countersink = countersink
        self.head_tol = head_tol
        self.extra_depth = extra_depth
        self.from_top = from_top

        if washer_diameter != 0 and countersink:
            raise ValueError("Bolt does not support both washer and countersink")

    def shape(self):
        dims = self.bolt_dimensions[self.type]
        part = bolt_shape(
            diameter=dims["tap_diameter"],
            height=self.length,
            head_diameter=dims["head_diameter"],
            head_height=dims["head_height"],
            position=(0, 0, 0),
            direction=(0, 0, -1),
            countersink=self.countersink,
            from_top=self.from_top,
        )
        return part

    def drill(self):
        dims = self.bolt_dimensions[self.type]
        if self.washer_diameter != None:
            head_diameter = self.washer_diameter
        else:
            head_diameter = dims["head_diameter"]
        head_diameter += self.head_tol
        part = bolt_shape(
            diameter=dims["tap_diameter"],
            height=self.length + self.extra_depth,
            head_diameter=head_diameter,
            head_height=dims["head_height"],
            position=(0, 0, 0),
            direction=(0, 0, -1),
            countersink=self.countersink,
            from_top=self.from_top,
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
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset
        self.ref_ratio = ref_ratio
        self.ref_polarization = ref_polarization
        self.ref_wavelengths = ref_wavelengths

    def interfaces(self):
        return [
            Reflection(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.diameter,
                ref_ratio=self.ref_ratio,
                ref_polarization=self.ref_polarization,
                ref_wavelengths=self.ref_wavelengths,
            )
        ]

    def subcomponents(self):
        if self.mount_definition != None:
            mount_offset = self.mount_offset
            if mount_offset is None:
                mount_offset = (-self.thickness, 0, 0)
            return [
                subcomponent(
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
            direction=(1, 0, 0),
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
                subcomponent(
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
            direction=(1, 0, 0),
        )
        return part


class polarizing_beam_splitter_cube:
    """
    A polarizing beam splitter cube component

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
        size: dim,
        ref_polarization: float = 0.0,
        mount_definition: object = None,
        mount_offset: tuple = None,
    ):
        self.size = size
        self.ref_polarization = ref_polarization
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset

    def interfaces(self):
        return [
            Reflection(
                position=(0, 0, 0),
                rotation=(0, 0, 45),
                width=self.size * np.sqrt(2),
                height=self.size * np.sqrt(2),
                ref_polarization=self.ref_polarization,
            )
        ]

    def subcomponents(self):
        if self.mount_definition != None:
            mount_offset = self.mount_offset
            if mount_offset is None:
                mount_offset = (0, 0, -self.size / 2)
            return [
                subcomponent(
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
            dimensions=(self.size, self.size, self.size),
            position=(0, 0, 0),
            center=(0, 0, 0),
        )
        diag = self.size * np.sqrt(2)
        part = part.cut(
            box_shape(
                dimensions=(0.1, diag, diag),
                position=(0, 0, 0),
                rotation=(0, 0, 45),
                center=(0, 0, 0),
            )
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
    """

    object_group = "mount"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("polaris-k05s1")

    def __init__(self, drill_depth: dim):
        self.drill_depth = drill_depth

    def subcomponents(self):
        return [
            subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=bolt(
                        "8_32",
                        length=dim(5.588, "mm") + self.drill_depth,
                        from_top=False,
                        extra_depth=0,
                    ),
                ),
                position=(-8.017, 0, -7.112),
                rotation=(0, 0, 0),
            )
        ]
