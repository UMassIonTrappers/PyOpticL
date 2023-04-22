import FreeCAD as App
import Mesh
import Part
from math import *
from . import layout
import numpy as np

from pathlib import Path

STL_PATH_thorlabs = str(Path(__file__).parent.resolve()) + "\\stl\\thorlabs\\"
STL_PATH_newport = str(Path(__file__).parent.resolve()) + "\\stl\\newport\\"

# Set all static dimentions
INCH = 25.4

TAP_DIA_6_32 = 0.1065*INCH
TAP_DIA_8_32 = 0.1360*INCH
TAP_DIA_14_20 = 0.201*INCH

CLR_DIA_4_40 = 0.120*INCH
TAP_DIA_4_40 = 0.089*INCH
NUT_DIA_4_40 = 6.4
HEAD_DIA_4_40 = 5.50

CLR_DIA_8_32 = 0.172*INCH
CLR_DIA_14_20 = 0.260*INCH

HEAD_DIA_8_32 = 7
HEAD_DIA_14_20 = 9.8

HEAD_DZ_8_32 = 4.4
HEAD_DZ_14_20 = 8

WASHER_DIA_14_20 = 9/16 * INCH; #12 washer

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

def _add_linked_object(obj, obj_name, obj_class, **args):
    new_obj = App.ActiveDocument.addObject(obj_class.type, obj_name)
    new_obj.addProperty("App::PropertyLinkChild","LinkToParent")
    new_obj.LinkToParent=obj
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

class baseplate_mount:
    '''
    Mount holes for attaching to an optical table
    Currently uses 14_20 bolts

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        bore_depth (float) : The depth (in mm) for the counterbore of the mount hole
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, bore_depth=10, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'BoreDepth').BoreDepth = bore_depth
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)
        ViewProvider(obj.ViewObject)

    def get_drill(self, obj):
        part = _mount_hole(CLR_DIA_14_20, drill_depth, 0, 0, -INCH/2, WASHER_DIA_14_20, obj.BoreDepth.Value)
        return part

    def execute(self, obj):
        len = INCH-obj.BoreDepth.Value+HEAD_DZ_14_20
        part = _mount_hole(CLR_DIA_14_20-1, len, 0, 0, -INCH*3/2+len, HEAD_DIA_14_20-1, HEAD_DZ_14_20)
        obj.Shape = part

class surface_adapter:
    '''
    Surface adapter for post-mounted parts

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mount_hole_dy (float) : The spacing (in mm) between the two mount holes of the adapter
        adapter_height (float) : The height (in mm) of the suface adapter
        outer_thickness (float) : The thickness (in mm) of the walls around the bolt holes
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, mount_offset, mount_hole_dy, adapter_height=8, outer_thickness=2, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.mount_offset = mount_offset

    def get_drill(self, obj):
        dx = HEAD_DIA_8_32+obj.OuterThickness.Value*2+1
        dy = obj.MountHoleDistance.Value+HEAD_DIA_8_32+obj.OuterThickness.Value*2+1
        dz = obj.AdapterHeight.Value-self.mount_offset[2]-INCH/2
        part = _custom_box(dx, dy, dz, 0, 0, -INCH/2, 5, (0,0,-1))
        for i in [-1, 1]:
            part = part.fuse(_mount_hole(TAP_DIA_8_32, drill_depth, 0, i*obj.MountHoleDistance.Value/2, -dz-INCH/2))
        return part

    def execute(self, obj):
        dx = HEAD_DIA_8_32+obj.OuterThickness.Value*2
        dy = obj.MountHoleDistance.Value+HEAD_DIA_8_32+obj.OuterThickness.Value*2
        dz = obj.AdapterHeight.Value
        part = _custom_box(dx, dy, dz, 0, 0, 0, 5, (0,0,-1))
        part = part.cut(_mount_hole(CLR_DIA_8_32, dz, 0, 0, -dz, HEAD_DIA_8_32, HEAD_DZ_8_32, dir=(0,0,1)))
        for i in [-1, 1]:
            part = part.cut(_mount_hole(CLR_DIA_8_32, dz, 0, i*obj.MountHoleDistance.Value/2, 0, HEAD_DIA_8_32, HEAD_DZ_8_32))
        part.translate(App.Vector(*self.mount_offset))
        part = part.fuse(part)
        obj.Shape = part
        parent = obj.LinkToParent
        obj.Placement=parent.Mesh.Placement
        

