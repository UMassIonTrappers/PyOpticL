from pathlib import Path

import Draft
import FreeCAD as App
import Mesh
import numpy as np
import Part

from .origin import Origin

INCH = 25.4

STL_PATH = str(Path(__file__).parent.parent.resolve()) + "/stl/"


def _import_stl(stl_name, rotate, translate, scale=1):
    mesh = Mesh.read(STL_PATH + stl_name)
    # mat = App.Matrix()
    # mat.scale(App.Vector(scale, scale, scale))
    # mesh.transform(mat)
    # mesh.rotate(*np.deg2rad(rotate))
    # mesh.translate(*translate)
    return mesh


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
        print(self.obj.Placement)
        mesh = Mesh.read(STL_PATH + self.stl_name)
        print(mesh.Placement)
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh


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
        mount_class=None,
        radius=0.5 * INCH,
        thickness=1 / 8 * INCH,
        max_angle=45,
    ):
        super().__init__(
            name, position, normal, radius, thickness, max_angle, reflect=True
        )
        if mount_class != None:
            self.place(
                mount_class(
                    name=f"{name}_mount",
                    placement=App.Placement(
                        App.Vector(-thickness, 0, 0),
                        App.Rotation(0, 0, 0),
                        App.Vector(0, 0, 0),
                    ),
                )
            )  # , rotation=rotation))


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
        )


class Km05:
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
        placement=App.Matrix(),
    ):
        self.obj = App.ActiveDocument.addObject("Mesh::FeaturePython", name)
        self.obj.addProperty(
            "App::PropertyPlacement", "BasePlacement"
        ).BasePlacement = placement * App.Placement(
            App.Vector(2.084, -1.148, 0.498),
            App.Rotation(90, -0, 90),
            App.Vector(0, 0, 0),
        )

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        # obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        # obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        # obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length
        # obj.addProperty('Part::PropertyPartShape', 'DrillPart')
        #
        # obj.ViewObject.ShapeColor = mount_color
        # self.part_numbers = ['KM05']
        #
        # if thumbscrews:
        #     _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, 9.906, 9.906))
        #     _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, -9.906, -9.906))

    def execute(self, obj):
        print(self.obj.Placement)
        mesh = Mesh.read(STL_PATH + "KM05-Step.stl")
        print(mesh.Placement)
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh

    def place(self, obj):
        """Place an object in the relative coordinate system"""

        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")

        self.obj.Children += [obj.obj]
        obj.obj.addProperty(
            "App::PropertyLinkHidden", "RelativeTo"
        ).RelativeTo = self.obj

        return obj

    def calculate(self, parent_placement=App.Placement(App.Matrix()), depth=0):
        """Recursively apply relative transforms to all children"""

        if depth > 250:  # recursion depth check
            return

        print(f"placement passed to mount: {parent_placement}")

        self.obj.Placement = parent_placement * self.obj.BasePlacement

        if hasattr(self.obj, "Children"):
            for i in self.obj.Children:
                i.Proxy.calculate(self.obj.Placement, depth + 1)


class K05S2:
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
        placement=App.Matrix(),
    ):
        self.obj = App.ActiveDocument.addObject("Mesh::FeaturePython", name)
        self.obj.addProperty(
            "App::PropertyPlacement", "BasePlacement"
        ).BasePlacement = placement * App.Placement(
            App.Vector(-4.514, 0.254, -0.254),
            App.Rotation(90, -0, -90),
            App.Vector(0, 0, 0),
        )

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        # obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        # obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        # obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length
        # obj.addProperty('Part::PropertyPartShape', 'DrillPart')
        #
        # obj.ViewObject.ShapeColor = mount_color
        # self.part_numbers = ['KM05']
        #
        # if thumbscrews:
        #     _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, 9.906, 9.906))
        #     _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, -9.906, -9.906))

    def execute(self, obj):
        print(self.obj.Placement)
        mesh = Mesh.read(STL_PATH + "POLARIS-K05S2-Step.stl")
        print(mesh.Placement)
        mesh.Placement = self.obj.Placement
        obj.Mesh = mesh

    def place(self, obj):
        """Place an object in the relative coordinate system"""

        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")

        self.obj.Children += [obj.obj]
        obj.obj.addProperty(
            "App::PropertyLinkHidden", "RelativeTo"
        ).RelativeTo = self.obj

        return obj

    def calculate(self, parent_placement=App.Placement(App.Matrix()), depth=0):
        """Recursively apply relative transforms to all children"""

        if depth > 250:  # recursion depth check
            return

        print(f"placement passed to mount: {parent_placement}")

        self.obj.Placement = parent_placement * self.obj.BasePlacement

        if hasattr(self.obj, "Children"):
            for i in self.obj.Children:
                i.Proxy.calculate(self.obj.Placement, depth + 1)


# def execute(self, obj):
#     return
# mesh = _import_stl("KM05-Step.stl", (90, -0, 90), (2.084, -1.148, 0.498))
# mesh.Placement = obj.Mesh.Placement
# obj.Mesh = mesh
#
# part = _bounding_box(obj, 2, 3, min_offset=(4.35, 0, 0))
# part = part.fuse(_bounding_box(obj, 2, 3, max_offset=(0, -20, 0)))
# part = _fillet_all(part, 3)
# part = part.fuse(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=inch,
#                                   head_dia=bolt_8_32['head_dia'], head_dz=0.92*inch-obj.BoltLength.Value,
#                                   x=-7.29, y=0, z=-inch*3/2, dir=(0,0,1)))
# part.Placement = obj.Placement
# obj.DrillPart = part


class ViewProvider:
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        return

    def getDefaultDisplayMode(self):
        return "Shaded"

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
