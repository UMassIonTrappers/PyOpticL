import FreeCAD as App
import Mesh
import Part
from math import *
from . import layout

from pathlib import Path

__package__ = "optics"
__name__ = "optomech"

STL_PATH = str(Path(__file__).parent.resolve()) + "\\stl\\thorlabs\\"

# Set all static dimentions
INCH = 25.4

TAP_DIA_6_32 = 0.1065*INCH
TAP_DIA_8_32 = 0.1360*INCH
TAP_DIA_14_20 = 0.201*INCH

CLR_DIA_8_32 = 0.172*INCH
CLR_DIA_14_20 = 0.260*INCH

HEAD_DIA_8_32 = 7
HEAD_DIA_14_20 = 9.8

HEAD_DZ_8_32 = 4.4
HEAD_DZ_14_20 = 10.0

WASHER_DIA_14_20 = 9/16 * INCH; #12 washer

default_mirror_thickness = 6

# Used to tranform an STL such that it's placement matches the optical center
### Should remove mountOff and integrate directly into each translation
def _orient_stl(stl, rotate, translate, scale=1):
    mesh = Mesh.read(STL_PATH+stl)
    mat = App.Matrix()
    mat.scale(App.Vector(scale, scale, scale))
    mesh.transform(mat)
    mesh.rotate(*rotate)
    mesh.translate(*translate)
    return mesh

# Drill geometry for most mirror mounts
def _mirror_drill(mountOff):
    part = Part.makeCylinder(TAP_DIA_8_32/2, INCH, App.Vector(*mountOff), App.Vector(0, 0, -1))
    tempPart = Part.makeCylinder(TAP_DIA_8_32/2, INCH, App.Vector(*mountOff), App.Vector(0, 0, -1))
    part = part.fuse(tempPart)
    tempPart = Part.makeCylinder(1, 3, App.Vector(*mountOff), App.Vector(0, 0, -1))
    tempPart.translate(App.Vector(0, -5, 0))
    part = part.fuse(tempPart)
    tempPart.translate(App.Vector(0, 10, 0))
    part = part.fuse(tempPart)
    return part

class surface_adapter:

    def __init__(self, obj, mountOff, mount_hole_dy):

        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = mount_hole_dy
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)

        self.Tags = ("adapter", "drill")
        self.ViewProvider = ViewProvider
        self.MountOffset = mountOff

        obj.setEditorMode('Placement', 2)

    def execute(self, obj):

        dx = HEAD_DIA_8_32+3
        dy = obj.MountHoleDistance.Value + CLR_DIA_8_32*2 + 2
        dz = HEAD_DZ_8_32+3
        part = Part.makeBox(dx, dy, dz)
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(0, 0, 1):
                part = part.makeFillet(4, [i])
        part.translate(App.Vector(-dx/2, -dy/2, -dz))
        temp = Part.makeCylinder(CLR_DIA_8_32/2, dz-HEAD_DZ_8_32, App.Vector(0, 0, 0), App.Vector(0, 0, -1))
        temp = temp.fuse(Part.makeCylinder(HEAD_DIA_8_32/2, HEAD_DZ_8_32, App.Vector(0, 0, HEAD_DZ_8_32-dz), App.Vector(0, 0, -1)))
        part = part.cut(temp)
        temp.rotate(App.Vector(0, 0, -dz/2), App.Vector(0, 1, 0), 180)
        temp.translate(App.Vector(0, -obj.MountHoleDistance.Value/2, 0))
        part = part.cut(temp)
        temp.translate(App.Vector(0, obj.MountHoleDistance.Value, 0))
        part = part.cut(temp)
        part.translate(App.Vector(*self.MountOffset))
        part = part.fuse(part)
        obj.Shape = part

        part = Part.makeBox(dx+1, dy+1, dz-self.MountOffset[2]-INCH/2)
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(0, 0, 1):
                part = part.makeFillet(4, [i])
        part.translate(App.Vector(-(dx+1)/2, -(dy+1)/2, -(dz-self.MountOffset[2]-INCH/2)))
        part.translate(App.Vector(0, 0, -INCH/2))
        temp = Part.makeCylinder(TAP_DIA_8_32/2, INCH, App.Vector(0, 0, 0), App.Vector(0, 0, -1))
        temp.translate(App.Vector(0, -obj.MountHoleDistance.Value/2, -(dz-self.MountOffset[2])))
        part = part.fuse(temp)
        temp.translate(App.Vector(0, obj.MountHoleDistance.Value, 0))
        part = part.fuse(temp)
        self.DrillPart = part
        self.DrillPart.Placement = obj.Placement
        layout.redraw()

