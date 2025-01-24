from pathlib import Path

import Draft
import FreeCAD as App
import Mesh
import numpy as np
import Part

from .origin import Origin

INCH = 25.4

STL_PATH = str(Path(__file__).parent.parent.resolve()) + "/stl/"


BOLT_4_40 = {
    "clear_dia": 0.120 * INCH,
    "tap_dia": 0.089 * INCH,
    "head_dia": 5.50,
    "head_dz": 2.79,
}

BOLT_8_32 = {
    "clear_dia": 0.172 * INCH,
    "tap_dia": 0.136 * INCH,
    "head_dia": 7,
    "head_dz": 4.4,
}

BOLT_14_20 = {
    "clear_dia": 0.260 * INCH,
    "tap_dia": 0.201 * INCH,
    "head_dia": 9.8,
    "head_dz": 8,
    "washer_dia": 9 / 16 * INCH,
}


def _custom_box(dx, dy, dz, position, fillet=0, dir=(0, 0, 1), fillet_dir=None):
    if fillet_dir == None:
        fillet_dir = np.abs(dir)
    part = Part.makeBox(dx, dy, dz)
    if fillet != 0:
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(*fillet_dir):
                part = part.makeFillet(fillet - 1e-3, [i])
    part.translate(
        App.Vector(
            position[0] - (1 - dir[0]) * dx / 2,
            position[1] - (1 - dir[1]) * dy / 2,
            position[2] - (1 - dir[2]) * dz / 2,
        )
    )
    part = part.fuse(part)
    return part


def _import_stl(stl_name, rotate, translate, scale=1):
    mesh = Mesh.read(STL_PATH + stl_name)
    # mat = App.Matrix()
    # mat.scale(App.Vector(scale, scale, scale))
    # mesh.transform(mat)
    # mesh.rotate(*np.deg2rad(rotate))
    # mesh.translate(*translate)
    return mesh


class Bolt(Origin):
    """
    Bolt. Bottom edge of the head is at the origin and points down by default. Can optionally specify position of tip instead (will rotate about tip instead)
    """

    def __init__(
        self,
        name,
        bolt_type,
        length,
        drill_type,
        drills=[],
        position=(0, 0, 0),
        rotation=(0.0, 0.0, 0.0),
        tip_relative=False,
        head_length=None,
    ) -> None:
        super().__init__(name, position, rotation)

        if tip_relative:
            self.obj.addProperty("App::PropertyBool", "TipRelative").TipRelative = True
        else:
            self.obj.addProperty("App::PropertyBool", "TipRelative").TipRelative = False

        self.bolt_type = bolt_type
        self.obj.addProperty("App::PropertyString", "DrillType").DrillType = drill_type
        self.obj.addProperty("App::PropertyFloat", "Length").Length = length
        self.obj.addProperty("App::PropertyFloat", "HeadLength")
        if head_length != None:
            self.obj.HeadLength = head_length
        else:
            self.obj.HeadLength = bolt_type["head_dz"]

        try:
            drills = iter(drills)
        except TypeError:
            drills = [
                drills,
            ]
        for i in drills:
            if not hasattr(i.obj, "DrilledBy"):
                i.obj.addProperty("App::PropertyLinkListHidden", "DrilledBy")
            i.obj.DrilledBy += [self.obj]

    def execute(self, obj):
        return  # TODO: draw actual bolt

    def getDrillObj(self):
        part = Part.makeCylinder(
            self.bolt_type[self.obj.DrillType] / 2,
            self.obj.Length,
            App.Vector(0, 0, 0),
            App.Vector(0, 0, -1),
        )
        part = part.fuse(
            Part.makeCylinder(
                self.bolt_type["head_dia"] / 2,
                self.obj.HeadLength,
                App.Vector(0, 0, 0),
                App.Vector(0, 0, 1),
            )
        )
        if self.obj.TipRelative:
            part.translate(App.Vector(0, 0, self.obj.Length))

        part.Placement = self.obj.Placement * part.Placement

        return part


