import FreeCAD as App
import numpy as np
import Part

from PyOpticL.beam_path import Reflection
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim

thorlabs_icon = """
    /* XPM */
    static char *_e94ebdf19f64588ceeb5b5397743c6amoxjrynTrPg9Fk5U[] = {
    /* columns rows colors chars-per-pixel */
    "16 16 2 1 ",
    "  c None",
    "& c red",
    /* pixels */
    "                ",
    "  &&&&&&&&&&&&  ",
    "  &&&&&&&&&&&&  ",
    "  &&&&&&&&&&&&  ",
    "  &&&&&&&&&&&&  ",
    "      &&&&      ",
    "      &&&&      ",
    "      &&&&      ",
    "      &&&&      ",
    "      &&&&      ",
    "      &&&&      ",
    "      &&&&      ",
    "      &&&&      ",
    "      &&&&      ",
    "      &&&&      ",
    "                "
    };
    """


def custom_box(
    dimensions: tuple,
    position: tuple,
    direction: tuple = (0, 0, 1),
    fillet: float = 0,
    fillet_direction: tuple = None,
) -> Part.Solid:
    """
    Create a box part with optional filleting in a specified direction

    Args:
    dimensions (tuple): Dimensions of the box (dx, dy, dz)
    position (tuple): Position of the box center (x, y, z)
    direction (tuple): +Z direction vector for box orientation
    fillet (float): Radius of fillet to apply to edges in fillet_dir
    fillet_dir (tuple): Direction vector for filleting edges; defaults to dir if None

    Returns:
    Part.Shape: The created box part
    """

    if fillet_direction == None:
        fillet_direction = np.abs(direction)
    part = Part.makeBox(*dimensions)
    if fillet != 0:
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(*fillet_direction):
                part = part.makeFillet(fillet - 1e-3, [i])
    part.translate(
        App.Vector(
            position[0] - (1 - direction[0]) * dimensions[0] / 2,
            position[1] - (1 - direction[1]) * dimensions[1] / 2,
            position[2] - (1 - direction[2]) * dimensions[2] / 2,
        )
    )
    part = part.fuse(part)
    return part


def custom_cylinder(
    diameter: float,
    height: float,
    position: tuple,
    direction: tuple = (0, 0, -1),
    head_diameter: float = 0,
    head_height: float = 0,
    countersink: bool = False,
) -> Part.Solid:
    """
    Create a cylinder part with optional bolt head

    Args:
    dia (float): Diameter of the cylinder
    dz (float): Height of the cylinder
    pos (tuple): Position of the cylinder base center (x, y, z)
    head_dia (float): Diameter of the bolt head
    head_dz (float): Height of the bolt head
    dir (tuple): +Z direction vector for cylinder orientation
    countersink (bool): Whether the head is a countersink (conical)

    Returns:
    Part.Shape: The created cylinder part
    """

    part = Part.makeCylinder(
        diameter / 2,
        height,
        App.Vector(*position),
        App.Vector(*direction),
    )
    if head_diameter != 0 and head_height != 0:
        if countersink:
            part = part.fuse(
                Part.makeCone(
                    head_diameter / 2,
                    diameter / 2,
                    head_height,
                    App.Vector(*position),
                    App.Vector(*direction),
                )
            )
        else:
            part = part.fuse(
                Part.makeCylinder(
                    head_diameter / 2,
                    head_height,
                    App.Vector(*position),
                    App.Vector(*direction),
                )
            )
    return part.removeSplitter()


