import FreeCAD as App
import Mesh
import Part
from math import *
from . import layout
import numpy as np

from pathlib import Path

stl_path = str(Path(__file__).parent.resolve()) + "/stl/"
drill_depth = 100
inch = 25.4

bolt_4_40 = {
    "clear_dia":0.120*inch,
    "tap_dia":0.089*inch,
    "head_dia":5.50,
    "head_dz":2.5 # TODO measure this
}

bolt_8_32 = {
    "clear_dia":0.172*inch,
    "tap_dia":0.136*inch,
    "head_dia":7,
    "head_dz":4.4
}

bolt_14_20 = {
    "clear_dia":0.260*inch,
    "tap_dia":0.201*inch,
    "head_dia":9.8,
    "head_dz":8,
    "washer_dia":9/16*inch
}

adapter_color = (0.6, 0.9, 0.6)
mount_color = (0.5, 0.5, 0.55)
glass_color = (0.5, 0.5, 0.8)
misc_color = (0.2, 0.2, 0.2)

# Used to tranform an STL such that it's placement matches the optical center
def _import_stl(stl_name, rotate, translate, scale=1):
    mesh = Mesh.read(stl_path+stl_name)
    mat = App.Matrix()
    mat.scale(App.Vector(scale, scale, scale))
    mesh.transform(mat)
    mesh.rotate(*np.deg2rad(rotate))
    mesh.translate(*translate)
    return mesh

def _bounding_box(obj, tol, fillet, x_tol=True, y_tol=True, z_tol=False, min_offset=(0, 0, 0), max_offset=(0, 0, 0), plate_off=0):
    if hasattr(obj, "Shape"):
        obj_body = obj.Shape.copy()
    elif hasattr(obj, "Mesh"):
        obj_body = obj.Mesh.copy()
    else:
        obj_body = obj
    obj_body.Placement = App.Placement()
    if hasattr(obj, "RelativePlacement"):
        obj_body.Placement = obj.RelativePlacement
        temp = obj
        while hasattr(temp, "ParentObject") and hasattr(temp.ParentObject, "RelativePlacement"):
            temp = temp.ParentObject
        #    obj_body.Placement *= temp.RelativePlacement
    global_bound = obj_body.BoundBox
    obj_body.Placement = App.Placement()
    bound = obj_body.BoundBox

    x_min, x_max = bound.XMin-tol*x_tol+min_offset[0], bound.XMax+tol*x_tol+max_offset[0]
    y_min, y_max = bound.YMin-tol*y_tol+min_offset[1], bound.YMax+tol*y_tol+max_offset[1]
    z_min = min(global_bound.ZMin-tol*z_tol+min_offset[2], -layout.inch/2+plate_off)-global_bound.ZMin+bound.ZMin
    z_max = max(global_bound.ZMax+tol*z_tol+max_offset[2], -layout.inch/2+plate_off)-global_bound.ZMax+bound.ZMax
    bound_part = _custom_box(dx=x_max-x_min, dy=y_max-y_min, dz=z_max-z_min,
                    x=x_min, y=y_min, z=z_min, dir=(1, 1, 1),
                    fillet=fillet, fillet_dir=(0, 0, 1))
    return bound_part

def _add_linked_object(obj, obj_name, obj_class, pos_offset=(0, 0, 0), rot_offset=(0, 0, 0), **args):
    new_obj = App.ActiveDocument.addObject(obj_class.type, obj_name)
    new_obj.addProperty("App::PropertyLinkHidden","Baseplate").Baseplate = obj.Baseplate
    new_obj.Label = obj_name
    obj_class(new_obj, **args)
    new_obj.setEditorMode('Placement', 2)
    new_obj.addProperty("App::PropertyPlacement","BasePlacement")
    if not hasattr(obj, "ChildObjects"):
        obj.addProperty("App::PropertyLinkListChild","ChildObjects")
    obj.ChildObjects += [new_obj]
    new_obj.addProperty("App::PropertyLinkHidden","ParentObject").ParentObject = obj
    new_obj.addProperty("App::PropertyPlacement","RelativePlacement").RelativePlacement
    rotx = App.Rotation(App.Vector(1,0,0), rot_offset[0])
    roty = App.Rotation(App.Vector(0,1,0), rot_offset[1])
    rotz = App.Rotation(App.Vector(0,0,1), rot_offset[2])
    new_obj.RelativePlacement.Rotation = App.Rotation(rotz*roty*rotx)
    new_obj.RelativePlacement.Base = App.Vector(*pos_offset)
    return new_obj

def _drill_part(part, obj, drill_obj):
    if hasattr(drill_obj, "DrillPart"):
        drill = drill_obj.DrillPart.copy()
        drill.Placement = obj.BasePlacement.inverse().multiply(drill.Placement)
        part = part.cut(drill)
    if hasattr(drill_obj, "ChildObjects"):
        for sub in drill_obj.ChildObjects:
            part = _drill_part(part, obj, sub)
    return part

def _custom_box(dx, dy, dz, x, y, z, fillet=0, dir=(0,0,1), fillet_dir=None):
    if fillet_dir == None:
        fillet_dir = np.abs(dir)
    part = Part.makeBox(dx, dy, dz)
    if fillet != 0:
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(*fillet_dir):
                part = part.makeFillet(fillet-1e-3, [i])
    part.translate(App.Vector(x-(1-dir[0])*dx/2, y-(1-dir[1])*dy/2, z-(1-dir[2])*dz/2))
    part = part.fuse(part)
    return part

def _fillet_all(part, fillet, dir=(0, 0, 1)):
    for i in part.Edges:
        if i.tangentAt(i.FirstParameter) == App.Vector(*dir):
            try:
                part = part.makeFillet(fillet-1e-3, [i])
            except:
                pass
    return part

def _custom_cylinder(dia, dz, x, y, z, head_dia=0, head_dz=0, dir=(0, 0, -1), countersink=False):
    part = Part.makeCylinder(dia/2, dz, App.Vector(0, 0, 0), App.Vector(*dir))
    if head_dia != 0 and head_dz != 0:
        if countersink:
            part = part.fuse(Part.makeCone(head_dia/2, dia/2, head_dz, App.Vector(0, 0, 0), App.Vector(*dir)))
        else:
            part = part.fuse(Part.makeCylinder(head_dia/2, head_dz, App.Vector(0, 0, 0), App.Vector(*dir)))
    part.translate(App.Vector(x, y, z))
    part = part.fuse(part)
    return part.removeSplitter()


class example_component:
    '''
    An example component class for reference on importing new components
    creates a simple cube which mounts using a single bolt

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        side_length (float) : The side length of the cube
    '''
    type = 'Part::FeaturePython' # if importing from stl, this will be 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, side_len=15):
        # required for all object classes
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        # define any user-accessible properties here
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Side_Length').Side_Length = side_len

        # additional parameters (ie color, constants, etc)
        obj.ViewObject.ShapeColor = adapter_color
        self.mount_bolt = bolt_8_32
        self.mount_dz = -obj.Baseplate.OpticsDz.Value

    # this defines the component body and drilling
    def execute(self, obj):
        part = _custom_box(dx=obj.Side_Length.Value, dy=obj.Side_Length.Value, dz=obj.Side_Length.Value,
                           x=0, y=0, z=self.mount_dz)
        part = part.cut(_custom_cylinder(dia=self.mount_bolt['clear_dia'], dz=obj.Side_Length.Value,
                                         head_dia=self.mount_bolt['head_dia'], head_dz=self.mount_bolt['head_dz'],
                                         x=0, y=0, z=obj.Side_Length.Value+self.mount_dz))
        obj.Shape = part

        # drilling part definition
        part = _custom_cylinder(dia=self.mount_bolt['tap_dia'], dz=drill_depth,
                                x=0, y=0, z=self.mount_dz)
        part.Placement = obj.Placement
        obj.DrillPart = part



class baseplate_mount:
    '''
    Mount holes for attaching to an optical table
    Uses 14_20 bolts with washers

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        bore_depth (float) : The depth for the counterbore of the mount hole
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, bore_depth=10, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'BoreDepth').BoreDepth = bore_depth
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color

    def execute(self, obj):
        bolt_len = inch-(obj.BoreDepth.Value-bolt_14_20['head_dz'])

        part = _custom_cylinder(dia=bolt_14_20['tap_dia'], dz=bolt_len,
                                head_dia=bolt_14_20['head_dia'], head_dz=bolt_14_20['head_dz'],
                                x=0, y=0, z=-(obj.Baseplate.OpticsDz.Value + obj.Baseplate.dz.Value)+bolt_len)
        obj.Shape = part

        part = _custom_cylinder(dia=bolt_14_20['clear_dia'], dz=drill_depth,
                                head_dia=bolt_14_20["washer_dia"], head_dz=obj.BoreDepth.Value,
                                x=0, y=0, z=-obj.Baseplate.OpticsDz.Value)
        part.Placement = obj.Placement
        obj.DrillPart = part

class pinhole_self_design:
    '''
    design a pinhole, 2mm in diameter. It have a similar function as iris. It can help the alignment

    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_hole_dy=20, adapter_height=8, outer_thickness=2):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)
        self.drill_tolerance = 1

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        dz = obj.AdapterHeight.Value
        z_translate = -10
        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=z_translate, dir=(0, 0, -1),
                           fillet=5)
        part = part.fuse(_custom_box(dx=5, dy=10, dz=20,
                           x=0, y=0, z=z_translate, dir=(0, 0, 1),
                           fillet=2))
        part = part.cut(_custom_cylinder(dia = 2, dz = 100, x=-10, y=0, z=0, dir=(1,0,0)))
        # part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
        #                                  head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
        #                                  x=0, y=0, z=z_translate-dz, dir=(0,0,1)))
        for i in [-1, 1]:
            part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz ,
                                             head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                             x=0, y=i*obj.MountHoleDistance.Value/2, z=0 + z_translate))
        obj.Shape = part
        
        part = _bounding_box(obj, self.drill_tolerance, 6)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=0 + z_translate))
        # part.translate(App.Vector(0,0,-30))
        part.Placement = obj.Placement
        obj.DrillPart = part

class surface_adapter:
    '''
    Surface adapter for post-mounted parts

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mount_hole_dy (float) : The spacing between the two mount holes of the adapter
        adapter_height (float) : The height of the suface adapter
        outer_thickness (float) : The thickness of the walls around the bolt holes
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_hole_dy=20, adapter_height=8, outer_thickness=2):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)
        self.drill_tolerance = 1

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        dz = obj.AdapterHeight.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=0, dir=(0, 0, -1),
                           fillet=5)
        part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                         head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                         x=0, y=0, z=-dz, dir=(0,0,1)))
        for i in [-1, 1]:
            part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                             head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                             x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        obj.Shape = part

        part = _bounding_box(obj, self.drill_tolerance, 6)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        part.Placement = obj.Placement
        obj.DrillPart = part

class surface_adapter_405:
    '''
    Surface adapter for post-mounted parts

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mount_hole_dy (float) : The spacing between the two mount holes of the adapter
        adapter_height (float) : The height of the suface adapter
        outer_thickness (float) : The thickness of the walls around the bolt holes
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_hole_dy=20, adapter_height=8, outer_thickness=2, slot=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)
        self.drill_tolerance = 1

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        dz = obj.AdapterHeight.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=0, dir=(0, 0, -1),
                           fillet=5)
        part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                         head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                         x=0, y=0, z=-dz, dir=(0,0,1)))
        for i in [-1, 1]:
            if obj.Slots:
                slot = 10
                dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2+slot
                part = part.cut(_custom_box(dx=bolt_8_32['head_dia'], dy=slot+bolt_8_32['head_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz,
                                            fillet=bolt_8_32['head_dia']/2, dir=(0,0,-1)))
                
                part = part.cut(_custom_box(dx=bolt_8_32['clear_dia'], dy=slot+bolt_8_32['clear_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz-bolt_8_32['head_dz'],
                                            fillet=bolt_8_32['clear_dia']/2, dir=(0,0,-1)))
            else:
                slot = 0
                dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
                part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                             head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                             x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        obj.Shape = part

        part = _bounding_box(obj, self.drill_tolerance, 6)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        part.Placement = obj.Placement
        obj.DrillPart = part

class skate_mount_crossholes:
    '''
    Skate mount for splitter cubes, add up one cross holes for other handedness

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        cube_dx, cube_dy (float) : The side length of the splitter cube
        mount_hole_dy (float) : The spacing between the two mount holes of the adapter
        cube_depth (float) : The depth of the recess for the cube
        outer_thickness (float) : The thickness of the walls around the bolt holes
        cube_tol (float) : The tolerance for size of the recess in the skate mount
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, cube_dx=10, cube_dy=10, cube_dz=10, mount_hole_dy=20, cube_depth=1, outer_thickness=2, cube_tol=0.1, slots=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'CubeDx').CubeDx = cube_dy
        obj.addProperty('App::PropertyLength', 'CubeDy').CubeDy = cube_dx
        obj.addProperty('App::PropertyLength', 'CubeDz').CubeDz = cube_dz
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'CubeDepth').CubeDepth = cube_depth+1e-3
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = cube_tol
        obj.addProperty('App::PropertyBool', 'Slots').Slots = slots
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def execute(self, obj):
        if obj.Slots:
            slot = 5
            dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2+slot
        else:
            slot = 0
            dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        raw_dz = obj.Baseplate.OpticsDz.Value-obj.CubeDz.Value/2+obj.CubeDepth.Value
        dz = max(raw_dz, 8)
        cut_dy = obj.CubeDx.Value+obj.CubeTolerance.Value
        cut_dx = obj.CubeDy.Value+obj.CubeTolerance.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=-obj.Baseplate.OpticsDz.Value, fillet=5)
        part = part.cut(_custom_box(dx=cut_dx, dy=cut_dy, dz=obj.CubeDepth.Value+1e-3,
                                    x=0, y=0, z=-obj.Baseplate.OpticsDz.Value+dz-obj.CubeDepth.Value-1e-3))
        
        for i in [-1, 1]:
            if obj.Slots:
                part = part.cut(_custom_box(dx=slot+bolt_8_32['head_dia'], dy=bolt_8_32['head_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz,
                                            fillet=bolt_8_32['head_dia']/2, dir=(0,0,-1)))
                part = part.cut(_custom_box(dx=slot+bolt_8_32['clear_dia'], dy=bolt_8_32['clear_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz-bolt_8_32['head_dz'],
                                            fillet=bolt_8_32['clear_dia']/2, dir=(0,0,-1)))
            else:
                part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                                head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                                x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz))
            
        part.translate(App.Vector(0, 0, obj.CubeDz.Value/2+(raw_dz-dz)))
        part = part.fuse(part)
        obj.Shape = part

        part = _bounding_box(obj, 1, 6,min_offset=(-slot, 0, 0), max_offset=(slot, 0, 0))
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+obj.CubeDz.Value/2))
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              y=0, x=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+obj.CubeDz.Value/2))
        part.Placement = obj.Placement
        obj.DrillPart = part

class skate_mount:
    '''
    Skate mount for splitter cubes

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        cube_dx, cube_dy (float) : The side length of the splitter cube
        mount_hole_dy (float) : The spacing between the two mount holes of the adapter
        cube_depth (float) : The depth of the recess for the cube
        outer_thickness (float) : The thickness of the walls around the bolt holes
        cube_tol (float) : The tolerance for size of the recess in the skate mount
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, cube_dx=10, cube_dy=10, cube_dz=10, mount_hole_dy=20, cube_depth=1, outer_thickness=2, cube_tol=0.1, slots=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'CubeDx').CubeDx = cube_dy
        obj.addProperty('App::PropertyLength', 'CubeDy').CubeDy = cube_dx
        obj.addProperty('App::PropertyLength', 'CubeDz').CubeDz = cube_dz
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'CubeDepth').CubeDepth = cube_depth+1e-3
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = cube_tol
        obj.addProperty('App::PropertyBool', 'Slots').Slots = slots
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def execute(self, obj):
        if obj.Slots:
            slot = 5
            dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2+slot
        else:
            slot = 0
            dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        raw_dz = obj.Baseplate.OpticsDz.Value-obj.CubeDz.Value/2+obj.CubeDepth.Value
        dz = max(raw_dz, 8)
        cut_dy = obj.CubeDx.Value+obj.CubeTolerance.Value
        cut_dx = obj.CubeDy.Value+obj.CubeTolerance.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=-obj.Baseplate.OpticsDz.Value, fillet=5)
        part = part.cut(_custom_box(dx=cut_dx, dy=cut_dy, dz=obj.CubeDepth.Value+1e-3,
                                    x=0, y=0, z=-obj.Baseplate.OpticsDz.Value+dz-obj.CubeDepth.Value-1e-3))
        
        for i in [-1, 1]:
            if obj.Slots:
                part = part.cut(_custom_box(dx=slot+bolt_8_32['head_dia'], dy=bolt_8_32['head_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz,
                                            fillet=bolt_8_32['head_dia']/2, dir=(0,0,-1)))
                part = part.cut(_custom_box(dx=slot+bolt_8_32['clear_dia'], dy=bolt_8_32['clear_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz-bolt_8_32['head_dz'],
                                            fillet=bolt_8_32['clear_dia']/2, dir=(0,0,-1)))
            else:
                part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                                head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                                x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz))
            
        part.translate(App.Vector(0, 0, obj.CubeDz.Value/2+(raw_dz-dz)))
        part = part.fuse(part)
        obj.Shape = part

        part = _bounding_box(obj, 1, 6,min_offset=(-slot, 0, 0), max_offset=(slot, 0, 0))
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+obj.CubeDz.Value/2))
        part.Placement = obj.Placement
        obj.DrillPart = part