class CutBox(Origin):
    """
    Negative box
    """

    def __init__(
        self,
        name,
        dx,
        dy,
        dz,
        drills=[],
        position=(0, 0, 0),
        rotation=(0.0, 0.0, 0.0),
        # TODO: add fillet
    ) -> None:
        super().__init__(name, position, rotation)

        self.obj.addProperty("App::PropertyFloat", "Dx").Dx = dx
        self.obj.addProperty("App::PropertyFloat", "Dy").Dy = dy
        self.obj.addProperty("App::PropertyFloat", "Dz").Dz = dz

        try:
            drills = iter(drills)
        except TypeError:
            drills = [
                drills,
            ]
        for i in drills:
            if not hasattr(i.obj, "DrilledBy"):
                i.obj.addProperty("App::PropertyLinkListHidden", "DrilledBy")
            i.obj.DrilledBy += [self.obj]

    def execute(self, obj):
        return

    def getDrillObj(self):
        part = Part.makeBox(self.obj.Dx, self.obj.Dy, self.obj.Dz)

        part.Placement = self.obj.Placement * part.Placement

        return part


class GenericStl:
    def __init__(
        self, name, stl_name, rotate, translate, scale=1, placement=App.Matrix(), quality=1.
    ) -> None:
        self.obj = App.ActiveDocument.addObject("Mesh::FeaturePython", name)
        self.stl_name = stl_name
        self.quality = quality
        self.obj.addProperty(
            "App::PropertyPlacement", "BasePlacement"
        ).BasePlacement = (
            App.Rotation(App.Vector(1, 0, 0), App.Vector(0, 0, -1))
            * placement
            * App.Placement(
                App.Vector(translate),
                App.Rotation(rotate[0], rotate[1], rotate[2]),
                App.Vector(0, 0, 0),
            )
        )

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

    def calculate(
        self,
        parent_placement=App.Placement(App.Matrix()),
        depth=0,
        recurse=True,
        transform=True,
    ):
        """Apply parent transform and/or recurse to all children"""

        if depth > 250:  # recursion depth check
            return

        if transform:
            self.obj.Placement = parent_placement * self.obj.BasePlacement

        if recurse and hasattr(self.obj, "Children"):
            for i in self.obj.Children:
                i.Proxy.calculate(self.obj.Placement, depth + 1)

    def execute(self, obj):
        mesh = Mesh.read(STL_PATH + self.stl_name)
        mesh.decimate(.1, self.quality)
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh


class RectangularOptic:
    """
    Defines a rectangle in space

    Args:
        name (string)
        position (tuple[float, float, float]): The vector location of the optical center
        normal (tuple[float, float, float]): The normal vector of the optical surface
        base_length (float): The base length of the recangle
        height_length (float): The height of the rectangle, will match base_length if not given
        thickness (float): The thickness of the recangle
    """

    def __init__(
        self,
        name,
        position=(0, 0, 0),
        normal=(1, 0, 0),
        base_length=5,
        height_length=None,
        thickness=1.0,
        max_angle=45,
        reflect=False,
        transmit=False,
        mount_class=None,
        mount_pos=(0, 0, 0),
        drills=None,
    ) -> None:
        if not height_length:
            height_length = base_length

        self.obj = App.ActiveDocument.addObject("Part::FeaturePython", name)

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        self.obj.addProperty(
            "App::PropertyVector", "BasePosition"
        ).BasePosition = App.Vector(position)
        self.obj.addProperty(
            "App::PropertyVector", "BaseNormal"
        ).BaseNormal = App.Vector(normal).normalize()
        self.obj.addProperty("App::PropertyVector", "BaseEdge1").BaseEdge1 = (
            App.Rotation(App.Vector(1, 0, 0), self.obj.BaseNormal)
            * App.Vector(0, base_length, 0)
        )
        self.obj.addProperty("App::PropertyVector", "BaseEdge2").BaseEdge2 = (
            App.Rotation(App.Vector(1, 0, 0), self.obj.BaseNormal)
            * App.Vector(0, 0, height_length)
        )
        self.obj.addProperty("App::PropertyVector", "Position")
        self.obj.addProperty("App::PropertyVector", "Normal")
        self.obj.addProperty("App::PropertyVector", "Edge1")
        self.obj.addProperty("App::PropertyVector", "Edge2")
        self.obj.addProperty("App::PropertyFloat", "Thickness").Thickness = thickness
        self.obj.addProperty("App::PropertyFloat", "MaxAngle").MaxAngle = max_angle
        self.obj.addProperty(
            "App::PropertyString", "OpticalShape"
        ).OpticalShape = "rectangle"
        self.obj.addProperty("App::PropertyBool", "Transmit").Transmit = transmit
        self.obj.addProperty("App::PropertyBool", "Reflect").Reflect = reflect
        # self.reflection_angle = 0
        # self.max_angle = 90
        # self.max_width = diameter

        if mount_class != None:
            self.place(
                mount_class(
                    name=f"{name}_mount",
                    additional_placement=App.Placement(
                        App.Vector(mount_pos),
                        App.Rotation(0, 0, 0),
                        App.Vector(0, 0, 0),
                    ),
                    drills=drills,
                )
            )  # , rotation=rotation))

    def calculate(
        self,
        parent_placement=App.Placement(App.Matrix()),
        depth=0,
        transform=True,
        recurse=True,
    ):
        """Recursively apply relative transforms to all children"""

        if depth > 250:  # recursion depth check
            return

        if transform:
            self.obj.Position = parent_placement * self.obj.BasePosition
            self.obj.Normal = parent_placement.Rotation * self.obj.BaseNormal
            self.obj.Edge1 = parent_placement.Rotation * self.obj.BaseEdge1
            self.obj.Edge2 = parent_placement.Rotation * self.obj.BaseEdge2

        self.obj.Placement = App.Placement(
            self.obj.Position,
            App.Rotation(App.Vector(1, 0, 0), self.obj.Normal),
            App.Vector(0, 0, 0),
        )  # TODO constrain the rotation about the normal aswell

        if recurse and hasattr(self.obj, "Children"):
            for i in self.obj.Children:
                i.Proxy.calculate(
                    App.Placement(
                        self.obj.Position,
                        App.Rotation(App.Vector(1, 0, 0), self.obj.Normal),
                        App.Vector(0, 0, 0),
                    ),
                    depth + 1,
                )  # everything else defines "0 rotation" to be +x

    def execute(self, obj):
        part = Part.makeBox(
            self.obj.Edge2.Length,
            self.obj.Edge1.Length,
            self.obj.Thickness,
            App.Vector(0, 0, 0),
            App.Vector(-1, 0, 0),
        )
        part.translate(
            self.obj.Edge1.Length * App.Vector(0, 0.5, 0)
            + self.obj.Edge2.Length * App.Vector(0, 0, 0.5)
        )
        obj.Shape = part
        obj.Placement = obj.Placement * part.Placement

    def place(self, obj):
        """Place an object in the relative coordinate system"""

        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")

        self.obj.Children += [obj.obj]
        obj.obj.addProperty(
            "App::PropertyLinkHidden", "RelativeTo"
        ).RelativeTo = self.obj

        return obj


class SquareMirror(RectangularOptic):
    """Square mirror"""

    def __init__(
        self,
        name,
        position=(0, 0, 0),
        normal=(1, 0, 0),
        side_length=0.5 * INCH,
        thickness=1 / 8 * INCH,
        max_angle=45,
        mount_class=None,
        drills=None,
    ):
        super().__init__(
            name,
            position,
            normal,
            side_length,
            side_length,
            thickness,
            max_angle,
            reflect=True,
            mount_class=mount_class,
            mount_pos=(-thickness, 0, 0),
            drills=drills,
        )


