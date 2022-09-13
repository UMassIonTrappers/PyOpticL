import FreeCAD as App
import Part
from optics import laser

INCH = 25.4

def place_element(obj_name, draw_class, x, y, angle):
    obj = App.ActiveDocument.addObject('Mesh::FeaturePython', obj_name)
    draw_class(obj)
    obj.Placement = App.Placement(App.Vector(x, y, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
    obj.Proxy.ViewProvider(obj.ViewObject)
    App.ActiveDocument.recompute()
    return obj

def place_element_pos(obj_name, draw_class, pos, angle):
    x = pos[0]
    y = pos[1]
    obj = App.ActiveDocument.addObject('Mesh::FeaturePython', obj_name)
    draw_class(obj)
    obj.Placement = App.Placement(App.Vector(x, y, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
    obj.Proxy.ViewProvider(obj.ViewObject)
    App.ActiveDocument.recompute()
    return obj

def create_baseplate(dx, dy, dz):
    obj = App.ActiveDocument.addObject('Part::FeaturePython', "Baseplate")
    baseplate(obj, dx, dy, dz)
    ViewProvider(obj.ViewObject)
    App.ActiveDocument.recompute()
    return obj

def add_beam_path(x, y, angle):
    obj = App.ActiveDocument.addObject('Part::FeaturePython', "Beam_Path")
    laser.beam_path(obj, x, y, angle)
    laser.ViewProvider(obj.ViewObject)
    obj.ViewObject.ShapeColor=(1.0, 0.0, 0.0)
    App.ActiveDocument.recompute()
    return obj

def redraw():
    App.ActiveDocument.Baseplate.touch()
    App.ActiveDocument.Beam_Path.touch()

class baseplate:

    def __init__(self, obj, dx, dy, dz):

        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'dx').dx = dx
        obj.addProperty('App::PropertyLength', 'dy').dy = dy
        obj.addProperty('App::PropertyLength', 'dz').dz = dz

        self.Tags = ("baseplate")

    def execute(self, obj):
        part = Part.makeBox(obj.dx, obj.dy, obj.dz, App.Vector(0, 0, -(obj.dz.Value+INCH/2)))
        for i in App.ActiveDocument.Objects:
            element = i.Proxy
            if "drill" in element.Tags:
                part = part.cut(element.DrillPart)
        obj.Shape = part

class ViewProvider:

    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        return

    def updateData(self, fp, prop):
        return

    def getDisplayModes(self,obj):
        return []

    def getDefaultDisplayMode(self):
        return "Shaded"

    def setDisplayMode(self,mode):
        return mode

    def onDelete(self, feature, subelements):
        for i in App.ActiveDocument.Objects:
            if i != feature.Object:
                App.ActiveDocument.removeObject(i.Name)
        return True

    def onChanged(self, vp, prop):
        App.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def getIcon(self):
        return 

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None