class Prism_pair:
    '''
    this is prism pair for laser profile
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj,drill = True , mount_type=None, mount_args=dict(), deviate_angle = 16.81):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = ['Prism pair']
        self.transmission = True
        self.max_angle = 90
        self.max_width = 1 * inch
        # self.transmission = True
        # obj.addProperty('App::PropertyAngle', 'DiffractionAngle').DiffractionAngle = deviate_angle
        # obj.addProperty('App::PropertyInteger', 'ForwardDirection').ForwardDirection = forward_direction
        # obj.addProperty('App::PropertyInteger', 'BackwardDirection').BackwardDirection = backward_direction
        # self.deviate_angle = 16.81
        # self.diffraction_angle = diffraction_angle
        # self.diffraction_dir = (forward_direction, backward_direction)
        # self.transmission = True
        if mount_type != None:
           _add_linked_object(obj, "Mount", mount_type, pos_offset=(0, 0, -8), **mount_args)

    def execute(self, obj):
        mesh = _import_stl("Prism pair.stl", (180, 0, -110), (13,-7,0.8))
        mesh_ = _import_stl("Prism pair.stl", (0, 0, -276), (-3,1,-2))
        mesh.addMesh(mesh_)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh      
          
class prism_pair_mount:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, cube_dx=9, cube_dy=12, cube_dz=11, mount_hole_dy=20, cube_depth=1, outer_thickness=10, cube_tol=0.1, slots=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'CubeDx').CubeDx = cube_dy
        obj.addProperty('App::PropertyLength', 'CubeDy').CubeDy = cube_dx
        obj.addProperty('App::PropertyLength', 'CubeDz').CubeDz = cube_dz
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'CubeDepth').CubeDepth = cube_depth+1e-3
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = cube_tol
        obj.addProperty('App::PropertyBool', 'Slots').Slots = slots
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def execute(self, obj):
        if obj.Slots:
            slot = 10
            dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2+slot
        else:
            slot = 0
            dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        raw_dz = obj.Baseplate.OpticsDz.Value-obj.CubeDz.Value/2+obj.CubeDepth.Value
        dz = max(raw_dz, 8)
        cut_dy = obj.CubeDx.Value+obj.CubeTolerance.Value
        cut_dx = obj.CubeDy.Value+obj.CubeTolerance.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=-obj.Baseplate.OpticsDz.Value, fillet=5)
        part.rotate(App.Vector(0,0,0), App.Vector(0,0,1), -5)
        part = part.cut(_custom_box(dx=cut_dx, dy=cut_dy, dz=obj.CubeDepth.Value+1e-3,
                                    x=-8, y=2, z=-obj.Baseplate.OpticsDz.Value+dz-obj.CubeDepth.Value-1e-3))
        part.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 37.5)
        
        part = part.cut(_custom_box(dx=cut_dx, dy=cut_dy, dz=obj.CubeDepth.Value+1e-3,
                                    x=8, y=6, z=-obj.Baseplate.OpticsDz.Value+dz-obj.CubeDepth.Value-1e-3))
        part.rotate(App.Vector(0,0,0), App.Vector(0,0,1),-32.5)
        for i in [-1.5, 1.5]:
            if obj.Slots:
                part = part.cut(_custom_box(dx=slot+bolt_8_32['head_dia'], dy=bolt_8_32['head_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz,
                                            fillet=bolt_8_32['head_dia']/2, dir=(0,0,-1)))
                part = part.cut(_custom_box(dx=slot+bolt_8_32['clear_dia'], dy=bolt_8_32['clear_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz-bolt_8_32['head_dz'],
                                            fillet=bolt_8_32['clear_dia']/2, dir=(0,0,-1)))
            else:
                part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                                head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                                x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz))

        part.rotate(App.Vector(0,0,0), App.Vector(0,0,1),0)    
        part.translate(App.Vector(0, 0, obj.CubeDz.Value/2+(raw_dz-dz)))
        part = part.fuse(part)
        obj.Shape = part

        part = _bounding_box(obj, 1, 6,min_offset=(-slot/4, 0, 0), max_offset=(slot/4, 0, 0))
        for i in [-1.5, 1.5]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+obj.CubeDz.Value/2))
        part.Placement = obj.Placement
        obj.DrillPart = part


class prism_pair_mount_circle:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, cube_dx=9, cube_dy=12, cube_dz=11, mount_hole_dy=28, cube_depth=1, outer_thickness=10, cube_tol=0.1, slots=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'CubeDx').CubeDx = cube_dy
        obj.addProperty('App::PropertyLength', 'CubeDy').CubeDy = cube_dx
        obj.addProperty('App::PropertyLength', 'CubeDz').CubeDz = cube_dz
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'CubeDepth').CubeDepth = cube_depth+1e-3
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = cube_tol
        obj.addProperty('App::PropertyBool', 'Slots').Slots = slots
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def execute(self, obj):
        if obj.Slots:
            slot = 15
            dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2+slot
        else:
            slot = 0
            dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        raw_dz = obj.Baseplate.OpticsDz.Value-obj.CubeDz.Value/2+obj.CubeDepth.Value
        dz = max(raw_dz, 8)
        dz1=5
        cut_dy = obj.CubeDx.Value+obj.CubeTolerance.Value
        cut_dx = obj.CubeDy.Value+obj.CubeTolerance.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=-obj.Baseplate.OpticsDz.Value, fillet=5)
        part.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 0)
        part = part.cut(_custom_cylinder(dia=16, dz=dz1,
                                                head_dia=16, head_dz=1,
                                                x=-8, y=4, z=-obj.Baseplate.OpticsDz.Value+dz))
        part.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 0)
        
        part = part.cut(_custom_cylinder(dia=16, dz=dz1,
                                                head_dia=16, head_dz=1,
                                                x=8, y=-4, z=-obj.Baseplate.OpticsDz.Value+dz))
        part.rotate(App.Vector(0,0,0), App.Vector(0,0,1),0)
        for i in [-1.5, 1.5]:
            if obj.Slots:
                part = part.cut(_custom_box(dx=bolt_8_32['head_dia'], dy=slot+bolt_8_32['head_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz,
                                            fillet=bolt_8_32['head_dia']/2, dir=(0,0,-1)))
                
                part = part.cut(_custom_box(dx=bolt_8_32['clear_dia'], dy=slot+bolt_8_32['clear_dia'], dz=bolt_8_32['head_dz'],
                                            x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz-bolt_8_32['head_dz'],
                                            fillet=bolt_8_32['clear_dia']/2, dir=(0,0,-1)))
                 

            else:
                part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                                head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                                x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz))

        part.rotate(App.Vector(0,0,0), App.Vector(0,0,1),0)    
        part.translate(App.Vector(0, 0, obj.CubeDz.Value/2+(raw_dz-dz)))
        part = part.fuse(part)
        obj.Shape = part

        part = _bounding_box(obj, 1, 6,min_offset=(0,-slot/2, 0), max_offset=(0, slot/2, 0))
        for i in [-1.5, 1.5]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+obj.CubeDz.Value/2))
        part.Placement = obj.Placement
        obj.DrillPart = part

class prism_pair_mount_chess:
    '''
    just put it on the plate. no need to drill
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, cube_dx=9, cube_dy=12, cube_dz=11, mount_hole_dy=28, cube_depth=1, outer_thickness=10, cube_tol=0.1, slots=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        # obj.addProperty('App::PropertyLength', 'CubeDx').CubeDx = cube_dy
        # obj.addProperty('App::PropertyLength', 'CubeDy').CubeDy = cube_dx
        # obj.addProperty('App::PropertyLength', 'CubeDz').CubeDz = cube_dz
        # obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        # obj.addProperty('App::PropertyLength', 'CubeDepth').CubeDepth = cube_depth+1e-3
        # obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        # obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = cube_tol
        # obj.addProperty('App::PropertyBool', 'Slots').Slots = slots
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def execute(self, obj):
        # for i in [-1., 1.]:
        part = _custom_cylinder(dia = 15, dz = 8, x = 8, y = -6, z = -4.70,head_dia=19.9, head_dz=3,dir=(0,0,1))
        # part = part.fuse(_custom_cylinder())  
        part = part.cut(_custom_box(dx=9,dy=12,dz = 6,x=8,y = -6,z = 2))  
        # part.translate(App.Vector(20 , 5, 0))
        # part = part.fuse(_custom_cylinder(dia = 15, dz = 8, x = -8, y = 6, z = -4.70,head_dia=19.9, head_dz=3,dir=(0,0,1)))
        # part = part.fuse(_custom_cylinder())  
        # part = part.cut(_custom_box(dx=9,dy=12,dz = 6,x=-8,y = 6,z = 2))  
        # part.translate(App.Vector(-20 , 5, 0))
            # part = part.fuse(part)
        obj.Shape = part

class slide_mount:
    '''
    Slide mount adapter for post-mounted parts

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        slot_length (float) : The length of the slot used for mounting to the baseplate
        drill_offset (float) : The distance to offset the drill hole along the slot
        adapter_height (float) : The height of the suface adapter
        post_thickness (float) : The thickness of the post that mounts to the element
        outer_thickness (float) : The thickness of the walls around the bolt holes
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, slot_length=10, drill_offset=0, adapter_height=8, post_thickness=4, outer_thickness=2):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'SlotLength').SlotLength = slot_length
        obj.addProperty('App::PropertyDistance', 'DrillOffset').DrillOffset = drill_offset
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'PostThickness').PostThickness = post_thickness
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')
        
        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.SlotLength.Value+obj.PostThickness.Value
        dz = obj.AdapterHeight.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=-dy/2, z=-obj.Baseplate.OpticsDz.Value, fillet=4)
        part = part.cut(_custom_box(dx=bolt_8_32['clear_dia'], dy=obj.SlotLength.Value+bolt_8_32['clear_dia'], dz=dz,
                                    x=0, y=-dy/2-obj.PostThickness.Value/2, z=-obj.Baseplate.OpticsDz.Value, fillet=bolt_8_32['clear_dia']/2))
        part = part.cut(_custom_box(dx=bolt_8_32['head_dia'], dy=obj.SlotLength.Value+bolt_8_32['head_dia'], dz=bolt_8_32['head_dz'],
                                    x=0, y=-dy/2-obj.PostThickness.Value/2, z=-obj.Baseplate.OpticsDz.Value+bolt_8_32['head_dz'], fillet=bolt_8_32['head_dia']/2))
        part = part.fuse(_custom_box(dx=dx, dy=obj.PostThickness.Value, dz=obj.Baseplate.OpticsDz.Value+bolt_8_32['head_dz'],
                                     x=0, y=-obj.PostThickness.Value/2, z=-obj.Baseplate.OpticsDz.Value))
        part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=obj.PostThickness.Value,
                                    x=0, y=0, z=0, dir=(0, -1, 0)))
        obj.Shape = part

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=0, y=-dy/2-obj.PostThickness.Value/2+obj.DrillOffset.Value, z=-obj.Baseplate.OpticsDz.Value)
        part.Placement = obj.Placement
        obj.DrillPart = part


class fiberport_mount_hca3:
    '''
    Part for mounting an HCA3 fiberport coupler to the side of a baseplate

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['HCA3', 'PAF2-5A']
        self.max_angle = 0
        self.max_width = 1

    def execute(self, obj):
        mesh = _import_stl("HCA3-Step.stl", (90, -0, 90), (-6.35, 19.05, -26.87))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = Part.Shape()
        for i in [-1, 0, 1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=inch,
                                              x=0, y=i*12.7, z=-20.65, dir=(1,0,0)))
        part.Placement = obj.Placement
        obj.DrillPart = part


class rotation_stage_rsp05:
    '''
    Rotation stage, model RSP05

    Args:
        invert (bool) : Whether the mount should be offset 90 degrees from the component
        mount_hole_dy (float) : The spacing between the two mount holes of it's adapter
        wave_plate_part_num (string) : The Thorlabs part number of the wave plate being used

    Sub-Parts:
        surface_adapter (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, invert=False, adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 25)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['RSP05']
        self.transmission = True
        self.max_angle = 90
        self.max_width = inch/2

        _add_linked_object(obj, "Surface Adapter", surface_adapter, pos_offset=(1.397, 0, -13.97), rot_offset=(0, 0, 90*obj.Invert), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("RSP05-Step.stl", (90, -0, 90), (2.032, -0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class pinhole_p2000k05_LMR05:
    '''
    Pinhole, 2mm 
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 25)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['p2000k05']

        _add_linked_object(obj, "Surface Adapter", surface_adapter, pos_offset=(0, 3.82, -16.00), rot_offset=(0, 0, 90), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("P2000K05_LMR05.stl", (90, -0, 0), (0, -0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class BSH01_cube_mount:
    '''
    BSH01 screw mount for 10mm cube polarized beam splitter
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 25)
        adapter_args.setdefault("outer_thickness", 3)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['BSH01']

        _add_linked_object(obj, "Surface Adapter", surface_adapter_4_40, pos_offset=(0, 0, 0), rot_offset=(0, 0, 90), **adapter_args)
        # _add_linked_object(obj, "Surface Adapter", surface_adapter_4_40, pos_offset=(0, 0, -5.15), rot_offset=(0, 0, 90), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("BSH10.stl", (90, -0, 0), (101.4, 74.1, -22))
        mesh.Placement = obj.Mesh.Placement

        obj.Mesh = mesh
        # part = _bounding_box(obj, 2, 2)
        # part.Placement = obj.Placement
        # obj.DrillPart = part
        obj.Mesh = mesh

class rotation_stage_rsp05_lying_down:
    '''
    Rotation stage, model RSP05

    Args:
        invert (bool) : Whether the mount should be offset 90 degrees from the component
        mount_hole_dy (float) : The spacing between the two mount holes of it's adapter
        wave_plate_part_num (string) : The Thorlabs part number of the wave plate being used

    Sub-Parts:
        surface_adapter (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, invert=False, adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 25)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['RSP05']

        _add_linked_object(obj, "Surface Adapter", surface_adapter_lying_down, pos_offset=(1.397, 0, -13.97), rot_offset=(0, 0, 90*obj.Invert), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("RSP05-Step.stl", (90, -0, 90), (2.032, -0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh



class mirror_mount_k05s2:
    '''
    Mirror mount, model K05S2

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thumbscrews=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-K05S2']

        if thumbscrews:
            _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-15.03, 8.89, 8.89))
            _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-15.03, -8.89, -8.89))

    def execute(self, obj):
        mesh = _import_stl("POLARIS-K05S2-Step.stl", (90, -0, -90), (-4.514, 0.254, -0.254))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=-8.017, y=0, z=-layout.inch/2)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                              x=-8.017, y=i*5, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part


class mirror_mount_k05s1:
    '''
    Mirror mount, model K05S1

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thumbscrews=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-K05S1']

        if thumbscrews:
            _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-11.22, 8.89, 8.89))
            _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-11.22, -8.89, -8.89))

    def execute(self, obj):
        mesh = _import_stl("POLARIS-K05S1-Step.stl", (90, 0, -90), (-4.514, 0.254, -0.254))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=-8.017, y=0, z=-layout.inch/2)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                              x=-8.017, y=i*5, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part


class moon_mirror_mount:
    '''
    Mirror mount, model K05S1

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thumbscrews=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['DMM05-Step']

    def execute(self, obj):
        mesh = _import_stl("DMM05-Step.stl", (-183, -9, 3), (-3, 3, 1.5))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['clear_dia'], dz=inch,
                                          head_dia=bolt_8_32['head_dia'], head_dz=0.92*inch-15,
                                          x=-7.2, y=6.2, z=-inch*3/2, dir=(0,0,1))
        
        # part = _fillet_all(part, 3)
        # part = part.fuse()
        part.Placement = obj.Placement
        obj.DrillPart = part
        # for i in [-1, 1]:
        #     part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
        #                                       x=-7.2, y=i*12.2, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part

class moon_mirror_mount_left:
    '''
    Mirror mount, model K05S1

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thumbscrews=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['DMM05-Step']

    def execute(self, obj):
        mesh = _import_stl("DMM05-Step.stl", (177, -9, 3), (-3, 3, 1.5))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=-7.2, y=6.2, z=-layout.inch/2)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                              x=-7.2, y=6.2, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part

class splitter_mount_b05g:
    '''
    Splitter mount, model B05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        splitter (bool) : Whether to add a splitter plate component to the mount

    Sub-Parts:
        circular_splitter (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-B05G']

    def execute(self, obj):
        mesh = _import_stl("POLARIS-B05G-Step.stl", (90, -0, 90), (-17.54, -5.313, -19.26))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=-5, y=0, z=-layout.inch/2)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                              x=-5, y=i*5, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part


class mirror_mount_c05g:
    '''
    Mirror mount, model C05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-C05G']

    def execute(self, obj):
        mesh = _import_stl("POLARIS-C05G-Step.stl", (90, -0, 90), (-18.94, -4.246, -15.2))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=-6.35, y=0, z=-layout.inch/2)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                              x=-6.35, y=i*5, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part

class KMS_MH_12:
    '''
    KMSS mirror mount
    Ø1/2" MH_12 mirror holder
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, bolt_length = 15):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')
        obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length
        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['MH12']

    def execute(self, obj):
        mesh = _import_stl("KMSS_MH12_step.stl", (-90, -90, 90), (-5, 0, -0.4))
        mesh.Placement = obj.Mesh.Placement

        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 0.1, 15, min_offset=(0,2,0))
        part = _fillet_all(part, 3)
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz= 1*inch,
                                          head_dia=bolt_8_32['head_dia'], head_dz=0.92*inch-obj.BoltLength.Value,
                                          x=-7.29-7, y=-29-10, z=-inch*3/2+37.7, dir=(0,1,0)))
        part.Placement = obj.Placement
        # part.Placement = obj.Placement
        obj.DrillPart = part

class rotation_stage_rsp1:
    '''
    Rotation stage, model RSP1

    Args:
        invert (bool) : Whether the mount should be offset 90 degrees from the component
        mount_hole_dy (float) : The spacing between the two mount holes of it's adapter
        wave_plate_part_num (string) : The Thorlabs part number of the wave plate being used

    Sub-Parts:
        surface_adapter (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, invert=False, adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 25)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['RSP1']

        _add_linked_object(obj, "Surface Adapter", surface_adapter, pos_offset=(5.461, 0, -27.73), rot_offset=(0, 0, 90*obj.Invert), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("RSP1-Step.stl", (180, -0, 90), (5.969, -0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_km100:
    '''
    Mirror mount, model KM100

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')
        obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = 15
        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM100']

    def execute(self, obj):
        mesh = _import_stl("KM100-Step.stl", (-180, 0, -90), (4.972, 0.084, -1.089))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 3, min_offset=(4.35, 0, 0))
        part = part.fuse(_bounding_box(obj, 2, 3, max_offset=(0, -20, 0)))
        part = _fillet_all(part, 3)
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=inch+100,
                                        #  head_dia=bolt_8_32['head_dia'], head_dz=0.92*inch-obj.BoltLength.Value+drill_depth+10,
                                         x=-7.29-1.19, y=0, z=-inch*3/2-drill_depth, dir=(0,0,1)))
        part = part.fuse(_custom_box(dx = 20, dy= 22, dz= 6, x=-7.29-18.9, y=-7.29-11.9, z=-31, fillet=3, dir=(0,0,1), fillet_dir=None))
        part.Placement = obj.Placement
        obj.DrillPart = part
        
class mirror_mount_km05:
    '''
    Mirror mount, model KM05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thumbscrews=False, bolt_length=15):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM05']

        if thumbscrews:
            _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, 9.906, 9.906))
            _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, -9.906, -9.906))

    def execute(self, obj):
        mesh = _import_stl("KM05-Step.stl", (90, -0, 90), (2.084, -1.148, 0.498))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 3, min_offset=(4.35, 0, 0))
        part = part.fuse(_bounding_box(obj, 2, 3, max_offset=(0, -20, 0)))
        part = _fillet_all(part, 3)
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=inch,
                                          head_dia=bolt_8_32['head_dia'], head_dz=0.92*inch-obj.BoltLength.Value,
                                          x=-7.29, y=0, z=-inch*3/2, dir=(0,0,1)))
        part.Placement = obj.Placement
        obj.DrillPart = part

