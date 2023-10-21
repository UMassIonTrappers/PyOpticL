import FreeCAD as App
import Mesh
import Part
from math import *
from . import layout
import numpy as np

from pathlib import Path

STL_PATH_thorlabs = str(Path(__file__).parent.resolve()) + "\\stl\\thorlabs\\"
STL_PATH_newport = str(Path(__file__).parent.resolve()) + "\\stl\\newport\\"

INCH = 25.4

bolt_4_40 = {
    "clear_dia":0.120*INCH,
    "tap_dia":0.089*INCH,
    "head_dia":5.50,
    "head_dz":2.5 # TODO measure this
}

bolt_8_32 = {
    "clear_dia":0.172*INCH,
    "tap_dia":0.136*INCH,
    "head_dia":7,
    "head_dz":4.4
}

bolt_14_20 = {
    "clear_dia":0.260*INCH,
    "tap_dia":0.201*INCH,
    "head_dia":9.8,
    "head_dz":8,
    "washer_dia":9/16*INCH
}

adapter_color = (0.6, 0.9, 0.6)
mount_color = (0.5, 0.5, 0.55)
glass_color = (0.5, 0.5, 0.7)
misc_color = (0.2, 0.2, 0.2)

drill_depth = 100
default_mirror_thickness = 6

# Used to tranform an STL such that it's placement matches the optical center
def _orient_stl(stl, rotate, translate, scale=1, STL_PATH = STL_PATH_thorlabs ):
    mesh = Mesh.read(STL_PATH+stl)
    mat = App.Matrix()
    mat.scale(App.Vector(scale, scale, scale))
    mesh.transform(mat)
    mesh.rotate(*rotate)
    mesh.translate(*translate)
    return mesh

def _add_linked_object(obj, obj_name, obj_class, pos_offset=(0, 0, 0), rot_offset=(0, 0, 0), **args):
    new_obj = App.ActiveDocument.addObject(obj_class.type, obj_name)
    new_obj.setEditorMode('Placement', 2)
    if not hasattr(obj, "ChildObjects"):
        obj.addProperty("App::PropertyLinkListChild","ChildObjects")
    obj.ChildObjects += [new_obj]
    new_obj.addProperty("App::PropertyLinkHidden","ParentObject").ParentObject = obj
    new_obj.addProperty("App::PropertyPlacement","RelativePlacement").RelativePlacement
    new_obj.RelativePlacement.Base = App.Vector(*pos_offset)
    rotx = App.Rotation(App.Vector(1,0,0), rot_offset[0])
    roty = App.Rotation(App.Vector(0,1,0), rot_offset[1])
    rotz = App.Rotation(App.Vector(0,0,1), rot_offset[2])
    new_obj.RelativePlacement.Rotation = App.Rotation(rotx*roty*rotz)
    obj_class(new_obj, **args)
    ViewProvider(new_obj.ViewObject)
    return new_obj

def _place_object(obj, rotate, translate, rel_obj=None):
    mat = App.Placement(App.Vector(0, 0, 0), rel_obj.Placement.Rotation, App.Vector(0, 0, 0)).toMatrix()
    mat.rotateX(rotate[0])
    mat.rotateY(rotate[1])
    mat.rotateZ(rotate[2])
    mat.move(*rel_obj.Placement.Base)
    mat.move(*translate)
    obj.Placement = App.Placement(mat)

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

def _mount_hole(dia, dz, x, y, z, head_dia=0, head_dz=0, dir=(0, 0, -1), countersink=False):
    part = Part.makeCylinder(dia/2, dz, App.Vector(0, 0, 0), App.Vector(*dir))
    if head_dia != 0 and head_dz != 0:
        if countersink:
            part = part.fuse(Part.makeCone(head_dia/2, dia/2, head_dz, App.Vector(0, 0, 0), App.Vector(*dir)))
        else:
            part = part.fuse(Part.makeCylinder(head_dia/2, head_dz, App.Vector(0, 0, 0), App.Vector(*dir)))
    part.translate(App.Vector(x, y, z))
    part = part.fuse(part)
    return part

def _absolute_cut(obj, part, cut_part):
    cut_part.translate(App.Vector(-obj.Placement.Base))
    return part.cut(cut_part)

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
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)
        self.mount_bolt = bolt_8_32
        self.mount_dz = -INCH/2

    # function which returns the drilling required to mount component
    def get_drill(self, obj):
        part = _mount_hole(dia=self.mount_bolt['tap_dia'], dz=drill_depth, x=0, y=0, z=self.mount_dz)
        return part

    # this defines the component body itself
    def execute(self, obj):
        part = _custom_box(dx=obj.Side_Length.Value, dy=obj.Side_Length.Value, dz=obj.Side_Length.Value,
                           x=0, y=0, z=self.mount_dz)
        part = part.cut(_mount_hole(dia=self.mount_bolt['clear_dia'], dz=obj.Side_Length.Value,
                                    head_dia=self.mount_bolt['head_dia'], head_dz=self.mount_bolt['head_dz'],
                                    x=0, y=0, z=obj.Side_Length.Value+self.mount_dz))
        obj.Shape = part

