from collections import namedtuple
from pathlib import Path

import FreeCAD as App
import Mesh
import numpy as np
import Part

stl_path = Path(__file__).parent / "stl"

subcomponent = namedtuple("subcomponent", ["component", "position", "rotation"])


def collect_children(parent: App.DocumentObject, output_list: list):
    """
    Recursively collect all children of a given FreeCAD document object.

    Args:
        parent (App.DocumentObject): The parent FreeCAD object.
        output_list (list): List to append the collected children to.
    """
    if hasattr(parent, "Children"):
        for child in parent.Children:
            output_list.append(child)
            collect_children(child, output_list)


def wavelength_to_rgb(wl: float) -> tuple:
    """
    Convert a wavelength in nm to an RGB color tuple.

    Args:
        wl (float): Wavelength in nanometers.
    """

    # clip input to visible range
    wl = max(380, min(780, wl))

    gamma = 0.8
    max_intensity = 1.0

    # basic values
    r = g = b = 0.0
    if 380 <= wl <= 439:
        r = -(wl - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= wl <= 489:
        r = 0.0
        g = (wl - 440) / (490 - 440)
        b = 1.0
    elif 490 <= wl <= 509:
        r = 0.0
        g = 1.0
        b = -(wl - 510) / (510 - 490)
    elif 510 <= wl <= 579:
        r = (wl - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= wl <= 644:
        r = 1.0
        g = -(wl - 645) / (645 - 580)
        b = 0.0
    elif 645 <= wl <= 780:
        r = 1.0
        g = 0.0
        b = 0.0

    # gamma correction factor
    if 380 <= wl <= 419:
        factor = 0.3 + 0.7 * (wl - 380) / (420 - 380)
    elif 420 <= wl <= 700:
        factor = 1.0
    elif 701 <= wl <= 780:
        factor = 0.3 + 0.7 * (780 - wl) / (780 - 700)
    else:
        factor = 0.0

    def scale(channel: float) -> float:
        if channel > 0:
            return float(max_intensity * ((channel * factor) ** gamma))
        return 0.0

    return (scale(r), scale(g), scale(b))


def box_shape(
    dimensions: tuple,
    position: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    center: tuple = (0, 0, 0),
    fillet: float = 0,
    fillet_direction: tuple = (0, 0, 1),
) -> Part.Shape:
    """
    Create a box part with optional filleting in a specified direction

    Args:
        dimensions (tuple): Dimensions of the box (dx, dy, dz)
        position (tuple): Position of the box origin (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        center (tuple): Position of the box origin with respect to its size. For example:
                        (0, 0, 0) origin at center of the box
                        (1, 0, 0) origin at +X face center
                        (1, 1, 0) origin at +X +Y edge center
                        (1, 1, 1) origin at +X +Y +Z corner
        fillet (float): Radius of fillet to apply to edges in fillet_dir
        fillet_dir (tuple): Direction vector of edges to fillet

    Returns:
        Part.Shape: The created box part
    """

    # create shape
    part = Part.makeBox(*dimensions)
    if fillet != 0:  # apply fillet to specified edges
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(*fillet_direction):
                part = part.makeFillet(fillet - 1e-3, [i])
    # move origin to specified center and position
    part.translate(
        App.Vector(
            position[0] - (1 + center[0]) * dimensions[0] / 2,
            position[1] - (1 + center[1]) * dimensions[1] / 2,
            position[2] - (1 + center[2]) * dimensions[2] / 2,
        )
    )
    # apply rotation
    part.rotate(
        App.Vector(*position),
        App.Vector(1, 0, 0),
        rotation[0],
    )
    part.rotate(
        App.Vector(*position),
        App.Vector(0, 1, 0),
        rotation[1],
    )
    part.rotate(
        App.Vector(*position),
        App.Vector(0, 0, 1),
        rotation[2],
    )
    return part


def cylinder_shape(
    diameter: float,
    height: float,
    position: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    direction: tuple = (0, 0, 1),
) -> Part.Shape:
    """
    Create a cylinder part

    Args:
        diameter (float): Diameter of the cylinder
        height (float): Height of the cylinder
        position (tuple): Position of the cylinder base center (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        direction (tuple): Direction vector for cylinder orientation

    Returns:
        Part.Shape: The created cylinder part
    """

    # create shape
    part = Part.makeCylinder(
        diameter / 2,
        height,
        App.Vector(*position),
        App.Vector(*direction),
    )
    # apply rotation
    part.rotate(
        App.Vector(*position),
        App.Vector(1, 0, 0),
        rotation[0],
    )
    part.rotate(
        App.Vector(*position),
        App.Vector(0, 1, 0),
        rotation[1],
    )
    part.rotate(
        App.Vector(*position),
        App.Vector(0, 0, 1),
        rotation[2],
    )
    return part


def bolt_shape(
    diameter: float,
    height: float,
    head_diameter: float,
    head_height: float,
    position: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    direction: tuple = (0, 0, -1),
    from_top: bool = True,
    countersink: bool = False,
) -> Part.Shape:
    """
    Create a simple bolt shape

    Args:
        diameter (float): Diameter of the bolt shaft
        height (float): Distance from origin to end of bolt shaft
        head_diameter (float): Diameter of the bolt head
        head_height (float): Height of the bolt head
        position (tuple): Position of the bolt head center (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        direction (tuple): Direction vector for bolt orientation
        from_top (bool): Whether the origin is the top or bottom of the head
        countersink (bool): Whether the head is a countersink (conical)

    Returns:
        Part.Shape: The created cylinder part
    """

    # create shaft
    part = Part.makeCylinder(
        diameter / 2,
        height,
        App.Vector(*position),
        App.Vector(*direction),
    )
    # create head
    if not from_top:
        direction = tuple(-i for i in direction)
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
    # remove internal edges
    part = part.removeSplitter()
    # apply rotation
    part.rotate(
        App.Vector(*position),
        App.Vector(1, 0, 0),
        rotation[0],
    )
    part.rotate(
        App.Vector(*position),
        App.Vector(0, 1, 0),
        rotation[1],
    )
    part.rotate(
        App.Vector(*position),
        App.Vector(0, 0, 1),
        rotation[2],
    )
    return part


def bolt_slot_shape(
    diameter: float,
    height: float,
    head_diameter: float,
    head_height: float,
    length: float,
    position: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    direction: tuple = (0, 0, -1),
) -> Part.Shape:
    """
    Create a bolt slot shape

    Args:
        diameter (float): Diameter of the bolt shaft
        height (float): Height of the slot
        head_diameter (float): Diameter of the bolt head
        head_height (float): Height of the bolt head
        length (float): Travel length for slot (full length - diameter)
        position (tuple): Position of the slot center (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        direction (tuple): Direction vector for slot orientation

    Returns:
        Part.Shape: The created bolt slot part
    """

    # create shape
    part = box_shape(
        dimensions=(length + diameter, diameter, height),
        position=position,
        center=(0, 0, 1),
    )
    part = part.fuse(
        box_shape(
            dimensions=(length + head_diameter, head_diameter, head_height),
            position=position,
            center=(0, 0, 1),
        )
    )
    # remove internal edges
    part = part.removeSplitter()
    # rotate to direction
    dir_rotation = App.Rotation(App.Vector(0, 0, 1), App.Vector(*direction))
    part.rotate(App.Vector(*position), dir_rotation.Axis, dir_rotation.Angle)
    # apply final rotation
    part.rotate(
        App.Vector(*position),
        App.Vector(1, 0, 0),
        rotation[0],
    )
    part.rotate(
        App.Vector(*position),
        App.Vector(0, 1, 0),
        rotation[1],
    )
    part.rotate(
        App.Vector(*position),
        App.Vector(0, 0, 1),
        rotation[2],
    )
    return part


def import_stl(
    stl_path: str | Path, translation: tuple, rotation: tuple, scale=1, internal=False
) -> Mesh.Mesh:
    # read mesh from file
    mesh = Mesh.read(str(stl_path))
    # scale using transformation matrix
    mat = App.Matrix()
    mat.scale(App.Vector(scale, scale, scale))
    mesh.transform(mat)
    # apply rotation and translation
    mesh.rotate(*np.deg2rad(rotation))
    mesh.translate(*translation)
    return mesh
