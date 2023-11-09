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
    drill = drill_obj.Proxy.get_drill(drill_obj)
    drill.Placement = drill_obj.BasePlacement
    drill.translate(App.Vector(-obj.BasePlacement.Base))
    return part.cut(drill)

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

def _custom_cylinder(dia, dz, x, y, z, head_dia=0, head_dz=0, dir=(0, 0, -1), countersink=False):
    part = Part.makeCylinder(dia/2, dz, App.Vector(0, 0, 0), App.Vector(*dir))
    if head_dia != 0 and head_dz != 0:
        if countersink:
            part = part.fuse(Part.makeCone(head_dia/2, dia/2, head_dz, App.Vector(0, 0, 0), App.Vector(*dir)))
        else:
            part = part.fuse(Part.makeCylinder(head_dia/2, head_dz, App.Vector(0, 0, 0), App.Vector(*dir)))
    part.translate(App.Vector(x, y, z))
    part = part.fuse(part)
    return part


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
        self.mount_dz = -inch/2

    # function which returns the drilling required to mount component
    def get_drill(self, obj):
        part = _custom_cylinder(dia=self.mount_bolt['tap_dia'], dz=drill_depth,
                                x=0, y=0, z=self.mount_dz)
        return part

    # this defines the component body itself
    def execute(self, obj):
        part = _custom_box(dx=obj.Side_Length.Value, dy=obj.Side_Length.Value, dz=obj.Side_Length.Value,
                           x=0, y=0, z=self.mount_dz)
        part = part.cut(_custom_cylinder(dia=self.mount_bolt['clear_dia'], dz=obj.Side_Length.Value,
                                    head_dia=self.mount_bolt['head_dia'], head_dz=self.mount_bolt['head_dz'],
                                    x=0, y=0, z=obj.Side_Length.Value+self.mount_dz))
        obj.Shape = part


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

        obj.ViewObject.ShapeColor = mount_color

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_14_20['clear_dia'], dz=drill_depth,
                           head_dia=bolt_14_20["washer_dia"], head_dz=obj.BoreDepth.Value,
                           x=0, y=0, z=-inch/2)
        return part

    def execute(self, obj):
        bolt_len = inch-(obj.BoreDepth.Value-bolt_14_20['head_dz'])

        part = _custom_cylinder(dia=bolt_14_20['tap_dia'], dz=bolt_len,
                           head_dia=bolt_14_20['head_dia'], head_dz=bolt_14_20['head_dz'],
                           x=0, y=0, z=-inch*3/2+bolt_len)
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
    def __init__(self, obj, drill=True, mount_hole_dy=20, adapter_height=8, outer_thickness=2):
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
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=0, y=i*obj.MountHoleDistance.Value/2, z=0))
        return part

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        dz = obj.AdapterHeight.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=0,
                           dir=(0, 0, -1), fillet=5)
        part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                    head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dia'],
                                    x=0, y=0, z=-dz, dir=(0,0,1)))
        for i in [-1, 1]:
            part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
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
        cube_tol (float) : The tolerance for size of the recess in the skate mount
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, cube_size=10, mount_hole_dy=20, cube_depth=1, outer_thickness=2, cube_tol=0.1):
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
        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=0, y=-obj.MountHoleDistance.Value/2, z=-inch/2)
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                     x=0, y=obj.MountHoleDistance.Value/2, z=-inch/2))
        return part

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.MountHoleDistance.Value
        dz = inch/2-obj.CubeSize.Value/2+obj.CubeDepth.Value
        cut_dx = obj.CubeSize.Value+obj.CubeTolerance.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=0, z=-inch/2, fillet=5)
        part = part.cut(_custom_box(dx=cut_dx, dy=cut_dx, dz=obj.CubeDepth.Value,
                                    x=0, y=0, z=-obj.CubeSize.Value/2))
        for i in [-1, 1]:
            part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=dz,
                                        head_dia=bolt_8_32['head_dia'], head_dz=bolt_8_32['head_dia'],
                                        x=0, y=i*obj.MountHoleDistance.Value/2, z=-inch/2+dz))
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
        
        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode('Placement', 2)

    def get_drill(self, obj):
        bolt_dy = -obj.PostThickness.Value-(obj.SlotLength.Value+bolt_8_32['head_dia']+obj.OuterThickness.Value*2)/2

        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=0, y=bolt_dy+obj.DrillOffset.Value, z=-inch/2)
        return part

    def execute(self, obj):
        dx = bolt_8_32['head_dia']+obj.OuterThickness.Value*2
        dy = dx+obj.SlotLength.Value+obj.PostThickness.Value
        dz = obj.AdapterHeight.Value

        part = _custom_box(dx=dx, dy=dy, dz=dz,
                           x=0, y=-dy/2, z=-inch/2, fillet=4)
        part = part.cut(_custom_box(dx=bolt_8_32['clear_dia'], dy=obj.SlotLength.Value+bolt_8_32['clear_dia'], dz=dz,
                                    x=0, y=-dy/2-obj.PostThickness.Value/2, z=-inch/2, fillet=bolt_8_32['clear_dia']/2))
        part = part.cut(_custom_box(dx=bolt_8_32['head_dia'], dy=obj.SlotLength.Value+bolt_8_32['head_dia'], dz=bolt_8_32['head_dia'],
                                    x=0, y=-dy/2-obj.PostThickness.Value/2, z=-inch/2+bolt_8_32['head_dia'], fillet=bolt_8_32['head_dia']/2))
        part = part.fuse(_custom_box(dx=dx, dy=obj.PostThickness.Value, dz=inch/2+bolt_8_32['clear_dia'],
                                     x=0, y=-obj.PostThickness.Value/2, z=-inch/2))
        part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=obj.PostThickness.Value,
                                    x=0, y=0, z=0, dir=(0, -1, 0)))
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
        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=inch,
                           x=0, y=0, z=-20.7, dir=(1,0,0))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=inch,
                                     x=0, y=-12.7, z=-20.7, dir=(1,0,0)))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=inch,
                                     x=0, y=12.7, z=-20.7, dir=(1,0,0)))
        return part

    def execute(self, obj):
        mesh = _import_stl("HCA3-Step.stl", (90, -0, 90), (-6.35, 19.05, -26.87))
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

        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert
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

        _add_linked_object(obj, "Adapter", skate_mount, cube_size=obj.CubeSize.Value)

    def execute(self, obj):
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
        invert (bool) : Whether the mount should be offset 90 degrees from the component
        mount_hole_dy (float) : The spacing between the two mount holes of it's adapter
        wave_plate_part_num (string) : The Thorlabs part number of the wave plate being used

    Sub-Parts:
        surface_adapter (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, invert=False, wave_plate_part_num='', adapter_args=dict()):
        adapter_args.setdefault("mount_hole_dy", 25)
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['RSP05', wave_plate_part_num]
        self.tran = True
        self.in_limit = 0
        self.in_width = inch/2

        _add_linked_object(obj, "Surface Adapter", surface_adapter, pos_offset=(-6.35, 0, -13.97), rot_offset=(0, 0, 90*obj.Invert), **adapter_args)

    def execute(self, obj):
        mesh = _import_stl("RSP05-Step.stl", (90, -0, 90), (-5.715, -0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class mirror_mount_k05s2:
    '''
    Mirror mount, model K05S2

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, mirror=True, mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'Mirror').Mirror = mirror

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-K05S1']
        self.x_offset = 0

        if mirror:
            _add_linked_object(obj, "Mirror", circular_mirror, **mirror_args)
            self.x_offset = -obj.ChildObjects[0].Thickness.Value

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-8+self.x_offset, y=0, z=-inch/2)
        part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                     x=-8+self.x_offset, y=-5, z=-inch/2))
        part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                     x=-8+self.x_offset, y=5, z=-inch/2))
        part = part.fuse(_custom_box(dx=17, dy=20, dz=(0.08*inch)+4,
                                     x=-(15+15)+self.x_offset, y=-31/2+6, z=-inch/2-0.08*inch-4, fillet=2))
        return part

    def execute(self, obj):
        mesh = _import_stl("POLARIS-K05S2-Step.stl", (90, -0, -90), (-4.514+self.x_offset, 0.254, -0.254))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class mirror_mount_k05s1:
    '''
    Mirror mount, model K05S1

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, mirror=True, mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'Mirror').Mirror = mirror

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-K05S1']
        self.x_offset = 0

        if mirror:
            _add_linked_object(obj, "Mirror", circular_mirror, **mirror_args)
            self.x_offset = -obj.ChildObjects[0].Thickness.Value

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-8+self.x_offset, y=0, z=-inch/2)
        part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                     x=-8+self.x_offset, y=-5, z=-inch/2))
        part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                     x=-8+self.x_offset, y=5, z=-inch/2))
        return part

    def execute(self, obj):
        mesh = _import_stl("POLARIS-K05S1-Step.stl", (90, 0, -90), (-4.514+self.x_offset, 0.254, -0.254))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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
    def __init__(self, obj, drill=True, splitter=True, splitter_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'Splitter').Splitter = splitter

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-B05G']
        self.x_offset = 0

        if splitter:
            _add_linked_object(obj, "Splitter Plate", circular_splitter, **splitter_args)
            self.x_offset = -obj.ChildObjects[0].Thickness.Value

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_8_32['tap_dia'],
                           dz=drill_depth, x=-5+self.x_offset, y=0, z=-inch/2)
        part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                     x=-5+self.x_offset, y=-5, z=-inch/2))
        part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                     x=-5+self.x_offset, y=5, z=-inch/2))
        return part

    def execute(self, obj):
        mesh = _import_stl("POLARIS-B05G-Step.stl", (90, -0, 90), (-17.54+self.x_offset, -5.313, -19.26))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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
    def __init__(self, obj, drill=True, mirror=True, mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'Mirror').Mirror = mirror

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-C05G']
        self.x_offset = 0

        if mirror:
            _add_linked_object(obj, "Mirror", circular_mirror, **mirror_args)
            self.x_offset = -obj.ChildObjects[0].Thickness.Value

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-6.4+self.x_offset, y=0, z=-inch/2)
        part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                     x=-6.4+self.x_offset, y=-5, z=-inch/2))
        part = part.fuse(_custom_cylinder(dia=2, dz=2.2,
                                     x=-6.4+self.x_offset, y=5, z=-inch/2))
        return part

    def execute(self, obj):
        mesh = _import_stl("POLARIS-C05G-Step.stl", (90, -0, 90), (-18.94+self.x_offset, -4.246, -15.2))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class mirror_mount_km05:
    '''
    Mirror mount, model KM05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, mirror=True, bolt_length=15, mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'Mirror').Mirror = mirror
        obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM05']
        self.x_offset = 0

        if mirror:
            _add_linked_object(obj, "Mirror", circular_mirror, **mirror_args)
            self.x_offset = -obj.ChildObjects[0].Thickness.Value

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_8_32['clear_dia'], dz=inch,
                           head_dia=bolt_8_32['head_dia'], head_dz=0.92*inch-obj.BoltLength.Value,
                           x=-7.4+self.x_offset, y=0, z=-inch*3/2, dir=(0,0,1))
        if obj.Drill:
            part = part.fuse(_custom_box(dx=18, dy=31, dz=0.08*inch,
                                        x=-2.4+self.x_offset, y=0, z=-inch/2-0.08*inch, fillet=3))
            part = part.fuse(_custom_box(dx=18, dy=9, dz=0.08*inch,
                                        x=-7.4+self.x_offset, y=-31/2+4.5, z=-inch/2-0.08*inch, fillet=2))
            part = part.fuse(_custom_box(dx=17, dy=20, dz=(0.08*inch)+4,
                                        x=-(15+8.4)+self.x_offset, y=-31/2+4.5, z=-inch/2-0.08*inch-4, fillet=2))
        return part

    def execute(self, obj):
        mesh = _import_stl("KM05-Step.stl", (90, -0, 90), (2.084+self.x_offset, -1.148, 0.498))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class mirror_mount_ks1t:
    '''
    Mirror mount, model KM05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        mirror (bool) : Whether to add a mirror component to the mount
        bolt_length (float) : The length of the bolt used for mounting

    Sub-Parts:
        circular_mirror (mirror_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, mirror=False, bolt_length=15, mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyBool', 'Mirror').Mirror = mirror
        obj.addProperty('App::PropertyLength', 'BoltLength').BoltLength = bolt_length

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM1T']
        self.x_offset = 0

        if mirror:
            _add_linked_object(obj, "Mirror", circular_mirror, **mirror_args)
            self.x_offset = -obj.ChildObjects[0].Thickness.Value

    def get_drill(self, obj):
        dx, dy, dz = 55, 60, inch/2
        x, y, z = -25, 0, -inch/2
        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                x=-16.94+self.x_offset, y=0, z=-inch/2, dir=(0,0,-1))
        part = part.fuse(_custom_box(dx=dx, dy=dy, dz=dz,
                                     x=x+self.x_offset, y=y, z=z,
                                     fillet=3, dir=(0, 0, -1)))
        part = part.fuse(_custom_box(dx=dx/2, dy=dy, dz=dz+2,
                                     x=-25+self.x_offset, y=0, z=z,
                                     fillet=3, fillet_dir=(0, 0, 1),
                                     dir=(-1, 0, -1)))
        return part

    def execute(self, obj):
        mesh = _import_stl("KS1T-Step.stl", (90, -0, -90), (22.06, 13.37, -30.35))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class fiberport_mount_km05:
    '''
    Mirror mount, model KM05, adapted to use as fiberport mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled

    Sub-Parts:
        mirror_mount_km05 (mount_args)
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, mount_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor = misc_color
        
        self.part_numbers = []
        self.in_limit = 0
        self.in_width = 1

        _add_linked_object(obj, "Mount", mirror_mount_km05, pos_offset=(0, 0, 0), mirror=False, **mount_args)

    def execute(self, obj):
        part = _custom_cylinder(dia=inch/2, dz=25.5,
                           x=0, y=0, z=0, dir=(1, 0, 0))
        obj.Shape = part


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
        
        self.part_numbers = []
        self.in_limit = pi-0.01
        self.in_width = 1

        mount = _add_linked_object(obj, "Mount", mirror_mount_km05, pos_offset=(-6, 0, 0), drill=False, mirror=False, **mount_args)
        upper_plate = _add_linked_object(obj, "Upper Plate", km05_tec_upper_plate, pos_offset=(-10, 0, -0.08*inch), drill_obj=mount, **upper_plate_args)
        _add_linked_object(obj, "Lower Plate", km05_tec_lower_plate, pos_offset=(-10, 0, -0.08*inch-tec_thickness-upper_plate.Thickness.Value), **lower_plate_args)

    def execute(self, obj):
        part = _custom_cylinder(dia=inch/2, dz=40,
                           x=10, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part


class km05_tec_upper_plate:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill_obj, width=inch, thickness=0.25*inch):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLinkHidden', 'DrillObject').DrillObject = drill_obj

        obj.ViewObject.ShapeColor = adapter_color
        self.part_numbers = []

    def execute(self, obj):
        part = _custom_box(dx=obj.Width.Value, dy=obj.Width.Value, dz=obj.Thickness.Value,
                           x=0, y=0, z=-inch/2, dir=(0, 0, -1))
        part = _drill_part(part, obj, obj.DrillObject)
        obj.Shape = part


class km05_tec_lower_plate:
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, width=1.5*inch, thickness=0.25*inch):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness

        obj.ViewObject.ShapeColor = adapter_color
        self.part_numbers = []

    def get_drill(self, obj):
        part = _custom_box(obj.Width.Value+5, obj.Width.Value+5, drill_depth, 0, 0, -inch/2-obj.Thickness.Value, 3, dir=(0, 0, 1))
        for x, y in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                              x=(obj.Width.Value/2-4)*x, y=(obj.Width.Value/2-4)*y, z=0, dir=(0, 0, -1)))
        return part

    def execute(self, obj):
        part = _custom_box(dx=obj.Width.Value, dy=obj.Width.Value, dz=obj.Thickness.Value,
                                     x=0, y=0, z=-inch/2, dir=(0, 0, -1))
        for x, y in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            part = part.cut(_custom_cylinder(dia=bolt_8_32['clear_dia'], dz=obj.Thickness.Value,
                                        x=(obj.Width.Value/2-4)*x, y=(obj.Width.Value/2-4)*y, z=-inch/2, dir=(0, 0, -1)))
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
    def __init__(self, obj, drill=True, mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['MK05']
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = inch/2

        _add_linked_object(obj, "Mirror", circular_mirror, **mirror_args)

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                           head_dia=bolt_4_40['head_dia'], head_dz=drill_depth-10,
                           x=-10.2, y=0, z=-10.2-drill_depth, dir=(0, 0, 1))
        return part

    def execute(self, obj):
        mesh = _import_stl("MK05-Step.stl", (90, -0, -90), (-22.91-obj.ChildObjects[0].Thickness.Value, 26, -5.629))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class mount_mk05pm:
    '''
    Mount, model MK05

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['MK05PM']

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_4_40['tap_dia'], dz=drill_depth,
                           head_dia=bolt_4_40['head_dia'], head_dz=drill_depth-5,
                           x=-7.675, y=7.699, z=4.493-10.2-drill_depth, dir=(0,0,1))
        part = part.fuse(_custom_box(dx=32, dy=25, dz=5,
                                     x=-7.675+10, y=7.699, z=4.493-11.3, fillet=2))
        return part

    def execute(self, obj):
        mesh = _import_stl("MK05PM-Step.stl", (180, 90, 0), (-7.675, 7.699, 4.493))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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
    def __init__(self, obj, littrow_angle=45, mount_args=dict(), grating_args=dict(), mirror_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyAngle', 'LittrowAngle').LittrowAngle = littrow_angle

        obj.ViewObject.ShapeColor = adapter_color
        self.part_numbers = []
        self.dx = 12/tan(radians(2*obj.LittrowAngle))

        _add_linked_object(obj, "Mount MK05PM", mount_mk05pm, pos_offset=(-12, -4, -4-12.7/2+2), **mount_args)
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
    def __init__(self, obj, drill=True, lens_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['POLARIS-L05G']

        _add_linked_object(obj, "Lens", circular_lens, **lens_args)

    def get_drill(self, obj):
        part = _custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                           x=-9.5, y=0, z=-inch/2)
        for i in [-1,1]:
            part = part.fuse(_custom_box(dx=5, dy=2, dz=2.2,
                                         x=-9.5, y=i*5, z=-inch/2,
                                         fillet=1, dir=(0, 0, -1)))
        return part

    def execute(self, obj):
        mesh = _import_stl("POLARIS-L05G-Step.stl", (90, -0, 90), (-26.57-obj.ChildObjects[0].Thickness.Value/2, -13.29, -18.44))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IDA12-P5']
        self.tran = True
        self.in_limit = 0
        self.in_width = 1
        self.block_width=inch/2
        self.slot_length=adapter_args['slot_length']

        _add_linked_object(obj, "Slide Mount", slide_mount,
                           pos_offset=(1.956, -12.83, 0), **adapter_args)

    def get_drill(self, obj):
        part = _custom_box(dx=6.5, dy=10+obj.ChildObjects[0].SlotLength.Value, dz=1,
                           x=1.956, y=0, z=-inch/2,
                           fillet=2, dir=(0,0,-1))
        return part

    def execute(self, obj):
        mesh = _import_stl("IDA12-P5-Step.stl", (90, 0, -90), (1.549, 0, -0))
        mesh.rotate(-pi/2, 0, 0)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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

        obj.ViewObject.ShapeColor = mount_color
        self.part_numbers = ['KM100PM']

    def get_drill(self, obj):
        part = _custom_box(dx=34, dy=54.5, dz=24.27,
                           x=-19.27, y=-8.02, z=0,
                           fillet=5, dir=(0, 0, -1))
        part = part.fuse(_custom_box(dx=40, dy=17.5, dz=26.2,
                                     x=-44.77, y=-26.52, z=0,
                                     fillet=5, dir=(0, 0, -1)))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                     x=-29.27, y=-7.52, z=0))
        part.translate(App.Vector((15.25, 20.15, 17.50)))
        part = part.fuse(part)
        return part

    def execute(self, obj):
        mesh = _import_stl("KM100PM-Step.stl", (90, -0, -90), (-8.877, 38.1, -6.731))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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

        obj.ViewObject.ShapeColor = mount_color
        obj.setEditorMode('Placement', 2)
        

    def get_drill(self, obj):
        part = _custom_box(dx=34, dy=54.5, dz=24.27,
                           x=-19.27+15, y=-8.02, z=0,
                           fillet=5, dir=(0, 0, -1))
        part.translate(App.Vector((15.25, 20.15, 17.50)))
        part = part.fuse(part)
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
            part = part.cut(_custom_cylinder(dia=bolt_4_40['clear_dia'], dz=stage_dz, head_dia=bolt_4_40['head_dia'],
                                        head_dz=obj.CounterDepth.Value, countersink=obj.Countersink,
                                        x=11.25, y=18.9+ddy, z=dz-4, dir=(0,0,1)))
        part.translate(App.Vector(dx/2, 25.4-15.2+obj.SlotLength.Value/2, -6.4))
        part = part.fuse(part)
        obj.Shape = part
        