class mirror_mount_km05_rot90:
    '''
    Mirror mount, model KM05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thumbscrews=False, bolt_length=15):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM05']

        if thumbscrews:
            _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, 9.906, -9.906))
            _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, -9.906, 9.906))

    def execute(self, obj):
        mesh = _import_stl("KM05-Step.stl", (90, 90, 90), (1.784, 0.1, 0.498))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 1, 3, min_offset=(3.35, 0, 0))
        part = part.fuse(_bounding_box(obj, 1, 3, max_offset=(0, 3, 0)))
        part = _fillet_all(part, 3)
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=inch,
                                          head_dia=bolt_8_32['head_dia']+1, head_dz=0.92*inch-obj.BoltLength.Value,
                                          x=-7.49, y=-0.38, z=-inch*3/2, dir=(0,0,1)))
        part.Placement = obj.Placement
        obj.DrillPart = part

class fixed_mount_smr05:
    '''
    Fixed mount, model SMR05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thumbscrews=False, bolt_length=15):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['SMR05']


    def execute(self, obj):
        mesh = _import_stl("SMR05-Step.stl", (90, 0, 90), (-3.81, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['clear_dia'], dz=inch,
                                          head_dia=bolt_8_32['head_dia'], head_dz=0.92*inch-obj.BoltLength.Value,
                                          x=-3.81, y=0, z=-16-obj.BoltLength.Value, dir=(0,0,1))
        part.Placement = obj.Placement
        obj.DrillPart = part


class prism_mount_km05pm:
    '''
    Mount, model KM05PM

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thumbscrews=False, bolt_length=15, arm=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'Arm').Arm = arm
        obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM05PM']

        if thumbscrews:
            _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-19.05, 6.985, 15.49))
            _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-19.05, -12.83, -4.318))

    def execute(self, obj):
        #mesh = _import_stl("KM05PM-Step.stl", (90, 0, 90), (-12.39, -0.894, 1.514))
        if obj.Arm:
            mesh = _import_stl("KM05PM-Step-No-Plate.stl", (90, -0, 90), (-6.425, -4.069, 6.086))
        else:
            mesh = _import_stl("KM05PM-Step-NoArm.stl", (90, 0, 90), (-3.25, -8.26, 10.4))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 3, 3, min_offset=(4.35, 0, 0))
        part = part.fuse(_bounding_box(obj, 3, 3, max_offset=(0, -20, 0)))
        part = part.fuse(_bounding_box(obj, 3, 3, min_offset=(14, 0, 0), z_tol=True))
        part = _fillet_all(part, 3)
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=drill_depth,
                                          head_dia=bolt_8_32['head_dia'], head_dz=drill_depth-obj.BoltLength.Value,
                                          x=-15.8, y=-2.921, z=-9.144-drill_depth, dir=(0,0,1)))
        part.Placement = obj.Placement
        obj.DrillPart = part


class grating_mount_on_km05pm:
    '''
    Grating and Parallel Mirror Mounted on MK05PM

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        littrow_angle (float) : The angle of the grating and parallel mirror

    Sub_Parts:
        mount_mk05pm (mount_args)
        square_grating (grating_args)
        square_mirror (mirror_args)
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, littrow_angle=55, mount_args=dict(), grating_args=dict(), mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyAngle', 'LittrowAngle').LittrowAngle = littrow_angle

        obj.ViewObject.ShapeColor = adapter_color
        self.dx = 12/tan(radians(2*obj.LittrowAngle))

        gap = 10
        lit_angle = radians(90-obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap/sin(2*beam_angle)
        ref_x = ref_len*cos(2*beam_angle)
        dx = ref_x+12.7*cos(lit_angle)+(6+3.2)*sin(lit_angle)
        extra_x = 20-dx
        grating_dx = -(6*sin(lit_angle)+12.7/2*cos(lit_angle))-extra_x
        mirror_dx = grating_dx-ref_x

        _add_linked_object(obj, "Mount MK05PM", prism_mount_km05pm, pos_offset=(-3.175, 8, -10), rot_offset=(0, 0, 180), drill=drill, **mount_args)
        _add_linked_object(obj, "Grating", square_grating, pos_offset=(grating_dx, 0, 0), rot_offset=(0, 0, 180-obj.LittrowAngle.Value), **grating_args)
        _add_linked_object(obj, "Mirror", square_mirror, pos_offset=(mirror_dx, gap, 0), rot_offset=(0, 0, -obj.LittrowAngle.Value), **mirror_args)

    def execute(self, obj):
        extra_y = 2
        gap = 10
        lit_angle = radians(90-obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap/sin(2*beam_angle)
        ref_x = ref_len*cos(2*beam_angle)
        dx = ref_x+12.7*cos(lit_angle)+(6+3.2)*sin(lit_angle)
        extra_x = 20-dx
        dy = gap+12.7*sin(lit_angle)+(6+3.2)*cos(lit_angle)
        dz = inch/2
        cut_x = 12.7*cos(lit_angle)

        part = _custom_box(dx=dx+extra_x, dy=dy+extra_y, dz=dz,
                           x=extra_x, y=0, z=-10, dir=(-1, 1, 1))
        temp = _custom_box(dx=ref_len*cos(beam_angle)+6+3.2, dy=dy/sin(lit_angle)+10, dz=dz,
                           x=-cut_x, y=-(dx-cut_x)*cos(lit_angle), z=-6, dir=(-1, 1, 1))
        temp.rotate(App.Vector(-cut_x, 0, 0), App.Vector(0, 0, 1), -obj.LittrowAngle.Value)
        part = part.cut(temp)
        part = part.cut(_custom_box(dx=8, dy=16, dz=dz-4,
                           x=extra_x, y=dy+extra_y, z=-6, dir=(-1, -1, 1)))
        part.translate(App.Vector(-extra_x, -12.7/2*sin(lit_angle)-6*cos(lit_angle), 0))
        part = part.fuse(part)
        part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=4,
                                         head_dia=bolt_4_40['head_dia'], head_dz=2,
                                         x=-3.175, y=8, z=-6, dir=(0, 0, -1)))
        part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=4,
                                         head_dia=bolt_4_40['head_dia'], head_dz=2,
                                         x=-3.175, y=8+2*3.175, z=-6, dir=(0, 0, -1)))
        obj.Shape = part


class grating_mount_on_km05pm_no_arm:
    '''
    Grating and Parallel Mirror Mounted on MK05PM

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        littrow_angle (float) : The angle of the grating and parallel mirror

    Sub_Parts:
        mount_mk05pm (mount_args)
        square_grating (grating_args)
        square_mirror (mirror_args)
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, littrow_angle=55, mount_args=dict(), grating_args=dict(), mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyAngle', 'LittrowAngle').LittrowAngle = littrow_angle

        obj.ViewObject.ShapeColor = adapter_color
        self.dx = 12/tan(radians(2*obj.LittrowAngle))

        gap = 10
        lit_angle = radians(90-obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap/sin(2*beam_angle)
        ref_x = ref_len*cos(2*beam_angle)
        dx = ref_x+12.7*cos(lit_angle)+(6+3.2)*sin(lit_angle)
        extra_x = 20-dx
        grating_dx = -(6*sin(lit_angle)+12.7/2*cos(lit_angle))-extra_x
        mirror_dx = grating_dx-ref_x

        _add_linked_object(obj, "Mount MK05PM", prism_mount_km05pm, pos_offset=(-3.175, 8, 4.064-inch/2), rot_offset=(0, 0, 180), arm=False, drill=drill, **mount_args)
        _add_linked_object(obj, "Grating", square_grating, pos_offset=(grating_dx, 0, 0), rot_offset=(0, 0, 180-obj.LittrowAngle.Value), **grating_args)
        _add_linked_object(obj, "Mirror", square_mirror, pos_offset=(mirror_dx, gap, 0), rot_offset=(0, 0, -obj.LittrowAngle.Value), **mirror_args)

    def execute(self, obj):
        extra_y = 2
        gap = 10
        lit_angle = radians(90-obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap/sin(2*beam_angle)
        ref_x = ref_len*cos(2*beam_angle)
        dx = ref_x+12.7*cos(lit_angle)+(6+3.2)*sin(lit_angle)
        extra_x = 20-dx
        dy = gap+12.7*sin(lit_angle)+(6+3.2)*cos(lit_angle)
        dz = inch/2
        cut_x = 12.7*cos(lit_angle)

        part = _custom_box(dx=dx+extra_x, dy=dy+extra_y, dz=dz,
                           x=extra_x, y=0, z=-10, dir=(-1, 1, 1))
        temp = _custom_box(dx=ref_len*cos(beam_angle)+6+3.2, dy=dy/sin(lit_angle)+10, dz=dz,
                           x=-cut_x, y=-(dx-cut_x)*cos(lit_angle), z=-6, dir=(-1, 1, 1))
        temp.rotate(App.Vector(-cut_x, 0, 0), App.Vector(0, 0, 1), -obj.LittrowAngle.Value)
        part = part.cut(temp)
        part = part.cut(_custom_box(dx=8, dy=16, dz=dz-4,
                           x=extra_x, y=dy+extra_y, z=-6, dir=(-1, -1, 1)))
        part.translate(App.Vector(-extra_x, -12.7/2*sin(lit_angle)-6*cos(lit_angle), 0))
        part = part.fuse(part)
        part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=4,
                                         head_dia=bolt_4_40['head_dia'], head_dz=2,
                                         x=-3.175, y=8, z=-6, dir=(0, 0, -1)))
        part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=4,
                                         head_dia=bolt_4_40['head_dia'], head_dz=2,
                                         x=-3.175, y=8+2*3.175, z=-6, dir=(0, 0, -1)))
        obj.Shape = part


class mount_tsd_405sluu:
    '''
    Mount, model KM05PM

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['TSD-405SLUU']

    def execute(self, obj):
        mesh = _import_stl("TSD-405SLUU.stl", (0, 0, -90), (-19, 0, -62))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 3, 3)
        for x, y in [(-34.88, 15.88), (-34.88, -15.88), (-3.125, 15.88), (-3.125, -15.88)]:
            part = part.fuse(_custom_cylinder(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                                            x=x, y=y, z=-62))
        part.Placement = obj.Placement
        obj.DrillPart = part


class mirror_mount_ks1t:
    '''
    Mirror mount, model KS1T

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM1T']

    def execute(self, obj):
        mesh = _import_stl("KS1T-Step.stl", (90, -0, -90), (22.06, 13.37, -30.35))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        dz = -0.5
        # dz = -inch-obj.Mesh.BoundBox.ZMin
        part = _bounding_box(obj, 3, 3, min_offset=(0, 0, dz))
        part = part.fuse(_bounding_box(obj, 3, 3, z_tol=True, max_offset=(-28, 0, 0)))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                          x=-16.94, y=0, z=-layout.inch/2, dir=(0,0,-1)))
        part.Placement = obj.Placement
        obj.DrillPart = part


class fiberport_mount_km05:
    '''
    Mirror mount, model KM05, adapted to use as fiberport mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        mirror_mount_km05 (mount_args)
        fiber_adapter_sm05fca2
        lens_tube_sm05l05
        lens_adapter_s05tm09
        mounted_lens_c220tmda
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = misc_color

        _add_linked_object(obj, "Mount", mirror_mount_km05, pos_offset=(0, 0, 0), **mount_args)
        _add_linked_object(obj, "Fiber Adapter", fiber_adapter_sm05fca2, pos_offset=(1.524, 0, 0))
        _add_linked_object(obj, "Lens Tube", lens_tube_sm05l05, pos_offset=(1.524+3.812, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s05tm09, pos_offset=(1.524+5, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(1.524+3.167+5, 0, 0))
class splitter_mount_b1g:
    '''
    Splitter mount, model B1G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        splitter (bool) : Whether to add a splitter plate component to the mount

    Sub-Parts:
        circular_splitter (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-B1G']

        _add_linked_object(obj, "Surface Adapter", surface_adapter, pos_offset=(-5, 0, -19.05), rot_offset=(0, 0, 0), mount_hole_dy=30)

    def execute(self, obj):
        mesh = _import_stl("POLARIS-B1G-Step.stl", (90, 0, 90), (-43.59, 1.26, -23.78))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=-5, y=0, z=-layout.inch/2)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                              x=-5, y=i*5, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part

class fiberport_mount_k1t1:
    '''
    Mirror mount, model KM05, adapted to use as fiberport mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        mirror_mount_km05 (mount_args)
        fiber_adapter_sm05fca2
        lens_tube_sm05l05
        lens_adapter_s05tm09
        mounted_lens_c220tmda
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = misc_color

        _add_linked_object(obj, "Mount", mirror_mount_k1t1, pos_offset=(0, 0, 0), **mount_args)
        # _add_linked_object(obj, "Fiber Adapter", fiber_adapter_sm05fca2, pos_offset=(1.524, 0, 0))
        # _add_linked_object(obj, "Lens Tube", lens_tube_sm05l05, pos_offset=(1.524+3.812, 0, 0))
        # _add_linked_object(obj, "Lens Adapter", lens_adapter_s05tm09, pos_offset=(1.524+5, 0, 0))
        # _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(1.524+3.167+5, 0, 0))
        _add_linked_object(obj, "Fiber Adapter", fiber_adapter_sm1fca2, pos_offset=(-3, 0, 0))
        _add_linked_object(obj, "Lens Tube", lens_tube_sm1l05, pos_offset=(0+10.6-2-2, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s1tm09, pos_offset=(1.524+6+13.6, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(1.524+2, 0, 0))
class mirror_mount_k1t1:
    '''
    Mirror mount, model K1t1

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM1T']

    def execute(self, obj):
        mesh = _import_stl("Fiberport_mount_k1t1.stl", (90, -0, -90), (97.06, 17.87, -10.35))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        dz = -0.5
        # dz = -inch-obj.Mesh.BoundBox.ZMin
        part = _bounding_box(obj, 3, 3, min_offset=(0, 0, dz))
        part = part.fuse(_bounding_box(obj, 3, 3, z_tol=True, max_offset=(-28-2-5, 0, 0)))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                          x=-16.94+1.18, y=0, z=-layout.inch/2, dir=(0,0,-1)))
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                              x=-15.667, y=i*5.05, z=-layout.inch/2-12.5))
        part.Placement = obj.Placement
        obj.DrillPart = part  

class fiberport_mount_ks1t:
    '''
    Mirror mount, model KM05, adapted to use as fiberport mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        mirror_mount_km05 (mount_args)
        fiber_adapter_sm05fca2
        lens_tube_sm05l05
        lens_adapter_s05tm09
        mounted_lens_c220tmda
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = misc_color

        _add_linked_object(obj, "Mount", mirror_mount_ks1t, pos_offset=(0, 0, 0), **mount_args)
        _add_linked_object(obj, "Fiber Adapter", fiber_adapter_sm1fca2, pos_offset=(-3, 0, 0))
        _add_linked_object(obj, "Lens Tube", lens_tube_sm1l05, pos_offset=(0, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s1tm09, pos_offset=(1.524+6, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(1.524+2, 0, 0))

class fiberport_mount_ks1t_with_tube:
    '''
    Mirror mount, model KM05, adapted to use as fiberport mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        mirror_mount_km05 (mount_args)
        fiber_adapter_sm05fca2
        lens_tube_sm05l05
        lens_adapter_s05tm09
        mounted_lens_c220tmda
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = misc_color

        _add_linked_object(obj, "Mount", mirror_mount_ks1t, pos_offset=(0, 0, 0), **mount_args)
        _add_linked_object(obj, "Fiber Adapter", fiber_adapter_sm1fca2, pos_offset=(-3, 0, 0))
        # _add_linked_object(obj, "Lens Tube", lens_tube_sm1l05, pos_offset=(0, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s1tm09, pos_offset=(1.524+6, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(1.524+2, 0, 0))
        _add_linked_object(obj, "Lens Slot Tube", lens_slot_tube, pos_offset=(1.524+2+5, 0, 0))

class lens_slot_tube:
    '''
    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        # self.part_numbers = ['HCA3', 'PAF2-5A']
        self.max_angle = 0
        self.max_width = 1

    def execute(self, obj):
        mesh = _import_stl("SM1L10C_slot_tube.stl", (90, 180, -90), (18.35, 0.05, -81.87))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 3, 3, min_offset=(0, 0, -3))
        part.Placement = obj.Placement
        obj.DrillPart = part

class km05_50mm_laser:
    '''
    Mirror mount, model KM05, adapted to use as laser mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        tec_thickness (float) : The thickness of the TEC used

    Sub-Parts:
        mirror_mount_km05 (mount_args)
        km05_tec_upper_plate (upper_plate_args)
        km05_tec_lower_plate (lower_plate_args)
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, tec_thickness=4, mount_args=dict(), upper_plate_args=dict(), lower_plate_args=dict()):
        mount_args.setdefault("bolt_length", 2)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'TecThickness').TecThickness = tec_thickness
        obj.ViewObject.ShapeColor = misc_color
        
        self.part_numbers = [] # TODO add part numbers
        self.max_angle = 0
        self.max_width = 1

        dx = -5.334+2.032
        _add_linked_object(obj, "Diode Adapter", diode_adapter_s05lm56, pos_offset=(0, 0, 0))
        _add_linked_object(obj, "Lens Tube", lens_tube_sm05l05, pos_offset=(dx+1.524+3.812, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s05tm09, pos_offset=(dx+1.524+5, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(dx+1.524+3.167+5, 0, 0))

        mount = _add_linked_object(obj, "Mount", mirror_mount_km05, pos_offset=(dx, 0, 0), drill=False, **mount_args)
        upper_plate = _add_linked_object(obj, "Upper Plate", km05_tec_upper_plate, pos_offset=(dx-4, 0, -0.08*inch), drill_obj=mount, **upper_plate_args)
        _add_linked_object(obj, "Lower Plate", km05_tec_lower_plate, pos_offset=(dx-4, 0, -0.08*inch-tec_thickness-upper_plate.Thickness.Value), **lower_plate_args)

class km05_50mm_laser_no_pad:
    '''
    Mirror mount, model KM05, adapted to use as laser mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        tec_thickness (float) : The thickness of the TEC used

    Sub-Parts:
        mirror_mount_km05 (mount_args)
        km05_tec_upper_plate (upper_plate_args)
        km05_tec_lower_plate (lower_plate_args)
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, tec_thickness=4, mount_args=dict(), upper_plate_args=dict(), lower_plate_args=dict()):
        mount_args.setdefault("bolt_length", 2)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'TecThickness').TecThickness = tec_thickness
        obj.ViewObject.ShapeColor = misc_color
        
        self.part_numbers = [] # TODO add part numbers
        self.max_angle = 0
        self.max_width = 1

        dx = -5.334+2.032
        _add_linked_object(obj, "Diode Adapter", diode_adapter_s05lm56, pos_offset=(0, 0, 0))
        _add_linked_object(obj, "Lens Tube", lens_tube_sm05l05, pos_offset=(dx+1.524+3.812, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s05tm09, pos_offset=(dx+1.524+5, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(dx+1.524+3.167+5, 0, 0))

        mount = _add_linked_object(obj, "Mount", mirror_mount_km05, pos_offset=(dx, 0, 0), drill=True, **mount_args)
        # upper_plate = _add_linked_object(obj, "Upper Plate", km05_tec_upper_plate, pos_offset=(dx-4, 0, -0.08*inch), drill_obj=mount, **upper_plate_args)
        # _add_linked_object(obj, "Lower Plate", km05_tec_lower_plate, pos_offset=(dx-4, 0, -0.08*inch-tec_thickness-upper_plate.Thickness.Value), **lower_plate_args)

class laser_cavity_mount:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, tec_thickness=4, mount_args=dict(), grating_args=dict(), upper_plate_args=dict(), lower_plate_args=dict()):
        mount_args.setdefault("bolt_length", 12.5)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'TecThickness').TecThickness = tec_thickness
        obj.ViewObject.ShapeColor = misc_color
        
        self.part_numbers = [] # TODO add part numbers
        self.max_angle = 0
        self.max_width = 1

        dx = -5.334+2.032
        _add_linked_object(obj, "Diode Adapter", diode_adapter_s05lm56, pos_offset=(0, 0, 0))
        _add_linked_object(obj, "Lens Tube", lens_tube_sm05l05, pos_offset=(dx+1.524+3.812, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s05tm09, pos_offset=(dx+1.524+5, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(dx+1.524+3.167+5, 0, 0))

        width = 3*inch
        mount = _add_linked_object(obj, "Mount", fixed_mount_smr05, pos_offset=(dx+5.334, 0, 16-inch/2), drill=False, **mount_args)
        grating = _add_linked_object(obj, "Grating", grating_mount_on_km05pm_no_arm, pos_offset=(dx+width*3/4, 0, 16-inch/2), drill=False, **grating_args)
        upper_plate = _add_linked_object(obj, "Upper Plate", laser_cavity_mount_upper_plate, pos_offset=(dx-8+width/2, 0, ), drill_objs=[mount, grating], **upper_plate_args)
        _add_linked_object(obj, "Lower Plate", laser_cavity_mount_lower_plate, pos_offset=(dx-8+width/2, 0, -tec_thickness-upper_plate.Thickness.Value), **lower_plate_args)

class laser_cavity_mount_upper_plate:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill_objs, width=inch, length=3*inch, thickness=0.25*inch):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Length').Length = length
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLinkListHidden', 'DrillObjects').DrillObjects = drill_objs

        obj.ViewObject.ShapeColor = adapter_color

    def execute(self, obj):
        part = _custom_box(dx=obj.Length.Value, dy=obj.Width.Value, dz=obj.Thickness.Value,
                           x=0, y=0, z=-inch/2, dir=(0, 0, -1))
        for sub_obj in obj.DrillObjects:
            part = _drill_part(part, obj, sub_obj)
            obj.Shape = part

class laser_cavity_mount_lower_plate:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, width=1.5*inch, length=3.5*inch, thickness=0.25*inch):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Length').Length = length
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color

    def execute(self, obj):
        part = _custom_box(dx=obj.Length.Value, dy=obj.Width.Value, dz=obj.Thickness.Value,
                                     x=0, y=0, z=-inch/2, dir=(0, 0, -1))
        for x, y in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=obj.Thickness.Value,
                                        x=(obj.Length.Value/2-4)*x, y=(obj.Width.Value/2-4)*y, z=-inch/2, dir=(0, 0, -1)))
        obj.Shape = part

        part = _bounding_box(obj, 3, 3)
        for x, y in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=(obj.Length.Value/2-4)*x, y=(obj.Width.Value/2-4)*y, z=0, dir=(0, 0, -1)))
        part = part.fuse(_custom_box(dx=20, dy=5, dz=inch/2,
                                     x=part.BoundBox.XMin, y=(part.BoundBox.YMax+part.BoundBox.YMin)/2, z=0,
                                     dir=(-1, 0, -1)))
        part.Placement = obj.Placement
        obj.DrillPart = part