class CubeSplitter(RectangularOptic):
    """Cube splitter"""

    def __init__(
        self,
        name,
        position=(0, 0, 0),
        normal=(1, 0, 0),
        cube_size=10,
        max_angle=45,
        mount_class=None,
        drills=None,
    ):
        super().__init__(
            name,
            position,
            normal,
            np.sqrt(2) * cube_size,
            cube_size,
            1,
            max_angle,
            reflect=True,
            transmit=True,
            mount_class=mount_class,
            drills=drills,
        )

        self.obj.ViewObject.Transparency = 50
        self.obj.ViewObject.ShapeColor = (0.5, 0.5, 0.8)

    def execute(self, obj):
        part = Part.makeBox(
            self.obj.Edge2.Length, self.obj.Edge2.Length, self.obj.Edge2.Length
        )
        part.Placement = part.Placement * App.Rotation(45, 0, 0)
        temp = Part.makeBox(
            0.1,
            self.obj.Edge1.Length + 1,
            self.obj.Edge2.Length,
            App.Vector(-0.05, -0.5, 0),
        )
        part = part.cut(temp)
        part.translate(
            self.obj.Edge1.Length * App.Vector(0, -0.5, 0)
            + self.obj.Edge2.Length * App.Vector(0, 0, -0.5)
        )
        obj.Shape = part
        obj.Placement = obj.Placement * part.Placement


class CylindricalOptic:
    """
    Defines a cylinder in space

    Args:
        name (string)
        position (tuple[float, float, float]): The vector location of the optical center
        normal (tuple[float, float, float]): The normal vector of the optical surface
        radius (float): The radius of the cylinder
        thickness (float): The thickness of the cylinder
    """

    def __init__(
        self,
        name,
        position,
        normal,
        radius,
        thickness,
        max_angle=45,
        reflect=False,
        transmit=False,
        drills=None,
        mount_class=None,
        mount_pos=(0, 0, 0),
        mount_rotation = (0,0,0),
    ):
        self.obj = App.ActiveDocument.addObject("Part::FeaturePython", name)

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        self.obj.addProperty(
            "App::PropertyVector", "BasePosition"
        ).BasePosition = App.Vector(position)
        self.obj.addProperty(
            "App::PropertyVector", "BaseNormal"
        ).BaseNormal = App.Vector(normal).normalize()
        self.obj.addProperty("App::PropertyVector", "Position")
        self.obj.addProperty("App::PropertyVector", "Normal")
        self.obj.addProperty("App::PropertyFloat", "Radius").Radius = radius
        self.obj.addProperty("App::PropertyFloat", "Thickness").Thickness = thickness
        self.obj.addProperty("App::PropertyFloat", "MaxAngle").MaxAngle = max_angle
        self.obj.addProperty(
            "App::PropertyString", "OpticalShape"
        ).OpticalShape = "circle"
        self.obj.addProperty("App::PropertyBool", "Transmit").Transmit = transmit
        self.obj.addProperty("App::PropertyBool", "Reflect").Reflect = reflect
        # self.reflection_angle = 0
        # self.max_angle = 90
        # self.max_width = diameter

         # Handle mount_class if provided
        if mount_class is not None:
            # Instead of passing additional arguments to the mount class,
            # we simply call mount_class with the arguments it expects
            mount_obj = mount_class(
                name=f"{name}_mount",  # Mount name
                additional_placement=App.Placement(
                        App.Vector(mount_pos),
                        App.Rotation(0, 0, 0),
                        App.Vector(0, 0, 0),
                    ),
                drills=drills,         # Passing drills as a possible argument
            )

            self.place(mount_obj)  
    def execute(self, obj):
        part = Part.makeCylinder(self.obj.Radius, self.obj.Thickness, App.Vector(0, 0, 0), App.Vector(-1, 0, 0))
        obj.Shape = part

    def calculate(
        self,
        parent_placement=App.Placement(App.Matrix()),
        depth=0,
        transform=True,
        recurse=True,
    ):
        """Recursively apply relative transforms to all children"""

        if depth > 250:  # recursion depth check
            return

        if transform:
            self.obj.Position = parent_placement * self.obj.BasePosition
            self.obj.Normal = parent_placement.Rotation * self.obj.BaseNormal

        self.obj.Placement = App.Placement(
            self.obj.Position,
            App.Rotation(App.Vector(0, 0, -1), self.obj.Normal),
            App.Vector(0, 0, 0),
        )

        if (
            recurse and hasattr(self.obj, "Children")
        ):  # don't apply mount transform to children but do apply mirror_thickness offset or similar
            for i in self.obj.Children:
                i.Proxy.calculate(
                    parent_placement * self.obj.OffsetPlacement,
                    depth + 1,
                )

        # if recurse and hasattr(self.obj, "Children"):
        #     for i in self.obj.Children:
        #         i.Proxy.calculate(
        #             App.Placement(
        #                 self.obj.Position,
        #                 App.Rotation(App.Vector(1, 0, 0), self.obj.Normal),
        #                 App.Vector(0, 0, 0),
        #             ),
        #             depth + 1,
        #         )  # everything else defines "0 rotation" to be +x

    def place(self, obj):
        """Place an object in the relative coordinate system"""
        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")
        self.obj.Children += [obj.obj]

        if not hasattr(obj.obj, "ParentPlacement"):
            obj.obj.addProperty("App::PropertyPlacement", "ParentPlacement")
            obj.obj.ParentPlacement = App.Placement()  # Initialize with default placement

        # Now set the mount's position relative to the optic (parent)
        obj.obj.addProperty("App::PropertyLinkHidden", "RelativeTo").RelativeTo = self.obj

        return obj



