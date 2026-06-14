import numpy as np

from PyOpticL.beam_path import Lens, Reflection, Waveplate
from PyOpticL.icons import optic_icon
from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library.adapters import Surface_Adapter
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import bounding_box_shape, box_shape, cylinder_shape


class Circular_Reflector:
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
        refractive_index (float): Refractive index of the substrate
        part_number (str): The part number for the reflector
    """

    object_group = "optics"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)

    def __init__(
        self,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(6, "mm"),
        mount_definition: object = None,
        mount_offset: tuple = None,
        ref_ratio: float = None,
        ref_polarization: float = None,
        ref_wavelengths: list = None,
        refractive_index: float = 1.5,
        part_number: str = "",
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset
        self.ref_ratio = ref_ratio
        self.ref_polarization = ref_polarization
        self.ref_wavelengths = ref_wavelengths
        self.refractive_index = refractive_index
        self.part_numbers = [part_number]

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
                single_sided=not self.bidirectional,
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
                        label="mounts",
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

    def drill(self):
        part = bounding_box_shape(self.shape(), padding=dim(0.5, "mm"))
        part = part.fuse(
            cylinder_shape(
                diameter=self.diameter - dim(2, "mm"),
                height=self.diameter,
                position=(-self.thickness / 2, 0, 0),
            )
        )
        return part


class Rectangular_Reflector:
    """
    A rectangular reflector component

    Args:
        width (float): The width of the reflector
        height (float): The height of the reflector
        thickness (float): The thickness of the reflector
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to reflector origin
                              If None, defaults to (-thickness, 0, 0)
        ref_ratio (float): The ratio of reflected to transmitted light
        ref_polarization (float): The reflected polarization angle
        ref_wavelengths (list): A list of tuples representing the ranges of wavelengths to be reflected
                                 Use None for open-ended ranges
        refractive_index (float): Refractive index of the substrate
        part_number (str): The part number for the reflector
    """

    object_group = "optics"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)

    def __init__(
        self,
        width: dim = dim(0.5, "in"),
        height: dim = dim(0.5, "in"),
        thickness: dim = dim(6, "mm"),
        mount_definition: object = None,
        mount_offset: tuple = None,
        ref_ratio: float = None,
        ref_polarization: float = None,
        ref_wavelengths: list = None,
        refractive_index: float = 1.5,
        part_number: str = "",
    ):
        self.width = width
        self.height = height
        self.thickness = thickness
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset
        self.ref_ratio = ref_ratio
        self.ref_polarization = ref_polarization
        self.ref_wavelengths = ref_wavelengths
        self.refractive_index = refractive_index
        self.part_numbers = [part_number]

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
                width=self.width,
                height=self.height,
                ref_ratio=self.ref_ratio,
                ref_polarization=self.ref_polarization,
                ref_wavelengths=self.ref_wavelengths,
                refractive_index_ratio=1 / self.refractive_index,
                max_angle=self.max_angle,
                single_sided=not self.bidirectional,
            ),
        ]

        if self.bidirectional:
            interfaces.append(
                Reflection(
                    position=(-self.thickness, 0, 0),
                    rotation=(0, 0, 180),
                    width=self.width,
                    height=self.height,
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
                        label="mounts",
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
            dimensions=(self.thickness, self.width, self.height),
            center=(1, 0, 0),
        )
        return part

    def drill(self):
        part = bounding_box_shape(self.shape())
        return part


class Circular_Mirror(Circular_Reflector):
    """
    A circular mirror component

    Args:
        diameter (float): The diameter of the mirror
        thickness (float): The thickness of the mirror
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to mirror origin
                              If None, defaults to (-thickness, 0, 0)
        part_number (str): The part number for the mirror
    """

    def __init__(
        self,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(6, "mm"),
        mount_definition: object = None,
        mount_offset: tuple = None,
        part_number: str = "",
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
            mount_definition=mount_definition,
            mount_offset=mount_offset,
            part_number=part_number,
        )


class Rectangular_Mirror(Rectangular_Reflector):
    """
    A rectangular mirror component

    Args:
        width (float): The width of the mirror
        height (float): The height of the mirror
        thickness (float): The thickness of the mirror
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to mirror origin
                              If None, defaults to (-thickness, 0, 0)
        part_number (str): The part number for the mirror
    """

    def __init__(
        self,
        width: dim = dim(0.5, "in"),
        height: dim = dim(0.5, "in"),
        thickness: dim = dim(6, "mm"),
        mount_definition: object = None,
        mount_offset: tuple = None,
        part_number: str = "",
    ):
        super().__init__(
            width=width,
            height=height,
            thickness=thickness,
            mount_definition=mount_definition,
            mount_offset=mount_offset,
            part_number=part_number,
        )


class Circular_Sampler(Circular_Reflector):
    """
    A circular sampler component

    Args:
        diameter (float): The diameter of the sampler
        thickness (float): The thickness of the sampler
        ref_ratio (float): The ratio of reflected to transmitted light
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to sampler origin
                              If None, defaults to (-thickness, 0, 0)
        refractive_index (float): Refractive index used for Fresnel splitting
        part_number (str): The part number for the sampler
    """

    def __init__(
        self,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(3, "mm"),
        ref_ratio: float = 0.5,
        mount_definition: object = None,
        mount_offset: tuple = None,
        refractive_index: float = 1.5,
        part_number: str = "",
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
            mount_definition=mount_definition,
            mount_offset=mount_offset,
            ref_ratio=ref_ratio,
            refractive_index=refractive_index,
            part_number=part_number,
        )

        self.object_transparency = int(100 * ref_ratio)


class Circular_Dichroic_Mirror(Circular_Reflector):
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
        refractive_index (float): Refractive index used for transmission/reflection modeling
        part_number (str): The part number for the dichroic mirror
    """

    object_transparency = 25

    def __init__(
        self,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(6, "mm"),
        ref_wavelengths: list = [],
        mount_definition: object = None,
        mount_offset: tuple = None,
        refractive_index: float = 1.5,
        part_number: str = "",
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
            mount_definition=mount_definition,
            mount_offset=mount_offset,
            ref_wavelengths=ref_wavelengths,
            refractive_index=refractive_index,
            part_number=part_number,
        )


