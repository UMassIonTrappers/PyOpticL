import FreeCAD as App
import Mesh
import Part
from math import *
from . import layout

from pathlib import Path

STL_PATH = str(Path(__file__).parent.resolve()) + "\\stl\\thorlabs\\"

# Set all static dimentions
INCH = 25.4

TAP_DIA_6_32 = 0.1065*INCH
TAP_DIA_8_32 = 0.1360*INCH
TAP_DIA_14_20 = 0.201*INCH

CLEAR_DIA_4_40 = 0.120*INCH
TAP_DIA_4_40 = 0.089*INCH
NUT_DIA_4_40 = 6.4
HEAD_DIA_4_40 = 5.50

CLR_DIA_8_32 = 0.172*INCH
CLR_DIA_14_20 = 0.260*INCH

HEAD_DIA_8_32 = 7
HEAD_DIA_14_20 = 9.8

HEAD_DZ_8_32 = 4.4
HEAD_DZ_14_20 = 10.0

WASHER_DIA_14_20 = 9/16 * INCH; #12 washer

drill_depth = 100
default_mirror_thickness = 6

# Used to tranform an STL such that it's placement matches the optical center
def _orient_stl(stl, rotate, translate, scale=1):
    mesh = Mesh.read(STL_PATH+stl)
    mat = App.Matrix()
    mat.scale(App.Vector(scale, scale, scale))
    mesh.transform(mat)
    mesh.rotate(*rotate)
    mesh.translate(*translate)
    return mesh


def _create_box(dx, dy, dz, x, y, z, fillet=0):
    part = Part.makeBox(dx, dy, dz)
    if fillet != 0:
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(0, 0, 1):
                part = part.makeFillet(fillet, [i])
    part.translate(App.Vector(x-dx/2, y-dy/2, z))
    part = part.fuse(part)
    return part

def _create_hole(dia, dz, x, y, z, head_dia=0, head_dz=0, dir=(0, 0, -1)):
    part = Part.makeCylinder(dia/2, dz, App.Vector(0, 0, 0), App.Vector(*dir))
    temp = Part.makeCylinder(head_dia/2, head_dz, App.Vector(0, 0, 0), App.Vector(*dir))
    part = part.fuse(temp)
    part.translate(App.Vector(x, y, z))
    part = part.fuse(part)
    return part

class baseplate_mount:
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)
        ViewProvider(obj.ViewObject)

    def get_drill(self, obj):
        part = _create_hole(CLR_DIA_14_20+0.5, drill_depth, 0, 0, -INCH/2, WASHER_DIA_14_20+0.5, 10)
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = Mesh.createCylinder((CLR_DIA_14_20-1)/2, INCH, True, 1, 50)
        temp = Mesh.createCylinder((WASHER_DIA_14_20-2)/2, 10, True, 1, 50)
        mesh.addMesh(temp)
        mesh.rotate(0, pi/2, 0)
        mesh.translate(0, 0, -INCH/2+0.5)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class surface_adapter:
    def __init__(self, obj, mountOff, mount_hole_dy, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.MountOffset = mountOff

    def get_drill(self, obj):
        dx = HEAD_DIA_8_32+4
        dy = obj.MountHoleDistance.Value+CLR_DIA_8_32*2+3
        dz = HEAD_DZ_8_32+3-self.MountOffset[2]-INCH/2
        part = _create_box(dx, dy, dz, 0, 0, -dz-INCH/2, 4)
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, 0, -obj.MountHoleDistance.Value/2, -dz-INCH/2))
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, 0, obj.MountHoleDistance.Value/2, -dz-INCH/2))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        dx = HEAD_DIA_8_32+3
        dy = obj.MountHoleDistance.Value+CLR_DIA_8_32*2+2
        dz = HEAD_DZ_8_32+3
        part = _create_box(dx, dy, dz, 0, 0, -dz, 4)
        temp = _create_hole(CLR_DIA_8_32, dz, 0, 0, -dz, HEAD_DIA_8_32, HEAD_DZ_8_32, dir=(0,0,1))
        temp = temp.fuse(_create_hole(CLR_DIA_8_32, dz, 0, -obj.MountHoleDistance.Value/2, 0, HEAD_DIA_8_32, HEAD_DZ_8_32))
        temp = temp.fuse(_create_hole(CLR_DIA_8_32, dz, 0, obj.MountHoleDistance.Value/2, 0, HEAD_DIA_8_32, HEAD_DZ_8_32))
        part = part.cut(temp)
        part.translate(App.Vector(*self.MountOffset))
        part = part.fuse(part)
        obj.Shape = part
        parent = obj.LinkToParent
        obj.Placement=parent.Mesh.Placement
        