class CircularMirror(CylindricalOptic):
    """Cylindrical mirror"""

    def __init__(
        self,
        name,
        position=(0, 0, 0),
        normal=(1, 0, 0),
        radius=0.5 * INCH,
        thickness=1 / 8 * INCH,
        max_angle=45,
        drills=None,
        mount_class=None,
    ):
        super().__init__(
            name,
            position,
            normal,
            radius,
            thickness,
            max_angle,
            reflect=True,
            drills=drills,
            mount_class=mount_class,
            mount_pos=(-thickness, 0, 0),
        )
        self.obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)


class CircularSplitter(CylindricalOptic):
    """Cylindrical beam splitter, (normal vector is to the reflection plane)"""

    def __init__(
        self,
        name,
        position=(0, 0, 0),
        normal=(1, 0, 0),
        radius=0.5 * INCH,
        thickness=1 / 8 * INCH,
        max_angle=45,
        drills=None,
        mount_class=None,
    ):
        super().__init__(
            name,
            position,
            normal,
            radius,
            thickness,
            max_angle,
            reflect=True,
            transmit=True,
            drills=drills,
            mount_class=mount_class,
            mount_pos=(-thickness / 2, 0, 0),
        )


class CircularTransmission(CylindricalOptic):
    """Cylindrical transmission optic"""

    def __init__(
        self,
        name,
        position=(0, 0, 0),
        normal=(1, 0, 0),
        radius=0.5 * INCH,
        thickness=1 / 8 * INCH,
        max_angle=45,
        drills=None,
        mount_class=None,
    ):
        super().__init__(
            name,
            position,
            normal,
            radius,
            thickness,
            max_angle,
            reflect=False,
            transmit=True,
            drills=drills,
            mount_class=mount_class,
            mount_pos=(-thickness, 0, 0),
        )
        self.obj.ViewObject.Transparency = 50
        self.obj.ViewObject.ShapeColor = (0.5, 0.5, 0.8)

class CircularStopper(CylindricalOptic):
    """Absorbs beams"""

    def __init__(
        self,
        name,
        position=(0, 0, 0),
        normal=(1, 0, 0),
        radius=0.5 * INCH,
        thickness=1 / 8 * INCH,
        max_angle=45,
        drills=None,
        mount_class=None,
    ):
        super().__init__(
            name,
            position,
            normal,
            radius,
            thickness,
            max_angle,
            reflect=False,
            transmit=False,
            drills=drills,
            mount_class=mount_class,
            mount_pos=(-thickness, 0, 0),
        )

        self.obj.addProperty("App::PropertyBool", "Absorb").Absorb = True
        self.obj.ViewObject.ShapeColor = (0, 0, 0)


