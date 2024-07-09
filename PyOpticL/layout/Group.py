import Draft
import FreeCAD as App
import Mesh
import Part


class Group:
    """
    A class for grouping objects on a common coordinate system

    Args:
    name (string)
    x, y, z (float): Coordinates of the group's origin
    angle_x, angle_y, angle_z (float): Rotation of the group's coordinate system
    parent: Parent object to make placements relative to

    """

    def __init__(
        self, name, x=0, y=0, z=0, angle_z=0, angle_y=0, angle_x=0, parent=None
    ) -> None:
        self.obj = App.ActiveDocument.addObject("App::FeaturePython", name, self)

        self.obj.Placement = App.Placement(
            App.Vector(x, y, z),
            App.Rotation(angle_z, angle_y, angle_x),
            App.Vector(0, 0, 0),
        )
        self.obj.addProperty("App::PropertyLinkList", "Children")

        if parent != None:
            self.obj.addProperty("App::PropertyLink", "Parent").Parent = parent

    def place(self, obj):
        obj.obj.Parent = self.obj
        self.obj.Children += [obj]

    def execute(self, obj):
        if hasattr(obj, "Children"):
            for i in self.obj.Children:
                i.obj.Placement = self.obj.Placement * i.obj.Placement


class ViewProvider:

    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        return

    def getDefaultDisplayMode(self):
        return "Shaded"

    def updateData(self, base_obj, prop):
        for obj in App.ActiveDocument.Objects:
            if hasattr(obj, "BasePlacement") and obj.Baseplate != None:
                obj.Placement.Base = (
                    obj.BasePlacement.Base + obj.Baseplate.Placement.Base
                )
                obj.Placement = App.Placement(
                    obj.Placement.Base,
                    obj.Baseplate.Placement.Rotation,
                    -obj.BasePlacement.Base,
                )
                obj.Placement.Rotation = obj.Placement.Rotation.multiply(
                    obj.BasePlacement.Rotation
                )

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