class skate_mount:
    def __init__(self, obj, cubeSize, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = 20
        obj.addProperty('App::PropertyLength', 'CubeTolerance').CubeTolerance = 0.1
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.CubeSize = cubeSize

    def get_drill(self, obj):
        part = _create_hole(TAP_DIA_8_32, drill_depth, 0, -obj.MountHoleDistance.Value/2, -INCH/2)
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, 0, obj.MountHoleDistance.Value/2, -INCH/2))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        dx = HEAD_DIA_8_32+5
        dy = obj.MountHoleDistance.Value + CLR_DIA_8_32*2 + 2
        dz = INCH/2-self.CubeSize/2+1
        part = _create_box(dx, dy, dz, 0, 0, -dz, 4)
        temp = _create_box(self.CubeSize+obj.CubeTolerance.Value, self.CubeSize+obj.CubeTolerance.Value, 1+1e-3, 0, 0, -1-1e-3)
        part = part.cut(temp)
        temp = _create_hole(CLR_DIA_8_32, dz, 0, -obj.MountHoleDistance.Value/2, 0, HEAD_DIA_8_32, HEAD_DZ_8_32)
        temp = temp.fuse(_create_hole(CLR_DIA_8_32, dz, 0, obj.MountHoleDistance.Value/2, 0, HEAD_DIA_8_32, HEAD_DZ_8_32))
        part = part.cut(temp)
        part.translate(App.Vector(0, 0, -self.CubeSize/2+1))
        part = part.fuse(part)
        obj.Shape = part
        parent = obj.LinkToParent
        obj.Placement=parent.Mesh.Placement


class slide_mount:
    def __init__(self, obj, mountOff, mount_hole_dy, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.MountOffset = mountOff

    def get_drill(self, obj):
        dx = HEAD_DIA_8_32+4
        dy = obj.MountHoleDistance.Value+CLR_DIA_8_32*2+3
        dz = HEAD_DZ_8_32+3-self.MountOffset[2]-INCH/2
        part = _create_box(dx, dy, dz, 0, 0, -dz-INCH/2, 4)
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, 0, -obj.MountHoleDistance.Value/2, -dz-INCH/2))
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, 0, obj.MountHoleDistance.Value/2, -dz-INCH/2))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        dx = HEAD_DIA_8_32+3
        dy = obj.MountHoleDistance.Value+CLR_DIA_8_32*2+2
        dz = HEAD_DZ_8_32+3
        part = _create_box(dx, dy, dz, 0, 0, -dz, 4)
        part = part.cut(temp)
        part.translate(App.Vector(*self.MountOffset))
        part = part.fuse(part)
        obj.Shape = part
        parent = obj.LinkToParent
        obj.Placement=parent.Mesh.Placement


class universal_mount:
    def __init__(self, obj, size, mountOff, zOff, mountDrill, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)
        obj.setEditorMode('Placement', 2)
        ViewProvider(obj.ViewObject)
        self.dx = size[0]
        self.dy = size[1]
        self.dz = size[2]
        self.mountOffset = mountOff
        self.zOff = zOff
        self.mountDrill = mountDrill

    def get_drill(self, obj):
        part = _create_box(self.dx+1, self.dy+1, self.dz, self.mountOffset[0], self.mountOffset[1], -self.dz-INCH/2, 4)
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, self.mountOffset[0], self.mountOffset[1]-self.dy/2+5, -self.dz-INCH/2))
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, self.mountOffset[0], self.mountOffset[1]+self.dy/2-5, -self.dz-INCH/2))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        dz = self.dz+self.zOff+INCH/2
        part = _create_box(self.dx, self.dy, dz, 0, 0, -dz, 4)
        temp = _create_hole(CLR_DIA_8_32, dz, 0, -self.dy/2+5, 0, HEAD_DIA_8_32, HEAD_DZ_8_32)
        temp = temp.fuse(_create_hole(CLR_DIA_8_32, dz, 0, self.dy/2-5, 0, HEAD_DIA_8_32, HEAD_DZ_8_32))
        part = part.cut(temp)
        part.translate(App.Vector(*self.mountOffset, self.zOff))
        part = part.cut(self.mountDrill)
        obj.Shape = part
        parent = obj.LinkToParent
        obj.Placement=parent.Mesh.Placement