class skate_mount:
    '''
    Skate mount for splitter cubes

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        cube_size (float) : The side length (in mm) of the splitter cube
        mount_hole_dy (float) : The spacing (in mm) between the two mount holes of the adapter
        cube_depth (float) : The depth (in mm) of the recess for the cube
        outer_thickness (float) : The thickness (in mm) of the walls around the bolt holes
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, cube_size, mount_hole_dy=20, cube_depth=1, outer_thickness=2, cube_tol=0.1, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.addProperty('App::PropertyLength', 'CubeDepth').CubeDepth = cube_depth+1e-3
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = cube_tol
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.cube_size = cube_size

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, drill_depth, 0, -obj.MountHoleDistance.Value/2, -INCH/2)
        part = part.fuse(_mount_hole(TAP_DIA_8_32, drill_depth, 0, obj.MountHoleDistance.Value/2, -INCH/2))
        return part

    def execute(self, obj):
        dx = HEAD_DIA_8_32+obj.OuterThickness.Value*2
        dy = obj.MountHoleDistance.Value + CLR_DIA_8_32*2+obj.OuterThickness.Value*2
        dz = INCH/2-self.cube_size/2+obj.CubeDepth.Value
        part = _custom_box(dx, dy, dz, 0, 0, 0, 5, (0,0,-1))
        part = part.cut(_custom_box(self.cube_size+obj.CubeTolerance.Value, self.cube_size+obj.CubeTolerance.Value, obj.CubeDepth.Value, 0, 0, 0, dir=(0,0,-1)))
        for i in [-1, 1]:
            part = part.cut(_mount_hole(CLR_DIA_8_32, dz, 0, i*obj.MountHoleDistance.Value/2, 0, HEAD_DIA_8_32, HEAD_DZ_8_32))
        part.translate(App.Vector(0, 0, -self.cube_size/2+1))
        part = part.fuse(part)
        obj.Shape = part
        parent = obj.LinkToParent
        obj.Placement=parent.Mesh.Placement


class slide_mount:
    '''
    Slide mount adapter for post-mounted parts

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        slot_length (float) : The length (in mm) of the slot used for mounting to the baseplate
        adapter_height (float) : The height (in mm) of the suface adapter
        post_thickness (float) : The thickness (in mm) of the post that mounts to the element
        outer_thickness (float) : The thickness (in mm) of the walls around the bolt holes
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, mount_offset, slot_length, drill_offset=0, adapter_height=8, post_thickness=4, outer_thickness=2, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'SlotLength').SlotLength = slot_length
        obj.addProperty('App::PropertyDistance', 'DrillOffset').DrillOffset = drill_offset
        obj.addProperty('App::PropertyLength', 'AdapterHeight').AdapterHeight = adapter_height
        obj.addProperty('App::PropertyLength', 'PostThickness').PostThickness = post_thickness
        obj.addProperty('App::PropertyLength', 'OuterThickness').OuterThickness = outer_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.mount_offset = mount_offset

    def get_drill(self, obj):
        bolt_dy = self.mount_offset[1]-obj.PostThickness.Value-(obj.SlotLength.Value+HEAD_DIA_8_32+obj.OuterThickness.Value*2)/2
        part = _mount_hole(TAP_DIA_8_32, drill_depth, self.mount_offset[0], bolt_dy+obj.DrillOffset.Value, -INCH/2)
        return part

    def execute(self, obj):
        dx = HEAD_DIA_8_32+obj.OuterThickness.Value*2
        dy = obj.SlotLength.Value+HEAD_DIA_8_32+obj.OuterThickness.Value*2+obj.PostThickness.Value
        dz = obj.AdapterHeight.Value
        part = _custom_box(dx, dy, dz, 0, -dy/2, -INCH/2, 4)
        part = part.cut(_custom_box(CLR_DIA_8_32, obj.SlotLength.Value+CLR_DIA_8_32, dz, 0, -dy/2-obj.PostThickness.Value/2, -INCH/2, CLR_DIA_8_32/2))
        part = part.cut(_custom_box(HEAD_DIA_8_32, obj.SlotLength.Value+HEAD_DIA_8_32, 3, 0, -dy/2-obj.PostThickness.Value/2, -INCH/2+HEAD_DZ_8_32, HEAD_DIA_8_32/2))
        part = part.fuse(_custom_box(dx, obj.PostThickness.Value, INCH/2+CLR_DIA_8_32, 0, -obj.PostThickness.Value/2, -INCH/2))
        part = part.cut(_mount_hole(CLR_DIA_8_32, obj.PostThickness.Value, 0, 0, 0, dir=(0, -1, 0)))
        part.translate(App.Vector(*self.mount_offset))
        part = part.fuse(part)
        obj.Shape = part
        parent = obj.LinkToParent
        obj.Placement=parent.Mesh.Placement