class baseplate_mount:
    '''
    Mount holes for attaching to an optical table
    Currently uses 14_20 bolts

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

        obj.ViewObject.ShapeColor = mount_color

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_14_20['clear_dia'], dz=drill_depth,
                           head_dia=bolt_14_20["washer_dia"], head_dz=obj.BoreDepth.Value,
                           x=0, y=0, z=-INCH/2)
        return part

    def execute(self, obj):
        bolt_len = INCH-(obj.BoreDepth.Value-bolt_14_20['head_dz'])

        part = _mount_hole(dia=bolt_14_20['tap_dia'], dz=bolt_len,
                           head_dia=bolt_14_20['head_dia'], head_dz=bolt_14_20['head_dz'],
                           x=0, y=0, z=-INCH*3/2+bolt_len)
        obj.Shape = part

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
    def __init__(self, obj, mount_hole_dy, adapter_height=8, outer_thickness=2, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)
        self.drill_tolerance = 1

    def get_drill(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2+self.drill_tolerance
        dy = dx+obj.MountHoleDistance.Value

        part = _custom_box(dx=dx, dy=dy, dz=drill_depth,
                           x=0, y=0, z=-obj.AdapterHeight.Value,
                           dir=(0, 0, 1), fillet=5)
        for i in [-1, 1]:
            part = part.fuse(_mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        return part

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        dz = obj.AdapterHeight.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=0,
                           dir=(0, 0, -1), fillet=5)
        part = part.cut(_mount_hole(dia=bolt_8_32['clear_dia'], dz=dz,
                                    head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dia'],
                                    x=0, y=0, z=-dz, dir=(0,0,1)))
        for i in [-1, 1]:
            part = part.cut(_mount_hole(dia=bolt_8_32['clear_dia'], dz=dz,
                                        head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dia'],
                                        x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        obj.Shape = part
        

class skate_mount:
    '''
    Skate mount for splitter cubes

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        cube_size (float) : The side length of the splitter cube
        mount_hole_dy (float) : The spacing between the two mount holes of the adapter
        cube_depth (float) : The depth of the recess for the cube
        outer_thickness (float) : The thickness of the walls around the bolt holes
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, cube_size, mount_hole_dy=20, cube_depth=1, outer_thickness=2, cube_tol=0.1, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'CubeSize').CubeSize = cube_size
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'CubeDepth').CubeDepth = cube_depth+1e-3
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = cube_tol

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=0, y=-obj.MountHoleDistance.Value/2, z=-INCH/2)
        part = part.fuse(_mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                     x=0, y=obj.MountHoleDistance.Value/2, z=-INCH/2))
        return part

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        dz = INCH/2-obj.CubeSize.Value/2+obj.CubeDepth.Value
        cut_dx = obj.CubeSize.Value+obj.CubeTolerance.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=-INCH/2, fillet=5)
        part = part.cut(_custom_box(dx=cut_dx, dy=cut_dx, dz=obj.CubeDepth.Value,
                                    x=0, y=0, z=-obj.CubeSize.Value/2))
        for i in [-1, 1]:
            part = part.cut(_mount_hole(dia=bolt_8_32['clear_dia'], dz=dz,
                                        head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dia'],
                                        x=0, y=i*obj.MountHoleDistance.Value/2, z=-INCH/2+dz))
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
    def __init__(self, obj, slot_length, drill_offset=0, adapter_height=8, post_thickness=4, outer_thickness=2, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'SlotLength').SlotLength = slot_length
        obj.addProperty('App::PropertyDistance', 'DrillOffset').DrillOffset = drill_offset
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'PostThickness').PostThickness = post_thickness
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        
        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def get_drill(self, obj):
        bolt_dy = -obj.PostThickness.Value-(obj.SlotLength.Value+bolt_8_32['head_dia']+obj.OuterThickness.Value*2)/2

        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=0, y=bolt_dy+obj.DrillOffset.Value, z=-INCH/2)
        return part

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.SlotLength.Value+obj.PostThickness.Value
        dz = obj.AdapterHeight.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=-dy/2, z=-INCH/2, fillet=4)
        part = part.cut(_custom_box(dx=bolt_8_32['clear_dia'], dy=obj.SlotLength.Value+bolt_8_32['clear_dia'], dz=dz,
                                    x=0, y=-dy/2-obj.PostThickness.Value/2, z=-INCH/2, fillet=bolt_8_32['clear_dia']/2))
        part = part.cut(_custom_box(dx=bolt_8_32['head_dia'], dy=obj.SlotLength.Value+bolt_8_32['head_dia'], dz=bolt_8_32['head_dia'],
                                    x=0, y=-dy/2-obj.PostThickness.Value/2, z=-INCH/2+bolt_8_32['head_dia'], fillet=bolt_8_32['head_dia']/2))
        part = part.fuse(_custom_box(dx=dx, dy=obj.PostThickness.Value, dz=INCH/2+bolt_8_32['clear_dia'],
                                     x=0, y=-obj.PostThickness.Value/2, z=-INCH/2))
        part = part.cut(_mount_hole(dia=bolt_8_32['clear_dia'], dz=obj.PostThickness.Value,
                                    x=0, y=0, z=0, dir=(0, -1, 0)))
        obj.Shape = part


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
    def __init__(self, obj, slot_length=8, countersink=False, counter_depth=3, arm_thickness=8, arm_clearance=2, stage_thickness=4, stage_length=21, drill=True):
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

        obj.ViewObject.ShapeColor = mount_color
        obj.setEditorMode('Placement', 2)
        

    def get_drill(self, obj):
        part = _custom_box(dx=34, dy=54.5, dz=24.27,
                           x=-19.27+15, y=-8.02, z=0,
                           fillet=5, dir=(0, 0, -1))
        return part

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
            part = part.cut(_mount_hole(dia=bolt_4_40['clear_dia'], dz=stage_dz, head_dia=bolt_4_40['head_dia'],
                                        head_dz=obj.CounterDepth.Value, countersink=obj.Countersink,
                                        x=11.25, y=18.9+ddy, z=dz-4, dir=(0,0,1)))
        part.translate(App.Vector(18, 0, -dz))
        part = part.fuse(part)
        obj.Shape = part


