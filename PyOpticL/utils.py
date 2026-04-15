from collections import namedtuple
from pathlib import Path

import FreeCAD as App
import Mesh
import MeshPart
import numpy as np
import Part
import json

from PyOpticL.settings import measurement_system, minimum_thread_engagement
from PyOpticL.types import Dimension as dim

models_dir = Path(__file__).parent / "models"

Subcomponent = namedtuple("Subcomponent", ["component", "position", "rotation"])


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
                        (1, -1, 0) origin at +X -Y edge center
                        (1, -1, 1) origin at +X -Y +Z corner
        fillet (float): Radius of fillet to apply to edges in fillet_dir
        fillet_dir (tuple): Direction vector of edges to fillet

    Returns:
        Part.Shape: The created box part
    """

    # create shape
    part = Part.makeBox(*dimensions, App.Vector(
            position[0] - (1 + center[0]) * dimensions[0] / 2,
            position[1] - (1 + center[1]) * dimensions[1] / 2,
            position[2] - (1 + center[2]) * dimensions[2] / 2,
        ))
    if fillet != 0:  # apply fillet to specified edges
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(*fillet_direction):
                part = part.makeFillet(fillet - 1e-3, [i])
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
) -> Part.Shape:
    """
    Create a cylinder part

    Args:
        diameter (float): Diameter of the cylinder
        height (float): Height of the cylinder
        position (tuple): Position of the cylinder base center (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees

    Returns:
        Part.Shape: The created cylinder part
    """

    # create shape
    part = Part.makeCylinder(
        diameter / 2,
        height,
        App.Vector(*position),
        App.Vector(0, 0, 1),
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
    part = part.fuse(part)
    return part


def bolt_shape(
    clear_diameter: float,
    tap_diameter: float,
    length: float,
    clear_depth: float,
    head_diameter: float,
    head_height: float,
    position: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    from_top: bool = True,
    countersink: bool = False,
) -> Part.Shape:
    """
    Create a simple bolt shape

    Args:
        clear_diameter (float): Clear diameter of the bolt shaft
        tap_diameter (float): Tap diameter of the bolt shaft
        length (float): Length of the bolt shaft
        clear_depth (float): The depth at which the hole threading should start
        head_diameter (float): Diameter of the bolt head
        head_height (float): Height of the bolt head
        position (tuple): Position of the bolt head center (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        from_top (bool): Whether the origin is the top or bottom of the head
        countersink (bool): Whether the head is a countersink (conical)

    Returns:
        Part.Shape: The created cylinder part
    """

    # create head
    if from_top:
        head_position = position
    else:
        head_position = (
            position[0],
            position[1],
            position[2] + head_height,
        )
    if countersink:
        part = Part.makeCone(
            head_diameter / 2,
            tap_diameter / 2,
            head_height,
            App.Vector(*head_position),
            App.Vector(0, 0, -1),
        )
    else:
        part = Part.makeCylinder(
            head_diameter / 2,
            head_height,
            App.Vector(*head_position),
            App.Vector(0, 0, -1),
        )
    # create clearance hole
    part = part.fuse(
        Part.makeCylinder(
            clear_diameter / 2,
            clear_depth,
            App.Vector(*position),
            App.Vector(0, 0, -1),
        )
    )
    # create tapped hole
    part = part.fuse(
        Part.makeCylinder(
            tap_diameter / 2,
            length,
            App.Vector(*position),
            App.Vector(0, 0, -1),
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
    clear_diameter: float,
    tap_diameter: float,
    length: float,
    clear_depth: float,
    head_diameter: float,
    head_height: float,
    slot_length: float,
    position: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    from_top: bool = True,
) -> Part.Shape:
    """
    Create a bolt slot shape

    Args:
        clear_diameter (float): Clear diameter of the bolt shaft
        tap_diameter (float): Tap diameter of the bolt shaft
        length (float): Length of the slot
        clear_depth (float): The depth at which the hole threading should start
        head_diameter (float): Diameter of the bolt head
        head_height (float): Height of the bolt head
        slot_length (float): Travel length for slot (full length - diameter)
        position (tuple): Position of the slot center (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        from_top (bool): Whether the origin is the top or bottom of the bolt head

    Returns:
        Part.Shape: The created bolt slot part
    """

    # create head
    part = box_shape(
        dimensions=(slot_length + head_diameter, head_diameter, head_height),
        position=position,
        center=(0, 0, 1) if from_top else (0, 0, -1),
        fillet=head_diameter / 2,
    )
    # create clearance hole
    part = part.fuse(
        box_shape(
            dimensions=(slot_length + clear_diameter, clear_diameter, clear_depth),
            position=position,
            center=(0, 0, 1),
            fillet=clear_diameter / 2,
        )
    )
    # create tapped hole
    part = part.fuse(
        Part.makeCylinder(
            tap_diameter / 2,
            length,
            App.Vector(*position),
            App.Vector(0, 0, -1),
        )
    )

    # remove internal edges
    part = part.removeSplitter()
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


def default_bolt_length(through_length: float, max_thread_engagement: float = None) -> float:
    """
    Determine the minimum standard bolt length for a given through length
    Note: The minimum bolt engagement global parameter is used to calculate the minimum length

    Args:
        through_length (float): The minimum required through length
        max_thread_engagement (float): The maximum thread engagement length

    Returns:
        float: The calculated bolt length
    """

    default_lengths = dict(
        imperial=dict(
            lower_values=[
                dim(1 / 4, "in"),
                dim(3 / 8, "in"),
                dim(1 / 2, "in"),
                dim(5 / 8, "in"),
                dim(3 / 4, "in"),
                dim(7 / 8, "in"),
                dim(1, "in"),
            ],
            upper_multiple=dim(1 / 2, "in"),
        ),
        metric=dict(
            lower_values=[
                dim(6, "mm"),
                dim(8, "mm"),
                dim(10, "mm"),
                dim(12, "mm"),
                dim(16, "mm"),
                dim(20, "mm"),
            ],
            upper_multiple=dim(5, "mm"),
        ),
    )

    lengths = default_lengths[measurement_system]
    if max_thread_engagement is None:
        minimum_length = through_length + minimum_thread_engagement
        for val in lengths["lower_values"]:
            if val >= minimum_length:
                return val
        multiple = lengths["upper_multiple"]
        return np.ceil(minimum_length / multiple) * multiple
    else:
        maximum_length = through_length + max_thread_engagement
        for val in lengths["lower_values"][::-1]:
            if val <= maximum_length:
                return val
        multiple = lengths["upper_multiple"]
        return np.floor(maximum_length / multiple) * multiple


def import_model(
    name: str,
    directory: Path | str = models_dir,
) -> Mesh.Mesh:
    """
    Import a mesh model from a PyOpticL specific models directory

    Args:
        name (str): Name of the model to import
        directory (Path | str): Path to the models directory (defaults to internal models directory)

    Returns:
        Mesh.Mesh: The imported mesh object
    """

    directory = Path(directory)
    model_path = directory / name

    try:
        # validate files
        if not directory.is_dir():
            raise FileNotFoundError(f"Models directory not found")
        if not model_path.is_dir():
            raise FileNotFoundError(f"Model not found in directory")
        if not (model_path / (f"{name}.step")).is_file():
            raise FileNotFoundError(f"Model STEP file not found")
        if not (model_path / (f"{name}.json")).is_file():
            raise FileNotFoundError(f"Model info file not found")

        if not (model_path / (f"{name}.stl")).is_file():
            shape = Part.read(str(model_path / (f"{name}.step")))
            info = json.load(open(model_path / (f"{name}.json")))

            rotation = App.Rotation("XYZ", *info["rotation"])
            rotation = App.Placement(App.Vector(0, 0, 0), rotation, App.Vector(0, 0, 0))
            translation = App.Placement(
                App.Vector(*info["translation"]),
                App.Rotation("XYZ", 0, 0, 0),
                App.Vector(0, 0, 0),
            )
            shape.Placement = rotation * translation

            mesh = MeshPart.meshFromShape(
                Shape=shape, LinearDeflection=0.1, AngularDeflection=0.5
            )
            mesh.write(str(model_path / (f"{name}.stl")))

        # read mesh from file
        mesh = Mesh.read(str(model_path / (f"{name}.stl")))
    
    except FileNotFoundError as e:
        print(f"Error importing model '{name}': {e}")
        mesh = Mesh.Mesh()  # return empty mesh on error

    return mesh
