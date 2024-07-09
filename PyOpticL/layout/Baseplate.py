import Draft
import FreeCAD as App
import Mesh
import Part


class Baseplate:
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
        x=0,
        y=0,
        z=0,
        angle_z=0,
        angle_y=0,
        angle_x=0,
        lx=0,
        ly=0,
        lz=0,
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
        self.obj = App.ActiveDocument.addObject("Part::FeaturePython", name, self)
        ViewProvider(self.obj.ViewObject)

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
        self.obj.addProperty("App::PropertyLength", "InvertLabel").InvertLabel = (
            invert_label
        )

        self.obj.Placement = App.Placement(
            App.Vector(x, y, z),
            App.Rotation(angle_z, angle_y, angle_x),
            App.Vector(0, 0, 0),
        )

    def place(self, obj):
        """Place an object in the group's relative coord system"""

        if not hasattr(self.obj, "Children"):
            self.obj.addProperty("App::PropertyLinkList", "Children")

        self.obj.Children += [obj.obj]
        obj.obj.addProperty("App::PropertyLink", "RelativeTo").RelativeTo = self.obj

        return obj

    def execute(self, obj):
        part = Part.makeBox(obj.lx.Value, obj.ly.Value, obj.lz.Value)

        obj.Shape = part.removeSplitter()

    def calculate(self, depth=0):
        """Recursively apply relative transforms to all children"""

        if depth > 250:  # recursion depth check
            return
        if hasattr(self.obj, "Children"):
            for i in self.obj.Children:
                i.Placement = self.obj.Placement * i.Placement
                i.Proxy.calculate(depth + 1)


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