class universal_mount:
    '''
    Universal adapter allowing for multiple mirror mounts to work on a single baseplate

    Args:
        mount_offset (float[3]) : The offset position of where the adapter mounts to the component
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, mount_offset, size, zOff, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.dx = size[0]
        self.dy = size[1]
        self.dz = size[2]
        self.mount_offset = mount_offset
        self.zOff = zOff

    def get_drill(self, obj):
        part = _custom_box(self.dx+1, self.dy+1, self.dz, self.mount_offset[0], self.mount_offset[1], -INCH/2, 4, (0,0,-1))
        part = part.fuse(_mount_hole(bolt_8_32['tap_dia'], drill_depth, self.mount_offset[0], self.mount_offset[1]-self.dy/2+5, -self.dz-INCH/2))
        part = part.fuse(_mount_hole(bolt_8_32['tap_dia'], drill_depth, self.mount_offset[0], self.mount_offset[1]+self.dy/2-5, -self.dz-INCH/2))
        return part

    def execute(self, obj):
        dz = self.dz+self.zOff+INCH/2
        part = _custom_box(self.dx, self.dy, dz, 0, 0, 0, 4, (0,0,-1))
        temp = _mount_hole(bolt_8_32['clear_dia'], dz, 0, -self.dy/2+5, 0, bolt_8_32['head_dia'], bolt_8_32['head_dia'])
        temp = temp.fuse(_mount_hole(bolt_8_32['clear_dia'], dz, 0, self.dy/2-5, 0, bolt_8_32['head_dia'], bolt_8_32['head_dia']))
        part = part.cut(temp)
        part.translate(App.Vector(*self.mount_offset, self.zOff))
        parent = obj.LinkToParent
        temp = parent.Proxy.get_drill(parent)
        temp.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0), App.Vector(0, 0, 0))
        part = part.cut(temp)
        obj.Shape = part


class fiberport_holder:
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

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['HCA3','PAF2-5A']
        self.in_limit = pi-0.01
        self.in_width = 1

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=INCH,
                           x=0, y=0, z=-20.7, dir=(1,0,0))
        part = part.fuse(_mount_hole(dia=bolt_8_32['tap_dia'], dz=INCH,
                                     x=0, y=-12.7, z=-20.7, dir=(1,0,0)))
        part = part.fuse(_mount_hole(dia=bolt_8_32['tap_dia'], dz=INCH,
                                     x=0, y=12.7, z=-20.7, dir=(1,0,0)))
        return part

    def execute(self, obj):
        mesh = _orient_stl("HCA3-Solidworks.stl", (-pi/2, pi, -pi/2), (-6.35, -38.1/2, -26.9))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        

class pbs_on_skate_mount:
    '''
    Beam-splitter cube

    Args:
        invert (bool) : Invert pick-off direction, false is left, true is right
        cube_size (float) : The side length of the splitter cube
        cube_part_num (string) : The Thorlabs part number of the splitter cube being used
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, invert=False, cube_size=10, cube_part_num='PBS101'):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'Invert').Invert = invert
        obj.addProperty('App::PropertyLength', 'CubeSize').CubeSize = cube_size


        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.part_numbers = [cube_part_num]
        
        if invert:
            self.ref_angle = -3*pi/4
        else:
            self.ref_angle = 3*pi/4
        self.tran = True
        self.in_limit = 0
        self.in_width = sqrt(200)

        _add_linked_object(obj, obj.Name+"_Adapter", skate_mount, cube_size=obj.CubeSize.Value)

    def execute(self, obj):
        # TODO make this a part
        part = _custom_box(dx=obj.CubeSize.Value, dy=obj.CubeSize.Value, dz=obj.CubeSize.Value,
                           x=0, y=0, z=0, dir=(0, 0, 0))
        temp = _custom_box(dx=sqrt(200)-0.25, dy=0.1, dz=obj.CubeSize.Value-0.25,
                           x=0, y=0, z=0, dir=(0, 0, 0))
        temp.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), -degrees(self.ref_angle))
        part = part.cut(temp)
        obj.Shape = part