class bolt:
    """
    Standard bolt

    Args:
        label (str): The label for the component
        type (string): Bolt type, supports "4_40", "8_32", "14_20"
        length (float): Length of the bolt including the head
        washer_diameter (float): Diameter of washer to include, 0 for none
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
        "14_20": dict(
            clear_diameter=dim(0.26, "in"),
            tap_diameter=dim(0.201, "in"),
            head_diameter=dim(9.8, "mm"),
            head_height=dim(8, "mm"),
        ),
    }

    object_type = "Part::FeaturePython"
    object_group = "hardware"
    object_icon = ""
    object_color = (0.8, 0.8, 0.8)

    def __init__(
        self,
        type: str,
        length: dim,
        washer_diameter: dim = dim(0, "mm"),
        countersink: bool = False,
        head_tol: dim = dim(1, "mm"),
    ):

        self.type = type
        self.length = length
        self.washer_diameter = washer_diameter
        self.countersink = countersink
        self.head_tol = head_tol

        if washer_diameter != 0 and countersink:
            raise ValueError("Bolt does not support both washer and countersink")

    def get_shape(self):
        dims = self.bolt_dimensions[self.type]
        part = custom_cylinder(
            diameter=dims["tap_diameter"],
            height=self.length,
            position=(0, 0, 0),
            direction=(0, 0, -1),
            head_diameter=dims["head_diameter"],
            head_height=dims["head_height"],
            countersink=self.countersink,
        )
        return part

    def get_drill(self):
        dims = self.bolt_dimensions[self.type]
        if self.washer_diameter != 0:
            head_diameter = self.washer_diameter
        else:
            head_diameter = dims["head_diameter"]
        head_diameter += self.head_tol
        part = custom_cylinder(
            diameter=dims["tap_diameter"],
            height=self.length,
            position=(0, 0, 0),
            direction=(0, 0, -1),
            head_diameter=head_diameter,
            head_height=dims["head_height"],
            countersink=self.countersink,
        )
        return part


class example_component:
    """
    An example component class for reference on importing new components
    creates a simple cube which mounts using a single bolt

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        side_length (float) : The side length of the cube
        height (float) : The height of the cube
        drill_depth (float) : The depth of the mounting hole
    """

    object_type = "Part::FeaturePython"
    object_icon = ""

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

    def get_components(self):
        """Define any sub-components"""
        components = [
            Component(
                "Mounting Bolt",
                bolt("8_32", length=self.height + self.drill_depth),
                position=(0, 0, 0),
                rotation=(0, 0, 0),
            )
        ]
        return components

    def get_shape(self):
        """Define the main shape of the component"""
        part = custom_box(
            dimensions=(self.side_length, self.side_length, self.height),
            position=(0, 0, 0),
            direction=(0, 0, -1),
            fillet=1,
        )
        return part


class circular_reflector:
    """
    A circular reflector component

    Args:
        diameter (float) : The diameter of the reflector
        thickness (float) : The thickness of the reflector
        ref_ratio (float) : The reflectivity of the interface
        ref_polarization (float) : The reflected polarization angle
        ref_wavelengths (list) : The reflection wavelength ranges
    """

    object_type = "Part::FeaturePython"
    object_group = "optic"
    object_icon = ""
    object_color = (0.5, 0.5, 0.8)

    def __init__(
        self,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(5, "mm"),
        ref_ratio: float = None,
        ref_polarization: float = None,
        ref_wavelengths: list = None,
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.ref_ratio = ref_ratio
        self.ref_polarization = ref_polarization
        self.ref_wavelengths = ref_wavelengths

    def get_interfaces(self):
        interfaces = [
            Reflection(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.diameter,
                ref_ratio=self.ref_ratio,
                ref_polarization=self.ref_polarization,
                ref_wavelengths=self.ref_wavelengths,
            )
        ]
        return interfaces

    def get_shape(self):
        part = custom_cylinder(
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
        diameter (float) : The diameter of the mirror
        thickness (float) : The thickness of the mirror
    """

    object_type = "Part::FeaturePython"
    object_group = "optic"
    object_icon = ""
    object_color = (0.5, 0.5, 0.8)

    def __init__(
        self,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(5, "mm"),
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
        )


class circular_sampler(circular_reflector):
    """
    A circular sampler component

    Args:
        diameter (float) : The diameter of the sampler
        thickness (float) : The thickness of the sampler
        ref_ratio (float) : The reflection ratio of the sampler
    """

    object_type = "Part::FeaturePython"
    object_group = "optic"
    object_icon = ""
    object_color = (0.5, 0.5, 0.8)

    def __init__(
        self,
        ref_ratio: float,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(5, "mm"),
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
            ref_ratio=ref_ratio,
        )

        self.object_transparency = int(100 * ref_ratio)


class circular_dichroic_mirror(circular_reflector):
    """
    A circular dichroic mirror component

    Args:
        diameter (float) : The diameter of the dichroic mirror
        thickness (float) : The thickness of the dichroic mirror
        ref_polarization (float) : The reflection polarization ratio of the dichroic mirror
    """

    object_type = "Part::FeaturePython"
    object_group = "optic"
    object_icon = ""
    object_color = (0.5, 0.5, 0.8)
    object_transparency = 25

    def __init__(
        self,
        ref_wavelengths: list,
        diameter: dim = dim(0.5, "in"),
        thickness: dim = dim(5, "mm"),
    ):
        super().__init__(
            diameter=diameter,
            thickness=thickness,
            ref_wavelengths=ref_wavelengths,
        )


class polarizing_beam_splitter_cube:
    """
    A polarizing beam splitter cube component

    Args:
        size (float) : The side length of the cube
        thickness (float) : The thickness of the beam splitter interface
    """

    object_type = "Part::FeaturePython"
    object_group = "optic"
    object_icon = ""
    object_color = (0.5, 0.5, 0.8)

    def __init__(
        self,
        size: dim = dim(12.7, "mm"),
        ref_polarization: float = 0.0,
    ):
        self.size = size
        self.ref_polarization = ref_polarization

    def get_interfaces(self):
        interfaces = [
            Reflection(
                position=(0, 0, 0),
                rotation=(0, 45, 0),
                dx=self.size * np.sqrt(2),
                dy=self.size * np.sqrt(2),
                ref_polarization=self.ref_polarization,
            )
        ]
        return interfaces

    def get_shape(self):
        part = custom_box(
            dimensions=(self.size, self.size, self.size),
            position=(0, 0, 0),
            direction=(0, 0, -1),
        )

        return part