class km05_tec_upper_plate:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill_obj, width=inch, thickness=0.25*inch):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLinkHidden', 'DrillObject').DrillObject = drill_obj

        obj.ViewObject.ShapeColor = adapter_color

    def execute(self, obj):
        part = _custom_box(dx=obj.Width.Value, dy=obj.Width.Value, dz=obj.Thickness.Value,
                           x=0, y=0, z=-inch/2, dir=(0, 0, -1))
        part = _drill_part(part, obj, obj.DrillObject)
        obj.Shape = part


class km05_tec_lower_plate:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, width=3*inch, height=.25*inch, thickness=3*inch, part_number=''): #thickness=130-inch/2-1,
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height

        obj.ViewObject.ShapeColor = adapter_color
        self.part_numbers = [part_number]

    def execute(self, obj):
        x_off = 0 #-2
        y_off = 0 #-4
        bolt_off = 2.5
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=x_off, y=y_off, z=-3/2*inch-3.95-obj.Thickness.Value, dir=(0, 0, -1))
        
        for x, y in [(0,0)]:
            part = part.cut(_custom_cylinder(dia=bolt_14_20['clear_dia'], dz=drill_depth,
                                    head_dia=bolt_14_20["washer_dia"], head_dz=8,
                                    x=1.5*inch*x+x_off, y=inch*y+y_off-bolt_off, z=-3/2*inch-3.95-inch/2))
        
        obj.Shape = part


class mirror_mount_mk05:
    '''
    Mirror mount, model MK05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['MK05']
        self.reflection_angle = 0
        self.max_angle = 90
        self.max_width = inch/2

    def execute(self, obj):
        mesh = _import_stl("MK05-Step.stl", (90, -0, -90), (-22.91-obj.ChildObjects[0].Thickness.Value, 26, -5.629))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                           head_dia=bolt_4_40['head_dia'], head_dz=drill_depth-10,
                           x=-5.562, y=0, z=-10.2-drill_depth, dir=(0, 0, 1))
        part.Placement = obj.Placement
        obj.DrillPart = part


class mount_mk05pm:
    '''
    Mount, model MK05PM

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['MK05PM']

    def execute(self, obj):
        mesh = _import_stl("MK05PM-Step.stl", (180, 90, 0), (-7.675, 7.699, 4.493))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 2)
        part = part.cut(_custom_box(dx=4, dy=15, dz=-layout.inch/2-obj.Mesh.BoundBox.ZMin,
                                    x=part.BoundBox.XMin, y=part.BoundBox.YMax, z=part.BoundBox.ZMin,
                                    dir=(1, -1, 1), fillet=2))
        part = _fillet_all(part, 2)
        part = part.fuse(_custom_cylinder(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                           head_dia=bolt_4_40['head_dia'], head_dz=drill_depth-5,
                           x=-7.675, y=7.699, z=4.493-10.2-drill_depth, dir=(0,0,1)))
        part.Placement = obj.Placement
        obj.DrillPart = part

class dichoric_mirror_mount_km05fl:
    '''
    Mirror mount, model MK05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM05fl']
        self.reflection_angle = 0
        self.max_angle = 90
        self.max_width = inch/2

    def execute(self, obj):
        mesh = _import_stl("KM05FL-Step.stl", (-180, 0, -90), (-11.53, -10.16, -10.16))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 2)
        part = part.cut(_custom_box(dx=4, dy=15, dz=-layout.inch/2-obj.Mesh.BoundBox.ZMin,
                                    x=part.BoundBox.XMin, y=part.BoundBox.YMax, z=part.BoundBox.ZMin,
                                    dir=(1, -1, 1), fillet=2))
        part = _fillet_all(part, 2)

        part = part.fuse(_custom_cylinder(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                           head_dia=bolt_4_40['head_dia'], head_dz=drill_depth-10,
                           x=7.378, y=7.378, z=-4.373-drill_depth, dir=(0, 0, 1)))
        part.Placement = obj.Placement
        obj.DrillPart = part

class dichoric_mirror_mount_km05fR:
    '''
    Mirror mount, model KM05FR

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM05fR']
        self.reflection_angle = 0
        self.max_angle = 90
        self.max_width = inch/2

    def execute(self, obj):
        mesh = _import_stl("KM05FR_M-Step.stl", (-90, 0, 0), (-11.53, -10.16, -10.16))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 2)
        part = part.cut(_custom_box(dx=4, dy=15, dz=-layout.inch/2-obj.Mesh.BoundBox.ZMin,
                                    x=part.BoundBox.XMin, y=part.BoundBox.YMax, z=part.BoundBox.ZMin,
                                    dir=(1, -1, 1), fillet=2))
        part = _fillet_all(part, 2)
        part = part.fuse(_custom_cylinder(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                           head_dia=bolt_4_40['head_dia'], head_dz=drill_depth-5,
                           x=-11.53, y=14.53, z=.275-drill_depth, dir=(0,0,1)))
        part.Placement = obj.Placement
        obj.DrillPart = part


class grating_mount_on_mk05pm:
    '''
    Grating and Parallel Mirror Mounted on MK05PM

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        littrow_angle (float) : The angle of the grating and parallel mirror

    Sub_Parts:
        mount_mk05pm (mount_args)
        square_grating (grating_args)
        square_mirror (mirror_args)
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, littrow_angle=45, mount_args=dict(), grating_args=dict(), mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyAngle', 'LittrowAngle').LittrowAngle = littrow_angle

        obj.ViewObject.ShapeColor = adapter_color
        self.dx = 12/tan(radians(2*obj.LittrowAngle))

        _add_linked_object(obj, "Mount MK05PM", mount_mk05pm, pos_offset=(-12, -4, -4-12.7/2+2), drill=drill, **mount_args)
        _add_linked_object(obj, "Grating", square_grating, pos_offset=(0, 0, 2), rot_offset=(0, 0, -obj.LittrowAngle.Value), **grating_args)
        _add_linked_object(obj, "Mirror", square_mirror, pos_offset=(self.dx, -12, 2), rot_offset=(0, 0, -obj.LittrowAngle.Value+180), **mirror_args)

    def execute(self, obj):
        # TODO add some variables to make this cleaner
        part = _custom_box(dx=25+self.dx, dy=35, dz=4,
                           x=-3.048, y=17.91, z=0, dir=(1, -1, 1))
        
        part = part.cut(_custom_box(dx=6, dy=8.1, dz=4,
                                    x=-3.048, y=17.91, z=0, dir=(1, -1, 1)))
        part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=4,
                                    x=0, y=0, z=0, dir=(0, 0, 1)))
        part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=4,
                                    x=13.34, y=15.62, z=0, dir=(0, 0, 1)))
        part.translate(App.Vector(-12, -4, -4))

        temp = _custom_box(dx=4, dy=12, dz=12,
                           x=-6, y=0, z=0, dir=(-1, 0, 1))
        temp.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), -obj.LittrowAngle.Value)
        part = part.fuse(temp)
        temp = _custom_box(dx=4, dy=12, dz=12,
                           x=self.dx+3.2, y=-12, z=0, dir=(1, 0, 1))
        temp.rotate(App.Vector(self.dx, -12, 0), App.Vector(0, 0, 1), -obj.LittrowAngle.Value)
        part = part.fuse(temp)
        part.translate(App.Vector(0, 0, -12.7/2+2))
        part = part.fuse(part)
        obj.Shape = part


class lens_holder_l05g:
    '''
    Lens Holder, Model L05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        circular_lens (lens_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-L05G']

    def execute(self, obj):
        mesh = _import_stl("POLARIS-L05G-Step.stl", (90, -0, 90), (-26.57, -13.29, -18.44))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=-8, y=0, z=-layout.inch/2)
        for i in [-1, 1]:
            part = part.fuse(_custom_box(dx=5, dy=2, dz=2.2,
                                         x=-8, y=i*5, z=-layout.inch/2,
                                         fillet=1, dir=(0, 0, -1)))
        part.Placement = obj.Placement
        obj.DrillPart = part


class pinhole_ida12:
    '''
    Pinhole Iris, Model IDA12

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        slide_mount (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, adapter_args=dict()):
        adapter_args.setdefault("slot_length", 10)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IDA12-P5']
        self.transmission = True
        self.max_angle = 90
        self.max_width = 1
        self.block_width=inch/2
        self.slot_length=adapter_args['slot_length']

        _add_linked_object(obj, "Slide Mount", slide_mount,
                           pos_offset=(1.956, -12.83, 0), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("IDA12-P5-Step.stl", (90, 0, -90), (1.549, 0, -0))
        mesh.rotate(-pi/2, 0, 0)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_box(dx=6.5, dy=15+obj.ChildObjects[0].SlotLength.Value, dz=1,
                           x=1.956, y=0, z=-layout.inch/2,
                           fillet=2, dir=(0,0,-1))
        part.Placement = obj.Placement
        obj.DrillPart = part


class prism_mount_km100pm:
    '''
    Kinematic Prism Mount, Model KM100PM

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM100PM']

    def execute(self, obj):
        mesh = _import_stl("KM100PM-Step.stl", (90, -0, -90), (-8.877, 38.1, -6.731))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 3, 4, max_offset=(-18, -38, 0), z_tol=True)
        part = part.fuse(_bounding_box(obj, 3, 4, min_offset=(17, 0, 0.63)))    
        # part = part.fuse(_bounding_box(obj, 3, 4, max_offset=(-18, -38, 0), z_tol=True))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                     x=-14.02, y=12.63, z=17.5))
        part.Placement = obj.Placement
        obj.DrillPart = part

class wire_tube:
    '''
    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        # self.part_numbers = ['HCA3', 'PAF2-5A']
        self.max_angle = 0
        self.max_width = 1

    def execute(self, obj):
        mesh = _import_stl("wire_tube.stl", (90, 90, 90), (-133, 0, -29.25))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 3, 3, min_offset=(0, 0, -3))
        part.Placement = obj.Placement
        obj.DrillPart = part      

class brewster_window:
    '''
    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = glass_color
        # self.part_numbers = ['HCA3', 'PAF2-5A']
        self.max_angle = 0
        self.max_width = 1

    def execute(self, obj):
        mesh = _import_stl("BW20M.stl", (90, 0, 90), (90, 20.79, -40.46))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 3, 3, min_offset=(0, 0, 0))
        part.Placement = obj.Placement
        obj.DrillPart = part            

class laser_box:

    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, thickness=115 + inch/4*2 +  inch, width=95 + inch, height=95, mat_thickness=0, part_number=''):
        # (self, obj, drill=True, thickness=4.5*inch, width=3.5*inch, height=80, mat_thickness=0, part_number=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height
        obj.addProperty('App::PropertyLength', 'MatThickness').MatThickness = mat_thickness

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = [part_number]

    def execute(self, obj):
        x_off = -2
        y_off = -4
        thickness = inch/4
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=x_off, y=y_off, z=-3/2*inch-3.95, dir=(0, 0, 1))
        
        # Bottom cuttout
        part = part.cut(_custom_box(dx=obj.Thickness.Value-inch/4*2-.7*inch, dy=obj.Width.Value-.7*inch, dz=80,   #-2*inch+5
                           x=x_off, y=y_off, z=-3/2*inch-3.95, dir=(0, 0, 1)))
        
        # Component cutouts
        parent = obj.ParentObject
        mount = parent.ChildObjects[0]
        parent.Proxy.execute(parent)
        for cutObj in [mount, parent]:
            try:
                temp = _bounding_box(cutObj, 19, 19, z_tol=False)
                temp.translate(cutObj.Placement.Base)
                temp.translate(App.Vector(-8,-7,0))
                #temp.rotate(App.Vector(0,0,0),App.Vector(0,0,1),0)
                part = part.cut(temp)
                print("yup")
            except Exception as e:
                print(e)
                pass
        
        #part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
        #                   x=x_off, y=y_off, z=-3/2*inch-3.95-inch/2-obj.MatThickness.Value, dir=(0, 0, 1))
        #part = part.cut(_custom_box(dx=obj.Thickness.Value-inch/4*2, dy=obj.Width.Value-inch/4*2, dz=obj.Height.Value-inch/4,
        #                   x=x_off, y=y_off, z=-3/2*inch-3.95-inch/2-obj.MatThickness.Value, dir=(0, 0, 1)))
        
        # Cable opening
        #Square cut 
        #part = part.cut(_custom_box(dx=obj.Width.Value, dy=10, dz=50,
        #                   x=x_off-obj.Thickness.Value/2, y=y_off+0, z=-2*inch-3.95-inch, dir=(0, 0, 1)))
        
        #Circular cut
        part = part.cut(_custom_cylinder(dia=28, dz=obj.Thickness.Value/2,
                           x=x_off-obj.Thickness.Value/2, y=y_off+4, z=-42, dir=(1, 0, 0)))

        # Laser opening
        part = part.cut(_custom_cylinder(dia=25.8, dz=obj.Thickness.Value/2,
                           x=x_off+obj.Thickness.Value/2, y=y_off+24, z=-2, dir=(-1, 0, 0)))
        
        # Bolt openings
        part = part.cut(_custom_cylinder(dia=5, dz=obj.Thickness.Value/2,
                           x=x_off-obj.Thickness.Value/2, y=y_off+25.5, z=12.9+6.4, dir=(1, 0, 0)))
        part = part.cut(_custom_cylinder(dia=5, dz=obj.Thickness.Value/2,
                           x=x_off-obj.Thickness.Value/2, y=y_off-12.2, z=-24.8+6.4, dir=(1, 0, 0)))
        obj.Shape = part

class laser_base:

    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, thickness=125 + inch/4*2 + 1 * inch, width=100+ inch, height=0.25*inch, mat_thickness=0.5*inch, part_number=''):
    #(self, obj, drill=True, thickness=4*inch, width=3*inch, height=0.25*inch, mat_thickness=0.25*inch, part_number=''): #thickness=130-inch/2-1,
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height
        obj.addProperty('App::PropertyLength', 'MatThickness').MatThickness = mat_thickness

        obj.ViewObject.ShapeColor = adapter_color
        self.part_numbers = [part_number]

    def execute(self, obj):
        x_off = -2
        y_off = -4
        bolt_off = 1.5
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=x_off, y=y_off, z=-3/2*inch-3.95-obj.MatThickness.Value, dir=(0, 0, -2))
        
        
        for x, y in [(-2,-2), (-2,1), (2,-2), (2,1)]:
            
            part = part.cut(_custom_cylinder(dia=6.6, dz=drill_depth,
                                    head_dia=6.6, head_dz=8,
                                    x=1*inch*x+x_off, y=inch*y+y_off-bolt_off+.5*inch, z=-3/2*inch-3.95-inch/2))  #bolt_14_20['tap_dia']
        
        obj.Shape = part

class ECDL:
    type = 'Part::FeaturePython' # if importing from stl, this will be 'Mesh::FeaturePython'
    def __init__(self, obj):
        # required for all object classes
        obj.Proxy = self
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')
        ViewProvider(obj.ViewObject)
        obj.ViewObject.ShapeColor = adapter_color
        self.mount_bolt = bolt_8_32

        _add_linked_object(obj, "mount", laser_mount_km100pm, pos_offset=(0, 0, 0))
    # this defines the component body and drilling
    def execute(self, obj):
        part = _custom_box(dx=0.01, dy=0.01, dz=0.01,
                           x=0, y=0, z=0.01)
        obj.Shape = part
        part.Placement = obj.Placement
        obj.DrillPart = part