class rotation_stage_rsp05:
    '''
    Rotation stage, model RSP05

    Args:
        mount_hole_dy (float) : The spacing between the two mount holes of it's adapter
        wave_plate_part_num (string) : The Thorlabs part number of the wave plate being used
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mount_hole_dy=25, wave_plate_part_num='', **adapter_args):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['RSP05', wave_plate_part_num]
        self.tran = True
        self.in_limit = pi/2
        self.in_width = INCH/2

        _add_linked_object(obj, obj.Name+"_Adapter", surface_adapter, pos_offset=(0, 0, -14), mount_hole_dy=mount_hole_dy, **adapter_args)

    def execute(self, obj):
        mesh = _orient_stl("RSP05-Solidworks.stl", (pi/2, 0, pi/2), (0.6, 0, 0), 1000)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_k05s2:
    '''
    Mirror mount, model K05S2

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, uMountParam=None , mirror_part_num = 'BB05-E02'):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-K05S1', mirror_part_num]
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-INCH/2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-8-obj.MirrorThickness.Value, y=0, z=-INCH/2)
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-8-obj.MirrorThickness.Value, y=-5, z=-INCH/2))
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-8-obj.MirrorThickness.Value, y=5, z=-INCH/2))
        return part

    def execute(self, obj):
        # TODO create seperate circular mirror component
        mesh = _orient_stl("POLARIS-K05S2-Solidworks.stl", (0, -pi/2, 0), (-4.5-obj.MirrorThickness.Value, -0.3, -0.25), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_k05s1:
    '''
    Mirror mount, model K05S1

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, uMountParam=None , mirror_part_num = 'BB05-E02'):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-K05S1' , mirror_part_num]
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-INCH/2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-8-obj.MirrorThickness.Value, y=0, z=-INCH/2)
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-8-obj.MirrorThickness.Value, y=-5, z=-INCH/2))
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-8-obj.MirrorThickness.Value, y=5, z=-INCH/2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-K05S1-Solidworks.stl", (0, 0, -pi/2), (-4.5-obj.MirrorThickness.Value, -0.3+0.5, -0.25), 1)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_b05g:
    '''
    Mirror mount, model B05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_thickness (float) : The thickness of the mirror being used
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mirror_thickness=4, uMountParam=None, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = mirror_thickness

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-B05G']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-INCH/2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'],
                           dz=drill_depth, x=-4-obj.MirrorThickness, y=0, z=-INCH/2)
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-4-obj.MirrorThickness, y=-5, z=-INCH/2))
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-4-obj.MirrorThickness, y=5, z=-INCH/2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-B05G-Solidworks.STL", (pi/2, 0, pi/2), (-16.7-obj.MirrorThickness, -9.0, -18.2-1.05))
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_c05g:
    '''
    Mirror mount, model C05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_thickness (float) : The thickness of the mirror being used
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mirror_thickness=6, uMountParam=None, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = mirror_thickness

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-C05G']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-INCH/2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-6.4-obj.MirrorThickness.Value, y=0, z=-INCH/2)
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-6.4-obj.MirrorThickness.Value, y=-5, z=-INCH/2))
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-6.4-obj.MirrorThickness.Value, y=5, z=-INCH/2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-C05G-Solidworks.stl", (pi/2, 0, pi/2), (-19-obj.MirrorThickness.Value, -4.3, -15.2), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_km05:
    '''
    Mirror mount, model KM05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_thickness (float) : The thickness of the mirror being used
        bolt_length (float) : The length of the bolt used for mounting
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mirror_thickness=6, bolt_length=15, uMountParam=None, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = mirror_thickness

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM05']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2
        self.bolt_len = bolt_length

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-0.58*INCH)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False
            self.bolt_len = uMountParam[0][2]-0.08*INCH-bolt_8_32['head_dia']+5

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['clear_dia'], dz=INCH,
                           head_dia=bolt_8_32['head_dia'], head_dz=0.92*INCH-self.bolt_len+5,
                           x=-13.4, y=0, z=-INCH*3/2, dir=(0,0,1))
        part = part.fuse(_custom_box(dx=18, dy=31, dz=0.08*INCH,
                                     x=-8.4, y=0, z=-INCH/2-0.08*INCH, fillet=3))
        part = part.fuse(_custom_box(dx=18, dy=9, dz=0.08*INCH,
                                     x=-13.4, y=-31/2+4.5, z=-INCH/2-0.08*INCH, fillet=2))
        part = part.fuse(_custom_box(dx=17, dy=20, dz=(0.08*INCH)+4,
                                     x=-(15+14.4), y=-31/2+4.5, z=-INCH/2-0.08*INCH-4, fillet=2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("KM05-Solidworks.stl", (0, 0, pi/2), ([-4.05, -1.2, 0.5]))
        temp = Mesh.createCylinder(INCH/4, 6, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class fiberport_mount_km05:
    '''
    Mirror mount, model KM05, adapted to use as fiberport mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_thickness (float) : The thickness of the mirror being used
        bolt_length (float) : The length of the bolt used for mounting
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, bolt_length=15, uMountParam=None, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM05']
        self.bolt_len = bolt_length
        self.in_limit = 0
        self.in_width = 1

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-0.58*INCH)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False
            self.bolt_len = uMountParam[0][2]-0.08*INCH-bolt_8_32['head_dia']+5

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['clear_dia'], dz=INCH,
                           head_dia=bolt_8_32['head_dia'], head_dz=0.92*INCH-self.bolt_len+5,
                           x=-13.4, y=0, z=-INCH*3/2, dir=(0,0,1))
        part = part.fuse(_custom_box(dx=18, dy=31, dz=0.08*INCH,
                                     x=-8.4, y=0, z=-INCH/2-0.08*INCH, fillet=3))
        part = part.fuse(_custom_box(dx=18, dy=9, dz=0.08*INCH,
                                     x=-12, y=-31/2+4.5, z=-INCH/2-0.08*INCH, fillet=2))
        part = part.fuse(_custom_box(dx=15, dy=20, dz=(0.08*INCH)+4,
                                     x=-(15+13.4), y=-31/2+4.5, z=-INCH/2-0.08*INCH-4, fillet=2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("KM05-Solidworks.stl", (0, 0, pi/2), ([-4.05, -1.2, 0.5]))
        temp = Mesh.createCylinder(INCH/4, 19.5, True, 1, 50)
        temp.rotate(0, 0, pi)
        temp.translate(18.75, 0, 0)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

# TODO make this a compound component
class km05_50mm_laser:
    '''
    Mirror mount, model KM05, adapted to use as laser mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_thickness (float) : The thickness of the mirror being used
        bolt_length (float) : The length of the bolt used for mounting
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, bolt_length=2, uMountParam=None, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['KM05']
        self.bolt_len = bolt_length
        self.in_limit = pi-0.01
        self.in_width = 1

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-0.58*INCH)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False
            self.bolt_len = uMountParam[0][2]-0.08*INCH-bolt_8_32['head_dia']+5

        _add_linked_object(obj, obj.Name+"_TEC_Mount", km05_tec_mount, pos_offset=(-10, 0, -0.08*INCH))

    def get_drill(self, obj):
        part = _mount_hole(bolt_8_32['clear_dia'], INCH, -13.4, 0, -INCH*3/2, bolt_8_32['head_dia'], 0.92*INCH-self.bolt_len+5, dir=(0,0,1))
        part = part.fuse(_custom_box(1.5*INCH+5, 1.5*INCH+5, 0.08*INCH+INCH/4+4+INCH/4, -10, 0, -INCH/2, 3, dir=(0, 0, -1)))
        return part

    def execute(self, obj):
        mesh = _orient_stl("KM05-Solidworks.stl", (0, 0, pi/2), ([-4.05, -1.2, 0.5]))
        temp = Mesh.createCylinder(INCH/4, 40, True, 1, 50)
        temp.rotate(0, 0, pi)
        temp.translate(10, 0, 0)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class km05_tec_mount:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = adapter_color
        self.part_numbers = []

    def get_drill(self, obj):
        bottom_dx = 1.5*INCH

        part = Part.makeSphere(0)
        for x, y in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            part = part.fuse(_mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=(bottom_dx/2-4)*x, y=(bottom_dx/2-4)*y, z=0, dir=(0, 0, -1)))
        return part

    def execute(self, obj):
        top_dx = INCH
        top_dz = INCH/4
        bottom_dx = 1.5*INCH
        bottom_dz = INCH/4
        tec_dz = 4

        part = _custom_box(dx=top_dx, dy=top_dx, dz=top_dz,
                           x=0, y=0, z=-INCH/2, dir=(0, 0, -1))
        part = part.cut(_mount_hole(dia=bolt_8_32['clear_dia'], dz=top_dz,
                                    head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dia'],
                                    x=-3.4, y=0, z=-INCH/2-top_dz, dir=(0,0,1)))
        part = part.fuse(_custom_box(dx=bottom_dx, dy=bottom_dx, dz=bottom_dz,
                                     x=0, y=0, z=-INCH/2-top_dz-tec_dz, dir=(0, 0, -1)))
        for x, y in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            part = part.cut(_mount_hole(dia=bolt_8_32['clear_dia'], dz=bottom_dz,
                                        x=(bottom_dx/2-4)*x, y=(bottom_dx/2-4)*y, z=-INCH/2-top_dz-tec_dz, dir=(0, 0, -1)))
        obj.Shape = part

class mirror_mount_mk05:
    '''
    Mirror mount, model MK05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_thickness (float) : The thickness of the mirror being used
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mirror_thickness=6, uMountParam=None, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = mirror_thickness
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['MK05']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-10.2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                           head_dia=bolt_4_40['head_dia'], head_dz=drill_depth-10,
                           x=-10.2, y=0, z=-10.2-drill_depth, dir=(0,0,1))
        return part

    def execute(self, obj):
        mesh = _orient_stl("MK05-Solidworks.stl", (0, -pi/2, 0), ([-27.5, -5.6, -26.0]), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mount_mk05pm:
    '''
    Mount, model MK05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, uMountParam=None, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['MK05PM']

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, True, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-10.2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                           head_dia=bolt_4_40['head_dia'], head_dz=drill_depth-5,
                           x=-15, y=0, z=-10.2-drill_depth, dir=(0,0,1))
        part = part.fuse(_custom_box(dx=30, dy=25, dz=5,
                                     x=-3, y=0, z=-11.3, fillet=2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("MK05PM.stl", (0, pi/2, pi), ([-15, 0, 0]))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class grating_mount_on_mk05pm:
    type = 'Part::FeaturePython'
    def __init__(self, obj, littrow_angle=45):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyAngle', 'LittrowAngle').LittrowAngle = littrow_angle

        obj.ViewObject.ShapeColor = adapter_color
        self.part_numbers = []

        self.dx = 12/tan(radians(2*obj.LittrowAngle))

        _add_linked_object(obj, obj.Name+"_mount", mount_mk05pm, pos_offset=(1.4-6, 2, -3.5))
        _add_linked_object(obj, obj.Name+"_grating", laser_grating, pos_offset=(0, 0, 6-3.5), rot_offset=(0, 0, -obj.LittrowAngle.Value))
        _add_linked_object(obj, obj.Name+"_mirror", square_mirror, pos_offset=(self.dx, -12, 6-3.5), rot_offset=(0, 0, -obj.LittrowAngle.Value+180))

    def execute(self, obj):
        # TODO add some variables to make this cleaner
        part = _custom_box(dx=25+self.dx, dy=35, dz=4,
                           x=0, y=0, z=0, dir=(1, -1, 1))
        part = part.cut(_custom_box(dx=6, dy=8, dz=4,
                                    x=0, y=0, z=0, dir=(1, -1, 1)))
        part = part.cut(_mount_hole(dia=bolt_4_40['clear_dia'], dz=4,
                                    x=3.1, y=-18.2, z=0, dir=(0, 0, 1)))
        part = part.cut(_mount_hole(dia=bolt_4_40['clear_dia'], dz=4,
                                    x=16.4, y=-2.6, z=0, dir=(0, 0, 1)))
        part.translate(App.Vector(-10.4, 10.5, -4.5))
        part.translate(App.Vector(1.4-6, 2, -3.5))
        temp = _custom_box(dx=4, dy=12, dz=12,
                           x=-6, y=0, z=-4, dir=(-1, 0, 1))
        temp.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), -obj.LittrowAngle.Value)
        part = part.fuse(temp)
        temp = _custom_box(dx=4, dy=12, dz=12,
                           x=self.dx+3.2, y=-12, z=-4, dir=(1, 0, 1))
        temp.rotate(App.Vector(self.dx, -12, 0), App.Vector(0, 0, 1), -obj.LittrowAngle.Value)
        part = part.fuse(temp)
        part = part.fuse(part)
        obj.Shape = part

