import json
import os
import sys
from pathlib import Path

import FreeCAD as App
import Mesh
import MeshPart
import numpy as np
import Part

from PyOpticL.settings import get_measurement_system, get_minimum_thread_engagement

models_dir = Path(__file__).parent.absolute() / "models"

# imported models, kept across module reloads (reload re-executes in the same namespace)
_model_cache = globals().get("_model_cache", {})


def _caller_filename(depth: int = 2) -> str:
    """
    Get the filename of a calling frame (much cheaper than inspect.stack())

    Args:
        depth (int): Number of frames above this function's caller (2 = caller's caller)

    Returns:
        str: Filename of the calling frame
    """

    return sys._getframe(depth).f_code.co_filename


turn_angle = {
    "up-right": -45,
    "right-up": 135,
    "up-left": -135,
    "left-up": 45,
    "down-right": 45,
    "right-down": -135,
    "down-left": 135,
    "left-down": -45,
}
cardinal_angle = {
    "right": 0,
    "left": 180,
    "up": 90,
    "down": -90,
    "ne": 45,
    "se": -45,
    "sw": -135,
    "nw": 135,
}


class Dimension(float):
    """
    Class to handle dimensions with units
    value is stored internally as mm

    Args:
        value (float) : numerical value of the dimension
        unit (str) : unit of the dimension, options are 'um', 'mm', 'cm', 'm', 'in', 'ft'
    """

    conversion_factors = {
        "um": 0.001,
        "mm": 1,
        "cm": 10,
        "m": 1000,
        "in": 25.4,
        "ft": 304.8,
        "grid": 25.4 if get_measurement_system() == "imperial" else 25,
    }

    def __new__(self, value: float, unit: str = "mm"):
        if unit not in self.conversion_factors:
            raise ValueError(f"Unsupported unit: {unit}")
        instance = super().__new__(self, value * self.conversion_factors[unit])
        instance.unit = unit
        return instance

    def to_unit(self, unit: str) -> float:
        if unit in self.conversion_factors:
            return self.value / self.conversion_factors[unit]
        else:
            raise ValueError(f"Unsupported unit: {unit}")


dim = Dimension  # alias for convenience


# modules loaded before the current macro run, kept across module reloads
_import_run = globals().get("_import_run", {"root": None, "stale": {}})


def _is_initializing(module) -> bool:
    """Whether a module is part way through being imported"""

    return getattr(getattr(module, "__spec__", None), "_initializing", False)


def fix_relative_imports(directory: str | list = ""):
    """
    Add directories to the import path and make sure modules from them are
    imported afresh once per macro run, so that changes to them are applied

    The first call in a macro run (identified by the outermost frame on the stack)
    marks every module loaded so far as stale. Stale modules inside the target
    directories are unloaded, so the following imports load them again exactly once.
    Modules imported during the current run are never unloaded, which avoids
    repeatedly reloading modules that themselves call this function.

    Args:
        directory (str | list): Directory or list of directories, relative to the
                                calling file (defaults to the calling file's directory)
    """

    if isinstance(directory, str):
        directories = [directory]
    else:
        directories = directory

    caller_filename = _caller_filename()

    # find the outermost frame and the namespaces of all code currently running
    active_namespaces = set()
    frame = sys._getframe(1)
    while frame is not None:
        active_namespaces.add(id(frame.f_globals))
        root_frame = frame
        frame = frame.f_back

    # a new macro run starts a new outermost frame
    if _import_run["root"] is not root_frame:
        _import_run["root"] = root_frame
        _import_run["stale"] = {
            name: module
            for name, module in sys.modules.items()
            if module is not None
            and id(module.__dict__) not in active_namespaces
            and not _is_initializing(module)
        }
    stale = _import_run["stale"]

    for directory in directories:
        directory = Path(directory)

        if not directory.is_absolute():
            base_path = Path(caller_filename).parent
            directory = base_path / directory

        directory = directory.resolve()

        if str(directory) not in sys.path:
            sys.path.append(str(directory))

        # Unload stale modules whose source files are inside the target directory.
        # (string comparison, as Path.resolve() per module is very slow on Windows)
        directory_prefix = os.path.normcase(str(directory)) + os.sep
        for name, module in list(stale.items()):
            module_file = getattr(module, "__file__", None)
            if not module_file:
                continue

            try:
                module_path = os.path.normcase(os.path.abspath(module_file))
            except (OSError, ValueError):
                continue

            if not module_path.startswith(directory_prefix):
                continue

            del stale[name]
            if sys.modules.get(name) is module:
                del sys.modules[name]
                # also detach from the parent package, otherwise
                # "from package import module" returns the stale module
                parent_name, _, child_name = name.rpartition(".")
                parent = sys.modules.get(parent_name)
                if parent is not None and getattr(parent, child_name, None) is module:
                    delattr(parent, child_name)


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