class laser_mount_km100pm:
    """
    ECDL device 
    """
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, slot_length=0, countersink=False, counter_depth=3, arm_thickness=8, arm_clearance=2, stage_thickness=6, stage_length=20, mat_thickness=10, littrow_angle=56.6): 
        obj.Proxy = self
        # obj.addProperty("App::PropertyPlacement", "BasePlacement")
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'SlotLength').SlotLength = slot_length
        obj.addProperty('App::PropertyBool', 'Countersink').Countersink = countersink
        obj.addProperty('App::PropertyLength', 'CounterDepth').CounterDepth = counter_depth
        obj.addProperty('App::PropertyLength', 'ArmThickness').ArmThickness = arm_thickness
        obj.addProperty('App::PropertyLength', 'ArmClearance').ArmClearance = arm_clearance
        obj.addProperty('App::PropertyLength', 'StageThickness').StageThickness = stage_thickness
        obj.addProperty('App::PropertyLength', 'StageLength').StageLength = stage_length
        obj.addProperty('App::PropertyLength', 'MatThickness').MatThickness = mat_thickness
        obj.addProperty('App::PropertyAngle', 'LittrowAngle').LittrowAngle = littrow_angle
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)


        dx = -5.334+2.032
        mount = _add_linked_object(obj, "Mount KM100PM", prism_mount_km100pm, pos_offset=(2.032+13.96-3.8, -25.91+16, -18.67))
        _add_linked_object(obj, "Diode Adapter", diode_adapter_s05lm56, pos_offset=(0, 0, 0))
        _add_linked_object(obj, "Lens Tube", lens_tube_sm05l05, pos_offset=(dx+1.524+3.812, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s05tm09, pos_offset=(dx+1.524+5, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(dx+1.524+3.167+5, 0, 0))

        _add_linked_object(obj, "Mount", fixed_mount_smr05, pos_offset=(2.032, 0, 0), rot_offset=(90, 0, 0), drill=False)
        _add_linked_object(obj, "Wire Tube", wire_tube, pos_offset=(0, 0, -.5*inch), rot_offset=(0, 0, 0), drill=False)
        _add_linked_object(obj, "Brewster_window", brewster_window, pos_offset=(0, 20, 1*inch), rot_offset=(0, 0, 0), drill=False)

        gap =22
        lit_angle = radians(90-obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap/sin(2*beam_angle)
        ref_x = ref_len*cos(2*beam_angle)
        dx = ref_x+12.7*cos(lit_angle)+(6+3.2)*sin(lit_angle)
        extra_x = 20-dx
        grating_dx = -(6*sin(lit_angle)+12.7/2*cos(lit_angle))-extra_x
        mirror_dx = grating_dx-ref_x

        _add_linked_object(obj, "Grating", square_grating, pos_offset=(grating_dx+47, -2+5, -2.7), rot_offset=(0, 0, 180-obj.LittrowAngle.Value))
        _add_linked_object(obj, "PZT", box, pos_offset=(grating_dx+48.6, -7+5, -2.7), rot_offset=(0, 0, 180-obj.LittrowAngle.Value))
        _add_linked_object(obj, "Mirror", square_mirror, pos_offset=(mirror_dx+36.5, gap-3, -2.7), rot_offset=(0, 0, -obj.LittrowAngle.Value))

        upper_plate = _add_linked_object(obj, "Upper Plate", km05_tec_upper_plate, pos_offset=(2.032+13.96-3.8-13.96, 0, -inch/4-6.3), width=1.5*inch, drill_obj=mount)
        _add_linked_object(obj, "TEC", TEC, pos_offset=(grating_dx+20, 0, -33.7), rot_offset=(90, 90, 90))
        _add_linked_object(obj, "Lower Plate", km05_tec_lower_plate, pos_offset=(2.032+13.96-3.8-13.96, 0, 3.25*inch), width=3*inch)
        _add_linked_object(obj, "Box", laser_box, pos_offset=(0, 0, 0*inch), rot_offset=(0, 0, 0), mat_thickness=mat_thickness)

    def execute(self, obj):
        dx = obj.ArmThickness.Value
        dy = 45
        dz = 17
        stage_dx = obj.StageLength.Value
        stage_dz = obj.StageThickness.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz-obj.ArmClearance.Value,
                           x=0, y=4, z=obj.ArmClearance.Value)
        part = part.fuse(_custom_box(dx=stage_dx, dy=dy, dz=dz-obj.ArmClearance.Value,
                                     x=0, y=4, z=dz, dir=(1, 0, -1)))
        for ddy in [15.2, 38.1]:
            part = part.cut(_custom_box(dx=stage_dx+dx, dy=obj.SlotLength.Value+bolt_4_40['clear_dia'], dz=bolt_4_40['clear_dia'],
                                        x=stage_dx, y=25.4-ddy+2.5, z=6.4,
                                        fillet=bolt_4_40['clear_dia']/2, dir=(-1, 0, 0)))
            part = part.cut(_custom_box(dx=stage_dx+dx-5-4, dy=obj.SlotLength.Value+bolt_4_40['head_dia'], dz=bolt_4_40['head_dia'],
                                        x=stage_dx, y=25.4-ddy+2.5, z=6.4,
                                        fillet=bolt_4_40['head_dia']/2, dir=(-1, 0, 0)))
            
        extra_y = 0
        gap = 22
        lit_angle = radians(90-obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap/sin(2*beam_angle)
        ref_x = ref_len*cos(2*beam_angle)
        dx2 = ref_x+9.7*cos(lit_angle)+(6+3.2)*sin(lit_angle)
        extra_x = 18-dx2
        dy2 = gap+9.7*sin(lit_angle)+(6+3.2)*cos(lit_angle)
        dz2 = inch/2
        cut_x = 18.7*cos(lit_angle)

        part = part.fuse(_custom_box(dx=stage_dx+dx/2, dy=dy, dz=stage_dz+12.7,
                                     x=-dx/2, y=4, z=dz+12.7, dir=(1, 0, -1)))

        part.translate(App.Vector(dx/2, 25.4-15.2+obj.SlotLength.Value/2, -6.4))
        part.translate(App.Vector(2.032+13.96-3.8, -25.91+16, -18.67))
        part = part.fuse(part)

        temp = _custom_box(dx=ref_len*cos(beam_angle)+12.2, dy=dy/sin(lit_angle)+15, dz=dz,
                           x=-cut_x+9, y=-(dx-cut_x)*cos(lit_angle)-15, z=-6-3.07, dir=(-1, 1, 1))
        temp.rotate(App.Vector(-cut_x, 0, 0), App.Vector(0, 0, 1), -obj.LittrowAngle.Value)
        temp.translate(App.Vector(-extra_x+36, -20.7/2*sin(lit_angle)-6*cos(lit_angle), .2))

        part = part.cut(temp)
        part.Placement = obj.Placement
        obj.Shape = part

        # part = _bounding_box(obj, 3, 4, z_tol=True, min_offset=(0, 0, 0.668))
        # part.Placement = obj.Placement 
        obj.DrillPart = part

        #_add_linked_object(obj, "Box", laser_box, pos_offset=(0, 5, 0), rot_offset=(0, 0, 0), mat_thickness=0)

class laser_mount_km100pm_LMR1:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, slot_length=0, countersink=False, counter_depth=3, arm_thickness=8, arm_clearance=2, stage_thickness=6, stage_length=20, mat_thickness=0, littrow_angle=53.43): #54 for 674
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'SlotLength').SlotLength = slot_length
        obj.addProperty('App::PropertyBool', 'Countersink').Countersink = countersink
        obj.addProperty('App::PropertyLength', 'CounterDepth').CounterDepth = counter_depth
        obj.addProperty('App::PropertyLength', 'ArmThickness').ArmThickness = arm_thickness
        obj.addProperty('App::PropertyLength', 'ArmClearance').ArmClearance = arm_clearance
        obj.addProperty('App::PropertyLength', 'StageThickness').StageThickness = stage_thickness
        obj.addProperty('App::PropertyLength', 'StageLength').StageLength = stage_length
        obj.addProperty('App::PropertyLength', 'MatThickness').MatThickness = mat_thickness
        obj.addProperty('App::PropertyAngle', 'LittrowAngle').LittrowAngle = littrow_angle
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)


        dx = -5.334+2.032
        _add_linked_object(obj, "Diode Adapter", diode_adapter_s05lm56, pos_offset=(0, 0, 0))
        _add_linked_object(obj, "Lens Tube", lens_tube_sm05l05, pos_offset=(dx+1.524+3.812, 0, 0))
        _add_linked_object(obj, "Lens Adapter", lens_adapter_s05tm09, pos_offset=(dx+1.524+5, 0, 0))
        _add_linked_object(obj, "Lens", mounted_lens_c220tmda, pos_offset=(dx+1.524+3.167+5, 0, 0))

        mount = _add_linked_object(obj, "Mount KM100PM", prism_mount_km100pm, pos_offset=(2.032+13.96-3.8, -25.91+16, -18.67))
        _add_linked_object(obj, "Mount", fixed_mount_smr05, pos_offset=(2.032, 0, 0), rot_offset=(90, 0, 0), drill=False)
       # _add_linked_object(obj, "Box", laser_box, pos_offset=(-10, 0, 0), rot_offset=(0, 0, 0), mat_thickness=mat_thickness)
       # _add_linked_object(obj, "Base", laser_base, pos_offset=(0, 0, 0), rot_offset=(0, 0, 0), mat_thickness=mat_thickness)

        gap = 23
        lit_angle = radians(90-obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap/sin(2*beam_angle)
        ref_x = ref_len*cos(2*beam_angle)
        dx = ref_x+12.7*cos(lit_angle)+(6+3.2)*sin(lit_angle)
        extra_x = 20-dx
        grating_dx = -(6*sin(lit_angle)+12.7/2*cos(lit_angle))-extra_x
        mirror_dx = grating_dx-ref_x

        _add_linked_object(obj, "Grating", square_grating, pos_offset=(grating_dx+40, -1, -2.7), rot_offset=(0, 0, 180-obj.LittrowAngle.Value))
        _add_linked_object(obj, "PZT", box, pos_offset=(grating_dx+34.6+9.2, -5.8, -2.7), rot_offset=(0, 0, 180-obj.LittrowAngle.Value))
        _add_linked_object(obj, "Mirror", square_mirror, pos_offset=(mirror_dx+36.5, gap-3, -2.7), rot_offset=(0, 0, -obj.LittrowAngle.Value))

        upper_plate = _add_linked_object(obj, "Upper Plate", km05_tec_upper_plate, pos_offset=(2.032+13.96-3.8-13.96, 0, -inch/4-6.3), width=1.5*inch, drill_obj=mount)
        _add_linked_object(obj, "TEC", TEC, pos_offset=(grating_dx+11.1, 0, -33.7), rot_offset=(90, 90, 90))
        _add_linked_object(obj, "Lower Plate", km05_tec_lower_plate, pos_offset=(2.032+13.96-3.8-13.96, 0, -inch/4-6.3-4-upper_plate.Thickness.Value), width=2.5*inch)

    def execute(self, obj):
        dx = obj.ArmThickness.Value
        dy = 45
        dz = 27
        stage_dx = obj.StageLength.Value
        stage_dz = obj.StageThickness.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz-obj.ArmClearance.Value,
                           x=0, y=4, z=obj.ArmClearance.Value)
        part = part.fuse(_custom_box(dx=stage_dx, dy=dy, dz=dz-obj.ArmClearance.Value,
                                     x=0, y=4, z=dz, dir=(1, 0, -1)))
        for ddy in [15.2, 38.1]:
            part = part.cut(_custom_box(dx=stage_dx+dx, dy=obj.SlotLength.Value+bolt_4_40['clear_dia'], dz=bolt_4_40['clear_dia'],
                                        x=stage_dx, y=25.4-ddy+2.5, z=6.4,
                                        fillet=bolt_4_40['clear_dia']/2, dir=(-1, 0, 0)))
            part = part.cut(_custom_box(dx=stage_dx+dx-5-4, dy=obj.SlotLength.Value+bolt_4_40['head_dia'], dz=bolt_4_40['head_dia'],
                                        x=stage_dx, y=25.4-ddy+2.5, z=6.4,
                                        fillet=bolt_4_40['head_dia']/2, dir=(-1, 0, 0)))
            
        extra_y = 0
        gap = 23
        lit_angle = radians(90-obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap/sin(2*beam_angle)
        ref_x = ref_len*cos(2*beam_angle)
        dx2 = ref_x+12.7*cos(lit_angle)+(6+3.2)*sin(lit_angle)
        extra_x = 18-dx2
        dy2 = gap+12.7*sin(lit_angle)+(6+3.2)*cos(lit_angle)
        dz2 = inch/2
        cut_x = 17.7*cos(lit_angle)

        part = part.fuse(_custom_box(dx=stage_dx+dx/2, dy=dy, dz=stage_dz+12.7,
                                     x=-dx/2, y=4, z=dz+12.7, dir=(1, 0, -1)))

        part.translate(App.Vector(dx/2, 25.4-15.2+obj.SlotLength.Value/2, -6.4))
        part.translate(App.Vector(2.032+13.96-3.8, -25.91+16, -18.67))
        part = part.fuse(part)

        temp = _custom_box(dx=ref_len*cos(beam_angle)+6+3.2+3, dy=dy/sin(lit_angle)+15, dz=dz,
                           x=-cut_x+5, y=-(dx-cut_x)*cos(lit_angle)-15, z=-6-3.07, dir=(-1, 1, 1))
        temp.rotate(App.Vector(-cut_x, 0, 0), App.Vector(0, 0, 1),-obj.LittrowAngle.Value)
        temp.translate(App.Vector(-extra_x+36, -17.7/2*sin(lit_angle)-6*cos(lit_angle), .2))

        part = part.cut(temp)
        obj.Shape = part

        part = _bounding_box(obj, 3, 4, z_tol=True, min_offset=(0, 0, 0.668))
        part.Placement = obj.Placement
        obj.DrillPart = part

class mount_for_km100pm:
    '''
    Adapter for mounting isomet AOMs to km100pm kinematic mount

    Args:
        mount_offset (float[3]) : The offset position of where the adapter mounts to the component
        drill (bool) : Whether baseplate mounting for this part should be drilled
        slot_length (float) : The length of the slots used for mounting to the km100pm
        countersink (bool) : Whether to drill a countersink instead of a counterbore for the AOM mount holes
        counter_depth (float) : The depth of the countersink/bores for the AOM mount holes
        arm_thickness (float) : The thickness of the arm the mounts to the km100PM
        arm_clearance (float) : The distance between the bottom of the adapter arm and the bottom of the km100pm
        stage_thickness (float) : The thickness of the stage that mounts to the AOM
        stage_length (float) : The length of the stage that mounts to the AOM
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, slot_length=5, countersink=False, counter_depth=3, arm_thickness=8, arm_clearance=2, stage_thickness=4, stage_length=21):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'SlotLength').SlotLength = slot_length
        obj.addProperty('App::PropertyBool', 'Countersink').Countersink = countersink
        obj.addProperty('App::PropertyLength', 'CounterDepth').CounterDepth = counter_depth
        obj.addProperty('App::PropertyLength', 'ArmThickness').ArmThickness = arm_thickness
        obj.addProperty('App::PropertyLength', 'ArmClearance').ArmClearance = arm_clearance
        obj.addProperty('App::PropertyLength', 'StageThickness').StageThickness = stage_thickness
        obj.addProperty('App::PropertyLength', 'StageLength').StageLength = stage_length
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def execute(self, obj):
        dx = obj.ArmThickness.Value
        dy = 47.5
        dz = 16.92
        stage_dx = obj.StageLength.Value
        stage_dz = obj.StageThickness.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz-obj.ArmClearance.Value,
                           x=0, y=0, z=obj.ArmClearance.Value)
        part = part.fuse(_custom_box(dx=stage_dx, dy=dy, dz=stage_dz,
                                     x=0, y=0, z=dz, dir=(1, 0, -1)))
        for ddy in [15.2, 38.1]:
            part = part.cut(_custom_box(dx=dx, dy=obj.SlotLength.Value+bolt_4_40['clear_dia'], dz=bolt_4_40['clear_dia'],
                                        x=dx/2, y=25.4-ddy, z=6.4,
                                        fillet=bolt_4_40['clear_dia']/2, dir=(-1, 0, 0)))
            part = part.cut(_custom_box(dx=dx/2, dy=obj.SlotLength.Value+bolt_4_40['head_dia'], dz=bolt_4_40['head_dia'],
                                        x=dx/2, y=25.4-ddy, z=6.4,
                                        fillet=bolt_4_40['head_dia']/2, dir=(-1, 0, 0)))
        for ddy in [0, -11.42, -26.65, -38.07]:
            part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=stage_dz, head_dia=bolt_4_40['head_dia'],
                                        head_dz=obj.CounterDepth.Value, countersink=obj.Countersink,
                                        x=11.25, y=18.9+ddy, z=dz-4, dir=(0,0,1)))
        part.translate(App.Vector(dx/2, 25.4-15.2+obj.SlotLength.Value/2, -6.4))
        part = part.fuse(part)
        obj.Shape = part

        part = _bounding_box(obj, 3, 4, z_tol=True, min_offset=(0, 0, 0.668))
        part.Placement = obj.Placement
        obj.DrillPart = part

class lens_mount_fmp1:
    type = 'Mesh::FeaturePython'
    # type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, adapter_args = {}):#, thumbscrews=False):
        adapter_args.setdefault("mount_hole_dy", 35)
        adapter_args.setdefault("outer_thickness", 3)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        # obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')
        obj.ViewObject.ShapeColor = mount_color
        _add_linked_object(obj, 'surface_adapter', surface_adapter_wide, pos_offset=(1.5 ,0 ,-22.1 ),rot_offset=(0, 0, 0), **adapter_args)

    def execute(self, obj):
        # mesh = _import_stl("POLARIS-K05S2-Step.stl", (90, -0, -90), (-4.514, 0.254-20, -0.254))
        mesh = _import_stl("lens_mount_FMP1.stl", (90,0, 90), (4.65,0,0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class surface_adapter_wide:
    '''
    Surface adapter for post-mounted parts

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mount_hole_dy (float) : The spacing between the two mount holes of the adapter
        adapter_height (float) : The height of the suface adapter
        outer_thickness (float) : The thickness of the walls around the bolt holes
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_hole_dy=20, adapter_height=8, outer_thickness=2):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)
        self.drill_tolerance = 1

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        dz = obj.AdapterHeight.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=0, dir=(0, 0, -1),
                           fillet=5)
        part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                         head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                         x=0, y=0, z=-dz, dir=(0,0,1)))
        for i in [-1, 1]:
            part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                             head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
                                             x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        obj.Shape = part

        part = _bounding_box(obj, self.drill_tolerance, 6)
        for i in [-1, 1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        part.Placement = obj.Placement
        obj.DrillPart = part

#this is a square hollow
class square_hollow:
    """
    gemerate a square hollow on the baseplate
    """
    type = 'Mesh::FeaturePython'
    # type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True):#, thumbscrews=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        # obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
        # self.part_numbers = ['POLARIS-K05S2']

        # if thumbscrews:
        #     _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-15.03, 8.89, 8.89))
        #     _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-15.03, -8.89, -8.89))

    def execute(self, obj):
        # mesh = _import_stl("POLARIS-K05S2-Step.stl", (90, -0, -90), (-4.514, 0.254-20, -0.254))
        mesh = _import_stl("small_box__.stl", (90, -0, -90), (-4.514, 0.254-20, -0.254))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        # part = _custom_box(dx=0.1, dy=0.1, dz=0.1,
                        #    x=0, y=0, z=0, dir=(0, 0, 0))
        # obj.Shape = part
        # part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
        #                         x=-8.017, y=0, z=-layout.inch/2)
        # for i in [-1, 1]:
        part = _bounding_box(obj, 20,3,x_tol=True, y_tol=True, z_tol=True,min_offset=(0, 0, -40), max_offset=(70, 1000, 0), plate_off=-48)
        part.Placement = obj.Placement
        obj.DrillPart = part

class isomet_1205c_on_km100pm:
    '''
    Isomet 1205C AOM on KM100PM Mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        diffraction_angle (float) : The diffraction angle (in degrees) of the AOM
        forward_direction (integer) : The direction of diffraction on forward pass (1=right, -1=left)
        backward_direction (integer) : The direction of diffraction on backward pass (1=right, -1=left)

    Sub-Parts:
        prism_mount_km100pm (mount_args)
        mount_for_km100pm (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, diffraction_angle=degrees(0.01), forward_direction=1, backward_direction=1, mount_args=dict(), adapter_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyAngle', 'DiffractionAngle').DiffractionAngle = diffraction_angle
        obj.addProperty('App::PropertyInteger', 'ForwardDirection').ForwardDirection = forward_direction
        obj.addProperty('App::PropertyInteger', 'BackwardDirection').BackwardDirection = backward_direction

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['ISOMET_1205C']
        self.diffraction_angle = diffraction_angle
        self.diffraction_dir = (forward_direction, backward_direction)
        self.transmission = True
        self.max_angle = 10
        self.max_width = 5

        # TODO fix these parts to remove arbitrary translations
        _add_linked_object(obj, "Mount KM100PM", prism_mount_km100pm,
                           pos_offset=(-15.25, -20.15, -17.50), **mount_args)
        _add_linked_object(obj, "Adapter Bracket", mount_for_km100pm,
                           pos_offset=(-15.25, -20.15, -17.50), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("isomet_1205c.stl", (0, 0, 90), (0, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class isolator_670:
    '''
    Isolator Optimized for 670nm, Model IOT-5-670-VLP

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        surface_adapter (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 45)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IOT-5-670-VLP']
        self.transmission = True
        self.max_angle = 10
        self.max_width = 5

        _add_linked_object(obj, "Surface Adapter", surface_adapter,
                           pos_offset=(0, 0, -22.1), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("IOT-5-670-VLP-Step.stl", (90, 0, -90), (-19.05, -0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_box(dx=80, dy=25, dz=5,
                           x=0, y= 0, z=-layout.inch/2,
                           fillet=5, dir=(0, 0, -1))
        part.Placement = obj.Placement
        obj.DrillPart = part


class isolator_405:
    '''
    Isolator Optimized for 405nm, Model IO-3D-405-PBS

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        surface_adapter
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 36)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IO-3D-405-PBS']
        self.transmission = True
        self.max_angle = 10
        self.max_width = 5

        _add_linked_object(obj, "Surface Adapter", surface_adapter,
                           pos_offset=(0, 0, -17.15), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("IO-3D-405-PBS-Step.stl", (90, 0, -90), (-9.461, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_box(dx=25, dy=15, dz=drill_depth,
                           x=0, y=0, z=-layout.inch/2,
                           fillet=5, dir=(0, 0, 1))
        part.Placement = obj.Placement
        obj.DrillPart = part
class rb_cell_holder_old:
    '''
    Rubidium Cell Holder

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color

    def execute(self, obj):
        mesh = _import_stl("rb_cell_holder_middle.stl", (0, 0, 0), ([0, 5, 0]))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 6, 3)
        dx = 90
        for x, y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=x*dx/2, y=y*15.7, z=-layout.inch/2))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                     x=45, y=-15.7, z=-layout.inch/2))
        for x in [1,-1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=x*dx/2, y=25.7, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part
class photodiode_fds010:
    '''
    Photodiode, model FDS010
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = True
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['FDS010']
        self.max_angle = 0
        self.max_width = 1

    def execute(self, obj):
        mesh = _import_stl("FDS010-Step.stl", (-90, -90, 0), (-0.7, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _custom_cylinder(dia=8.5, dz=4,
                                x=0, y=0, z=0, dir=(1, 0, 0))
        part.Placement = obj.Placement
        obj.DrillPart = part
class rb_cell_cube:
    '''
    Rubidium Cell Holder

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, cube_size=10, mount_type=None, mount_args=dict(), drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'CubeSize').CubeSize = cube_size
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.transmission = True
        self.max_angle = 10
        self.max_width = 1

    def execute(self, obj):
        part = _custom_box(dx=obj.CubeSize.Value, dy=obj.CubeSize.Value, dz=obj.CubeSize.Value,
                           x=0, y=0, z=0, dir=(0, 0, 0))
        obj.Shape = part
        
        part = _bounding_box(obj, 0, 0)
        for x, y in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            part = part.fuse(_custom_cylinder(dia=5, dz=drill_depth,
                                            x=x*obj.CubeSize.Value/2, y=y*obj.CubeSize.Value/2, z=-obj.CubeSize.Value/2, dir=(0, 0, 1)))
        part.Placement = obj.Placement
        obj.DrillPart = part