class Mount:
    def __init__(
        self,
        name,
        mount_position=(0, 0, 0),
        mount_rotation=(0, 0, 0),
        additional_placement=App.Matrix(),
    ):
        """
        Parent class for mounts
        """
        self.mount_position = mount_position
        self.mount_rotation = mount_rotation
        self.additional_placement = additional_placement
        self.obj = App.ActiveDocument.addObject("Mesh::FeaturePython", name)
        self.obj.addProperty(
            "App::PropertyPlacement", "OffsetPlacement"
        ).OffsetPlacement = additional_placement
        self.obj.addProperty(
            "App::PropertyPlacement", "BasePlacement"
        ).BasePlacement = additional_placement * App.Placement(
            App.Vector(mount_position),
            App.Rotation(
                float(mount_rotation[0]),
                float(mount_rotation[1]),
                float(mount_rotation[2]),
            ),
            App.Vector(0, 0, 0),
        )
        self.obj.addProperty("App::PropertyVector", "Position")
        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        self.obj.ViewObject.ShapeColor = (0.5, 0.5, 0.55)

    def place(self, obj):
        """Place an object in the relative coordinate system"""
        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")

        # Handle Part::FeaturePython objects
        if hasattr(obj, 'obj'):  # this indicates it's a Part::FeaturePython or similar
            self.obj.Children += [obj.obj]
            obj.obj.addProperty("App::PropertyLinkHidden", "RelativeTo").RelativeTo = self.obj
        # else:  # assuming obj is a Mesh::MeshObject
        #     # Create a Part::FeaturePython object to wrap the mesh
        #     mesh_obj = App.ActiveDocument.addObject("Part::FeaturePython", f"MeshWrapper_{str(id(obj))}")
            
        #     # Convert Mesh.MeshObject to Part.Shape and assign it to the new Part::FeaturePython
        #     if hasattr(obj, 'Mesh'):
        #         # If the object is a Mesh object, we convert it to Part shape
        #         part_shape = Part.Shape(obj.Mesh)
        #         mesh_obj.Shape = part_shape
        #     mesh_obj.Placement = mesh_obj.Placement * self.additional_placement * App.Placement(
        #     App.Vector(self.mount_position),
        #     App.Rotation(
        #         float(self.mount_rotation[0]),
        #         float(self.mount_rotation[1]),
        #         float(self.mount_rotation[2]),
        #     ),
        #     App.Vector(0, 0, 0),
        # )
        #     # Now add this wrapped mesh object to the mount's Children
        #     self.obj.Children += [mesh_obj]
        #     mesh_obj.addProperty("App::PropertyLinkHidden", "RelativeTo").RelativeTo = self.obj

        return obj

    def calculate(
        self,
        parent_placement=App.Placement(App.Matrix()),
        depth=0,
        recurse=True,
        transform=True,
    ):
        """Apply parent transform and/or recurse to all children"""

        if depth > 250:  # recursion depth check
            return

        if transform:
            self.obj.Placement = parent_placement * self.obj.BasePlacement * self.obj.OffsetPlacement

        if (
            recurse and hasattr(self.obj, "Children")
        ):  # don't apply mount transform to children but do apply mirror_thickness offset or similar
            for i in self.obj.Children:
                i.Proxy.calculate(
                    parent_placement * self.obj.OffsetPlacement,
                    depth + 1,
                )


class Rsp05(Mount):
    """
    Rotation mount, Rsp05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        bolt_length (float) : The length of the bolt used for mounting

    """

    def __init__(
        self,
        name,
        drills=None,
        bolt_length=15,
        additional_placement=App.Matrix(),
    ):
        super().__init__(
            name,
            (2.032, 0, 0),
            (90, 0, 90),
            additional_placement,
        )

        if drills != None:
            self.place(
                Bolt(
                    f"{name}_mountbolt",
                    BOLT_8_32,
                    0.375 * INCH,
                    "clear_dia",
                    drills,
                    (1.397, 0, -13.97 + 0.25 * INCH),
                    (0, 180, 0),
                    tip_relative=True,
                )
            )

    def execute(self, obj):
        mesh = Mesh.read(STL_PATH + "RSP05-Step.stl")
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh


class Rsp05ForRedstone(Mount):
    """
    Rotation mount, Rsp05
    """

    def __init__(
        self,
        name,
        drills=None,
        bolt_length=15,
        additional_placement=App.Matrix(),
    ):
        super().__init__(
            name,
            (2.032, 0, 0),
            (90, 0, 90),
            additional_placement,
        )

        if drills != None:
            self.place(
                Bolt(
                    f"{name}_mountbolt",
                    BOLT_8_32,
                    0.75 * INCH,
                    "clear_dia",
                    drills,
                    (1.397, 0, -13.97 + 0.25 * INCH),
                    (0, 180, 0),
                    tip_relative=True,
                )
            )
            self.place(
                CutBox(
                    f"{name}_boundbox",
                    2 * INCH,
                    1.5 * INCH,
                    1.5 * INCH,
                    drills,
                    (1.397 - INCH, -0.75 * INCH, -13.97),
                )
            )

    def execute(self, obj):
        return
        # mesh = Mesh.read(STL_PATH + "RSP05-Step.stl")
        # mesh.Placement = self.obj.Placement
        # mesh.decimate(.1, .9)
        # obj.Mesh = mesh


class PBSForRedstone(Mount):
    def __init__(self, name, drills=None, additional_placement=App.Matrix()):
        super().__init__(name)

        if drills != None:
            self.place(
                CutBox(
                    f"{name}_mount",
                    10.1,
                    10.1,
                    1,
                    drills,
                    (0, -5.05 * np.sqrt(2), -5),
                    (45, 0, 0),
                )
            )
            self.place(
                CutBox(
                    f"{name}_mount",
                    1.5 * INCH,
                    2 * INCH,
                    1.5 * INCH,
                    drills,
                    (-0.75 * INCH, -1 * INCH, -4),
                )
            )

    def execute(self, obj):
        return


class Km05(Mount):
    """
    Mirror mount, model KM05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    """

    def __init__(
        self,
        name,
        drills=None,
        thumbscrews=False,
        bolt_length=15,
        additional_placement=App.Matrix(),
    ):
        super().__init__(
            name, (-1.916, -1.148, 0.498), (90, 0, 90), additional_placement
        )
       
        if drills != None:
            self.place(
                Bolt(
                    f"{name}_mountbolt",
                    BOLT_8_32,
                    0.75 * INCH + 30,
                    "clear_dia",
                    drills,
                    (-11.29, 0, -6.7),
                    (0, 180, 0),
                    True,
                    head_length=15
                )
            )
            self.place(
                CutBox(
                    f"{name}_bounding_box",
                    2 * INCH,
                    1.5 * INCH,
                    1.5 * INCH,
                    drills,
                    (-1 * INCH, -0.75 * INCH, -14.73),
                )
            )

    def execute(self, obj):
        mesh = Mesh.read(STL_PATH + "KM05-Step.stl")
        # self.place(mesh)
        mesh.Placement = self.obj.Placement * App.Placement(
            App.Vector(self.mount_position),
            App.Rotation(
                float(self.mount_rotation[0]),
                float(self.mount_rotation[1]),
                float(self.mount_rotation[2]),
            ),
            App.Vector(0, 0, 0),
        )
        obj.Mesh = mesh

class Chamber_with_chip:
    def __init__(
        self,
        name,
        position,
        direction
    ):
        self.obj = App.ActiveDocument.addObject("Mesh::FeaturePython", name)
        self.obj.addProperty("App::PropertyPlacement", "ParentPlacement").ParentPlacement = App.Placement(App.Matrix())
        self.obj.addProperty("App::PropertyVector", "BaseOrigin").BaseOrigin = App.Vector(position)
        self.obj.addProperty("App::PropertyVector", "BaseOffset").BaseOffset = App.Vector(direction).normalize()
        self.obj.addProperty("App::PropertyVector", "Position")
        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        self.obj.ViewObject.ShapeColor = (0.5, 0.5, 0.55)
    def place(self, obj):
        pass

    def calculate(
        self,
        parent_placement=App.Placement(App.Matrix()),
        depth=0,
        recurse=True,
        transform=True,
    ):
        pass
       
    def execute(self, obj):
        mesh = Mesh.read(STL_PATH + "room temperature chamber with chip.stl")
        
        mesh.Placement = self.obj.Placement 
        obj.Mesh = mesh


