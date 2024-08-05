import Draft
import FreeCAD as App
import Mesh
import Part

from .origin import Origin


class Baseplate(Origin):
    """
    A class for defining new baseplates

    Args:
        dx, dy, dz (float): The footprint of the baseplate including the gaps
        x, y (float): The coordinates the baseplate (and all elements) should be placed at (in inches)
        gap (float): The amount of material to remove around the edge of the baseplate
        name (string): Name of the baseplate object
        drill (bool): Whether or not the baseplate should be drilled
        mount_holes (tuple[]): An array representing the x and y coordinates of each mount point (in inches)
        label (string): The label to be embossed into the side of the baseplate
        x_offset, y_offset (float): Additional offset from the grid in the x and y directions
        optics_dz (float): The optical height of baseplate
        invert_label (bool): Wheather to switch the face the label is embossed on
    """

    def __init__(
        self,
        name="Baseplate",
        position=(0, 0, 0),
        rotation=(0.0, 0.0, 0.0),
        lx=0.0,
        ly=0.0,
        lz=0.0,
        gap=0,
        drill=True,
        mount_holes=[],
        label="",
        x_offset=0,
        y_offset=0,
        # optics_dz=inch / 2,
        x_splits=[],
        y_splits=[],
        invert_label=False,
    ):
        super().__init__(name, position, rotation)

        self.obj.addProperty("App::PropertyLength", "lx").lx = lx
        self.obj.addProperty("App::PropertyLength", "ly").ly = ly
        self.obj.addProperty("App::PropertyLength", "lz").lz = lz
        self.obj.addProperty("App::PropertyLength", "Gap").Gap = gap
        self.obj.addProperty("App::PropertyLength", "AutosizeTol").AutosizeTol = 15
        self.obj.addProperty("App::PropertyBool", "Drill").Drill = drill
        self.obj.addProperty("App::PropertyString", "CutLabel").CutLabel = label
        self.obj.addProperty("App::PropertyDistance", "xOffset").xOffset = x_offset
        self.obj.addProperty("App::PropertyDistance", "yOffset").yOffset = y_offset
        # self.# obj.addProperty("App::PropertyDistance", "OpticsDz").OpticsDz = optics_dz
        self.obj.addProperty("App::PropertyFloatList", "xSplits").xSplits = x_splits
        self.obj.addProperty("App::PropertyFloatList", "ySplits").ySplits = y_splits
        self.obj.addProperty(
            "App::PropertyLength", "InvertLabel"
        ).InvertLabel = invert_label

    def execute(self, obj):
        part = Part.makeBox(obj.lx.Value, obj.ly.Value, obj.lz.Value)

        part.Placement = self.obj.Placement # drill objects are in absolute coordinates

        if hasattr(self.obj, "DrilledBy"):
            for i in self.obj.DrilledBy:
                part = part.cut(i.Proxy.getDrillObj())
                print(f"drilled by {i}")

        part.Placement = self.obj.Placement.inverse() * part.Placement # revert to relative coord

        obj.Shape = part.removeSplitter()


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
        if hasattr(self.Object, "Children"):
            return self.Object.Children
        else:
            return []

    def getIcon(self):
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