class skate_mount:

    def __init__(self, obj, cubeSize):

        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'MountHoleDistance').MountHoleDistance = 20
        obj.ViewObject.ShapeColor=(0.6, 0.9, 0.6)

        self.Tags = ("adapter", "drill")
        self.ViewProvider = ViewProvider
        self.CubeSize = cubeSize


    def execute(self, obj):
        
        dx = HEAD_DIA_8_32+5
        dy = obj.MountHoleDistance.Value + CLR_DIA_8_32*2 + 2
        dz = INCH/2-self.CubeSize/2+1
        part = Part.makeBox(dx, dy, dz)
        for i in part.Edges:
            if i.tangentAt(i.FirstParameter) == App.Vector(0, 0, 1):
                part = part.makeFillet(4, [i])
        part.translate(App.Vector(-dx/2, -dy/2, -dz))
        temp = Part.makeBox(self.CubeSize+0.1, self.CubeSize+0.1, 1.1)
        temp.translate(App.Vector(-(self.CubeSize+0.1)/2, -(self.CubeSize+0.1)/2, -1.1))
        part = part.cut(temp)
        temp = Part.makeCylinder(HEAD_DIA_8_32/2, HEAD_DZ_8_32, App.Vector(0, 0, 0), App.Vector(0, 0, -1))
        temp = temp.fuse(Part.makeCylinder(CLR_DIA_8_32/2, dz-HEAD_DZ_8_32, App.Vector(0, 0, -HEAD_DZ_8_32), App.Vector(0, 0, -1)))
        temp.translate(App.Vector(0, -obj.MountHoleDistance.Value/2, 0))
        part = part.cut(temp)
        temp.translate(App.Vector(0, obj.MountHoleDistance.Value, 0))
        part = part.cut(temp)
        part.translate(App.Vector(0, 0, -self.CubeSize/2+1))
        part = part.fuse(part)
        obj.Shape = part

        part = Part.makeCylinder(TAP_DIA_8_32/2, INCH, App.Vector(0, 0, 0), App.Vector(0, 0, -1))
        part.translate(App.Vector(0, -obj.MountHoleDistance.Value/2, -INCH/2))
        temp = part.copy()
        temp.translate(App.Vector(0, obj.MountHoleDistance.Value, 0))
        part = part.fuse(temp)
        self.DrillPart = part
        self.DrillPart.Placement=obj.Placement
        layout.redraw()

class fiberport_holder:

    def __init__(self, obj):

        obj.Proxy = self
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.6)

        self.Tags = ("fiberport", "drill")
        self.ViewProvider = ViewProvider


    def execute(self, obj):

        mesh = _orient_stl("HCA3-Solidworks.stl", (-pi/2, pi, -pi/2), (-6.35, -38.1/2, -26.9), 1)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        temp = Part.makeCylinder(TAP_DIA_8_32/2, INCH, App.Vector(0, 0, -20.7), App.Vector(1, 0, 0))
        part = temp.copy()
        temp.translate(App.Vector(0, -12.7, 0))
        part = part.fuse(temp)
        temp.translate(App.Vector(0, 12.7*2, 0))
        part = part.fuse(temp)
        self.DrillPart = part
        self.DrillPart.Placement=obj.Placement
        layout.redraw()