class splitter_mount_c05g:
    '''
    Splitter mount, model C05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        plate_thickness (float) : The thickness of the splitter plate being used
        plate_part_num (string) : The Thorlabs part number of the splitter plate being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, plate_thickness=3, drill=True, plate_part_num=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'PlateThickness').PlateThickness = plate_thickness
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-C05G', plate_part_num]
        self.ref_angle = 0
        self.tran = True
        self.in_limit = pi/2
        self.in_width = INCH/2

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-6.4-obj.PlateThickness.Value, y=0, z=-INCH/2)
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-6.4-obj.PlateThickness.Value, y=-5, z=-INCH/2))
        part = part.fuse(_mount_hole(dia=2, dz=2.2,
                                     x=-6.4-obj.PlateThickness.Value, y=5, z=-INCH/2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-C05G-Solidworks.stl", (pi/2, 0, pi/2), (-19-obj.PlateThickness.Value, -4.3, -15.2), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.PlateThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class lens_holder_l05g:
    '''
    Lens holder, model L05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        foc_len (float) : The focal length of the lens being used
        lens_part_num (string) : The Thorlabs part number of the lens being used
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, foc_len=50, drill=True, lens_part_num=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-L05G', lens_part_num]
        self.tran = True
        self.foc_len = foc_len
        self.in_limit = 0
        self.in_width = INCH/2

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-9.5, y=0, z=-INCH/2)
        for i in [-1,1]:
            part = part.fuse(_custom_box(dx=5, dy=2, dz=2.2,
                                         x=-9.5, y=i*5, z=-INCH/2,
                                         fillet=1, dir=(0, 0, -1)))
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-L05G-Solidworks.stl", (pi/2, 0, pi/2), (-28.0, -13.3, -18.4), 1000)
        temp = Mesh.createCylinder(INCH/4, 1, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class pinhole_ida12:
    '''
    Pinhole iris, model IDA12

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, slot_length=10, drill=True, **adapter_args):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IDA12-P5']
        self.tran = True
        self.in_limit = 0
        self.in_width = 1
        self.block_width=INCH/2
        self.slot_length=slot_length

        _add_linked_object(obj, obj.Name+"_Adapter", slide_mount, pos_offset=(-0.75, -12.85, 0), slot_length=slot_length, **adapter_args)

    def get_drill(self, obj):
        part = _custom_box(dx=6.5, dy=10+self.slot_length, dz=1,
                           x=-0.75, y=0, z=-INCH/2,
                           fillet=2, dir=(0,0,-1))
        return part

    def execute(self, obj):
        mesh = _orient_stl("IDA12-P5-Solidworks.stl", (-pi/2, 0, -pi/2), (-0.35, 0.05, 0), 1000)
        mesh.rotate(pi/2, 0, 0)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class kinematic_mount_km100pm:

    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mount_offset, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM100PM']
        self.mount_offset = mount_offset

    def get_drill(self, obj):
        part = _custom_box(dx=34, dy=54.5, dz=24.27,
                           x=-19.27, y=-8.02, z=0,
                           fillet=5, dir=(0, 0, -1))
        part = part.fuse(_custom_box(dx=40, dy=17.5, dz=26.2,
                                     x=-44.77, y=-26.52, z=0,
                                     fillet=5, dir=(0, 0, -1)))
        part = part.fuse(_mount_hole(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                     x=-29.27, y=-7.52, z=0))
        return part

    def execute(self, obj):
        mesh = _orient_stl("KM100PM-Solidworks-modified.stl", (pi/2, 0, -pi/2), np.add((14.2, 26.0, -17.92), self.mount_offset), 1)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        

class isomet_1205c_on_km100pm:
    '''
    AOM on a kinematic mount, AOM model isomet-1205C, mount model KM100PM
    https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        diff_angle (float) : The diffraction angle (in radians) of the AOM
        diff_dir (int[2]) : The forward and reverse diffraction factor, ie (1,-1) would
            diffract right on a forward pass and left on a return pass
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, diff_angle=-0.026, diff_dir=(1,1), exp=False):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        # TODO add parameters here

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['ISOMET_1205C']
        self.diff_dir = diff_dir
        self.tran = True
        if exp:
            self.diff_angle = diff_angle
        self.in_limit = 0
        self.in_width = 5

        _add_linked_object(obj, obj.Name+"_Mount", kinematic_mount_km100pm, mount_offset=(-(51.8-25.7-12+15.17), -(6.35+0.089*INCH/2), -6.98))
        _add_linked_object(obj, obj.Name+"_Adapter", mount_for_km100pm, pos_offset=(-(51.8-25.7-12+15.17), -(6.35+0.089*INCH/2), -6.98), slot_length=5)

    def execute(self, obj):
        mesh = _orient_stl("isomet_1205c.stl", (0, 0, pi/2), (0, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class periscope:
    '''
    Custom periscope mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        lower_dz (float) : Distance from the bottom of the mount to the center of the lower mirror
        upper_dz (float) : Distance from the bottom of the mount to the center of the upper mirror
        lower_mirror (obj class) : Object class of lower mirror to be used
        upper_mirror (obj class) : Object class of upper mirror to be used
        table_mount (bool) : Whether the periscope is meant to be mounted directly to the optical table
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, lower_dz, upper_dz, left_handed=False, table_mount=False, lower_mirror=mirror_mount_k05s2, upper_mirror=mirror_mount_k05s2, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'Lower_dz').Lower_dz = lower_dz
        obj.addProperty('App::PropertyLength', 'Upper_dz').Upper_dz = upper_dz
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = adapter_color
        self.in_limit = pi-0.01
        self.in_width = 1
        self.left_handed = left_handed
        if table_mount:
            self.z_off = -3*INCH/2
        else:
            self.z_off = -INCH/2

        self.lower_obj = _add_linked_object(obj, obj.Name+"_Lower_Mirror", lower_mirror)
        self.upper_obj = _add_linked_object(obj, obj.Name+"_Upper_Mirror", upper_mirror)

    def get_drill(self, obj):
        part = _mount_hole(dia=bolt_8_32['tap_dia'], dz=INCH,
                           x=0, y=0, z=-20.7, dir=(1,0,0))
        part = part.fuse(_mount_hole(dia=bolt_8_32['tap_dia'], dz=INCH,
                                     x=0, y=-12.7, z=-20.7, dir=(1,0,0)))
        part = part.fuse(_mount_hole(dia=bolt_8_32['tap_dia'], dz=INCH,
                                     x=0, y=12.7, z=-20.7, dir=(1,0,0)))
        return part

    def execute(self, obj):
        # TODO use new object linking to fix
        if self.left_handed:
            inv = -1
        else:
            inv = 1
        width = INCH #Must be INCH wide to keep periscope mirrors 1 inch from mount holes. 
        fillet = 15
        part = _custom_box(dx=70, dy=width, dz=obj.Upper_dz.Value+20,
                           x=0, y=0, z=0)
        for i in [-1, 1]:
            part = part.cut(_custom_box(dx=fillet*2+4, dy=width, dz=obj.Upper_dz.Value+20,
                                        x=i*(35+fillet), y=0, z=20, fillet=15,
                                        dir=(-i,0,1), fillet_dir=(0,1,0)))
            part = part.cut(_mount_hole(dx=bolt_14_20['clear_dia']+0.5, dy=INCH+5, dz=i*INCH,
                                        x=0, y=25, z=bolt_14_20['head_dia']+0.5,
                                        fillet=10, dir=(0,0,-1)))
        part.translate(App.Vector(0, -inv*(width/2+INCH/2), self.z_off))
        part = part.fuse(part)
        _place_object(self.lower_obj, (-inv*pi/2, -pi/4, 0), (0, 0, obj.Lower_dz.Value+self.z_off), obj)
        _place_object(self.upper_obj, (-inv*pi/2, 3*pi/4, 0), (0, 0, obj.Upper_dz.Value+self.z_off), obj)
        for i in [self.lower_obj, self.upper_obj]:
            drill = i.Proxy.get_drill(i)
            drill.Placement = i.Placement
            part = _absolute_cut(obj, part, drill)
        part.translate(App.Vector(0, inv*(width+INCH), 0))
        part = part.fuse(part)
        _place_object(self.lower_obj, (inv*pi/2, -pi/4, 0), (0, 0, obj.Lower_dz.Value+self.z_off), obj)
        _place_object(self.upper_obj, (inv*pi/2, 3*pi/4, 0), (0, 0, obj.Upper_dz.Value+self.z_off), obj)
        for i in [self.lower_obj, self.upper_obj]:
            drill = i.Proxy.get_drill(i)
            drill.Placement = i.Placement
            part = _absolute_cut(obj, part, drill)
        obj.Shape = part



class isolator_670:
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mount_hole_dy=45, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IOT-5-670-VLP']
        self.tran = True
        self.in_limit = pi/2
        self.in_width = INCH/2

        _add_linked_object(obj, obj.Name+"_Adapter", surface_adapter, pos_offset=(0, 0, -22.1), mount_hole_dy=mount_hole_dy)

    def get_drill(self, obj):
        part = _custom_box(dx=80, dy=25, dz=5,
                           x=0, y= 0, z=-INCH/2,
                           fillet=5, dir=(0, 0, -1))
        return part

    def execute(self, obj):
        mesh = _orient_stl("IOT-5-670-VLP.stl", (pi/2, 0, pi/2), (19, 0, 0), 1) #Thorlabs 670 (better for injection?)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class isolator_405:
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mount_hole_dy=36, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IOT-5-670-VLP']
        self.tran = True
        self.in_limit = pi/2
        self.in_width = INCH/2

        _add_linked_object(obj, obj.Name+"_Adapter", surface_adapter, pos_offset=(0, 0, -17.15), mount_hole_dy=mount_hole_dy)

    def get_drill(self, obj):
        part = _custom_box(dx=25, dy=15, dz=drill_depth,
                           x=0, y=0, z=-INCH/2,
                           fillet=5, dir=(0, 0, 1))
        return part

    def execute(self, obj):
        mesh = _orient_stl("IO-3D-405-PBS.stl", (pi/2, 0, pi/2), (9.45, 0, 0), 1)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh



class laser_diode_mount:
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['LT230P-B','AD15NT']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

    def execute(self, obj):
        mesh = _orient_stl("LT230P-B.stl", (0, pi/2, 0 ), ([0, 0, 0]))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh



class laser_grating:
    type = 'Part::FeaturePython'
    def __init__(self, obj, thickness=6, width=12.7, height=12.7, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = []
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = width

    def execute(self, obj):
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part

class square_mirror:
    type = 'Part::FeaturePython'
    def __init__(self, obj, thickness=3.2, width=12.7, height=12.7, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = []
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = width

    def execute(self, obj):
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part

class rb_cell:
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = []
        self.tran = True
        self.in_limit = 0
        self.in_width = 1

    def get_drill(self, obj):
        part = _custom_box(110, 62, 25.4-INCH/2, 0, 5, -INCH/2, 3, (0,0,-1))
        for x, y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
            part = part.fuse(_mount_hole(bolt_8_32['tap_dia'], drill_depth, x*45, y*15.7, -INCH/2))
        part = part.fuse(_mount_hole(bolt_8_32['tap_dia'], drill_depth, 45, -15.7, -INCH/2))
        for x in [1,-1]:
            part = part.fuse(_mount_hole(bolt_8_32['tap_dia'], drill_depth, x*45, 25.7, -INCH/2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("rb_cell_holder_middle.stl", (0, 0, 0), ([0, 5, 0]))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class ViewProvider:
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        return

    def getDefaultDisplayMode(self):
        return "Shaded"

    def onDelete(self, feature, subelements):
        element = feature.Object.Proxy
        for i in App.ActiveDocument.Objects:
            if hasattr(i, "ChildObjects"):
                for obj in i.ChildObjects:
                    App.ActiveDocument.removeObject(obj.Name)
                    if hasattr(obj.Proxy, "get_drill"):
                        layout.redraw()
        if hasattr(element, "get_drill"):
            layout.redraw()
        if "Adapter" in feature.Object.Name:
            return False
        return True

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
