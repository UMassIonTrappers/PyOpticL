import FreeCAD as App
import Mesh
import Part
import Draft
from . import laser, optomech
from pathlib import Path
import MeshPart
inch = 25.4

cardinal = {"right":0,
            "left":180,
            "up":90,
            "down":-90,
            "ne":45,
            "se": -45,
            "sw": -135,
            "nw": 135}
turn = {"up-right":-45,
        "right-up":135,
        "up-left":-135,
        "left-up":45,
        "down-right":45,
        "right-down":-135,
        "down-left":135,
        "left-down":-45}

def check_bound(obj1, obj2):
    bound1 = obj1.BoundBox
    bound2 = obj2.BoundBox
    if bound1.XMin < bound2.XMax and bound2.XMin < bound1.XMax:
        if bound1.YMin < bound2.YMax and bound2.YMin < bound1.YMax:
            if bound1.ZMin < bound2.ZMax and bound2.ZMin < bound1.ZMax:
                return True
    return False

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
    def __init__(self, dx=0, dy=0, dz=inch, x=0, y=0, angle=0, gap=0, name="Baseplate", drill=True, mount_holes=[], label="", x_offset=0, y_offset=0, optics_dz=inch/2, x_splits=[], y_splits=[], invert_label=False, z=0):
        obj = App.ActiveDocument.addObject('Part::FeaturePython', name)
        ViewProvider(obj.ViewObject)
        obj.Proxy = self

        obj.addProperty('App::PropertyLength', 'dx').dx = dx #define and set baseplate dimentions
        obj.addProperty('App::PropertyLength', 'dy').dy = dy
        obj.addProperty('App::PropertyLength', 'dz').dz = dz
        obj.addProperty('App::PropertyLength', 'Gap').Gap = gap
        obj.addProperty('App::PropertyLength', 'AutosizeTol').AutosizeTol = 15
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyString', 'CutLabel').CutLabel = label
        obj.addProperty('App::PropertyDistance', 'xOffset').xOffset = x_offset
        obj.addProperty('App::PropertyDistance', 'yOffset').yOffset = y_offset
        obj.addProperty('App::PropertyDistance', 'OpticsDz').OpticsDz = optics_dz
        obj.addProperty('App::PropertyFloatList', 'xSplits').xSplits = x_splits
        obj.addProperty('App::PropertyFloatList', 'ySplits').ySplits = y_splits
        obj.addProperty('App::PropertyLength', 'InvertLabel').InvertLabel = invert_label

        obj.Placement = App.Placement(App.Vector(x*inch, y*inch, z*inch), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
        self.active_baseplate = obj.Name
        obj.addProperty("App::PropertyLinkListHidden","ChildObjects")
        for x, y in mount_holes:
            mount = self.place_element("Mount Hole (%d, %d)"%(x, y), optomech.baseplate_mount, (x+0.5)*inch, (y+0.5)*inch, 0)
            obj.ChildObjects += [mount]
    
    def add_cover(self, dz):
        obj = App.ActiveDocument.addObject('Part::FeaturePython', "Table Grid")
        baseplate = getattr(App.ActiveDocument, self.active_baseplate)
        obj.Placement = baseplate.Placement
        baseplate_cover(obj, baseplate, dz=dz)


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
            obj.Proxy.transmission = True
            if hasattr(obj, "ChildObjects"):
                for child in obj.ChildObjects:
                    child.Proxy.transmission = True
        return obj
    
    # def change_chirality(self,input_y, obj_list, Command = "up_down"):
    #         '''
    #         change the chirality of the baseplate
    #         '''
    #         if Command == "up_down":
    #             # y >>> 2Y - y
    #             # layout.turn['up-right'] >>> -layout.turn['up-right']
    #             # layout.turn['right-up'] >>> -layout.turn['right-up']
                
    #             for i in obj_list:
    #                 # i.length =  2 * input_y - i.length
    #                 i
                    
    #             return self
    #         if Command == "right_left":
    #             # x >>> 2X - x

    #             return self


    def place_element_general(self, name, obj_class, x, y, z, angle_x, angle_y, angle_z, optional=False, **args):
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
        obj.BasePlacement = App.Placement(App.Vector(x, y, z), App.Rotation(angle_x, angle_y, angle_z), App.Vector(0, 0, 0))

        if optional:
            obj.Proxy.transmission = True
            if hasattr(obj, "ChildObjects"):
                for child in obj.ChildObjects:
                    child.Proxy.transmission = True
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
            obj.Proxy.transmission = True
            if hasattr(obj, "ChildObjects"):
                for child in obj.ChildObjects:
                    child.Proxy.transmission = True
        return obj

    def place_element_relative(self, name, obj_class, rel_obj, angle, x_off=0, y_off=0, z_off=0, optional=False, grid_comp=False, **args):
        '''
        Place an element relative to another object

        Args:
            name (string): Label for the object
            obj_class (class): The object class associated with the part to be placed
            rel_obj (obj): The parent object which this object will be relative to
            angle (float): The rotation of the object about the z axis
            x_off, y_off (float): The offset between the parent object and this object
            optional (bool): If this is true the object will also transmit beams
            grid_comp (bool): If this object is part of a grid setup
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
        obj.RelativePlacement.Base = App.Vector(x_off, y_off, z_off)
        # rel_pos = rel_obj.BasePlacement.Base
        # print(rel_pos)
        # print(rel_obj.BasePlacement)
        # print(rel_obj)
        # obj.BasePlacement = App.Placement(App.Vector(x_off, y_off, z_off) + rel_pos, App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
        obj.addProperty("App::PropertyLinkHidden","RelativeParent").RelativeParent = rel_obj
        if not hasattr(rel_obj, "RelativeObjects"):
            rel_obj.addProperty("App::PropertyLinkListChild","RelativeObjects")
        rel_obj.RelativeObjects += [obj]

        if optional:
            obj.Proxy.transmission = True
            if hasattr(obj, "ChildObjects"):
                for child in obj.ChildObjects:
                    child.Proxy.transmission = True

        if grid_comp:
            obj.addProperty("App::PropertyBool", "GridComponent")
            obj.GridComponent = True
        return obj

    def add_beam_path(self, x, y, angle, name="Beam Path", color=(1.0, 0.0, 0.0),z = 0, **args):
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
        laser.beam_path(obj, **args)

        obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate = getattr(App.ActiveDocument, self.active_baseplate) 
        obj.addProperty("App::PropertyPlacement","BasePlacement")
        obj.BasePlacement = App.Placement(App.Vector(x, y, z), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
        obj.addProperty("App::PropertyLinkListHidden","PathObjects").PathObjects
        obj.ViewObject.ShapeColor = color
        return obj
    
    def execute(self, obj):
        if obj.dx == 0 and obj.dy == 0:
            for i in App.ActiveDocument.Objects:
                if hasattr(i, "Baseplate") and i.Baseplate == obj:
                    if hasattr(i, "Shape"):
                        obj_body = i.Shape.copy()
                    elif hasattr(i, "Mesh"):
                        obj_body = i.Mesh.copy()
                    else:
                        obj_body = i
                    if hasattr(obj_body, "BoundBox") and hasattr(i, "BasePlacement"):
                        obj_body.Placement = i.BasePlacement
                        bound = obj_body.BoundBox
                        obj.xOffset = min(obj.xOffset.Value, bound.XMin-obj.AutosizeTol.Value)
                        obj.yOffset = min(obj.yOffset.Value, bound.YMin-obj.AutosizeTol.Value)
                        obj.dx = max(obj.dx.Value, bound.XMax+obj.AutosizeTol.Value-obj.xOffset.Value)
                        obj.dy = max(obj.dy.Value, bound.YMax+obj.AutosizeTol.Value-obj.yOffset.Value)
                        print(i.Name, obj.dy)

        if obj.dx == 0 and obj.dy == 0:
            return
        
        part = Part.makeBox(obj.dx.Value-2*obj.Gap.Value, obj.dy.Value-2*obj.Gap.Value, obj.dz.Value,
                            App.Vector(obj.Gap.Value+obj.xOffset.Value, obj.Gap.Value+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value))

        if len(obj.xSplits) > 0:
            for i in obj.xSplits:
                part = part.cut(Part.makeBox(2*obj.Gap.Value, obj.dy.Value-2*obj.Gap.Value, obj.dz.Value, 
                                            App.Vector(i-obj.Gap.Value+obj.xOffset.Value, obj.Gap.Value+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value)))
        if len(obj.ySplits) > 0:
            for i in obj.ySplits:
                part = part.cut(Part.makeBox(obj.dx.Value-2*obj.Gap.Value, 2*obj.Gap.Value, obj.dz.Value, 
                                            App.Vector(obj.Gap.Value+obj.xOffset.Value, i-obj.Gap.Value+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value)))
        if obj.Drill:
            for i in App.ActiveDocument.Objects:
                if hasattr(i, 'DrillPart'):
                    if i.Drill and i.Baseplate == obj:
                        drill = i.DrillPart.copy()
                        drill.Placement = obj.Placement.inverse()*drill.Placement
                        part = part.cut(drill)
        if obj.CutLabel != "":
            face = Draft.make_shapestring(obj.CutLabel, str(Path(__file__).parent.resolve()) + "/font/OpenSans-Regular.ttf", 5)
            if obj.InvertLabel:
                face.Placement.Base = App.Vector(obj.Gap.Value+obj.xOffset.Value, obj.dy.Value+obj.yOffset.Value-obj.Gap.Value-2, -obj.OpticsDz.Value-6)
                face.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), -90)*App.Rotation(App.Vector(1, 0, 0), 90)
                text = face.Shape.extrude(App.Vector(0.5, 0, 0))
            else:
                face.Placement.Base = App.Vector(obj.Gap.Value+obj.xOffset.Value+2, obj.Gap.Value+obj.yOffset.Value, -obj.OpticsDz.Value-6)
                face.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
                text = face.Shape.extrude(App.Vector(0, 0.5, 0))
            part = part.cut(text)
            App.ActiveDocument.removeObject(face.Label)
        obj.Shape = part.removeSplitter()

    def add_beam_path_general(self, x, y, z, angle_x, angle_y, angle_z, name="Beam Path", color=(1.0, 0.0, 0.0)):
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
        obj.BasePlacement = App.Placement(App.Vector(x, y, z), App.Rotation(angle_x, angle_y, angle_z), App.Vector(0, 0, 0))
        obj.addProperty("App::PropertyLinkListHidden","PathObjects").PathObjects
        obj.ViewObject.ShapeColor = color
        return obj
    
    def execute(self, obj):
        if obj.dx == 0 and obj.dy == 0:
            for i in App.ActiveDocument.Objects:
                if hasattr(i, "Baseplate") and i.Baseplate == obj:
                    if hasattr(i, "Shape"):
                        obj_body = i.Shape.copy()
                    elif hasattr(i, "Mesh"):
                        obj_body = i.Mesh.copy()
                    else:
                        obj_body = i
                    if hasattr(obj_body, "BoundBox") and hasattr(i, "BasePlacement"):
                        obj_body.Placement = i.BasePlacement
                        bound = obj_body.BoundBox
                        obj.xOffset = min(obj.xOffset.Value, bound.XMin-obj.AutosizeTol.Value)
                        obj.yOffset = min(obj.yOffset.Value, bound.YMin-obj.AutosizeTol.Value)
                        obj.dx = max(obj.dx.Value, bound.XMax+obj.AutosizeTol.Value-obj.xOffset.Value)
                        obj.dy = max(obj.dy.Value, bound.YMax+obj.AutosizeTol.Value-obj.yOffset.Value)
                        print(i.Name, obj.dy)

        if obj.dx == 0 and obj.dy == 0:
            return
        
        part = Part.makeBox(obj.dx.Value-2*obj.Gap.Value, obj.dy.Value-2*obj.Gap.Value, obj.dz.Value,
                            App.Vector(obj.Gap.Value+obj.xOffset.Value, obj.Gap.Value+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value))

        if len(obj.xSplits) > 0:
            for i in obj.xSplits:
                part = part.cut(Part.makeBox(2*obj.Gap.Value, obj.dy.Value-2*obj.Gap.Value, obj.dz.Value, 
                                            App.Vector(i-obj.Gap.Value+obj.xOffset.Value, obj.Gap.Value+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value)))
        if len(obj.ySplits) > 0:
            for i in obj.ySplits:
                part = part.cut(Part.makeBox(obj.dx.Value-2*obj.Gap.Value, 2*obj.Gap.Value, obj.dz.Value, 
                                            App.Vector(obj.Gap.Value+obj.xOffset.Value, i-obj.Gap.Value+obj.yOffset.Value, -obj.dz.Value-obj.OpticsDz.Value)))
        if obj.Drill:
            for i in App.ActiveDocument.Objects:
                if hasattr(i, 'DrillPart'):
                    if i.Drill and i.Baseplate == obj:
                        drill = i.DrillPart.copy()
                        drill.Placement = obj.Placement.inverse()*drill.Placement
                        part = part.cut(drill)
        if obj.CutLabel != "":
            face = Draft.make_shapestring(obj.CutLabel, str(Path(__file__).parent.resolve()) + "/font/OpenSans-Regular.ttf", 5)
            if obj.InvertLabel:
                face.Placement.Base = App.Vector(obj.Gap.Value+obj.xOffset.Value, obj.dy.Value+obj.yOffset.Value-obj.Gap.Value-2, -obj.OpticsDz.Value-6)
                face.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), -90)*App.Rotation(App.Vector(1, 0, 0), 90)
                text = face.Shape.extrude(App.Vector(0.5, 0, 0))
            else:
                face.Placement.Base = App.Vector(obj.Gap.Value+obj.xOffset.Value+2, obj.Gap.Value+obj.yOffset.Value, -obj.OpticsDz.Value-6)
                face.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
                text = face.Shape.extrude(App.Vector(0, 0.5, 0))
            part = part.cut(text)
            App.ActiveDocument.removeObject(face.Label)
        obj.Shape = part.removeSplitter()

def place_element_on_table(name, obj_class, x, y, angle, z=0, **args):
        '''
        Place an element at a fixed coordinate on the baseplate

        Args:
            name (string): Label for the object
            obj_class (class): The object class associated with the part to be placed
            x, y, z (float): The coordinates the object should be placed at in inches
            angle (float): The rotation of the object about the z axis
            optional (bool): If this is true the object will also transmit beams
            args (any): Additional args to be passed to the object (see object class docs)
        '''
        obj = App.ActiveDocument.addObject(obj_class.type, name)
        obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate = None
        obj.Label = name
        obj_class(obj, **args)
        
        obj.addProperty("App::PropertyPlacement","BasePlacement")
        obj.BasePlacement = App.Placement(App.Vector(x*inch, y*inch, z*inch), App.Rotation(angle, 0, 0), App.Vector(0, 0, 0))
        return obj
    
# zhenyu editing for general rotation.
# just a small change
def place_element_on_table_general(name, obj_class, x, y, z=0,angle_x = 0, angle_y = 0, angle_z = 0,  **args):
        '''
        Place an element at a fixed coordinate on the baseplate

        Args:
            name (string): Label for the object
            obj_class (class): The object class associated with the part to be placed
            x, y, z (float): The coordinates the object should be placed at in inches
            angle (float): The rotation of the object about the z axis
            optional (bool): If this is true the object will also transmit beams
            args (any): Additional args to be passed to the object (see object class docs)
        '''
        obj = App.ActiveDocument.addObject(obj_class.type, name)
        obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate = None
        obj.Label = name
        obj_class(obj, **args)
        
        obj.addProperty("App::PropertyPlacement","BasePlacement")
        obj.BasePlacement = App.Placement(App.Vector(x*inch, y*inch, z*inch), App.Rotation(angle_x, angle_y, angle_z), App.Vector(0, 0, 0))
        return obj

class baseplate_cover:
    '''
    Add an optical table mounting grid

    Args:
        dx, yy (float): The dimentions of the table grid (in inches)
        z_off (float): The z offset of the top of the grid surface
    '''
    def __init__(self, obj, baseplate, dz, wall_thickness=10, beam_tol=10, drill=True):
        ViewProvider(obj.ViewObject)
        obj.Proxy = self

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate =  baseplate
        obj.addProperty('App::PropertyLength', 'dz').dz = dz
        obj.addProperty('App::PropertyLength', 'WallThickness').WallThickness = wall_thickness
        obj.addProperty('App::PropertyLength', 'BeamTol').BeamTol = beam_tol
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        self.slots = []

    def execute(self, obj):
        baseplate = obj.Baseplate


        part = Part.makeBox(baseplate.dx.Value-2*baseplate.Gap.Value, baseplate.dy.Value-2*baseplate.Gap.Value, obj.dz.Value,
                            App.Vector(baseplate.Gap.Value+baseplate.xOffset.Value, baseplate.Gap.Value+baseplate.yOffset.Value, -baseplate.OpticsDz.Value))
        part = part.fuse(Part.makeBox(baseplate.dx.Value-2*baseplate.Gap.Value-obj.WallThickness.Value-1, baseplate.dy.Value-2*baseplate.Gap.Value-obj.WallThickness.Value-1, 1,
                            App.Vector(baseplate.Gap.Value+baseplate.xOffset.Value+obj.WallThickness.Value/2+0.5, baseplate.Gap.Value+baseplate.yOffset.Value+obj.WallThickness.Value/2+0.5, -baseplate.OpticsDz.Value-1)))
        part = part.cut(Part.makeBox(baseplate.dx.Value-2*baseplate.Gap.Value-2*obj.WallThickness.Value+1, baseplate.dy.Value-2*baseplate.Gap.Value-2*obj.WallThickness.Value+1, obj.dz.Value-obj.WallThickness.Value+1,
                            App.Vector(baseplate.Gap.Value+baseplate.xOffset.Value+obj.WallThickness.Value-0.5, baseplate.Gap.Value+baseplate.yOffset.Value+obj.WallThickness.Value-0.5, -baseplate.OpticsDz.Value-1)))
        
        temp = Part.makeBox(baseplate.dx.Value-2*baseplate.Gap.Value-obj.WallThickness.Value, baseplate.dy.Value-2*baseplate.Gap.Value-obj.WallThickness.Value, 1.5,
                            App.Vector(baseplate.Gap.Value+baseplate.xOffset.Value+obj.WallThickness.Value/2, baseplate.Gap.Value+baseplate.yOffset.Value+obj.WallThickness.Value/2, -baseplate.OpticsDz.Value-1.5))
        temp = temp.cut(Part.makeBox(baseplate.dx.Value-2*baseplate.Gap.Value-2*obj.WallThickness.Value, baseplate.dy.Value-2*baseplate.Gap.Value-2*obj.WallThickness.Value, 1.5,
                            App.Vector(baseplate.Gap.Value+baseplate.xOffset.Value+obj.WallThickness.Value, baseplate.Gap.Value+baseplate.yOffset.Value+obj.WallThickness.Value, -baseplate.OpticsDz.Value-1.5)))
        
        temp.Placement = obj.Placement
        obj.DrillPart = temp

        if obj.Drill:
            for i in App.ActiveDocument.Objects:
                if isinstance(i.Proxy, laser.beam_path) and i.Baseplate == baseplate:
                    exploded = i.Shape.Solids
                    for shape in exploded:
                        drill = optomech._bounding_box(shape, obj.BeamTol.Value, 10, z_tol=True, plate_off=-1)
                        drill.Placement = i.Placement
                        part = part.cut(drill)
        obj.Shape = part


        if baseplate.CutLabel != "":
            face = Draft.make_shapestring(baseplate.CutLabel, str(Path(__file__).parent.resolve()) + "/font/OpenSans-Regular.ttf", 1)
            if baseplate.InvertLabel:
                face.Placement.Base = App.Vector(baseplate.Gap.Value, baseplate.dy.Value-baseplate.Gap.Value-2, -baseplate.OpticsDz.Value-6)
                face.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), -90)*App.Rotation(App.Vector(1, 0, 0), 90)
                text = face.Shape.extrude(App.Vector(0.5, 0, 0))
            else:
                face.Placement.Base = App.Vector(baseplate.Gap.Value+2, baseplate.Gap.Value, -baseplate.OpticsDz.Value-6)
                face.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
                text = face.Shape.extrude(App.Vector(0, 0.5, 0))
            part = part.cut(text)
            App.ActiveDocument.removeObject(face.Label)
        obj.Shape = part.removeSplitter()


class table_grid:
    '''
    Add an optical table mounting grid

    Args:
        dx, yy (float): The dimentions of the table grid (in inches)
        z_off (float): The z offset of the top of the grid surface
    '''
    def __init__(self, dx, dy, z_off=-3/2*inch):
        obj = App.ActiveDocument.addObject('Part::FeaturePython', "Table Grid")
        self.holes = App.ActiveDocument.addObject("Part::Feature", "Holes")
        obj.addProperty("App::PropertyLinkListChild","ChildObjects").ChildObjects += [self.holes]
        ViewProvider(obj.ViewObject)
        obj.Proxy = self
        self.dx = dx
        self.dy = dy
        self.z_off = z_off

        obj.ViewObject.ShapeColor = (0.9, 0.9, 0.9)

    def execute(self, obj):
        part = Part.makeBox(self.dx*inch, self.dy*inch, inch/4, App.Vector(0, 0, self.z_off-inch/4))
        holes = []
        for x in range(self.dx):
            for y in range(self.dy):
                for z in [self.z_off+1e-2, self.z_off-inch/4-1e-2]:
                    holes.append(Part.Circle(App.Vector((x+0.5)*inch, (y+0.5)*inch, z), App.Vector(0, 0, 1), inch/10))
        temp = Part.makeCompound(holes)
        self.holes.Shape = temp
        obj.Shape = part

# this is zhenyu editing
class table_no_grid:
    '''
    Add an optical table without mounting grid

    Args:
        dx, yy (float): The dimentions of the table grid (in inches)
        z_off (float): The z offset of the top of the grid surface
    '''
    def __init__(self, dx, dy, z_off=-3/2*inch):
        obj = App.ActiveDocument.addObject('Part::FeaturePython', "Table Grid")
        self.holes = App.ActiveDocument.addObject("Part::Feature", "Holes")
        obj.addProperty("App::PropertyLinkListChild","ChildObjects").ChildObjects += [self.holes]
        ViewProvider(obj.ViewObject)
        obj.Proxy = self
        self.dx = dx
        self.dy = dy
        self.z_off = z_off

        obj.ViewObject.ShapeColor = (0.9, 0.9, 0.9)

    def execute(self, obj):
        part = Part.makeBox(self.dx*inch, self.dy*inch, inch/4, App.Vector(0, 0, self.z_off-inch/4))
        # holes = []
        # for x in range(self.dx):
        #     for y in range(self.dy):
        #         for z in [self.z_off+1e-2, self.z_off-inch/4-1e-2]:
        #             holes.append(Part.Circle(App.Vector((x+0.5)*inch, (y+0.5)*inch, z), App.Vector(0, 0, 1), inch/10))
        # temp = Part.makeCompound(holes)
        # self.holes.Shape = temp
        obj.Shape = part
            
# Update function for dynamic elements
def redraw():
    for class_type in [laser.beam_path, baseplate, baseplate_cover, baseplate]:
        for i in App.ActiveDocument.Objects:
            if hasattr(i, "Proxy") and isinstance(i.Proxy, class_type):
                i.touch()
        App.ActiveDocument.recompute()

def show_components(state):
    for i in App.ActiveDocument.Objects:
        if hasattr(i, "Proxy") and not isinstance(i.Proxy, baseplate):
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
            if hasattr(obj, "BasePlacement") and obj.Baseplate != None:
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