class pbs_on_skate_mount:

    def __init__(self, obj):

        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'CubeSize').CubeSize = 10
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.7)
        obj.ViewObject.Transparency=50

        self.Tags = ("pbs")
        self.ViewProvider = ViewProvider
        self.Adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")
        skate_mount(self.Adapter, obj.CubeSize.Value)
        ViewProvider(self.Adapter.ViewObject)


    def execute(self, obj):
        
        mesh = Mesh.createBox(obj.CubeSize.Value, obj.CubeSize.Value, obj.CubeSize.Value)
        temp = Mesh.createBox(10-1, sqrt(200)-1, 0.01)
        temp.rotate(0, pi/2, -pi/4)
        mesh = mesh.unite(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        self.Adapter.Placement = mesh.Placement

class rotation_stage_rsp05:

    def __init__(self, obj):

        obj.Proxy = self
        obj.ViewObject.ShapeColor=(0.2, 0.2, 0.2)

        self.Tags = ("rts")
        self.ViewProvider = ViewProvider
        self.Adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")

    def execute(self, obj):
        
        mesh = _orient_stl("RSP05-Solidworks.stl", (pi/2, 0, pi/2), (0.6, 0, 0), 1000)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        surface_adapter(self.Adapter, (0, 0, -14), 25)
        self.Adapter.Placement = mesh.Placement
        ViewProvider(self.Adapter.ViewObject)

        

class mirror_mount_k05s2:

    def __init__(self, obj):

        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)

        self.Tags = ("mirror", "drill")
        self.ViewProvider = ViewProvider

    def execute(self, obj):

        mesh = _orient_stl("POLARIS-K05S2-Solidworks.stl", (0, -pi/2, 0), (-4.5-obj.MirrorThickness.Value, -0.3, -0.25), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        
        self.DrillPart = _mirror_drill((-8.0-obj.MirrorThickness.Value, 0, -INCH/2))
        self.DrillPart.Placement=obj.Placement
        layout.redraw()


class mirror_mount_c05g:

    def __init__(self, obj):

        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)

        self.Tags = ("mirror", "drill")
        self.ViewProvider = ViewProvider

    def execute(self, obj):

        mesh = _orient_stl("POLARIS-C05G-Solidworks.stl", (pi/2, 0, pi/2), (-19-obj.MirrorThickness.Value, -4.3, -15.2), 1000)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        self.DrillPart = _mirror_drill((-(6.4+obj.MirrorThickness.Value), 0, -INCH/2))
        self.DrillPart.Placement=obj.Placement
        layout.redraw()


class baseplate_mount:

    def __init__(self, obj):

        obj.Proxy = self
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)

        self.Tags = ("drill")
        self.ViewProvider = ViewProvider


    def execute(self, obj):
        
        mesh = Mesh.createCylinder((CLR_DIA_14_20-1)/2, INCH, True, 1, 50)
        temp = Mesh.createCylinder((WASHER_DIA_14_20-2)/2, 10, True, 1, 50)
        mesh.addMesh(temp)
        mesh.rotate(0, pi/2, 0)
        mesh.translate(0, 0, -INCH/2)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        part = Part.makeCylinder(CLR_DIA_14_20/2, INCH, App.Vector(0, 0, -INCH/2), App.Vector(0, 0, -1))
        tempPart = Part.makeCylinder(WASHER_DIA_14_20/2, 10, App.Vector(0, 0, -INCH/2), App.Vector(0, 0, -1))
        part = part.fuse(tempPart)
        self.DrillPart = part
        self.DrillPart.Placement=obj.Placement
        layout.redraw()

class isomet_1205c_on_km100pm:

    ##isomet_1205c parameters
    aom_dz = 16;    # height of AOM optical axis from base of AOM
    aom_dx = 22.34; # AOM depth (along optical axis) in mm
    aom_dy = 50.76; # AOM width (perpendicular to optical axis) in mm

    def __init__(self, obj):

        obj.Proxy = self
        obj.addProperty('App::PropertyLength', 'MirrorThickness').MirrorThickness = default_mirror_thickness
        obj.ViewObject.ShapeColor=(0.6, 0.6, 0.65)

        self.Tags = ("mirror", "drill")
        self.ViewProvider = ViewProvider

    def execute(self, obj):

        mesh = _orient_stl("isomet_1205c_on_km100pm.stl", (0, 0, 0), (-6.4-obj.MirrorThickness.Value, 0, 0))

        # temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        # temp.rotate(0, 0, pi)
        # mesh.addMesh(temp)

        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


        mesh_drill = _orient_stl("isomet_1205c_on_km100pm_drill.stl", (0, 0, 0), (-6.4-obj.MirrorThickness.Value, 0, 0))
        shape = Part.Shape()
        shape.makeShapeFromMesh(mesh_drill.Topology, 0.5) # the second arg is the tolerance for sewing
        solid = Part.makeSolid(shape)

        self.DrillPart = solid
        self.DrillPart.Placement=obj.Placement
        layout.redraw()



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
        element = feature.Object.Proxy
        if hasattr(element, "Adapter"):
            App.ActiveDocument.removeObject(element.Adapter.Name)
            element = element.Adapter.Proxy
        if "drill" in element.Tags:
            layout.redraw()
        if "Adapter" in feature.Object.Name:
            return False
        return True

    def onChanged(self, vp, prop):
        App.Console.PrintMessage("Change property: " + str(prop) + "\n")

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