class mount_for_km100pm:
    '''
    Adapter for mounting isomet AOMs to km100pm kinematic mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        slot_length (float) : The length (in mm) of the slots used for mounting to the km100pm
        countersink_depth (float) : The depth (in mm) of the countersinks for the AOM mount holes
        arm_thickness (float) : The thickness (in mm) of the arm the mounts to the km100PM
        arm_clearance (float) : The distance (in mm) between the bottom of the adapter arm and the bottom of the km100pm
        stage_thickness (float) : The thickness (in mm) of the stage that mounts to the AOM
        stage_length (float) : The length (in mm) of the stage that mounts to the AOM
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, mount_offset, slot_length=8, countersink_depth=0, arm_thickness=8, arm_clearance=2, stage_thickness=4, stage_length=21, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'SlotLength').SlotLength = slot_length
        obj.addProperty('App::PropertyLength', 'CountersinkDepth').CountersinkDepth = countersink_depth
        obj.addProperty('App::PropertyLength', 'ArmThickness').ArmThickness = arm_thickness
        obj.addProperty('App::PropertyLength', 'ArmClearance').ArmClearance = arm_clearance
        obj.addProperty('App::PropertyLength', 'StageThickness').StageThickness = stage_thickness
        obj.addProperty('App::PropertyLength', 'StageLength').StageLength = stage_length
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.mount_offset = mount_offset

    def execute(self, obj):
        dx = obj.ArmThickness.Value
        dy = 47.5
        dz = 16.92
        stage_dx = obj.StageLength.Value
        stage_dz = obj.StageThickness.Value
        part = _custom_box(dx, dy, dz-obj.ArmClearance.Value, 0, 0, obj.ArmClearance.Value)
        part = part.fuse(_custom_box(stage_dx, dy, stage_dz, 0, 0, dz, dir=(1,0,-1)))
        for ddy in [15.2, 38.1]:
            part = part.cut(_custom_box(dx, obj.SlotLength.Value+CLR_DIA_4_40, CLR_DIA_4_40, dx/2, 25.4-ddy, 6.4, CLR_DIA_4_40/2, (-1,0,0)))
            part = part.cut(_custom_box(dx/2, obj.SlotLength.Value+HEAD_DIA_4_40, HEAD_DIA_4_40, dx/2, 25.4-ddy, 6.4, HEAD_DIA_4_40/2, (-1,0,0)))
        for ddy in [0, -11.42, -26.65, -38.07]:
            part = part.cut(_mount_hole(CLR_DIA_4_40, stage_dz, 11.25, 18.9+ddy, dz-4, HEAD_DIA_4_40, obj.CountersinkDepth.Value, (0,0,1), True))
        part.translate(App.Vector(*np.add((18, 0, -dz), self.mount_offset)))
        part = part.fuse(part)
        obj.Shape = part
        parent = obj.LinkToParent
        obj.Placement=parent.Mesh.Placement


class universal_mount:
    '''
    Universal adapter allowing for multiple mirror mounts to work on a single baseplate

    Args:
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
        part = part.fuse(_mount_hole(TAP_DIA_8_32, drill_depth, self.mount_offset[0], self.mount_offset[1]-self.dy/2+5, -self.dz-INCH/2))
        part = part.fuse(_mount_hole(TAP_DIA_8_32, drill_depth, self.mount_offset[0], self.mount_offset[1]+self.dy/2-5, -self.dz-INCH/2))
        return part

    def execute(self, obj):
        dz = self.dz+self.zOff+INCH/2
        part = _custom_box(self.dx, self.dy, dz, 0, 0, 0, 4, (0,0,-1))
        temp = _mount_hole(CLR_DIA_8_32, dz, 0, -self.dy/2+5, 0, HEAD_DIA_8_32, HEAD_DZ_8_32)
        temp = temp.fuse(_mount_hole(CLR_DIA_8_32, dz, 0, self.dy/2-5, 0, HEAD_DIA_8_32, HEAD_DZ_8_32))
        part = part.cut(temp)
        part.translate(App.Vector(*self.mount_offset, self.zOff))
        parent = obj.LinkToParent
        temp = parent.Proxy.get_drill(parent)
        temp.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0), App.Vector(0, 0, 0))
        part = part.cut(temp)
        obj.Shape = part
        obj.Placement=parent.Mesh.Placement


