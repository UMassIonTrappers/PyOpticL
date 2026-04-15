import numpy as np

from PyOpticL.beam_path import Lens, Reflection, Waveplate
from PyOpticL.icons import optic_icon
from PyOpticL.layout import Component
from PyOpticL.library.adapters import surface_adapter
from PyOpticL.types import Dimension as dim
from PyOpticL.utils import Subcomponent, box_shape, cylinder_shape


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
        thickness: dim = dim(6, "mm"),
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
        thickness: dim = dim(1, "mm"),
        retardance: float = 0.5,
        fast_axis_angle: float = 0,
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
    A generic beamsplitter cube component, optionally mounted on a surface adapter

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
        ref_polarization: float = 0,
        ref_ratio: float = None,
        rotate_cube: bool = False,
        surface_adapter: bool = False,
        optical_height: dim = 0,
        rotate_adapter: bool = False,
        inset_depth: dim = dim(1, "mm"),
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
        drill_tolerance: dim = dim(0.5, "mm"),
        corner_drill_diameter: dim = dim(3, "mm"),
    ):
        if ref_ratio is None and ref_polarization is None:
            raise ValueError("Either ref_ratio or ref_polarization must be specified")

        self.adapter_parameters = dict(
            height=optical_height - side_length / 2 + inset_depth,
            min_length=side_length + corner_drill_diameter + dim(2, "mm"),
            bolt_spacing=side_length + dim(10, "mm"),
            bolt_types=["8_32", "M4"],
            bolt_length=bolt_length,
            drill_depth=drill_depth,
            extra_thickness=dim(6, "mm"),
            slot_length=dim(0, "mm"),
            fillet_radius=dim(5, "mm"),
            drill_tolerance=dim(1, "mm"),
        )
        self.adapter_parameters |= adapter_parameters
        self.side_length = side_length
        self.ref_polarization = ref_polarization
        self.ref_ratio = ref_ratio
        self.surface_adapter = surface_adapter
        self.optical_height = optical_height
        self.rotate_cube = rotate_cube
        self.rotate_adapter = rotate_adapter
        self.inset_depth = inset_depth
        self.drill_tolerance = drill_tolerance
        self.corner_drill_diameter = corner_drill_diameter

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
        components = []
        if self.surface_adapter:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Surface Adapter",
                        definition=surface_adapter(**self.adapter_parameters),
                    ),
                    position=(0, 0, self.inset_depth - self.side_length / 2),
                    rotation=(0, 0, 90 if self.rotate_adapter else 0),
                )
            )
        return components

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