def translate_shape(shape: Part.Shape, translation: tuple):
    """
    Translate a FreeCAD shape by a given vector

    Args:
        shape (Part.Shape): The input shape to translate
        translation (tuple): The translation vector (x, y, z)

    Returns:
        Part.Shape: The translated shape
    """

    shape.translate(App.Vector(*translation))
    return bake_placement(shape)


def bake_placement(shape: Part.Shape) -> Part.Shape:
    """
    Apply a shape's placement to its geometry so that its placement is the identity
    (cheaper than the equivalent self-fuse)

    Args:
        shape (Part.Shape): The input shape

    Returns:
        Part.Shape: The shape with its placement applied to its geometry
    """

    matrix = shape.Placement.toMatrix()
    shape = shape.copy()
    shape.Placement = App.Placement()
    shape.transformShape(matrix, True)
    return shape


def rotate_shape(shape: Part.Shape, rotation: tuple):
    """
    Rotate a FreeCAD shape by given Euler angles

    Args:
        shape (Part.Shape): The input shape to rotate
        rotation (tuple): The rotation angles (angle_x, angle_y, angle_z) in degrees

    Returns:
        Part.Shape: The rotated shape
    """

    shape.rotate(
        App.Vector(0, 0, 0),
        App.Vector(1, 0, 0),
        rotation[0],
    )
    shape.rotate(
        App.Vector(0, 0, 0),
        App.Vector(0, 1, 0),
        rotation[1],
    )
    shape.rotate(
        App.Vector(0, 0, 0),
        App.Vector(0, 0, 1),
        rotation[2],
    )
    return bake_placement(shape)


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
    part = Part.makeBox(
        *dimensions,
        App.Vector(0, 0, 0),
    )
    if fillet != 0:  # apply fillet to specified edges
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(*fillet_direction):
                part = part.makeFillet(fillet - 1e-3, [i])
    # apply centering
    part = translate_shape(
        part,
        (
            (1 + center[0]) * -dimensions[0] / 2,
            (1 + center[1]) * -dimensions[1] / 2,
            (1 + center[2]) * -dimensions[2] / 2,
        ),
    )
    # apply rotation
    part = rotate_shape(part, rotation)
    # apply translation
    part = translate_shape(part, position)
    return part


def cylinder_shape(
    diameter: float,
    height: float,
    position: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    center: int = -1,
) -> Part.Shape:
    """
    Create a cylinder part
    By default cylinder points in +Z direction with origin at the base center

    Args:
        diameter (float): Diameter of the cylinder
        height (float): Height of the cylinder
        position (tuple): Position of the cylinder base center (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        center (int): Position of the cylinder origin with respect to its height. For example:
                      -1 origin at base of the cylinder
                       0 origin at center of the cylinder
                       1 origin at top of the cylinder

    Returns:
        Part.Shape: The created cylinder part
    """

    # create shape
    part = Part.makeCylinder(
        diameter / 2,
        height,
        App.Vector(0, 0, 0),
        App.Vector(0, 0, 1),
    )
    # adjust to center
    part = translate_shape(part, (0, 0, (center + 1) * -height / 2))
    # apply rotation
    part = rotate_shape(part, rotation)
    # apply translation
    part = translate_shape(part, position)
    return part