class Km05ForRedstone(Mount):
    """
    Mirror mount, model KM05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    """

    def __init__(
        self,
        name,
        drill=True,
        thumbscrews=False,
        drills=None,
        additional_placement=App.Matrix(),
    ):
        super().__init__(
            name, (2.048, -1.148, 0.498), (90, 0, 90), additional_placement
        )
        if drills != None:
            self.place(
                Bolt(
                    f"{name}_mountbolt",
                    BOLT_8_32,
                    0.75 * INCH,
                    "clear_dia",
                    drills,
                    (-7.29, 0, -6.7),
                    (0, 180, 0),
                    True,
                )
            )
            self.place(
                CutBox(
                    f"{name}_bounding_box",
                    2 * INCH,
                    1.5 * INCH,
                    1.5 * INCH,
                    drills,
                    (-1 * INCH, -0.75 * INCH, -14.73),
                )
            )
            
    def execute(self, obj):
        return
        # mesh = Mesh.read(STL_PATH + "KM05-Step.stl")
        # mesh.Placement = self.obj.Placement
        # mesh.decimate(.1, .9)
        # obj.Mesh = mesh


class K05S2(Mount):
    """
    Mirror mount, model Polaris K05S2

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    """

    def __init__(
        self,
        name,
        drill=True,
        thumbscrews=False,
        bolt_length=15,
        additional_placement=App.Matrix(),
    ):
        super().__init__(
            name, (-4.514, 0.254, -0.254), (90, 0, 90), additional_placement
        )

    def execute(self, obj):
        mesh = Mesh.read(STL_PATH + "POLARIS-K05S2-Step.stl")
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh


class ViewProvider:
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        return

    def getDefaultDisplayMode(self):
        return "Shaded"

    def claimChildren(self):
        # return
        if hasattr(self.Object, "Children"):
            return self.Object.Children
        else:
            return []

    def updateData(self, obj, prop):
        if str(prop) == "ParentPlacement":
            # Debug: Check if the object has ParentPlacement property, and if it should have OpticalShape
            if not hasattr(obj, "ParentPlacement"):
                # print(f"Adding ParentPlacement to {obj.Name}")
                obj.addProperty("App::PropertyPlacement", "ParentPlacement")
                obj.ParentPlacement = App.Placement()  # Default placement (no position or rotation)
            else:
                print(f"{obj.Name} already has ParentPlacement")

            # print(f"Current ParentPlacement for {obj.Name}: {obj.ParentPlacement}")
            obj.Position = obj.ParentPlacement.Base  # Update position based on parent placement
            # print(f"Updated Position for {obj.Name}: {obj.Position}")

            # Only check for OpticalShape if the object is an optical element (e.g., CylindricalOptic, Beam, etc.)
            if hasattr(obj, "OpticalShape"):  # Check if it has OpticalShape property
                # Handle optical shapes (circle or rectangle)
                if obj.OpticalShape == "circle":
                    obj.Normal = obj.ParentPlacement.Rotation * App.Vector(1, 0, 0)
                elif obj.OpticalShape == "rectangle":
                    obj.Edge1 = obj.ParentPlacement.Rotation * obj.BaseEdge1
                    obj.Edge2 = obj.ParentPlacement.Rotation * obj.BaseEdge2

                # Print the normal and edges for debugging
                # print(f"Updated Normal for {obj.Name}: {obj.Normal}")
                if obj.OpticalShape == "rectangle":
                    print(f"Updated Edges for {obj.Name}: {obj.Edge1}, {obj.Edge2}")

            obj.Placement = obj.ParentPlacement  # Update the object's placement
            # print(f"Updated Placement for {obj.Name}: {obj.Placement}")

            # If the object has children, update their ParentPlacement recursively
            if hasattr(obj, "Children"):
                # print(f"{obj.Name} has {len(obj.Children)} children. Updating their ParentPlacement.")
                for child in obj.Children:
                    # print(f"Setting ParentPlacement for child {child.Name}")
                    child.ParentPlacement = obj.Placement  # Set child's ParentPlacement to parent's Placement

            # print(f"Data update complete for {obj.Name}")




    # def onDelete(self, feature, subelements):
    # # delete all elements when baseplate is deleted
    # for i in App.ActiveDocument.Objects:
    #     if i != feature.Object:
    #         App.ActiveDocument.removeObject(i.Name)
    # return True

    def getIcon(self):
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