# this is cylindrical rb_cell version, more used in demo
class rb_cell_cylindrical:
    '''
    Rubidium Cell Holder

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, mount_type=None, mount_args=dict(), drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = glass_color
        self.transmission = True
        self.max_angle = 10
        self.max_width = 1

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, **mount_args)

    def execute(self, obj):
        cell_dx = 80
        cell_dia = 22
        end_dia = 26
        part = _custom_cylinder(dia=cell_dia, dz=cell_dx,
                                x=-cell_dx/2, y=0, z=0,
                                dir=(1, 0, 0))
        part = part.fuse(_custom_cylinder(dia=end_dia, dz=8,
                                          x=-cell_dx/2, y=0, z=0,
                                          dir=(1, 0, 0)))
        part = part.fuse(_custom_cylinder(dia=end_dia, dz=8,
                                          x=cell_dx/2, y=0, z=0,
                                          dir=(-1, 0, 0)))
        
        obj.Shape = part

        temp = _bounding_box(obj, 0, 0, min_offset=(0, 0, cell_dia/2))
        part = part.fuse(temp)

        part.Placement = obj.Placement
        obj.DrillPart = part

# this is rb_cell with mount
class rb_cell:
    '''
    Rubidium Cell Holder

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill = True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        self.transmission = True
        self.max_angle = 10
        self.max_width = 1
    def execute(self, obj):
        mesh = _import_stl("rb_cell_holder_middle.stl", (0, 0, 0), ([0, 5, 0]))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 6, 3)
        dx = 90
        for x, y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=x*dx/2, y=y*15.7, z=-layout.inch/2))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                     x=45, y=-15.7, z=-layout.inch/2))
        for x in [1,-1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=x*dx/2, y=25.7, z=-layout.inch/2))
        part.Placement = obj.Placement
        obj.DrillPart = part


class rb_cell_new:
    #Rb cell with changed wall thickness and longer tube
    '''
    Rubidium Cell Holder

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = adapter_color
        self.transmission = True
        self.max_angle = 10
        self.max_width = 1

    def execute(self, obj):
        cell_dx = 88        #longer tibe, was 88
        cell_dia = 25
        end_dia = 28
        wall_thickness = 30    # Wall thickness was 15 mm before
        base_dy=5.75*inch
        dx = cell_dx+wall_thickness*2
        dy = cell_dia+wall_thickness*2
        dz = cell_dia+15*2
        base = _custom_box(dx=dx, dy=dy, dz=dz/2,
                           x=0, y=0, z=dz/2, dir=(0, 0, -1))
        base = base.fuse(_custom_box(dx=dx, dy=base_dy, dz=3/4*inch,
                           x=0, y=0, z=-(1/2*inch-dz/2), dir=(0, 0, -1)))
        cover = _custom_box(dx=dx, dy=dy, dz=dz/2,
                           x=0, y=0, z=dz/2, dir=(0, 0, 1))
        cover = cover.cut(_custom_box(dx=20, dy=dy/2, dz=5,
                           x=0, y=0, z=dz/2+2.5, dir=(0, -1, 0)))
        cell = _custom_cylinder(dia=cell_dia, dz=cell_dx,
                                x=-cell_dx/2, y=0, z=dz/2,
                                dir=(1, 0, 0))
        cell = cell.fuse(_custom_cylinder(dia=end_dia, dz=10,               # Longer tube, it was 10 mm before
                                          x=-cell_dx/2, y=0, z=dz/2,
                                          dir=(1, 0, 0)))
        cell = cell.fuse(_custom_cylinder(dia=end_dia, dz=10,               # longer tube, it was 10 mm before.
                                          x=cell_dx/2, y=0, z=dz/2,
                                          dir=(-1, 0, 0)))
        cell = cell.fuse( _custom_cylinder(dia=5, dz=dx,
                                           x=-dx/2, y=0, z=dz/2,
                                           dir=(1, 0, 0)))
        cell = cell.fuse(_custom_cylinder(dia=15, dz=cell_dia/2+10,
                                         x=0, y=0, z=dz/2,
                                         dir=(0, 1, 0)))
        
        base = base.cut(cell)
        cover = cover.cut(cell)

        for x, y in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            hole = _custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz/2,
                                    x=x*(dx/2-wall_thickness/2), y=y*(dy/2-wall_thickness/2), z=dz,
                                    head_dia=bolt_8_32['head_dia'], head_dz=dz/4)
            hole = hole.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=3/2*inch,
                                    x=x*(dx/2-wall_thickness/2), y=y*(dy/2-wall_thickness/2), z=dz/2))
            base = base.cut(hole)
            cover = cover.cut(hole)
            base = base.cut(_custom_cylinder(dia=bolt_14_20['clear_dia'], dz=inch,
                                             x=x*1.5*inch, y=y*2*inch, z=-(1/2*inch-dz/2),
                                             head_dia=bolt_14_20['washer_dia'], head_dz=10))

        base.translate(App.Vector(0, 0, -dz/2))
        cover.translate(App.Vector(0, 0, -dz/2))
   
        obj.Shape = Part.Compound([base, cover])

class telescope_track:
    '''
    a long track enables us to walk the distance of the lens of the telescope
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = mount_color
    def execute(self, obj):
        base_dx = 10 * layout.inch
        base_dy = 3 * layout.inch
        base_dz = 1 * layout.inch
        baseplate = _custom_box(dx=base_dx, dy=base_dy, dz=base_dz,
                           x=0, y=0, z=- layout.inch, dir=(1, 0, 0))
        baseplate = baseplate.fuse(_custom_box(dx=base_dx, dy=5, dz=20,x = 0, y = 9.125 + 2.5, z = -4, dir=(1,0,0)))
        baseplate = baseplate.fuse(_custom_box(dx=base_dx, dy=5, dz=20,x = 0, y = -9.125 - 2.5, z = -4, dir=(1,0,0)))
        part = _custom_cylinder(dia=bolt_14_20['clear_dia'], dz=drill_depth,
                                head_dia=bolt_14_20["washer_dia"], head_dz=10,
                                x=9.5 * layout.inch, y=1*layout.inch, z=-layout.inch / 2)
        baseplate = baseplate.cut(part)
        part = _custom_cylinder(dia=bolt_14_20['clear_dia'], dz=drill_depth,
                                head_dia=bolt_14_20["washer_dia"], head_dz=10,
                                x=0.5 * layout.inch, y=1*layout.inch, z=-layout.inch / 2)
        baseplate = baseplate.cut(part)
        part = _custom_cylinder(dia=bolt_14_20['clear_dia'], dz=drill_depth,
                                head_dia=bolt_14_20["washer_dia"], head_dz=10,
                                x=9.5 * layout.inch, y=-1 * layout.inch, z=-layout.inch / 2)
        baseplate = baseplate.cut(part)
        part = _custom_cylinder(dia=bolt_14_20['clear_dia'], dz=drill_depth,
                                head_dia=bolt_14_20["washer_dia"], head_dz=10,
                                x=0.5 * layout.inch, y=-1 * layout.inch, z=-layout.inch / 2)
        baseplate = baseplate.cut(part)
        baseplate.Placement = obj.Placement
        # obj.DrillPart = baseplate
        obj.Shape = baseplate


class photodetector_pda10a2:
    '''
    Photodetector, model pda10a2

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        surface_adapter (adapter_args)
    
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 60)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['PDA10A2']
        self.max_angle = 80
        self.max_width = 5

        _add_linked_object(obj, "Surface Adapter", surface_adapter, pos_offset=(-10.54, 0, -25), **adapter_args)
        _add_linked_object(obj, "Lens Tube", lens_tube_SM1L03, pos_offset=(-0.124, 0, -0))

    def execute(self, obj):
        mesh = _import_stl("PDA10A2-Step.stl", (90, 0, -90), (-19.87, -0, -0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 3, 4)
        part.Placement = obj.Placement
        obj.DrillPart = part

class lens_tube_SM1L03:
    '''
    SM1 Lens Tube, model SM1L03
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['SM1L03']
        self.max_angle = 0
        self.max_width = 1

    def execute(self, obj):
        mesh = _import_stl("SM1L03-Step.stl", (90, -0, 0), (8.382, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 3, z_tol=True, min_offset=(0, 4, 0), max_offset=(0, -4, 0))
        part.Placement = obj.Placement
        obj.DrillPart = part


class periscope:
    '''
    Custom periscope mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        lower_dz (float) : Distance from the bottom of the mount to the center of the lower mirror
        upper_dz (float) : Distance from the bottom of the mount to the center of the upper mirror
        mirror_type (obj class) : Object class of mirrors to be used
        table_mount (bool) : Whether the periscope is meant to be mounted directly to the optical table

    Sub-Parts:
        mirror_type x2 (mirror_args)
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, lower_dz=1.5*inch, upper_dz=3*inch, invert=True, mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'LowerHeight').LowerHeight = lower_dz
        obj.addProperty('App::PropertyLength', 'UpperHeight').UpperHeight = upper_dz
        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert

        obj.ViewObject.ShapeColor = adapter_color
        if obj.Baseplate == None:
            self.z_off = -layout.inch*3/2
        else:
            self.z_off = 0

        _add_linked_object(obj, "Lower Mirror", circular_mirror, rot_offset=((-1)**invert*90, -45, 0), pos_offset=(0, 0, obj.LowerHeight.Value+self.z_off), **mirror_args)
        _add_linked_object(obj, "Upper Mirror", circular_mirror, rot_offset=((-1)**invert*90, 135, 0), pos_offset=(0, 0, obj.UpperHeight.Value+self.z_off), **mirror_args)

    def execute(self, obj):
        width = 2*inch #Must be inch wide to keep periscope mirrors 1 inch from mount holes. 
        fillet = 15
        part = _custom_box(dx=70, dy=width, dz=obj.UpperHeight.Value+20,
                           x=0, y=0, z=0)
        for i in [-1, 1]:
            part = part.cut(_custom_box(dx=fillet*2+4, dy=width, dz=obj.UpperHeight.Value+20,
                                        x=i*(35+fillet), y=0, z=20, fillet=15,
                                        dir=(-i,0,1), fillet_dir=(0,1,0)))
            for y in [-inch/2, inch/2]:
                part = part.cut(_custom_cylinder(dia=bolt_14_20['clear_dia']+0.5, dz=inch+5,
                                            head_dia=bolt_14_20['head_dia']+0.5, head_dz=10,
                                            x=i*inch, y=y, z=25, dir=(0,0,-1)))
        part.translate(App.Vector(0, (-1)**obj.Invert*(width/2+inch/2), self.z_off))
        part = part.fuse(part)
        for i in obj.ChildObjects:
            part = _drill_part(part, obj, i)
        obj.Shape = part

class periscope_for_redstone:
    '''
    Custom periscope mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        lower_dz (float) : Distance from the bottom of the mount to the center of the lower mirror
        upper_dz (float) : Distance from the bottom of the mount to the center of the upper mirror
        mirror_type (obj class) : Object class of mirrors to be used
        table_mount (bool) : Whether the periscope is meant to be mounted directly to the optical table

    Sub-Parts:
        mirror_type x2 (mirror_args)
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, lower_dz=1.5*inch, upper_dz=3*inch, invert=True, mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'LowerHeight').LowerHeight = lower_dz
        obj.addProperty('App::PropertyLength', 'UpperHeight').UpperHeight = upper_dz
        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert

        # obj.ViewObject.ShapeColor = adapter_color
        if obj.Baseplate == None:
            self.z_off = -layout.inch*3/2
        else:
            self.z_off = 0

        # _add_linked_object(obj, "Lower Mirror", circular_mirror, rot_offset=((-1)**invert*90, -45, 0), pos_offset=(0, 0, obj.LowerHeight.Value+self.z_off), **mirror_args)
        # _add_linked_object(obj, "Upper Mirror", circular_mirror, rot_offset=((-1)**invert*90, 135, 0), pos_offset=(0, 0, obj.UpperHeight.Value+self.z_off), **mirror_args)
        # for i in range(6):
        #     for j in range(6):
        #         _add_linked_object(obj, 'Upper Mirror' + str(i) + str(j), circular_mirror, rot_offset=(135,90,45), pos_offset=(-110 +  i * 35, 100 -  j * 24, 20 +  j * 24 ), **mirror_args)

        #         _add_linked_object(obj, 'Lower Mirror' + str(i) + str(j), circular_mirror, rot_offset=(0, 0, 45), pos_offset=(- 110 + j * 35, 250 - j * 24, 20 +  i * 27), **mirror_args)
                

    def execute(self, obj):
        width = 0.8*inch 
        # mesh = _import_stl("baseplate_for_periscope_redstone.stl", rotate=(0, 0, 0), translate=(0, 0, 3))
        
        # mesh.Placement = obj.Mesh.Placement

        # obj.Mesh = mesh
        part = _custom_box(dx=210, dy=  1.1 * width, dz=obj.UpperHeight.Value + 78,
                           x=-20, y= - 20, z=0)
        
        for i in range(6): # lower
            part = part.fuse(_custom_box(dx=1.7 * width  , dy=150 + 18 - (i + 1 )*25 , dz=obj.UpperHeight.Value + 95   ,
                           x= 100 - (i + 1 )*35, y=200 + width + (i + 1 )*12.5, z=0))

        for i in range(6): # upper
            part = part.fuse(_custom_box(dx=210  , dy=1.2 * width, dz=obj.UpperHeight.Value + 78 - (i + 1 )*23 ,
                           x= -20, y= -20 +  1.1 * width * (i+1), z=-3))
        part.translate(App.Vector(0, (-1)**obj.Invert*(width/2+inch/2), 0))
        part.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
        part = part.fuse(part)
        # # for i in obj.ChildObjects:
        # #     part = _drill_part(part, obj, i)
        obj.Shape = part
        part.Placement = obj.Placement
        obj.DrillPart = part

