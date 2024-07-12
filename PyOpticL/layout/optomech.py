from pathlib import Path

import Draft
import FreeCAD as App
import Mesh
import numpy as np
import Part

from .origin import Origin


class CylindricalOptic:
    """
    Defines a cylinder in space

    Args:
        name (string)
        position (App.Vector): The vector location of the optical center
        normal (App.Vector): The normal vector of the optical surface
        radius (float): The radius of the cylinder
        thickness (float): The thickness of the cylinder
    """

    type = "Part::FeaturePython"

    def __init__(self, name, position, normal, radius, thickness):
        self.obj = App.ActiveDocument.addObject("Part::FeaturePython", name)

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        self.obj.addProperty("App::PropertyVector", "Position").Position = position
        self.obj.addProperty("App::PropertyVector", "Vec2").Vec2 = normal
        self.obj.addProperty("App::PropertyLength", "Radius").Radius = radius
        self.obj.addProperty("App::PropertyLength", "Thickness").Thickness = thickness

        # self.reflection_angle = 0
        # self.max_angle = 90
        # self.max_width = diameter

    def execute(self, obj):
        part = Part.makeCylinder(self.obj.Radius, self.obj.Thickness)
        obj.Shape = part

    def calculate(self, parent_placement=App.Placement(App.Matrix()), depth=0):
        """Recursively apply relative transforms to all children"""

        if depth > 250:  # recursion depth check
            return
        
        print(parent_placement)

        self.obj.Placement = parent_placement * (
            App.Placement(
                self.obj.Position,
                App.Rotation(App.Vector(0, 0, -1), self.obj.Vec2),
                App.Vector(0, 0, 0),
            )
        )

        if hasattr(self.obj, "Children"):
            for i in self.obj.Children:
                i.Proxy.calculate(self.obj.Placement, depth + 1)


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