class fiberport_holder:
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.6)
        ViewProvider(obj.ViewObject)
        self.is_ref = False
        self.is_tran = False
        self.in_limit = pi-0.01
        self.in_width = 1

    def get_drill(self, obj):
        part = _create_hole(TAP_DIA_8_32, INCH, 0, 0, -20.7, dir=(1,0,0))
        part = part.fuse(_create_hole(TAP_DIA_8_32, INCH, 0, -12.7, -20.7, dir=(1,0,0)))
        part = part.fuse(_create_hole(TAP_DIA_8_32, INCH, 0, 12.7, -20.7, dir=(1,0,0)))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("HCA3-Solidworks.stl", (-pi/2, pi, -pi/2), (-6.35, -38.1/2, -26.9), 1)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        

class pbs_on_skate_mount:
    def __init__(self, obj, invert=False):
        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'CubeSize').CubeSize = 10
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.7)
        obj.ViewObject.Transparency=50
        self.invert = invert
        ViewProvider(obj.ViewObject)
        self.is_ref = True
        self.is_tran = True
        if invert:
            self.ref_angle = -3*pi/4
        else:
            self.ref_angle = 3*pi/4
        self.tran_angle = 0
        self.in_limit = 0
        self.in_width = sqrt(200)

        adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")
        adapter.addProperty("App::PropertyLink","LinkToParent")
        adapter.LinkToParent=obj
        skate_mount(adapter, obj.CubeSize.Value)
        ViewProvider(adapter.ViewObject)

    def execute(self, obj):
        mesh = Mesh.createBox(obj.CubeSize.Value, obj.CubeSize.Value, obj.CubeSize.Value)
        temp = Mesh.createBox(10-1, sqrt(200)-1, 0.01)
        temp.rotate(0, pi/2, -pi/4)
        mesh = mesh.unite(temp)
        if self.invert:
            self.ref_angle = -3*pi/4
            mesh.rotate(0, 0, pi/2)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class rotation_stage_rsp05:
    def __init__(self, obj):
        obj.Proxy = self
        obj.ViewObject.ShapeColor=(0.2, 0.2, 0.2)
        ViewProvider(obj.ViewObject)
        self.is_ref = False
        self.is_tran = True
        self.tran_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2
        
        adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")
        adapter.addProperty("App::PropertyLinkChild","LinkToParent")
        adapter.LinkToParent=obj
        surface_adapter(adapter, (0, 0, -14), 25)
        ViewProvider(adapter.ViewObject)
        obj.Label = obj.Label

    def execute(self, obj):
        mesh = _orient_stl("RSP05-Solidworks.stl", (pi/2, 0, pi/2), (0.6, 0, 0), 1000)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_k05s2:
    def __init__(self, obj, drill=True, uMountParam=None):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)
        ViewProvider(obj.ViewObject)
        self.is_ref = True
        self.is_tran = False
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")
            adapter.addProperty("App::PropertyLinkChild","LinkToParent")
            adapter.LinkToParent=obj
            universal_mount(adapter, *uMountParam, -INCH/2, self.get_drill(obj))
            ViewProvider(adapter.ViewObject)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _create_hole(TAP_DIA_8_32, drill_depth, -8-obj.MirrorThickness.Value, 0, -INCH/2)
        part = part.fuse(_create_hole(2, 2.2, -8-obj.MirrorThickness.Value, -5, -INCH/2))
        part = part.fuse(_create_hole(2, 2.2, -8-obj.MirrorThickness.Value, 5, -INCH/2))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-K05S2-Solidworks.stl", (0, -pi/2, 0), (-4.5-obj.MirrorThickness.Value, -0.3, -0.25), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