def bounding_box_shape(
    shape: Part.Shape,
    padding: dim = dim(0, "mm"),
    fillet: dim = dim(0, "mm"),
    fillet_dir: tuple = (0, 0, 1),
    pad_x: bool = True,
    pad_y: bool = True,
    pad_z: bool = False,
    min_offset: tuple[dim, dim, dim] = (dim(0, "mm"), dim(0, "mm"), dim(0, "mm")),
    max_offset: tuple[dim, dim, dim] = (dim(0, "mm"), dim(0, "mm"), dim(0, "mm")),
) -> Part.Shape:
    """
    Create a box part based on the bounding box of a given shape

    Args:
        shape (Part.Shape): The input shape to create a bounding box around
        padding (dim): Uniform padding to apply to all dimensions of the bounding box
        fillet (dim): Radius of fillet to apply to edges in fillet_dir
        fillet_dir (tuple): Direction vector of edges to fillet
        pad_x (bool): Whether to apply padding in the X dimension
        pad_y (bool): Whether to apply padding in the Y dimension
        pad_z (bool): Whether to apply padding in the Z dimension
        min_offset (tuple[dim, dim, dim]): Minimum offset to apply to the bounding box in each dimension
        max_offset (tuple[dim, dim, dim]): Maximum offset to apply to the bounding box in each dimension

    Returns:
        Part.Shape: The created bounding box part
    """

    # reset positioning
    shape = shape.copy()
    shape.Placement = App.Placement()

    # get bounding box dimensions and position
    bbox = shape.BoundBox
    dx = bbox.XLength + (padding if pad_x else 0) + min_offset[0] + max_offset[0]
    dy = bbox.YLength + (padding if pad_y else 0) + min_offset[1] + max_offset[1]
    dz = bbox.ZLength + (padding if pad_z else 0) + min_offset[2] + max_offset[2]
    x = bbox.XMin - (padding / 2 if pad_x else 0) - min_offset[0]
    y = bbox.YMin - (padding / 2 if pad_y else 0) - min_offset[1]
    z = bbox.ZMin - (padding / 2 if pad_z else 0) - min_offset[2]

    # create box shape
    part = box_shape(
        dimensions=(dx, dy, dz),
        position=(x, y, z),
        fillet=fillet,
        fillet_direction=fillet_dir,
        center=(-1, -1, -1),
    )
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
    if clear_depth > 0:
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
    part = rotate_shape(part, rotation)
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
    if clear_depth > 0:
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
    part = rotate_shape(part, rotation)
    return part


def default_bolt_length(
    through_length: float, max_thread_engagement: float = None
) -> float:
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

    lengths = default_lengths[get_measurement_system()]
    if max_thread_engagement is None:
        minimum_length = through_length + get_minimum_thread_engagement()
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

    if not directory.is_absolute():
        base_path = Path(_caller_filename()).parent
        directory = base_path / directory

    model_path = directory / name

    # reuse a previously imported mesh if none of its files have changed
    cache_key = str(model_path)
    stamp = []
    for ext in ("json", "stl", "step"):
        try:
            stamp.append(os.stat(os.path.join(model_path, f"{name}.{ext}")).st_mtime_ns)
        except OSError:
            stamp.append(None)
    stamp = tuple(stamp)
    cached = _model_cache.get(cache_key)
    if cached is not None and cached[0] == stamp:
        return cached[1].copy()

    try:
        # validate files
        if not directory.is_dir():
            raise FileNotFoundError(f"Models directory not found at {model_path}")
        elif not model_path.is_dir():
            raise FileNotFoundError(f"Model not found in directory")
        elif not (model_path / (f"{name}.json")).is_file():
            raise FileNotFoundError(f"Model info file not found")

        if not (model_path / (f"{name}.stl")).is_file():
            if not (model_path / (f"{name}.step")).is_file():
                raise FileNotFoundError(f"Model STEP file not found")

            shape = Part.read(str(model_path / (f"{name}.step")))

            mesh = MeshPart.meshFromShape(
                Shape=shape, LinearDeflection=0.1, AngularDeflection=0.5
            )
            mesh.write(str(model_path / (f"{name}.stl")))

        # read mesh from file
        mesh = Mesh.read(str(model_path / (f"{name}.stl")))

        # apply transformations from json
        info = json.load(open(model_path / (f"{name}.json")))

        rot = App.Rotation("XYZ", *info["rotation"])
        trans = App.Vector(*info["translation"])
        # Build matrices
        rot_mat = rot.toMatrix()
        trans_mat = App.Matrix()
        trans_mat.move(trans)
        # Compose: translate first, then rotate
        final_mat = rot_mat.multiply(trans_mat)
        # Apply transform directly to mesh geometry
        mesh.transform(final_mat)

    except FileNotFoundError as e:
        print(f"Error importing model '{name}': {e}")
        return Mesh.Mesh()  # return empty mesh on error (not cached)

    _model_cache[cache_key] = (stamp, mesh.copy())
    return mesh
