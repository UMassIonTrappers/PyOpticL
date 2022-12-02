import FreeCAD as App
import Part
from . import laser

INCH = 25.4

# Add an element to the active baseplate with position and angle
# Draw class is the type of object, usually defined in another module
def place_element(obj_name, draw_class, x, y, angle):
    obj = App.ActiveDocument.addObject('Mesh::FeaturePython', obj_name)
    draw_class(obj)
    obj.Placement = App.Placement(App.Vector(x, y, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
    obj.Proxy.ViewProvider(obj.ViewObject)
    App.ActiveDocument.recompute()
    return obj

def place_element_along_beam(obj_name, draw_class, beam_obj, beam_index, distance, angle, pre_refs=0):
    obj = App.ActiveDocument.addObject('Mesh::FeaturePython', obj_name)
    draw_class(obj)
    obj.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
    obj.Proxy.ViewProvider(obj.ViewObject)
    while len(beam_obj.Proxy.components)-1 < beam_index:
        beam_obj.Proxy.components.append([])
    beam_obj.Proxy.components[beam_index].append((obj, distance, pre_refs))
    App.ActiveDocument.recompute()
    return obj

# Creates a new active baseplate
def create_baseplate(dx, dy, dz):
    obj = App.ActiveDocument.addObject('Part::FeaturePython', "Baseplate")
    baseplate(obj, dx, dy, dz)
    ViewProvider(obj.ViewObject)
    App.ActiveDocument.recompute()
    return obj

# Create a new dynamic beam path
def add_beam_path(x, y, angle):
    obj = App.ActiveDocument.addObject('Part::FeaturePython', "Beam_Path")
    laser.beam_path(obj, x, y, angle)
    laser.ViewProvider(obj.ViewObject)
    obj.ViewObject.ShapeColor=(1.0, 0.0, 0.0)
    App.ActiveDocument.recompute()
    return obj

# Update function for dynamicly updated elements
def redraw():
    App.ActiveDocument.Beam_Path.touch()
    App.ActiveDocument.recompute()
    App.ActiveDocument.Baseplate.touch()

class baseplate:

    def __init__(self, obj, dx, dy, dz):
        obj.Proxy = self

        obj.addProperty('App::PropertyLength', 'dx').dx = dx #define and set baseplate dimentions
        obj.addProperty('App::PropertyLength', 'dy').dy = dy
        obj.addProperty('App::PropertyLength', 'dz').dz = dz

        self.Tags = ("baseplate") #set tags for classification

    def execute(self, obj):
        part = Part.makeBox(obj.dx, obj.dy, obj.dz, App.Vector(0, 0, -(obj.dz.Value+INCH/2))) #recompute geometry on part update

        for i in App.ActiveDocument.Objects: #add drill holes for all necessary elements
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
        #App.Console.PrintMessage("Change property: " + str(prop) + "\n")
        pass

    def getIcon(self):
        return 

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None