class fiberport_holder:
    '''
    Part for mounting an HCA3 fiberport coupler to the side of a baseplate

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.6)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['HCA3','PAF2-5A'] #https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=2940
        self.in_limit = pi-0.01
        self.in_width = 1

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, INCH, 0, 0, -20.7, dir=(1,0,0))
        part = part.fuse(_mount_hole(TAP_DIA_8_32, INCH, 0, -12.7, -20.7, dir=(1,0,0)))
        part = part.fuse(_mount_hole(TAP_DIA_8_32, INCH, 0, 12.7, -20.7, dir=(1,0,0)))
        return part

    def execute(self, obj):
        mesh = _orient_stl("HCA3-Solidworks.stl", (-pi/2, pi, -pi/2), (-6.35, -38.1/2, -26.9), 1)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        

class pbs_on_skate_mount:
    '''
    Beam-splitter cube

    Args:
        invert (bool) : Invert pick-off direction, false is left, true is right
        cube_size (float) : The side length (in mm) of the splitter cube
        cube_part_num (string) : The Thorlabs part number of the splitter cube being used
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, invert=False, cube_size=10, cube_part_num='PBS101'):
        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'Invert').Invert = invert
        obj.addProperty('App::PropertyLength', 'CubeSize').CubeSize = cube_size
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.7)
        obj.ViewObject.Transparency=50
        self.part_numbers = [cube_part_num]
        ViewProvider(obj.ViewObject)
        if invert:
            self.ref_angle = -3*pi/4
        else:
            self.ref_angle = 3*pi/4
        self.tran = True
        self.in_limit = 0
        self.in_width = sqrt(200)
        _add_linked_object(obj, obj.Name+"_Adapter", skate_mount, cube_size=obj.CubeSize.Value)

    def execute(self, obj):
        mesh = Mesh.createBox(obj.CubeSize.Value, obj.CubeSize.Value, obj.CubeSize.Value)
        temp = Mesh.createBox(10-1, sqrt(200)-1, 0.01)
        temp.rotate(0, pi/2, -pi/4)
        mesh = mesh.unite(temp)
        if obj.Invert:
            self.ref_angle = -3*pi/4
            mesh.rotate(0, 0, pi/2)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class rotation_stage_rsp05:
    '''
    Rotation stage, model RSP05

    Args:
        mount_hole_dy (float) : The spacing (in mm) between the two mount holes of it's adapter
        wave_plate_part_num (string) : The Thorlabs part number of the wave plate being used
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mount_hole_dy=25, wave_plate_part_num='', **adapter_args):
        obj.Proxy = self
        obj.ViewObject.ShapeColor=(0.2, 0.2, 0.2)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['RSP05',wave_plate_part_num]
        self.tran = True
        self.in_limit = pi/2
        self.in_width = INCH/2
        _add_linked_object(obj, obj.Name+"_Adapter", surface_adapter, mount_offset=(0, 0, -14), mount_hole_dy=mount_hole_dy, **adapter_args)

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
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['POLARIS-K05S1', mirror_part_num]
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-INCH/2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, drill_depth, -8-obj.MirrorThickness.Value, 0, -INCH/2)
        part = part.fuse(_mount_hole(2, 2.2, -8-obj.MirrorThickness.Value, -5, -INCH/2))
        part = part.fuse(_mount_hole(2, 2.2, -8-obj.MirrorThickness.Value, 5, -INCH/2))
        return part

    def execute(self, obj):
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
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['POLARIS-K05S1' , mirror_part_num]
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-INCH/2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, drill_depth, -8-obj.MirrorThickness.Value, 0, -INCH/2)
        part = part.fuse(_mount_hole(2, 2.2, -8-obj.MirrorThickness.Value, -5, -INCH/2))
        part = part.fuse(_mount_hole(2, 2.2, -8-obj.MirrorThickness.Value, 5, -INCH/2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-K05S1-Solidworks.stl", (0, 0, -pi/2), (-4.5-obj.MirrorThickness.Value, -0.3+0.5, -0.25), 1)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class mirror_mount_c05g:
    '''
    Mirror mount, model C05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_thickness (float) : The thickness (in mm) of the mirror being used
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mirror_thickness=6, uMountParam=None, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = mirror_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['POLARIS-C05G']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-INCH/2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, drill_depth, -6.4-obj.MirrorThickness.Value, 0, -INCH/2)
        part = part.fuse(_mount_hole(2, 2.2, -6.4-obj.MirrorThickness.Value, -5, -INCH/2))
        part = part.fuse(_mount_hole(2, 2.2, -6.4-obj.MirrorThickness.Value, 5, -INCH/2))
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
        mirror_thickness (float) : The thickness (in mm) of the mirror being used
        bolt_length (float) : The length (in mm) of the bolt used for mounting
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mirror_thickness=6, bolt_length=15, uMountParam=None, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = mirror_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['KM05']
        self.bolt_len = bolt_length
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-0.58*INCH)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False
            self.bolt_len = uMountParam[0][2]-0.08*INCH-HEAD_DZ_8_32+5

    def get_drill(self, obj):
        part = _mount_hole(CLR_DIA_8_32, INCH, -13.4, 0, -INCH*3/2, HEAD_DIA_8_32, 0.92*INCH-self.bolt_len+5, dir=(0,0,1))
        part = part.fuse(_custom_box(18, 31, 0.08*INCH, -8.4, 0, -INCH/2-0.08*INCH, 3))
        part = part.fuse(_custom_box(18, 9, 0.08*INCH, -12, -31/2+4.5, -INCH/2-0.08*INCH, 2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("KM05-Solidworks.stl", (0, 0, pi/2), ([-4.05, -1.2, 0.5]))
        temp = Mesh.createCylinder(INCH/4, 6, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_mk05:
    '''
    Mirror mount, model MK05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror_thickness (float) : The thickness (in mm) of the mirror being used
        mirror_part_num (string) : The Thorlabs part number of the mirror being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mirror_thickness=6, uMountParam=[(20, 28, 10), (-10, 0)], drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = mirror_thickness
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['MK05']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            _add_linked_object(obj, obj.Name+"_Adapter", universal_mount, mount_offset=uMountParam[1], size=uMountParam[0], zOff=-10.2)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_4_40, drill_depth, -10.2, 0, -10.2)
        return part

    def execute(self, obj):
        mesh = _orient_stl("MK05-Solidworks.stl", (0, -pi/2, 0), ([-27.5, -5.6, -26.0]), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class splitter_mount_c05g:
    '''
    Splitter mount, model C05G

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        plate_thickness (float) : The thickness (in mm) of the splitter plate being used
        plate_part_num (string) : The Thorlabs part number of the splitter plate being used
        uMountParam (float[3], float[2]) : Universal mount parameters consisting of a tuple for the size of
            the mount in x,y,z and a tuple of the x,y offset of the mount
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, plate_thickness=3, drill=True, plate_part_num=''):
        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'PlateThickness').PlateThickness = plate_thickness
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['POLARIS-C05G', plate_part_num]
        self.ref_angle = 0
        self.tran = True
        self.in_limit = pi/2
        self.in_width = INCH/2

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, drill_depth, -6.4-obj.PlateThickness.Value, 0, -INCH/2)
        part = part.fuse(_mount_hole(2, 2.2, -6.4-obj.PlateThickness.Value, -5, -INCH/2))
        part = part.fuse(_mount_hole(2, 2.2, -6.4-obj.PlateThickness.Value, 5, -INCH/2))
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-C05G-Solidworks.stl", (pi/2, 0, pi/2), (-19, -4.3, -15.2), 1000)
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
        foc_len (float) : The focal length (in mm) of the lens being used
        lens_part_num (string) : The Thorlabs part number of the lens being used
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, foc_len=50, drill=True, lens_part_num=''):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['POLARIS-L05G', lens_part_num]
        self.tran = True
        self.foc_len = foc_len
        self.in_limit = 0
        self.in_width = INCH/2

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, drill_depth, -9.5, 0, -INCH/2)
        part = part.fuse(_mount_hole(2, 2.2, -9.5, -5, -INCH/2))
        part = part.fuse(_mount_hole(2, 2.2, -9.5, 5, -INCH/2))
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
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['IDA12-P5']
        self.tran = True
        self.in_limit = 0
        self.in_width = 1
        self.slot_length=slot_length
        _add_linked_object(obj, obj.Name+"_Adapter", slide_mount, mount_offset=(-0.75, -12.85, 0), slot_length=slot_length, **adapter_args)

    def get_drill(self, obj):
        part = _custom_box(6.5, 10+self.slot_length, 1, -0.75, 0, -INCH/2, 2, (0,0,-1))
        return part

    def execute(self, obj):
        mesh = _orient_stl("IDA12-P5-Solidworks.stl", (-pi/2, 0, -pi/2), (-0.35, 0.05, 0), 1000)
        mesh.rotate(pi/2, 0, 0)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class kinematic_mount_km100pm:
    type = 'Mesh::FeaturePython'
    #https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf
    def __init__(self, obj, mount_offset, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['KM100PM']
        self.mount_offset = mount_offset

    def get_drill(self, obj):
        part = _custom_box(34, 54.5, 23.9, -19.27, -8.02, -23.9, 5)
        part = part.fuse(_custom_box(40, 17.5, 26, -44.77, -26.52, 0, 5, (0,0,-1)))
        part = part.fuse(_mount_hole(TAP_DIA_8_32, drill_depth, -29.27, -7.52, 0))
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
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['ISOMET_1205C']
        self.diff_dir = diff_dir
        self.tran = True
        if exp:
            self.diff_angle = diff_angle
        self.in_limit = 0
        self.in_width = 5

        self.mount = _add_linked_object(obj, obj.Name+"_Mount", kinematic_mount_km100pm, mount_offset=(-(51.8-25.7-12+15.17), -(6.35+0.089*INCH/2), -6.98))
        _add_linked_object(obj, obj.Name+"_Adapter", mount_for_km100pm, mount_offset=(-(51.8-25.7-12+15.17), -(6.35+0.089*INCH/2), -6.98), slot_length=5)

    def execute(self, obj):
        mesh = _orient_stl("isomet_1205c.stl", (0, 0, pi/2), (0, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        self.mount.Placement = obj.Placement
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
        obj.addProperty('App::PropertyLength', 'Lower_dz').Lower_dz = lower_dz
        obj.addProperty('App::PropertyLength', 'Upper_dz').Upper_dz = upper_dz
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.6)
        ViewProvider(obj.ViewObject)
        self.in_limit = pi-0.01
        self.in_width = 1
        if table_mount:
            self.z_off = -3*INCH/2
        else:
            self.z_off = -INCH/2

        self.lower_obj = _add_linked_object(obj, obj.Name+"_Lower_Mirror", lower_mirror)
        self.upper_obj = _add_linked_object(obj, obj.Name+"_Upper_Mirror", upper_mirror)
        self.left_handed = left_handed

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, INCH, 0, 0, -20.7, dir=(1,0,0))
        part = part.fuse(_mount_hole(TAP_DIA_8_32, INCH, 0, -12.7, -20.7, dir=(1,0,0)))
        part = part.fuse(_mount_hole(TAP_DIA_8_32, INCH, 0, 12.7, -20.7, dir=(1,0,0)))
        return part

    def execute(self, obj):
        if self.left_handed:
            inv = -1
        else:
            inv = 1
        width = INCH #Must be INCH wide to keep periscope mirrors 1 inch from mount holes. 
        fillet = 15
        part = _custom_box(70, width, obj.Upper_dz.Value+20, 0, 0, 0)
        for i in [-1, 1]:
            part = part.cut(_custom_box(fillet*2+4, width, obj.Upper_dz.Value+20, i*(35+fillet), 0, 20, 15, dir=(-i,0,1), fillet_dir=(0,1,0)))
            part = part.cut(_mount_hole(CLR_DIA_14_20+0.5, INCH+5, i*INCH, 0, 25, HEAD_DIA_14_20+0.5, 10, dir=(0,0,-1)))
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
    def __init__(self, obj, mount_hole_dy=50, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.2, 0.2, 0.2)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['IOT-5-670-VLP']
        self.tran = True
        self.in_limit = pi/2
        self.in_width = INCH/2
        _add_linked_object(obj, obj.Name+"_Adapter", surface_adapter, mount_offset=(0, 0, -22.1), mount_hole_dy=mount_hole_dy)

    def get_drill(self, obj):
        part = _custom_box(80, 25, 5, 0, 0, -INCH/2, 5, (0,0,-1))
        return part

    def execute(self, obj):
        # mesh = _orient_stl("ISO-04-650-LP.stl", (pi/2, 0, 0), (0, 0, 0), 1, STL_PATH = STL_PATH_newport) #Newport ISO-04-650-LP
        mesh = _orient_stl("IOT-5-670-VLP.stl", (pi/2, 0, pi/2), (19, 0, 0), 1) #Thorlabs 670 (better for injection?)
        # if self.newport:
            # mesh = _orient_stl("ISO-04-650-LP.stl", (pi/2, 0, 0), (19, 0, 0), 1, STL_PATH = STL_PATH_newport) #Newport ISO-04-650-LP
        # else:
            # mesh = _orient_stl("IOT-5-670-VLP.stl", (pi/2, 0, pi/2), (19, 0, 0), 1) #Thorlabs 670
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh



class laser_diode_mount:
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['LT230P-B','AD15NT']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, drill_depth, -13.4*0, 0, -INCH/2)
        return part

    def execute(self, obj):
        mesh = _orient_stl("LT230P-B.stl", (0, pi/2, 0 ), ([0, 0, 0]))
        # temp = Mesh.createCylinder(INCH/4, 6, True, 1, 50)
        # temp.rotate(0, 0, pi)
        # mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh



class laser_grating_mount:
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, mirror_thickness=6, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = mirror_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.part_numbers = ['GH13-24V']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

    def get_drill(self, obj):
        part = _mount_hole(TAP_DIA_8_32, drill_depth, 0, 0, -INCH/2)
        return part

    def execute(self, obj):
        mesh = _orient_stl("GH13-24V.stl", (0, pi/2, 0), ([-3, 0, 0]))
        # temp = Mesh.createCylinder(INCH/4, 6, True, 1, 50)
        # temp.rotate(0, 0, pi)
        # mesh.addMesh(temp)
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
            if hasattr(i, "LinkToParent"):
                if i.LinkToParent == feature.Object:
                    App.ActiveDocument.removeObject(i.Name)
                    if hasattr(i.Proxy, "get_drill"):
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