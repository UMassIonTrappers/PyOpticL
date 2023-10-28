import FreeCAD as App
import Mesh
import Part
import Draft
from . import laser, optomech
from pathlib import Path

inch = 25.4

cardinal = {"right":0,
            "left":180,
            "up":90,
            "down":-90}
turn = {"up-right":-45,
        "right-up":135,
        "up-left":-135,
        "left-up":45,
        "down-right":45,
        "right-down":-135,
        "down-left":135,
        "left-down":-45}

class baseplate:
    '''
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
    '''
    def __init__(self, dx, dy, dz, x=0, y=0, angle=0, gap=0, name="Baseplate", drill=True, mount_holes=[], label="", x_offset=0, y_offset=0, optics_dz=inch/2, x_split=0, y_split=0, invert_label=False):
        obj = App.ActiveDocument.addObject('Part::FeaturePython', name)
        ViewProvider(obj.ViewObject)
        obj.Proxy = self

        obj.addProperty('App::PropertyLength', 'dx').dx = dx #define and set baseplate dimentions
        obj.addProperty('App::PropertyLength', 'dy').dy = dy
        obj.addProperty('App::PropertyLength', 'dz').dz = dz
        obj.addProperty('App::PropertyLength', 'Gap').Gap = gap
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyString', 'CutLabel').CutLabel = label
        obj.addProperty('App::PropertyLength', 'xOffset').xOffset = x_offset
        obj.addProperty('App::PropertyLength', 'yOffset').yOffset = y_offset
        obj.addProperty('App::PropertyLength', 'OpticsDz').OpticsDz = optics_dz
        obj.addProperty('App::PropertyLength', 'xSplit').xSplit = x_split
        obj.addProperty('App::PropertyLength', 'ySplit').ySplit = y_split
        obj.addProperty('App::PropertyLength', 'InvertLabel').InvertLabel = invert_label

        obj.Placement = App.Placement(App.Vector(x*inch, y*inch, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
        self.active_baseplate = obj.Name
        obj.addProperty("App::PropertyLinkListHidden","ChildObjects")
        for x, y in mount_holes:
            mount = self.place_element("Mount Hole (%d, %d)"%(x, y), optomech.baseplate_mount, (x+0.5)*inch, (y+0.5)*inch, 0)
            obj.ChildObjects += [mount]

    def place_element(self, name, obj_class, x, y, angle, optional=False, **args):
        '''
        Place an element at a fixed coordinate on the baseplate

        Args:
            name (string): Label for the object
            obj_class (class): The object class associated with the part to be placed
            x, y (float): The coordinates the object should be placed at
            angle (float): The rotation of the object about the z axis
            optional (bool): If this is true the object will also transmit beams
            args (any): Additional args to be passed to the object (see object class docs)
        '''
        obj = App.ActiveDocument.addObject(obj_class.type, name)
        obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate = getattr(App.ActiveDocument, self.active_baseplate)
        obj.Label = name
        obj_class(obj, **args)
        
        obj.addProperty("App::PropertyPlacement","BasePlacement")
        obj.BasePlacement = App.Placement(App.Vector(x, y, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))

        if optional:
            obj.Proxy.tran = True
            if hasattr(obj, "ChildObjects"):
                for child in obj.ChildObjects:
                    child.Proxy.tran = True
        return obj

    def place_element_along_beam(self, name, obj_class, beam_obj, beam_index, angle, distance=None, x=None, y=None, pre_refs=0, optional=False, **args):
        '''
        Place an element at along a given beam path

        Args:
            name (string): Label for the object
            obj_class (class): The object class associated with the part to be placed
            beam_obj (beam_path): The beam path object to be associated with this object
            beam_index (int): The beam index the object should be placed along (binary format recommended)
            angle (float): The rotation of the object about the z axis
            distance, x, y (float): The constraint of the placement, either a distance from the last object or a single coordinate value
            pre_refs (int): The number of interactions which must take place before this object can be placed along the beam
            optional (bool): If this is true the object will also transmit beams
            args (any): Additional args to be passed to the object (see object class docs)
        '''
        obj = App.ActiveDocument.addObject(obj_class.type, name)
        obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate = getattr(App.ActiveDocument, self.active_baseplate)
        obj.Label = name
        obj_class(obj, **args)
        beam_obj.PathObjects += [obj]
        
        obj.setEditorMode('Placement', 2)
        obj.addProperty("App::PropertyPlacement","BasePlacement")
        obj.addProperty("App::PropertyAngle","Angle").Angle = angle
        if distance != None:
            obj.addProperty("App::PropertyDistance","Distance").Distance = distance
        if x != None:
            obj.addProperty("App::PropertyDistance","xPos").xPos = x
        if y != None:
            obj.addProperty("App::PropertyDistance","yPos").yPos = y
        obj.addProperty("App::PropertyInteger","BeamIndex").BeamIndex = beam_index
        obj.addProperty("App::PropertyInteger","PreRefs").PreRefs = pre_refs

        if optional:
            obj.Proxy.tran = True
            if hasattr(obj, "ChildObjects"):
                for child in obj.ChildObjects:
                    child.Proxy.tran = True
        return obj

    def place_element_relative(self, name, obj_class, rel_obj, angle, x_off=0, y_off=0, optional=False, **args):
        '''
        Place an element relative to another object

        Args:
            name (string): Label for the object
            obj_class (class): The object class associated with the part to be placed
            rel_obj (obj): The parent object which this object will be relative to
            angle (float): The rotation of the object about the z axis
            x_off, y_off (float): The offset between the parent object and this object
            optional (bool): If this is true the object will also transmit beams
            args (any): Additional args to be passed to the object (see object class docs)
        '''
        obj = App.ActiveDocument.addObject(obj_class.type, name)
        obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate = getattr(App.ActiveDocument, self.active_baseplate)
        obj.Label = name
        obj_class(obj, **args)

        obj.setEditorMode('Placement', 2)
        obj.addProperty("App::PropertyPlacement","BasePlacement")
        obj.addProperty("App::PropertyAngle","Angle").Angle = angle
        obj.addProperty("App::PropertyPlacement","RelativePlacement").RelativePlacement
        obj.RelativePlacement.Base = App.Vector(x_off, y_off, 0)
        obj.addProperty("App::PropertyLinkHidden","ParentObject").ParentObject = rel_obj
        if not hasattr(obj, "RelativeObjects"):
            rel_obj.addProperty("App::PropertyLinkListChild","RelativeObjects")
        rel_obj.RelativeObjects += [obj]

        if optional:
            obj.Proxy.tran = True
            if hasattr(obj, "ChildObjects"):
                for child in obj.ChildObjects:
                    child.Proxy.tran = True
        return obj

    def add_beam_path(self, x, y, angle, name="Beam Path", color=(1.0, 0.0, 0.0)):
        '''
        Add a new dynamic beam path

        Args:
            x, y (float): The coordinate the beam should enter at
            angle (float): The angle the beam should enter at
            name (string): Label for the beam path object
            color (float[3]): Color of the beam path object in RGB format
        '''
        obj = App.ActiveDocument.addObject('Part::FeaturePython', name)
        obj.Label = name
        laser.ViewProvider(obj.ViewObject)
        laser.beam_path(obj)

        obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate = getattr(App.ActiveDocument, self.active_baseplate) 
        obj.addProperty("App::PropertyPlacement","BasePlacement")
        obj.BasePlacement = App.Placement(App.Vector(x, y, 0), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
        obj.addProperty("App::PropertyLinkListHidden","PathObjects").PathObjects
        obj.ViewObject.ShapeColor = color
        return obj
    
    def execute(self, obj):
        part = Part.makeBox(obj.dx.Value-2*obj.Gap.Value, obj.dy.Value-2*obj.Gap.Value, obj.dz.Value,
                            App.Vector(obj.Gap.Value+obj.xOffset.Value, obj.Gap.Value+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value))
        if obj.xSplit > 0:
            part = part.cut(Part.makeBox(obj.Gap.Value, obj.dy.Value-2*obj.Gap.Value, obj.dz.Value, 
                                         App.Vector(obj.xSplit.Value-obj.Gap.Value/2+obj.xOffset.Value, obj.Gap.Value+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value)))
        if obj.ySplit > 0:
            part = part.cut(Part.makeBox(obj.dx.Value-2*obj.Gap.Value, obj.Gap.Value, obj.dz.Value, 
                                         App.Vector(obj.Gap.Value+obj.xOffset.Value, obj.ySplit.Value-obj.Gap.Value/2+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value)))
        if obj.Drill:
            for i in App.ActiveDocument.Objects:
                if hasattr(i.Proxy, 'get_drill'):
                    if i.Drill and i.Baseplate == obj:
                        temp = i.Proxy.get_drill(i)
                        temp.Placement = i.BasePlacement
                        part = part.cut(temp)
        if obj.CutLabel != "":
            face = Draft.make_shapestring(obj.CutLabel, str(Path(__file__).parent.resolve()) + "/font/OpenSans-Regular.ttf", 5)
            if obj.InvertLabel:
                face.Placement.Base = App.Vector(obj.Gap.Value, obj.dy.Value-obj.Gap.Value-2, -obj.OpticsDz.Value-6)
                face.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), -90)*App.Rotation(App.Vector(1, 0, 0), 90)
                text = face.Shape.extrude(App.Vector(0.5, 0, 0))
            else:
                face.Placement.Base = App.Vector(obj.Gap.Value+2, obj.Gap.Value, -obj.OpticsDz.Value-6)
                face.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
                text = face.Shape.extrude(App.Vector(0, 0.5, 0))
            part = part.cut(text)
            App.ActiveDocument.removeObject(face.Label)
        obj.Shape = part


class table_grid:
    '''
    Add an optical table mounting grid

    Args:
        dx, yy (float): The dimentions of the table grid (in inches)
        z_off (float): The z offset of the top of the grid surface
    '''
    def __init__(self, dx, dy, z_off=-3/2*inch):
        obj = App.ActiveDocument.addObject('Part::FeaturePython', "Table Grid")
        ViewProvider(obj.ViewObject)
        obj.Proxy = self
        self.dx = dx
        self.dy = dy
        self.z_off = z_off

        obj.ViewObject.ShapeColor = (0.9, 0.9, 0.9)

    def execute(self, obj):
        part = Part.makeBox(self.dx*inch, self.dy*inch, inch/4, App.Vector(0, 0, self.z_off-inch/4))
        for x in range(self.dx):
            for y in range(self.dy):
                part = part.cut(Part.makeCylinder(inch/10, inch/4, App.Vector((x+0.5)*inch, (y+0.5)*inch, self.z_off), App.Vector(0, 0, -1)))
        obj.Shape = part
    
            
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
            if hasattr(obj, "BasePlacement"):
                obj.Placement.Base = obj.BasePlacement.Base + obj.Baseplate.Placement.Base
                obj.Placement = App.Placement(obj.Placement.Base, obj.Baseplate.Placement.Rotation, -obj.BasePlacement.Base)
                obj.Placement.Rotation = obj.Placement.Rotation.multiply(obj.BasePlacement.Rotation)

    def onDelete(self, feature, subelements):
        # delete all elements when baseplate is deleted
        for i in App.ActiveDocument.Objects:
            if i != feature.Object:
                App.ActiveDocument.removeObject(i.Name)
        return True
    
    def claimChildren(self):
        if hasattr(self.Object, "ChildObjects"):
            return self.Object.ChildObjects
        else:
            return []

    def getIcon(self):
        return 

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