class Spherical_Lens:
    """
    A spherical lens component

    Args:
        diameter (float): The diameter of the lens
        thickness (float): The thickness of the lens
        focal_length (float): The focal length of the lens
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to lens origin
                              If None, defaults to (0, 0, 0)
        part_number (str): The part number for the lens
    """

    object_group = "optics"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)
    object_transparency = 75

    def __init__(
        self,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(2, "mm"),
        focal_length: dim = dim(100, "mm"),
        mount_definition: object = None,
        mount_offset: tuple = None,
        part_number: str = "",
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.focal_length = focal_length
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset
        self.part_numbers = [part_number]

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
                mount_offset = (-self.thickness / 2, 0, 0)
            return [
                Subcomponent(
                    component=Component(
                        label="mounts",
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

    def drill(self):
        part = bounding_box_shape(self.shape(), padding=dim(0.5, "mm"))
        part = part.fuse(
            cylinder_shape(
                diameter=self.diameter - dim(2, "mm"),
                height=self.diameter,
                position=(-self.thickness / 2, 0, 0),
            )
        )
        return part


class Circular_Waveplate:
    """
    A circular waveplate component

    Args:
        diameter (float): The diameter of the waveplate
        thickness (float): The thickness of the waveplate
        retardance (float): The phase delay in waves (0.25 quarter-wave, 0.5 half-wave)
        fast_axis_angle (float): The angle of the fast axis in degrees
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to the waveplate origin
        part_number (str): The part number for the waveplate
    """

    object_group = "optics"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)
    object_transparency = 75

    def __init__(
        self,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(1, "mm"),
        retardance: float = 0.5,
        fast_axis_angle: float = 0,
        mount_definition: object = None,
        mount_offset: tuple = None,
        part_number: str = "",
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.retardance = retardance
        self.fast_axis_angle = fast_axis_angle
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset
        self.part_numbers = [part_number]

    def interfaces(self):
        return [
            Waveplate(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.diameter,
                retardance=self.retardance,
                fast_axis_angle=self.fast_axis_angle,
                max_angle=180,
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
                        label="mounts",
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

    def drill(self):
        part = bounding_box_shape(self.shape(), padding=dim(0.5, "mm"))
        part = part.fuse(
            cylinder_shape(
                diameter=self.diameter - dim(2, "mm"),
                height=self.diameter,
                position=(-self.thickness / 2, 0, 0),
            )
        )
        return part


class Beamsplitter_Cube:
    """
    A generic beamsplitter cube component

    Args:
        side_length (float): The side length of the cube
        ref_polarization (float): Reflected polarization angle in degrees
        ref_ratio (float): Reflected power ratio
        rotate_cube (bool): Whether to rotate the internal splitting plane orientation
        mount_definition (object): The definition of the mount component
        mount_offset (tuple): The (x, y, z) offset of the mount relative to the cube origin
                              If None, defaults to (0, 0, -side_length/2)
        drill_tolerance (float): Tolerance to add around the cube for drilling operations
        corner_drill_diameter (float): Diameter of corner relief drill holes
        part_number (str): The part number for the cube
    """

    object_group = "optics"
    object_icon = optic_icon
    object_color = (0.5, 0.5, 0.8)
    object_transparency = 75

    def __init__(
        self,
        side_length: dim = dim(0.5, "in"),
        ref_polarization: float = None,
        ref_ratio: float = None,
        rotate_cube: bool = False,
        mount_definition: object = None,
        mount_offset: tuple = None,
        drill_tolerance: dim = dim(0.5, "mm"),
        corner_drill_diameter: dim = dim(3, "mm"),
        part_number: str = "",
    ):
        if ref_ratio is None and ref_polarization is None:
            ref_ratio = 0.5  # default to 50/50 beamsplitter if not specified

        self.side_length = side_length
        self.ref_polarization = ref_polarization
        self.ref_ratio = ref_ratio
        self.rotate_cube = rotate_cube
        self.mount_definition = mount_definition
        self.mount_offset = mount_offset
        self.drill_tolerance = drill_tolerance
        self.corner_drill_diameter = corner_drill_diameter
        self.part_numbers = [part_number]

    def interfaces(self):
        return [
            Reflection(
                position=(0, 0, 0),
                rotation=(0, 0, 45 if self.rotate_cube else -45),
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
                        label="mounts",
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
                rotation=(0, 0, 45 if self.rotate_cube else -45),
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


class Beamsplitter_Cube_on_Surface_Adapter(Beamsplitter_Cube):
    """
    Beamsplitter cube on a surface adapter with logical defaults for the adapter sizing

    Args:
        side_length (float): The side length of the cube
        optical_height (float): Target optical height of the cube centerline
        ref_polarization (float): The reflected polarization angle
        ref_ratio (float): The ratio of reflected to transmitted light
        rotate_cube (bool): Whether to rotate the internal splitting plane orientation
        rotate_adapter (bool): Whether to rotate the adapter footprint by 90 degrees
        inset_depth (float): Depth the cube is inset into the adapter
        drill_depth (float): Drill depth for adapter mounting holes
        bolt_length (float): Length of adapter mounting bolts
        adapter_parameters (dict): A dictionary of parameters to override the default surface adapter parameters
        part_number (str): The part number for the cube
    """

    def __init__(
        self,
        side_length: dim = dim(10, "mm"),
        optical_height: dim = dim(0.5, "in"),
        ref_polarization: float = None,
        ref_ratio: float = None,
        rotate_cube: bool = False,
        rotate_adapter: bool = False,
        inset_depth: dim = dim(1, "mm"),
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
        part_number: str = "",
    ):
        super().__init__(
            side_length=side_length,
            ref_polarization=ref_polarization,
            ref_ratio=ref_ratio,
            rotate_cube=rotate_cube,
            part_number=part_number,
        )
        self.adapter_parameters = dict(
            height=optical_height - side_length / 2 + inset_depth,
            min_length=side_length + self.corner_drill_diameter + dim(2, "mm"),
            bolt_spacing=dim(25, "mm"),
            bolt_types=["8_32", "M4"],
            bolt_length=bolt_length,
            drill_depth=drill_depth,
        )
        self.adapter_parameters |= adapter_parameters
        self.optical_height = optical_height
        self.rotate_adapter = rotate_adapter
        self.inset_depth = inset_depth

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Surface Adapter",
                    definition=Surface_Adapter(**self.adapter_parameters),
                ),
                position=(0, 0, self.inset_depth - self.side_length / 2),
                rotation=(0, 0, 90 if self.rotate_adapter else 0),
            )
        ]
