import FreeCAD as App
import Mesh
import Part
import Draft
from . import laser

INCH = 25.4

# Add an element to the active baseplate with position and angle
# Obj class is the type of object, usually defined in another module
def place_element(obj_name, obj_class, x, y, angle, **args):
    obj = App.ActiveDocument.addObject(obj_class.type, obj_name)
    obj_class(obj, **args)
    obj.Placement = App.Placement(App.Vector(x, y, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
    return obj

# Add an element along a beampath with a set angle and an extra constraint of distance from last element, x position, or y position
# Obj class is the type of object, usually defined in another module
def place_element_along_beam(obj_name, obj_class, beam_obj, beam_index, angle, distance=None, x=None, y=None, pre_refs=0, **args):
    obj = App.ActiveDocument.addObject(obj_class.type, obj_name)
    obj_class(obj, **args)
    obj.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
    while len(beam_obj.Proxy.components) <= beam_index:
        beam_obj.Proxy.components.append([])
    beam_obj.Proxy.components[beam_index].append((obj, [distance, x, y], pre_refs))
    return obj

# Creates a new active baseplate
def create_baseplate(dx, dy, dz, drill=True, name="Baseplate", x=0, y=0, label=""):
    obj = App.ActiveDocument.addObject('Part::FeaturePython', name)
    baseplate(obj, dx, dy, dz, drill, label)
    obj.Placement = App.Placement(App.Vector(x, y, 0), App.Rotation(0, 0, 0), App.Vector(0, 0, 0))
    ViewProvider(obj.ViewObject)
    App.ActiveDocument.recompute()
    return obj

# Create a new dynamic beam path
def add_beam_path(x, y, angle):
    obj = App.ActiveDocument.addObject('Part::FeaturePython', "Beam_Path")
    laser.beam_path(obj)
    obj.Placement = App.Placement(App.Vector(x, y, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
    laser.ViewProvider(obj.ViewObject)
    obj.ViewObject.ShapeColor=(1.0, 0.0, 0.0)
    return obj

# Update function for dynamic elements
def redraw():
    for i in App.ActiveDocument.Objects:
        if isinstance(i.Proxy, laser.beam_path):
            i.touch()
    App.ActiveDocument.recompute()
    for i in App.ActiveDocument.Objects:
        if isinstance(i.Proxy, baseplate):
            i.touch()
    App.ActiveDocument.recompute()

def show_components(state):
    for i in App.ActiveDocument.Objects:
        if not isinstance(i.Proxy, baseplate):
            if state:
                i.ViewObject.show()
            else:
                i.ViewObject.hide()

class baseplate:

    def __init__(self, obj, dx, dy, dz, drill, label):
        obj.Proxy = self

        obj.addProperty('App::PropertyLength', 'dx').dx = dx #define and set baseplate dimentions
        obj.addProperty('App::PropertyLength', 'dy').dy = dy
        obj.addProperty('App::PropertyLength', 'dz').dz = dz
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyString', 'CutLabel').CutLabel = label


    def execute(self, obj):
        part = Part.makeBox(obj.dx, obj.dy, obj.dz, App.Vector(0, 0, -(obj.dz.Value+INCH/2)))
        if obj.Drill:
            for i in App.ActiveDocument.Objects: #add drill holes for all necessary elements
                if hasattr(i.Proxy, 'get_drill'):
                    if i.Drill:
                        temp = i.Proxy.get_drill(i)
                        temp.translate(App.Vector(-obj.Placement.Base))
                        part = part.cut(temp)
        if obj.CutLabel != "":
            face = Draft.make_shapestring(obj.CutLabel, "C:/Windows/Fonts/Arial.ttf", 4)
            face.Placement.Base = App.Vector(5, 0, -INCH-10)
            face.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
            text = face.Shape.extrude(App.Vector(0,0.5,0))
            part = part.cut(text)
            App.ActiveDocument.removeObject(face.Label)
        obj.Shape = part


class ViewProvider:

    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        return
    
    def getDefaultDisplayMode(self):
        return "Shaded"

    def onDelete(self, feature, subelements):
        # delete all elements when baseplate is deleted
        for i in App.ActiveDocument.Objects:
            if i != feature.Object:
                App.ActiveDocument.removeObject(i.Name)
        return True

    def getIcon(self):
        return 

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None