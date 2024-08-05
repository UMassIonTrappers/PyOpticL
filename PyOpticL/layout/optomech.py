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
        self.obj.Shape = part

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
        self, name, stl_name, rotate, translate, scale=1, placement=App.Matrix()
    ) -> None:
        self.obj = App.ActiveDocument.addObject("Mesh::FeaturePython", name)
        self.stl_name = stl_name
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
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh


class SquareOptic:
    """
    Defines a square in space

    Args:
        name (string)
        position (tuple[float, float, float]): The vector location of the optical center
        normal (tuple[float, float, float]): The normal vector of the optical surface
        side_length (float): The side length of the square
        thickness (float): The thickness of the square
        thickness (float): The thickness of the recangle
    """

    def __init__(
        self,
        name,
        position,
        normal,
        base_length,
        height_length=None,
        thickness=1,
        max_angle=45,
        reflect=False,
        transmit=False,
        mount_class=None,
        mount_pos=(0, 0, 0),
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
        ).OpticalShape = "square"
        self.obj.addProperty("App::PropertyBool", "Transmit").Transmit = transmit
        self.obj.addProperty("App::PropertyBool", "Reflect").Reflect = reflect
        # self.reflection_angle = 0
        # self.max_angle = 90
        # self.max_width = diameter

        if mount_class != None:
            self.place(
                mount_class(
                    name=f"{name}_mount",
                    placement=App.Placement(
                        App.Vector(mount_pos),
                        App.Rotation(0, 0, 0),
                        App.Vector(0, 0, 0),
                    ),
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

    def execute(self, obj):
        part = Part.makeCylinder(self.obj.Radius, self.obj.Thickness)
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

    def place(self, obj):
        """Place an object in the relative coordinate system"""

        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")

        self.obj.Children += [obj.obj]
        obj.obj.addProperty(
            "App::PropertyLinkHidden", "RelativeTo"
        ).RelativeTo = self.obj

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


class Mount:
    def __init__(
        self,
        name,
        mount_position,
        mount_rotation,
        additional_placement=App.Matrix(),
    ):
        """
        Parent class for mounts
        """

        self.obj = App.ActiveDocument.addObject("Mesh::FeaturePython", name)
        self.obj.addProperty(
            "App::PropertyPlacement", "OffsetPlacement"
        ).OffsetPlacement = additional_placement
        self.obj.addProperty(
            "App::PropertyPlacement", "BasePlacement"
        ).BasePlacement = additional_placement * App.Placement(
            App.Vector(mount_position),
            App.Rotation(mount_rotation),
            App.Vector(0, 0, 0),
        )

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

    def place(self, obj):
        """Place an object in the relative coordinate system"""

        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")

        self.obj.Children += [obj.obj]
        obj.obj.addProperty(
            "App::PropertyLinkHidden", "RelativeTo"
        ).RelativeTo = self.obj

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
            self.obj.Placement = parent_placement * self.obj.BasePlacement

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
                name, (2.084, -1.148, .498),
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
                name, (2.084, -1.148, .498),
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
            self.place(
                CutBox(
                    f"{name}_boundbox",
                    0.75 * INCH,
                    1.5 * INCH,
                    1.5 * INCH,
                    drills,
                    (1.397 - 0.375 * INCH, -0.75 * INCH, -13.97),
                )
            )

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

    def execute(self, obj):
        mesh = Mesh.read(STL_PATH + "RSP05-Step.stl")
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh


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
        drill=True,
        thumbscrews=False,
        bolt_length=15,
        additional_placement=App.Matrix(),
    ):
        super().__init__(name, (2.084, -1.148, .498), (90, 0, 90), additional_placement)

    def execute(self, obj):
        mesh = Mesh.read(STL_PATH + "KM05-Step.stl")
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
        super().__init__(name, (2.048, -1.148, .498), (90, 0, 90), additional_placement)
        if drills != None:
            self.place(
                Bolt(
                    f"{name}_mountbolt",
                    BOLT_8_32,
                    INCH,
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
                    1.2 * INCH,
                    1.5 * INCH,
                    1.5 * INCH,
                    drills,
                    (0.2 * INCH, -0.375 * INCH, -14.73),
                )
            )

    def execute(self, obj):
        mesh = Mesh.read(STL_PATH + "KM05-Step.stl")
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh


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
        super().__init__(name, (-4.514, .254, -.254), (90, 0, 90), additional_placement)

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
        if hasattr(self.Object, "Children"):
            return self.Object.Children
        else:
            return []

    # def updateData(self, base_obj, prop):
    #     if prop in "Children":
    #
    #
    #     for obj in App.ActiveDocument.Objects:
    #         if hasattr(obj, "BasePlacement") and obj.Baseplate != None:
    #             obj.Placement.Base = (
    #                 obj.BasePlacement.Base + obj.Baseplate.Placement.Base
    #             )
    #             obj.Placement = App.Placement(
    #                 obj.Placement.Base,
    #                 obj.Baseplate.Placement.Rotation,
    #                 -obj.BasePlacement.Base,
    #             )
    #             obj.Placement.Rotation = obj.Placement.Rotation.multiply(
    #                 obj.BasePlacement.Rotation
    #             )

    # def onDelete(self, feature, subelements):
    # # delete all elements when baseplate is deleted
    # for i in App.ActiveDocument.Objects:
    #     if i != feature.Object:
    #         App.ActiveDocument.removeObject(i.Name)
    # return True

    def claimChildren(self):
        if hasattr(self.Object, "ChildObjects"):
            return self.Object.ChildObjects
        else:
            return []

    def getIcon(self):
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