class isomet_1205c_on_km100pm:
    '''
    Isomet 1205C AOM on KM100PM Mount

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
        diffraction_angle (float) : The diffraction angle (in radians) of the AOM
        forward_direction (integer) : The direction of diffraction on forward pass (1=right, -1=left)
        backward_direction (integer) : The direction of diffraction on backward pass (1=right, -1=left)

    Sub-Parts:
        prism_mount_km100pm (mount_args)
        mount_for_km100pm (adapter_args)
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True, diffraction_angle=-0.026, forward_direction=True, backward_direction=True, mount_args=dict(), adapter_args=dict()):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyAngle', 'DiffractionAngle').DiffractionAngle = diffraction_angle
        obj.addProperty('App::PropertyInteger', 'ForwardDirection').ForwardDirection = forward_direction
        obj.addProperty('App::PropertyInteger', 'BackwardDirection').BackwardDirection = backward_direction

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['ISOMET_1205C']
        self.diff_angle = diffraction_angle
        self.diff_dir = (forward_direction, backward_direction)
        self.tran = True
        self.in_limit = 0
        self.in_width = 5

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

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IOT-5-670-VLP']
        self.tran = True
        self.in_limit = pi/2
        self.in_width = inch/2

        _add_linked_object(obj, "Surface Adapter", surface_adapter,
                           pos_offset=(0, 0, -22.1), **adapter_args)

    def get_drill(self, obj):
        part = _custom_box(dx=80, dy=25, dz=5,
                           x=0, y= 0, z=-inch/2,
                           fillet=5, dir=(0, 0, -1))
        return part

    def execute(self, obj):
        mesh = _import_stl("IOT-5-670-VLP-Step.stl", (90, 0, -90), (-19.05, -0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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

        obj.ViewObject.ShapeColor = misc_color
        self.part_numbers = ['IO-3D-405-PBS']
        self.tran = True
        self.in_limit = pi/2
        self.in_width = inch/2

        _add_linked_object(obj, "Surface Adapter", surface_adapter,
                           pos_offset=(0, 0, -17.15), **adapter_args)

    def get_drill(self, obj):
        part = _custom_box(dx=25, dy=15, dz=drill_depth,
                           x=0, y=0, z=-inch/2,
                           fillet=5, dir=(0, 0, 1))
        return part

    def execute(self, obj):
        mesh = _import_stl("IO-3D-405-PBS-Step.stl", (90, 0, -90), (-9.461, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = width

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
    def __init__(self, obj, drill=True, thickness=3, diameter=inch/2, part_number=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.part_numbers = [part_number]
        self.tran = True
        self.ref_angle = 0
        self.in_limit = 0
        self.in_width = inch/2

    def execute(self, obj):
        part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
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
    def __init__(self, obj, drill=True, focal_length=50, thickness=3, diameter=inch/2, part_number=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'FocalLength').FocalLength = focal_length
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        obj.ViewObject.ShapeColor = glass_color
        obj.ViewObject.Transparency=50
        self.part_numbers = [part_number]
        self.tran = True
        self.foc_len = obj.FocalLength.Value
        self.in_limit = 0
        self.in_width = inch/2

    def execute(self, obj):
        part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
                           x=obj.Thickness.Value/2, y=0, z=0, dir=(-1, 0, 0))
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
    def __init__(self, obj, drill=True, thickness=6, diameter=inch/2, part_num=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Diameter').Diameter = diameter

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = [part_num]
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = diameter

    def execute(self, obj):
        part = _custom_cylinder(dia=obj.Diameter.Value, dz=obj.Thickness.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part


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
    def __init__(self, obj, drill=True, thickness=3.2, width=12.7, height=12.7, part_num=''):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'Thickness').Thickness = thickness
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'Height').Height = height

        obj.ViewObject.ShapeColor = glass_color
        self.part_numbers = [part_num]
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = width

    def execute(self, obj):
        part = _custom_box(dx=obj.Thickness.Value, dy=obj.Width.Value, dz=obj.Height.Value,
                           x=0, y=0, z=0, dir=(-1, 0, 0))
        obj.Shape = part


class rb_cell:
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

        obj.ViewObject.ShapeColor = adapter_color
        self.tran = True
        self.in_limit = 0
        self.in_width = 1

    def get_drill(self, obj):
        dx = 90
        dy = 52

        part = _custom_box(dx=dx+20, dy=dy+20, dz=25.4-inch/2,
                           x=0, y=10, z=-inch/2,
                           fillet=3, dir=(0,0,-1))
        for x, y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=x*dx/2, y=y*15.7, z=-inch/2))
        part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                     x=45, y=-15.7, z=-inch/2))
        for x in [1,-1]:
            part = part.fuse(_custom_cylinder(dia=bolt_8_32['tap_dia'], dz=drill_depth,
                                         x=x*dx/2, y=25.7, z=-inch/2))
        return part

    def execute(self, obj):
        mesh = _import_stl("rb_cell_holder_middle.stl", (0, 0, 0), ([0, 5, 0]))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class photodetector_pda10a2:
    '''
    Photodetector, model pda10a2

    Args:
        drill (bool) : Whether baseplate mounting for this part should be drilled
    
    '''
    type = 'Mesh::FeaturePython'
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill

        obj.ViewObject.ShapeColor = misc_color
        self.in_limit = 0
        self.in_width = 1

        _add_linked_object(obj, "Surface Adapter", surface_adapter, pos_offset=(-10.54, 0, -25))

    def get_drill(self, obj):
        part = _custom_box(dx=30, dy=55, dz=25-inch/2,
                           x=-10.54, y=0, z=-inch/2,
                           fillet=3, dir=(0,0,-1))
        return part

    def execute(self, obj):
        mesh = _import_stl("PDA10A2-Step.stl", (90, 0, -90), (-19.87, -0, -0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


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
        mirror_type x2
    '''
    type = 'Part::FeaturePython'
    def __init__(self, obj, drill=True, lower_dz=inch, upper_dz=3*inch, mirror_type=mirror_mount_k05s2, invert=False, table_mount=True):
        obj.Proxy = self
        ViewProvider(obj.ViewObject)

        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'LowerHeight').LowerHeight = lower_dz
        obj.addProperty('App::PropertyLength', 'UpperHeight').UpperHeight = upper_dz
        obj.addProperty('App::PropertyBool', 'Invert').Invert = invert
        obj.addProperty('App::PropertyBool', 'TableMount').TableMount = table_mount

        obj.ViewObject.ShapeColor = adapter_color
        self.in_limit = pi-0.01
        self.in_width = 1
        self.z_off = -inch/2-obj.TableMount*inch

        _add_linked_object(obj, "Lower Mirror", mirror_type, rot_offset=((-1)**invert*90, -45, 0), pos_offset=(0, 0, obj.LowerHeight.Value+self.z_off))
        _add_linked_object(obj, "Upper Mirror", mirror_type, rot_offset=((-1)**invert*90, 135, 0), pos_offset=(0, 0, obj.UpperHeight.Value+self.z_off))

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
            obj.Placement.Base = obj.BasePlacement.Base + obj.Baseplate.Placement.Base
            obj.Placement = App.Placement(obj.Placement.Base, obj.Baseplate.Placement.Rotation, -obj.BasePlacement.Base)
            obj.Placement.Rotation = obj.Placement.Rotation.multiply(obj.BasePlacement.Rotation)
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