class thumbscrew_hkts_5_64:
    '''
    Thumbscrew for 5-64 hex adjusters, model HKTS 5-64

    Sub-Parts:
        slide_mount (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, adapter_args=dict()):
        adapter_args.setdefault("slot_length", 10)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['HKTS-5/64(P4)']

    def execute(self, obj):
        mesh = _import_stl("HKTS-5_64-Step.stl", (90, 0, 90), (-11.31, -0.945, 0.568))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 3, z_tol=True, min_offset=(-6, 0, 0), max_offset=(-6, 0, 0))
        part.Placement = obj.Placement
        obj.DrillPart = part

class fiber_adapter_sm05fca2:
    '''
    Fiber Adapter Plate, model SM05FCA2
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['SM05FCA2']
        self.max_angle = 0
        self.max_width = 1

    def execute(self, obj):
        mesh = _import_stl("SM05FCA2-Step.stl", (0, 90, 0), (-2.334, -3.643, -0.435))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class fiber_adapter_sm1fca2:
    '''
    Fiber Adapter Plate, model SM1FCA2
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['SM1FCA2']
        self.max_angle = 0
        self.max_width = 1

    def execute(self, obj):
        mesh = _import_stl("SM1FCA2-Step.stl", (-180, 90, 0), (-12.47, -0.312, 15.41))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class lens_adapter_s05tm09:
    '''
    SM05 to M9x0.5 Lens Cell Adapter, model S05TM09
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['S05TM09']

    def execute(self, obj):
        mesh =  _import_stl("S05TM09-Step.stl", (90, 0, -90), (6.973, 0, -0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class lens_adapter_s1tm09:
    '''
    SM1 to M9x0.5 Lens Cell Adapter, model S1TM09
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['S1TM09']

    def execute(self, obj):
        mesh =  _import_stl("S1TM09-Step.stl", (90, 0, 90), (-3.492, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class lens_tube_sm05l05:
    '''
    Lens Tube, model SM05L05
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['SM05L05']

    def execute(self, obj):
        mesh = _import_stl("SM05L05-Step.stl", (90, 0, -90), (0, 0, -0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class lens_tube_sm1l05:
    '''
    Lens Tube, model SM1L05
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['SM1L05']

    def execute(self, obj):
        mesh = _import_stl("SM1L05-Step.stl", (90, -0, 0), (13.46, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = _bounding_box(obj, 2, 3, z_tol=True)
        part.Placement = obj.Placement
        obj.DrillPart = part


class mounted_lens_c220tmda:
    '''
    Mounted Aspheric Lens, model C220TMD-A
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = ['C220TMD-A']

    def execute(self, obj):
        mesh = _import_stl("C220TMD-A-Step.stl", (-90, 0, -180), (0.419, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class diode_adapter_s05lm56:
    '''
    Diode Mount Adapter, model S05LM56
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['S05LM56']

    def execute(self, obj):
        mesh = _import_stl("S05LM56-Step.stl", (90, 0, -90), (0, 0, -0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class Room_temp_chamber:
    '''
    importing the room temperature schamber
    Room_temperature_Chamber_simplified_version

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['Room_temp_chamber']

    def execute(self, obj):
        mesh = _import_stl("Room_temp_chamber_step.stl", (0, 0, 0), (-48.89, 1.266, 0.813))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class Room_temp_chamber_Mechanical:
    '''
    importing the room temperature schamber
    Room_temperature_Chamber_version

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['Room_temp_chamber']

    def execute(self, obj):
        mesh = _import_stl("Room Temp Chamber Mechanical.stl", (0, 0, 0), (-33.46, -10.12, -59.69))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        
class Room_temp_chamber_Mechanical_with_chip:
    '''
    importing the room temperature schamber
    Room_temperature_Chamber_version

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['Room_temp_chamber']

    def execute(self, obj):
        mesh = _import_stl("room temperature chamber with chip.stl", (0, 0, 45), (-33.46, -10.12, -59.69))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
class TEC:
    '''
    importing the room temperature schamber
    Room_temperature_Chamber_version

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['TEC']

    def execute(self, obj):
        mesh =  _import_stl("TEC.stl", (180, 0, 90), (0, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh        

class box:

    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, thickness=3, width=10, height=10, part_number=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = [part_number]

    def execute(self, obj):
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part

class square_grating:
    '''
    Square Grating

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        thickness (float) : The thickness of the grating
        width (float) : The width of the grating
        height (float) : The height of the grating
        part_number (string) : The part number of the grating being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, thickness=6, width=12.7, height=12.7, part_number=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = [part_number]
        self.reflection_angle = 0
        self.max_angle = 90
        self.max_width = width

    def execute(self, obj):
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part


class circular_splitter:
    '''
    Circular Beam Splitter Plate

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        thickness (float) : The edge thickness of the plate
        diameter (float) : The width of the plate
        part_number (string) : The part number of the plate being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, thickness=3, diameter=inch/2, part_number='', mount_type=None, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, pos_offset=(-thickness, 0, 0), **mount_args)

        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.part_numbers = [part_number]
        self.transmission = True
        self.reflection_angle = 0
        self.max_angle = 90
        self.max_width = diameter

    def execute(self, obj):
        part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part

class cube_splitter:
    '''
    Beam-splitter cube

    Args:
        cube_size (float) : The side length of the splitter cube
        invert (bool) : Invert pick-off direction, false is left, true is right
        cube_part_number (string) : The Thorlabs part number of the splitter cube being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, cube_size=10, invert=False, cube_part_number='', mount_type=None, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'CubeSize').CubeSize = cube_size
        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert

        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.part_numbers = [cube_part_number]
        
        if invert:
            self.reflection_angle = -135
        else:
            self.reflection_angle = 135
        self.transmission = True
        self.max_angle = 90
        self.max_width = sqrt(200)

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, pos_offset=(0, 0, -cube_size/2), **mount_args)

    def execute(self, obj):
        part = _custom_box(dx=obj.CubeSize.Value, dy=obj.CubeSize.Value, dz=obj.CubeSize.Value,
                           x=0, y=0, z=0, dir=(0, 0, 0))
        temp = _custom_box(dx=sqrt(200)-0.25, dy=0.1, dz=obj.CubeSize.Value-0.25,
                           x=0, y=0, z=0, dir=(0, 0, 0))
        temp.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), -self.reflection_angle)
        part = part.cut(temp)
        obj.Shape = part

class ruler_125mm:
    '''
    125mm ruler
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, focal_length=50, thickness=3, diameter=inch/2, part_number='', mount_type=None, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'FocalLength').FocalLength = focal_length
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, pos_offset=(-thickness/2, 0, 0), **mount_args)

        obj.ViewObject.ShapeColor = (0,0,1)
        obj.ViewObject.Transparency=0
        self.part_numbers = [part_number]
        self.transmission = True
        self.focal_length = obj.FocalLength.Value
        self.max_angle = 90
        self.max_width = diameter

    def execute(self, obj):
        part = _custom_cylinder(dia=2, dz=125,
                                x=0, y=0, z=0, dir=(1, 0, 0))
        obj.Shape = part

class circular_lens:
    '''
    Circular Lens

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        focal_length (float) : The focal length of the lens
        thickness (float) : The edge thickness of the lens
        diameter (float) : The width of the lens
        part_number (string) : The part number of the lens being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, focal_length=50, thickness=3, diameter=inch/2, part_number='', mount_type=None, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'FocalLength').FocalLength = focal_length
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, pos_offset=(-thickness/2, 0, 0), **mount_args)

        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.part_numbers = [part_number]
        self.transmission = True
        self.focal_length = obj.FocalLength.Value
        self.max_angle = 90
        self.max_width = diameter

    def execute(self, obj):
        part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
                                x=-obj.Thickness.Value/2, y=0, z=0, dir=(1, 0, 0))
        obj.Shape = part


class cylindrical_lens:
    '''
    Cylindrical Lens

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        focal_length (float) : The focal length of the lens
        thickness (float) : The edge thickness of the lens
        width (float) : The width of the lens
        height (float) : The width of the lens
        part_number (string) : The part number of the lens being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, focal_length=50, thickness=4, width=20, height=22, slots=False, part_number='', mount_type=skate_mount, mount_args=dict()):
        mount_args.setdefault("cube_dx", thickness)
        mount_args.setdefault("cube_dy", width)
        mount_args.setdefault("cube_dz", height)
        mount_args.setdefault("mount_hole_dy", width+10)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'FocalLength').FocalLength = focal_length
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, pos_offset=(thickness/2, 0, -height/2), mount_hole_dy=width+10, cube_dy=width, cube_dz=height, cube_dx=thickness, slots=slots)

        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.part_numbers = [part_number]
        self.transmission = True
        self.focal_length = obj.FocalLength.Value
        self.max_angle = 90
        self.max_width = width

    def execute(self, obj):
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=0, y=0, z=0,
                           dir=(1, 0, 0))
        obj.Shape = part


class waveplate:
    '''
    Waveplate

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        thickness (float) : The thickness of the waveplate
        diameter (float) : The width of the waveplate
        part_number (string) : The part number of the waveplate being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, thickness=1, diameter=inch/2, part_number='', mount_type=None, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, pos_offset=(-thickness/2, 0, 0), **mount_args)

        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.part_numbers = [part_number]
        self.transmission = True
        self.max_angle = 90
        self.max_width = diameter

    def execute(self, obj):
        part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
                                x=-obj.Thickness.Value/2, y=0, z=0, dir=(1, 0, 0))
        obj.Shape = part


class circular_mirror:
    '''
    Circular Mirror

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        thickness (float) : The thickness of the mirror
        diameter (float) : The width of the mirror
        part_number (string) : The part number of the mirror being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, thickness=6, diameter=inch/2, part_number='', mount_type=None, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, pos_offset=(-thickness, 0, 0), **mount_args)

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = [part_number]
        self.reflection_angle = 0
        self.max_angle = 90
        self.max_width = diameter

    def execute(self, obj):
        part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part

class moon_mirror:
    '''
    Circular Mirror

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        thickness (float) : The thickness of the mirror
        diameter (float) : The width of the mirror
        part_number (string) : The part number of the mirror being used
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, thickness=6, diameter=inch/2, part_number='', mount_type=None, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        if mount_type != None:
            _add_linked_object(obj, "Mount", mount_type, pos_offset=(4.5, -3.5, 0), **mount_args)

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = [part_number]
        self.reflection_angle = 0
        self.max_angle = 90
        self.max_width = diameter

    def execute(self, obj):
        mesh = _import_stl("BBD05-E02-Step.stl", (-30,-120,-30), (-3,1, 4))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh        


class square_mirror:
    '''
    Square Mirror

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        thickness (float) : The thickness of the mirror
        width (float) : The width of the mirror
        height (float) : The height of the mirror
        part_number (string) : The part number of the mirror being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, thickness=3.2, width=12.7, height=12.7, part_number=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = [part_number]
        self.reflection_angle = 0
        self.max_angle = 90
        self.max_width = width

    def execute(self, obj):
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part


class ViewProvider:
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        return

    def getDefaultDisplayMode(self):
        return "Shaded"

    def onDelete(self, feature, subelements):
        if hasattr(feature.Object, "ParentObject"):
            if feature.Object.ParentObject != None:
                return False
        if hasattr(feature.Object, "ChildObjects"):
            for obj in feature.Object.ChildObjects:
                App.ActiveDocument.removeObject(obj.Name)
        return True
    
    def updateData(self, obj, prop):
        if str(prop) == "BasePlacement":
            if obj.Baseplate != None:
                obj.Placement.Base = obj.BasePlacement.Base + obj.Baseplate.Placement.Base
                obj.Placement = App.Placement(obj.Placement.Base, obj.Baseplate.Placement.Rotation, -obj.BasePlacement.Base)
                obj.Placement.Rotation = obj.Placement.Rotation.multiply(obj.BasePlacement.Rotation)
            else:
                obj.Placement = obj.BasePlacement
            if hasattr(obj, "ChildObjects"):
                for child in obj.ChildObjects:
                    child.BasePlacement.Base = obj.BasePlacement.Base + child.RelativePlacement.Base
                    if hasattr(child, "Angle"):
                        obj.BasePlacement.Rotation = App.Rotation(App.Vector(0, 0, 1), obj.Angle)
                    else:
                        child.BasePlacement = App.Placement(child.BasePlacement.Base, obj.BasePlacement.Rotation, -child.RelativePlacement.Base)
                        child.BasePlacement.Rotation = child.BasePlacement.Rotation.multiply(child.RelativePlacement.Rotation)
            if hasattr(obj, "RelativeObjects"):
                for child in obj.RelativeObjects:
                    child.BasePlacement.Base = obj.BasePlacement.Base + child.RelativePlacement.Base
        if str(prop) == "Angle":
            obj.BasePlacement.Rotation = App.Rotation(App.Vector(0, 0, 1), obj.Angle)
        return
    
    def claimChildren(self):
        if hasattr(self.Object, "ChildObjects"):
            return self.Object.ChildObjects
        else:
            return []

    def getIcon(self):
        return """
            /* XPM */
            static char *_e94ebdf19f64588ceeb5b5397743c6amoxjrynTrPg9Fk5U[] = {
            /* columns rows colors chars-per-pixel */
            "16 16 2 1 ",
            "  c None",
            "& c red",
            /* pixels */
            "                ",
            "  &&&&&&&&&&&&  ",
            "  &&&&&&&&&&&&  ",
            "  &&&&&&&&&&&&  ",
            "  &&&&&&&&&&&&  ",
            "      &&&&      ",
            "      &&&&      ",
            "      &&&&      ",
            "      &&&&      ",
            "      &&&&      ",
            "      &&&&      ",
            "      &&&&      ",
            "      &&&&      ",
            "      &&&&      ",
            "      &&&&      ",
            "                "
            };
            """

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
    


####################################### ARXIV #######################################
# just rotate it 90 degrees but do not want to change other code....
# class circular_mirror_rot90:
#     '''
#     Circular Mirror

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         thickness (float) : The thickness of the mirror
#         diameter (float) : The width of the mirror
#         part_number (string) : The part number of the mirror being used
#     '''
#     type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True, thickness=6, diameter=inch/2, part_number='', mount_type=None, mount_args=dict()):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
#         obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

#         if mount_type != None:
#             _add_linked_object(obj, "Mount", mount_type, pos_offset=(-thickness, 0, 0), rot_offset=(0, 0, 90), **mount_args)

#         obj.ViewObject.ShapeColor = glass_color
#         self.part_numbers = [part_number]
#         self.reflection_angle = 0
#         self.max_angle = 90
#         self.max_width = diameter

#     def execute(self, obj):
#         part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
#                            x=0, y=0, z=0, dir=(-1, 0, 0))
#         obj.Shape = part
# this is zhenyu editing
# class circular_splitter_rot90:
#     '''
#     Circular Beam Splitter Plate

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         thickness (float) : The edge thickness of the plate
#         diameter (float) : The width of the plate
#         part_number (string) : The part number of the plate being used
#     '''
#     type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True, thickness=3, diameter=inch/2, part_number='', mount_type=None, mount_args=dict()):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
#         obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

#         if mount_type != None:
#             _add_linked_object(obj, "Mount", mount_type, pos_offset=(-thickness, 0, 0), rot_offset=(0, 0, 0), **mount_args)

#         obj.ViewObject.ShapeColor = glass_color
#         obj.ViewObject.Transparency=50
#         self.part_numbers = [part_number]
#         self.transmission = True
#         self.reflection_angle = 0
#         self.max_angle = 90
#         self.max_width = diameter

#     def execute(self, obj):
#         part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
#                            x=0, y=0, z=0, dir=(-1, 0, 0))
#         obj.Shape = part
#this is zhenyu editing
# class lens_mount_optosigma_TSD_1inch_in:
#     type = 'Mesh::FeaturePython'
#     # type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True):#, thumbscrews=False):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         # obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
#         obj.addProperty('Part::PropertyPartShape', 'DrillPart')
#         obj.ViewObject.ShapeColor = mount_color

#     def execute(self, obj):
#         # mesh = _import_stl("POLARIS-K05S2-Step.stl", (90, -0, -90), (-4.514, 0.254-20, -0.254))
#         mesh = _import_stl("lens_mount_optosigma_tsd_1inch_in.stl", (0, 0, 180), (16,-135.8,0))
#         mesh.Placement = obj.Mesh.Placement
#         obj.Mesh = mesh
#         # part = _bounding_box(obj, 2,3)#,x_tol=True, y_tol=True, z_tol=True,min_offset=(0, 0, -40), max_offset=(40, 95, 0), plate_off=-28)
#         # part.Placement = obj.Placement
#         # obj.DrillPart = part
# class lens_mount_optosigma_TSD:
#     type = 'Mesh::FeaturePython'
#     # type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True):#, thumbscrews=False):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         # obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
#         obj.addProperty('Part::PropertyPartShape', 'DrillPart')
#         obj.ViewObject.ShapeColor = mount_color

#     def execute(self, obj):
#         # mesh = _import_stl("POLARIS-K05S2-Step.stl", (90, -0, -90), (-4.514, 0.254-20, -0.254))
#         mesh = _import_stl("lens_mount_optosigma_TSD.stl", (0, 0, 180), (-10,-135.8,0))
#         mesh.Placement = obj.Mesh.Placement
#         obj.Mesh = mesh
#         part = _bounding_box(obj, 2,3)#,x_tol=True, y_tol=True, z_tol=True,min_offset=(0, 0, -40), max_offset=(40, 95, 0), plate_off=-28)
#         part.Placement = obj.Placement
#         obj.DrillPart = part
# class lens_mount_MT3A:
#     type = 'Mesh::FeaturePython'
#     # type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True):#, thumbscrews=False):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         # obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
#         obj.addProperty('Part::PropertyPartShape', 'DrillPart')
#         obj.ViewObject.ShapeColor = mount_color

#     def execute(self, obj):
#         # mesh = _import_stl("POLARIS-K05S2-Step.stl", (90, -0, -90), (-4.514, 0.254-20, -0.254))
#         mesh = _import_stl("MT3A_translation_stage.stl", (90, 0, 90), (-30,158,-70))
#         mesh.Placement = obj.Mesh.Placement
#         obj.Mesh = mesh
#         # part = _custom_box(dx=0.1, dy=0.1, dz=0.1,
#                         #    x=0, y=0, z=0, dir=(0, 0, 0))
#         # obj.Shape = part
#         # part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
#         #                         x=-8.017, y=0, z=-layout.inch/2)
#         # for i in [-1, 1]:
#         # part = _bounding_box(obj, 2,3)#,x_tol=True, y_tol=True, z_tol=True,min_offset=(0, 0, -40), max_offset=(40, 95, 0), plate_off=-28)
#         # part.Placement = obj.Placement
#         # obj.DrillPart = part
#This is zhenyu editing
# class surface_adapter_lying_down:
#     '''
#     Surface adapter for post-mounted parts

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         mount_hole_dy (float) : The spacing between the two mount holes of the adapter
#         adapter_height (float) : The height of the suface adapter
#         outer_thickness (float) : The thickness of the walls around the bolt holes
#     '''
#     type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True, mount_hole_dy=20, adapter_height=8, outer_thickness=2):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
#         obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
#         obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
#         obj.addProperty('Part::PropertyPartShape', 'DrillPart')

#         obj.ViewObject.ShapeColor = adapter_color
#         obj.setEditorMode('Placement', 2)
#         self.drill_tolerance = 0.2 * inch

#     def execute(self, obj):
#         dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
#         dy = dx+obj.MountHoleDistance.Value
#         dz = obj.AdapterHeight.Value

#         part = _custom_box(dx=dx, dy=dy, dz=dz,
#                            x=0, y=0, z=0, dir=(0, 0, -1),
#                            fillet=5)
#         part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
#                                          head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
#                                          x=0, y=0, z=-dz, dir=(0,0,1)))
#         for i in [-1, 1]:
#             part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
#                                              head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
#                                              x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
#         obj.Shape = part

#         part = _bounding_box(obj, self.drill_tolerance, 2,x_tol=1.7,y_tol=0.5,z_tol=True, plate_off=26,min_offset=(0,0,5), max_offset=(0,0,5))
#         for i in [-1, 1]:
#             part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
#                                               x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
#         part.Placement = obj.Placement
#         obj.DrillPart = part
#This is zhenyu editing
# class surface_adapter_4_40:
#     '''
#     Surface adapter for post-mounted parts

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         mount_hole_dy (float) : The spacing between the two mount holes of the adapter
#         adapter_height (float) : The height of the suface adapter
#         outer_thickness (float) : The thickness of the walls around the bolt holes
#     '''
#     type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True, mount_hole_dy=20, adapter_height=8, outer_thickness=5):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
#         obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
#         obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
#         obj.addProperty('Part::PropertyPartShape', 'DrillPart')

#         obj.ViewObject.ShapeColor = adapter_color
#         obj.setEditorMode('Placement', 2)
#         self.drill_tolerance = 1#0.2 * inch

#     def execute(self, obj):
#         dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
#         dy = dx+obj.MountHoleDistance.Value
#         dz = obj.AdapterHeight.Value

