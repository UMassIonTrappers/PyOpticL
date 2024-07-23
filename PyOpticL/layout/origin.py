import Draft
import FreeCAD as App
import Mesh
import Part


class Origin:
    """
    A class defining a coordinate system

    Args:
    name (string)
    x, y, z (float): Coordinates of the group's origin
    angle_x, angle_y, angle_z (float): Rotation of the group's coordinate system

    """

    def __init__(self, name, x=0, y=0, z=0, angle_z=0, angle_y=0, angle_x=0) -> None:
        self.obj = App.ActiveDocument.addObject("Part::FeaturePython", name)
        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        self.obj.addProperty("App::PropertyPlacement", "BasePlacement").BasePlacement = App.Placement(
            App.Vector(x, y, z),
            App.Rotation(angle_z, angle_y, angle_x),
            App.Vector(0, 0, 0),
        )

    def place(self, obj):
        """Place an object in the relative coordinate system"""

        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")

        self.obj.Children += [obj.obj]
        obj.obj.addProperty("App::PropertyLinkHidden", "RelativeTo").RelativeTo = self.obj

        return obj

    def execute(self, obj):
        return

    def calculate(self, parent_placement=App.Placement(App.Matrix()), depth=0):
        """Recursively apply relative transforms to all children"""

        if depth > 250:  # recursion depth check
            return

        self.obj.Placement = parent_placement * self.obj.BasePlacement

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