class mirror_mount_c05g:
    def __init__(self, obj, drill=True, uMountParam=None):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.is_ref = True
        self.is_tran = False
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")
            adapter.addProperty("App::PropertyLinkChild","LinkToParent")
            adapter.LinkToParent=obj
            universal_mount(adapter, *uMountParam, -INCH/2, self.get_drill(obj))
            ViewProvider(adapter.ViewObject)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _create_hole(TAP_DIA_8_32, drill_depth, -6.4-obj.MirrorThickness.Value, 0, -INCH/2)
        part = part.fuse(_create_hole(2, 2.2, -6.4-obj.MirrorThickness.Value, -5, -INCH/2))
        part = part.fuse(_create_hole(2, 2.2, -4.6-obj.MirrorThickness.Value, 5, -INCH/2))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-C05G-Solidworks.stl", (pi/2, 0, pi/2), (-19-obj.MirrorThickness.Value, -4.3, -15.2), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_km05:
    def __init__(self, obj, drill=True, uMountParam=None):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.is_ref = True
        self.is_tran = False
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")
            adapter.addProperty("App::PropertyLinkChild","LinkToParent")
            adapter.LinkToParent=obj
            universal_mount(adapter, *uMountParam, -0.58*INCH, self.get_drill(obj))
            ViewProvider(adapter.ViewObject)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _create_hole(TAP_DIA_8_32, drill_depth, -13.4, 0, -INCH/2)
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("KM05-Solidworks.stl", (0, 0, pi/2), ([-4.05, -1.2, 0.5]))
        temp = Mesh.createCylinder(INCH/4, 6, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class mirror_mount_mk05:
    def __init__(self, obj, drill=True, uMountParam=None):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.is_ref = True
        self.is_tran = False
        self.ref_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

        if uMountParam != None:
            adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")
            adapter.addProperty("App::PropertyLinkChild","LinkToParent")
            adapter.LinkToParent=obj
            universal_mount(adapter, *uMountParam, -10.2, self.get_drill(obj))
            ViewProvider(adapter.ViewObject)
            obj.setEditorMode('Drill', 2)
            obj.Drill = False

    def get_drill(self, obj):
        part = _create_hole(TAP_DIA_4_40, drill_depth, -10.2, 0, -10.2)
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("MK05-Solidworks.stl", (0, -pi/2, 0), ([-27.5, -5.6, -26.0]), 1000)
        temp = Mesh.createCylinder(INCH/4, 6, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class splitter_mount_c05g:
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = 0.5
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.is_ref = True
        self.is_tran = True
        self.ref_angle = 0
        self.tran_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

    def get_drill(self, obj):
        part = _create_hole(TAP_DIA_8_32, drill_depth, -6.4-obj.MirrorThickness.Value, 0, -INCH/2)
        part = part.fuse(_create_hole(2, 2.2, -6.4-obj.MirrorThickness.Value, -5, -INCH/2))
        part = part.fuse(_create_hole(2, 2.2, -6.4-obj.MirrorThickness.Value, 5, -INCH/2))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-C05G-Solidworks.stl", (pi/2, 0, pi/2), (-19-obj.MirrorThickness.Value, -4.3, -15.2), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class lens_holder_l05g:
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.is_ref = False
        self.is_tran = True
        self.tran_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

    def get_drill(self, obj):
        part = _create_hole(TAP_DIA_8_32, drill_depth, -9.5, 0, -INCH/2)
        part = part.fuse(_create_hole(2, 2.2, -9.5, -5, -INCH/2))
        part = part.fuse(_create_hole(2, 2.2, -9.5, 5, -INCH/2))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("POLARIS-L05G-Solidworks.stl", (pi/2, 0, pi/2), (-28.0, -13.3, -18.4), 1000)
        temp = Mesh.createCylinder(INCH/4, 1, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

class pinhole_ida12:
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.is_ref = False
        self.is_tran = True
        self.tran_angle = 0
        self.in_limit = pi/2
        self.in_width = INCH/2

    def execute(self, obj):
        mesh = _orient_stl("IDA12-P5-Solidworks.stl", (pi/2, 0, -pi/2), (-0.35, 0.05, 0), 1000)
        mesh.rotate(pi/2, 0, 0)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        

class isomet_1205c_on_km100pm:
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.is_ref = False
        self.is_tran = True
        self.tran_angle = -0.026 #https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf
        self.in_limit = pi/2
        self.in_width = 5

    def get_drill(self, obj):
        part = _create_box(34, 53.5, 23.9, -19.27, -7.52, -23.9, 5)
        part = part.fuse(_create_box(40, 15.5, 26, -44.77, -26.52, -26, 5))
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, -29.27, -7.52, 0))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("isomet_1205c_on_km100pm.stl", (0, 0, 0), (0, 0, 0))
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

      

class isomet_1205c_on_km100pm_doublepass:
    def __init__(self, obj, drill=True):
        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)
        ViewProvider(obj.ViewObject)
        self.is_ref = False
        self.is_tran = True
        self.tran_angle = 0 #doublepass must retro reflect to connect back to PBS
        self.in_limit = 0
        self.in_width = 5

    def get_drill(self, obj):
        part = _create_box(34, 53.5, 23.9, -19.27, -7.52, -23.9, 5)
        part = part.fuse(_create_box(40, 15.5, 26, -44.77, -26.52, -26, 5))
        part = part.fuse(_create_hole(TAP_DIA_8_32, drill_depth, -29.27, -7.52, 0))
        part.Placement=obj.Placement
        return part

    def execute(self, obj):
        mesh = _orient_stl("isomet_1205c_on_km100pm.stl", (0, 0, 0), (0, 0, 0))
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