#         part = _custom_box(dx=dx+5, dy=dy, dz=dz ,
#                            x=0, y=0, z=0, dir=(0, 0, -1),
#                            fillet=5)
#         part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=dz,
#                                          head_dia=bolt_4_40['head_dia'], head_dz=bolt_4_40['head_dz'],
#                                          x=0, y=0, z=-dz, dir=(0,0,1)))
#         part = part.cut(_custom_box(dx = 30,dy = 15.21, dz = 17 , x = 0.05, y = 0.69, z = -5, fillet = 1))
#         for x_ in np.linspace(-2.5,2.5,20):
#             for i in [-1, 1]:
#                 part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
#                                                 head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
#                                                 x=x_, y=i*obj.MountHoleDistance.Value/2, z=0))
#         obj.Shape = part

#         # part = _bounding_box(obj, self.drill_tolerance, 6,x_tol=1.7,y_tol=0.5,z_tol=True,plate_off=1,min_offset=(0,0,0), max_offset=(0,0,0))
#         # part = _bounding_box(obj, self.drill_tolerance, 6)
#         for i in [-1, 1]:
#             part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
#                                               x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
#         part.Placement = obj.Placement
#         obj.DrillPart = part
#This is zhenyu editing:
# class mirror_mount_km100:
#     '''
#     Mirror mount, model KM100

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         mirror (bool) : Whether to add a mirror component to the mount
#         thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
#         bolt_length (float) : The length of the bolt used for mounting

#     Sub-Parts:
#         circular_mirror (mirror_args)
#     '''
#     type = 'Mesh::FeaturePython'
#     def __init__(self, obj, drill=True):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('Part::PropertyPartShape', 'DrillPart')

#         obj.ViewObject.ShapeColor = mount_color
#         self.part_numbers = ['KM100']

#     def execute(self, obj):
#         mesh = _import_stl("KM100-Step.stl", (-180, 0, -90), (4.972, 0.084, -1.089))
#         mesh.Placement = obj.Mesh.Placement
#         obj.Mesh = mesh
# class mirror_mount_km05_lying_down:
#     '''
#     Mirror mount, model KM05

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         mirror (bool) : Whether to add a mirror component to the mount
#         thumbscrews (bool): Whether or not to add two HKTS 5-64 adjusters
#         bolt_length (float) : The length of the bolt used for mounting

#     Sub-Parts:
#         circular_mirror (mirror_args)
#     '''
#     type = 'Mesh::FeaturePython'
#     def __init__(self, obj, drill=True, thumbscrews=False, bolt_length=15):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('App::PropertyBool', 'ThumbScrews').ThumbScrews = thumbscrews
#         obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length
#         obj.addProperty('Part::PropertyPartShape', 'DrillPart')

#         obj.ViewObject.ShapeColor = mount_color
#         self.part_numbers = ['KM05']

#         if thumbscrews:
#             _add_linked_object(obj, "Upper Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, 9.906, 9.906))
#             _add_linked_object(obj, "Lower Thumbscrew", thumbscrew_hkts_5_64, pos_offset=(-10.54, -9.906, -9.906))

#     def execute(self, obj):
#         mesh = _import_stl("KM05-Step.stl", (90, -0, 90), (2.084, -1.148, 0.498))
#         mesh.Placement = obj.Mesh.Placement
#         obj.Mesh = mesh

#         part = _bounding_box(obj, 2, 3, min_offset=(4.35, 0, 0))
#         part = part.fuse(_bounding_box(obj, 2, 3, max_offset=(0, -20, 0)))
#         part = part.fuse(_bounding_box(obj, 2, 3, min_offset=(-20, 0, 0)))
#         part = _fillet_all(part, 3)
#         part = part.fuse(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=inch,
#                                           head_dia=bolt_8_32['head_dia'], head_dz=0.92*inch-obj.BoltLength.Value,
#                                           x=-7.29, y=0, z=-inch*3/2, dir=(0,0,1)))
#         part.Placement = obj.Placement
#         obj.DrillPart = part
#this is zhenyu editing:
# class grid_waveplate_lying_down:
#     '''
#     waveplate grid, fixed as 6 * 6

#     coordinates of waveplate:
#     x=(2 * i + 1.25) * layout.inch, y=(2 * j + 1.25) * layout.inch
#     size of grid:
#     base_dx = 2.1 * layout.inch
#     base_dy = 2.1 * layout.inch
#     base_dz = 1 * layout.inch
#     size = base_dx*Row_numnber, base_dy*Column_number
#     '''
#     type = 'Mesh::FeaturePython'
#     def __init__(self, obj):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)
#         for i in range(6):
#             for j in range(6):
#                 _add_linked_object(obj, 'waveplate_' + str(i) + str(j), waveplate, pos_offset=( (2 * i + 1.25) * layout.inch,-26.5, -(2 * j + 1.25) * layout.inch),rot_offset=(0, 0, 90))
#                 _add_linked_object(obj, 'rotation stage' + str(i) + str(j), rotation_stage_rsp05_lying_down, pos_offset=( (2 * i + 1.25) * layout.inch,-26.5, -(2 * j + 1.25) * layout.inch),rot_offset=(0, 0, 90))
#                 # _add_linked_object(obj, 'mount_' + str(i) + str(j), thumbscrew_hkts_5_64, pos_offset=(-10.54, 9.906, 9.906))
#                 # _add_linked_object(obj, 'surface_adapter' + str(i) + str(j), thumbscrew_hkts_5_64, pos_offset=(-10.54, -9.906, -9.906))
#     def execute(self, obj):
        
#         mesh = _import_stl("grid_waveplate_lying_down_baseplate.stl", rotate=(270, 0, 0), translate=(0, 0, 0))
        
#         mesh.Placement = obj.Mesh.Placement

#         obj.Mesh = mesh
# this is zhenyu editing:
# class grid_mirror_lying_down:
#     '''
#     mirror grid, fixed as 6 * 6

#     coordinates of waveplate:
#     x=(2 * i + 1.25) * layout.inch, y=(2 * j + 1.25) * layout.inch
#     size of grid:
#     base_dx = 2.1 * layout.inch
#     base_dy = 2.1 * layout.inch
#     base_dz = 1 * layout.inch
#     size = base_dx*Row_numnber, base_dy*Column_number
#     '''
#     type = 'Mesh::FeaturePython'
#     def __init__(self, obj):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)
#         for i in range(6):
#             for j in range(6):
#                 _add_linked_object(obj, 'cicular mirror' + str(i) + str(j), circular_mirror, pos_offset=( (2 * i + 1.25) * layout.inch,-18., -(2 * j + 1.25) * layout.inch),rot_offset=(0, 0, 90))
#                 _add_linked_object(obj, 'mirror_mount' + str(i) + str(j), mirror_mount_km05_lying_down, pos_offset=( (2 * i + 1.25) * layout.inch,-18., -(2 * j + 1.25) * layout.inch),rot_offset=(0, 0, 90))
#                 # _add_linked_object(obj, 'mount_' + str(i) + str(j), thumbscrew_hkts_5_64, pos_offset=(-10.54, 9.906, 9.906))
#                 # _add_linked_object(obj, 'surface_adapter' + str(i) + str(j), thumbscrew_hkts_5_64, pos_offset=(-10.54, -9.906, -9.906))
#     def execute(self, obj):
        
#         mesh = _import_stl("grid_mirror_lying_down_baseplate.stl", rotate=(270, 0, 0), translate=(0, 0, 0))
        
#         mesh.Placement = obj.Mesh.Placement

#         obj.Mesh = mesh
# #This is zhenyu editing    
# class skate_mount_lying_down:
#     '''
#     Skate mount for splitter cubes

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         cube_dx, cube_dy (float) : The side length of the splitter cube
#         mount_hole_dy (float) : The spacing between the two mount holes of the adapter
#         cube_depth (float) : The depth of the recess for the cube
#         outer_thickness (float) : The thickness of the walls around the bolt holes
#         cube_tol (float) : The tolerance for size of the recess in the skate mount
#     '''
#     type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True, cube_dx=10, cube_dy=10, cube_dz=10, mount_hole_dy=20, cube_depth=1, outer_thickness=2, cube_tol=0.1, slots=False):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('App::PropertyLength', 'CubeDx').CubeDx = cube_dy
#         obj.addProperty('App::PropertyLength', 'CubeDy').CubeDy = cube_dx
#         obj.addProperty('App::PropertyLength', 'CubeDz').CubeDz = cube_dz
#         obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
#         obj.addProperty('App::PropertyLength', 'CubeDepth').CubeDepth = cube_depth+1e-3
#         obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
#         obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = cube_tol
#         obj.addProperty('App::PropertyBool', 'Slots').Slots = slots
#         obj.addProperty('Part::PropertyPartShape', 'DrillPart')

#         obj.ViewObject.ShapeColor = adapter_color
#         obj.setEditorMode('Placement', 2)

#     def execute(self, obj):
#         if obj.Slots:
#             slot = 5
#             dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2+slot
#         else:
#             slot = 0
#             dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
#         dy = dx+obj.MountHoleDistance.Value
#         raw_dz = obj.Baseplate.OpticsDz.Value-obj.CubeDz.Value/2+obj.CubeDepth.Value
#         dz = max(raw_dz, 8)
#         cut_dy = obj.CubeDx.Value+obj.CubeTolerance.Value
#         cut_dx = obj.CubeDy.Value+obj.CubeTolerance.Value

#         part = _custom_box(dx=dx, dy=dy, dz=dz,
#                            x=0, y=0, z=-obj.Baseplate.OpticsDz.Value, fillet=5)
#         part = part.cut(_custom_box(dx=cut_dx, dy=cut_dy, dz=obj.CubeDepth.Value+1e-3,
#                                     x=0, y=0, z=-obj.Baseplate.OpticsDz.Value+dz-obj.CubeDepth.Value-1e-3))
#         for i in [-1, 1]:
#             if obj.Slots:
#                 part = part.cut(_custom_box(dx=slot+bolt_8_32['head_dia'], dy=bolt_8_32['head_dia'], dz=bolt_8_32['head_dz'],
#                                             x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz,
#                                             fillet=bolt_8_32['head_dia']/2, dir=(0,0,-1)))
#                 part = part.cut(_custom_box(dx=slot+bolt_8_32['clear_dia'], dy=bolt_8_32['clear_dia'], dz=bolt_8_32['head_dz'],
#                                             x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz-bolt_8_32['head_dz'],
#                                             fillet=bolt_8_32['clear_dia']/2, dir=(0,0,-1)))
#             else:
#                 part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
#                                                 head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dz'],
#                                                 x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+dz))
            
#         part.translate(App.Vector(0, 0, obj.CubeDz.Value/2+(raw_dz-dz)))
#         part = part.fuse(part)
#         obj.Shape = part

#         part = _bounding_box(obj, 0.2*inch, 2,x_tol=4,y_tol=1,z_tol=True, plate_off=20,min_offset=(0,0,5), max_offset=(0,0,5))# ,min_offset=(-slot, 0, 0), max_offset=(slot, 0, 0))
        
#         for i in [-1, 1]:
#             part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
#                                               x=0, y=i*obj.MountHoleDistance.Value/2, z=-obj.Baseplate.OpticsDz.Value+obj.CubeDz.Value/2))
#         part.Placement = obj.Placement
#         obj.DrillPart = part
# this is zhenyu editing
# this is zhenyu and k editing
# class EOM_:
#     '''
#     Isomet 1205C AOM on KM100PM Mount

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         diffraction_angle (float) : The diffraction angle (in degrees) of the AOM
#         forward_direction (integer) : The direction of diffraction on forward pass (1=right, -1=left)
#         backward_direction (integer) : The direction of diffraction on backward pass (1=right, -1=left)

#     Sub-Parts:
#         prism_mount_km100pm (mount_args)
#         mount_for_km100pm (adapter_args)
#     '''
#     type = 'Mesh::FeaturePython'
#     def __init__(self, obj, drill=True, diffraction_angle=degrees(0.026), forward_direction=1, backward_direction=1, mount_args=dict(), adapter_args=dict()):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('App::PropertyAngle', 'DiffractionAngle').DiffractionAngle = diffraction_angle
#         obj.addProperty('App::PropertyInteger', 'ForwardDirection').ForwardDirection = forward_direction
#         obj.addProperty('App::PropertyInteger', 'BackwardDirection').BackwardDirection = backward_direction

#         obj.ViewObject.ShapeColor = misc_color
#         self.part_numbers = ['ISOMET_1205C']
#         self.diffraction_angle = diffraction_angle
#         self.diffraction_dir = (forward_direction, backward_direction)
#         self.transmission = True
#         self.max_angle = 10
#         self.max_width = 5

#         # TODO fix these parts to remove arbitrary translations
#         _add_linked_object(obj, "Mount KM100PM", prism_mount_km100pm,
#                            pos_offset=(-15.25, -20.15, -17.50), **mount_args)
#         _add_linked_object(obj, "Adapter Bracket", mount_for_km100pm,
#                            pos_offset=(-15.25, -20.15, -17.50), **adapter_args)

#     def execute(self, obj):
#         mesh = _import_stl("isomet_1205c.stl", (0, 0, 90), (0, 0, 0))
#         mesh.Placement = obj.Mesh.Placement
#         obj.Mesh = mesh
# this is zhenyu editing:
# class grid_optics:
#     type = 'Mesh::FeaturePython'
#     def __init__(self, obj):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)
#         Number_of_light_source = 13
#         base_dx = Number_of_light_source* 1.5 * layout.inch + 2 + 1 * layout.inch
#         base_dy = Number_of_light_source* 1.5 * layout.inch + 2 + 1 * layout.inch
        
#         base_dz = 1 * layout.inch
#         input_x = 1.0 * layout.inch
#         input_y = 0.3 * layout.inch
#         for i in 1 + np.arange(Number_of_light_source):
#             _add_linked_object(obj, 'Laser_diode_LT230P-B_' + str(i), km05_50mm_laser_no_pad,
#                                     pos_offset=(input_x, input_y + i * 1.5 * layout.inch, 0), rot_offset = (0,0,layout.turn['left-up']))
#             _add_linked_object(obj, 'Laser_diode_LT230P-B_' + str(i), km05_50mm_laser_no_pad,
#                                     pos_offset=(input_y + i * 1.5 * layout.inch,input_x, 0), rot_offset = (0,0,layout.turn['left-up']))
            
#             _add_linked_object(obj, 'mirror_' + str(i), circular_mirror, 
#                                          pos_offset=(base_dx -5, input_y + i * 1.5 * layout.inch, 0) , rot_offset=(0,0,180,),  #layout.turn['up-right'],
#                                         mount_type=mirror_mount_k05s1, mount_args=dict(thumbscrews=True))
            
#             _add_linked_object(obj, 'mirror__' + str(i), circular_mirror, pos_offset=(input_y + i * 1.5 * layout.inch, base_dx - 5, 0), rot_offset=(0,0,-90),  #layout.turn['up-right'],
#                                         mount_type=mirror_mount_k05s1, mount_args=dict(thumbscrews=True))
#     def execute(self, obj):
#         mesh = _import_stl("grid_optics_fast_baseplate.stl", rotate=(0, 0, 0), translate=(0, 0, 0))
        
#         mesh.Placement = obj.Mesh.Placement

#         obj.Mesh = mesh
# # this is zhenyu editing:
# class grid_beamsplitter_lying_down:
#     '''
#     mirror grid, fixed as 6 * 6

#     coordinates of waveplate:
#     x=(2 * i + 1.25) * layout.inch, y=(2 * j + 1.25) * layout.inch
#     size of grid:
#     base_dx = 2.1 * layout.inch
#     base_dy = 2.1 * layout.inch
#     base_dz = 1 * layout.inch
#     size = base_dx*Row_numnber, base_dy*Column_number
#     '''
#     type = 'Mesh::FeaturePython'
#     def __init__(self, obj):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)
#         for i in range(6):
#             for j in range(6):
#                 _add_linked_object(obj, 'cube_splitter' + str(i) + str(j), cube_splitter, pos_offset=( (2 * i + 1.25) * layout.inch,-18., -(2 * j + 1.25) * layout.inch),rot_offset=(0, 0, 45))
#                 # _add_linked_object(obj, 'surface_adapter' + str(i) + str(j), skate_mount_lying_down, pos_offset=( (2 * i + 1.25) * layout.inch,-18., -(2 * j + 1.25) * layout.inch),rot_offset=(0, 0, 45))
#                 # _add_linked_object(obj, 'waveplate_' + str(i) + str(j), mirror_mount_km05_lying_down, pos_offset=( (2 * i + 1.25) * layout.inch,-18., -(2 * j + 1.25) * layout.inch),rot_offset=(0, 0, 90))
#                 # _add_linked_object(obj, 'mount_' + str(i) + str(j), thumbscrew_hkts_5_64, pos_offset=(-10.54, 9.906, 9.906))
#                 # _add_linked_object(obj, 'surface_adapter' + str(i) + str(j), thumbscrew_hkts_5_64, pos_offset=(-10.54, -9.906, -9.906))
#     def execute(self, obj):
        
#         mesh = _import_stl("grid_beamsplitter_lying_down_baseplate_mount.stl", rotate=(270, 0, 0), translate=(0, 0, 0))
        
#         mesh.Placement = obj.Mesh.Placement

#         obj.Mesh = mesh
# class periscope_for_redstone_:
#     '''
#     Custom periscope mount

#     Args:
#         drill (bool) : Whether baseplate mounting for this part should be drilled
#         lower_dz (float) : Distance from the bottom of the mount to the center of the lower mirror
#         upper_dz (float) : Distance from the bottom of the mount to the center of the upper mirror
#         mirror_type (obj class) : Object class of mirrors to be used
#         table_mount (bool) : Whether the periscope is meant to be mounted directly to the optical table

#     Sub-Parts:
#         mirror_type x2 (mirror_args)
#     '''
#     type = 'Part::FeaturePython'
#     def __init__(self, obj, drill=True, lower_dz=1.5*inch, upper_dz=3*inch, invert=True, mirror_args=dict()):
#         obj.Proxy = self
#         ViewProvider(obj.ViewObject)

#         obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
#         obj.addProperty('App::PropertyLength', 'LowerHeight').LowerHeight = lower_dz
#         obj.addProperty('App::PropertyLength', 'UpperHeight').UpperHeight = upper_dz
#         obj.addProperty('App::PropertyBool', 'Invert').Invert = invert

#         obj.ViewObject.ShapeColor = adapter_color
#         if obj.Baseplate == None:
#             self.z_off = -layout.inch*3/2
#         else:
#             self.z_off = 0

#         # _add_linked_object(obj, "Lower Mirror", circular_mirror, rot_offset=((-1)**invert*90, -45, 0), pos_offset=(0, 0, obj.LowerHeight.Value+self.z_off), **mirror_args)
#         # _add_linked_object(obj, "Upper Mirror", circular_mirror, rot_offset=((-1)**invert*90, 135, 0), pos_offset=(0, 0, obj.UpperHeight.Value+self.z_off), **mirror_args)
#         # for i in range(6):
#         #     for j in range(6):
#         #         _add_linked_object(obj, 'Upper Mirror' + str(i) + str(j), circular_mirror, rot_offset=(135,90,45), pos_offset=(-110 +  i * 35, 100 -  j * 24, 20 +  j * 24 ), **mirror_args)

#         #         _add_linked_object(obj, 'Lower Mirror' + str(i) + str(j), circular_mirror, rot_offset=(0, 0, 45), pos_offset=(- 110 + j * 35, 250 - j * 24, 20 +  i * 27), **mirror_args)
#     def execute(self, obj):
#         mesh = _import_stl("periscope_for_redstone.stl", (0, 0, 0), (20, 20, 20))
#         mesh.Placement = obj.Mesh.Placement
#         obj.Mesh = mesh