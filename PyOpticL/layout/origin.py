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

    def __init__(self, name, position=(0, 0, 0), rotation=(0.0, 0.0, 0.0)) -> None:
        self.obj = App.ActiveDocument.addObject("Part::FeaturePython", name)
        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        self.obj.addProperty("App::PropertyPlacement", "BasePlacement").BasePlacement = App.Placement(
            App.Vector(position),
            App.Rotation(rotation[0], rotation[1], rotation[2]),
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

    def addDrill(self, obj, recurse=False):
        """
        Adds obj to the drill list for self, and optionally passes to all parents
        """
        if not hasattr(self.obj, "DrilledBy"):
            self.obj.addProperty("App::PropertyLinkListHidden", "DrilledBy")
        self.obj.DrilledBy += [obj]

        if recurse and hasattr(self.obj, "RelativeTo"):
            self.obj.RelativeTo.Proxy.addDrill(obj, recurse=True)


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

    def getIcon(self):
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
