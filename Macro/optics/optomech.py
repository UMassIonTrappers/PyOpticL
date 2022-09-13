import FreeCAD as App
import Mesh
import Part
from math import *
from optics import layout

from pathlib import Path

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

washer_dia_14_20 = 9/16 * INCH; #12 washer


drill_depth = 26
default_mirror_thickness = 6

# Used to tranform an STL such that it's placement matches the optical center
### Should remove mountOff and integrate directly into each translation
def _orient_stl(stl, rotate, translate, scale=1, mountOff=(0,0,0)):
    mesh = Mesh.read(STL_PATH+stl)
    mat = App.Matrix()
    mat.scale(App.Vector(scale, scale, scale))
    mesh.transform(mat)
    mesh.rotate(*rotate)
    mesh.translate(*translate)
    mesh.translate(*mountOff)
    return mesh

# Drill geometry for most mirror mounts
def _mirror_drill(mountOff):
    part = Part.makeCylinder(TAP_DIA_8_32/2, drill_depth, App.Vector(*mountOff), App.Vector(0, 0, -1))
    tempPart = Part.makeCylinder(TAP_DIA_8_32/2, drill_depth, App.Vector(*mountOff), App.Vector(0, 0, -1))
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
        temp = Part.makeCylinder(TAP_DIA_8_32/2, drill_depth, App.Vector(0, 0, 0), App.Vector(0, 0, -1))
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

        part = Part.makeCylinder(TAP_DIA_8_32/2, drill_depth, App.Vector(0, 0, 0), App.Vector(0, 0, -1))
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
        
        mountOff = (0, 0, -20.7)
        mesh = _orient_stl("HCA3-Solidworks.stl", (-pi/2, pi, -pi/2), (-6.35, -38.1/2, -6.2), 1, mountOff)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        temp = Part.makeCylinder(TAP_DIA_8_32/2, drill_depth, App.Vector(*mountOff), App.Vector(1, 0, 0))
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


    def execute(self, obj):
        
        mesh = Mesh.createBox(obj.CubeSize.Value, obj.CubeSize.Value, obj.CubeSize.Value)
        temp = Mesh.createBox(10-1, sqrt(200)-1, 0.01)
        temp.rotate(0, pi/2, -pi/4)
        mesh = mesh.unite(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        skate_mount(self.Adapter, obj.CubeSize.Value)
        self.Adapter.Placement = mesh.Placement
        ViewProvider(self.Adapter.ViewObject)

class rotation_stage_rsp05:

    def __init__(self, obj):

        obj.Proxy = self
        obj.ViewObject.ShapeColor=(0.2, 0.2, 0.2)

        self.Tags = ("rts")
        self.ViewProvider = ViewProvider
        self.Adapter = App.ActiveDocument.addObject('Part::FeaturePython', obj.Name+"_Adapter")

    def execute(self, obj):
        
        mountOff = (0, 0, -14)
        mesh = _orient_stl("RSP05-Solidworks.stl", (pi/2, 0, pi/2), (0.6, 0, 14), 1000, mountOff)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        surface_adapter(self.Adapter, mountOff, 25)
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

        mountOff = (-(8.0+obj.MirrorThickness.Value), 0, -INCH/2)
        mesh = _orient_stl("POLARIS-K05S2-Solidworks.stl", (0, -pi/2, 0), (3.5, -0.3, 12.45), 1000, mountOff)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh
        
        self.DrillPart = _mirror_drill(mountOff)
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

        mountOff = (-(6.4+obj.MirrorThickness.Value), 0, -INCH/2)
        mesh = _orient_stl("POLARIS-C05G-Solidworks.stl", (pi/2, 0, pi/2), (-12.6, -4.3, -2.5), 1000, mountOff)
        temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        temp.rotate(0, 0, pi)
        mesh.addMesh(temp)
        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh

        self.DrillPart = _mirror_drill(mountOff)
        self.DrillPart.Placement=obj.Placement
        layout.redraw()


class baseplate_mount:

    def __init__(self, obj):

        obj.Proxy = self
        obj.ViewObject.ShapeColor=(0.5, 0.5, 0.55)

        self.Tags = ("screw", "drill")
        self.ViewProvider = ViewProvider


    def execute(self, obj):
        
        mesh = Mesh.createCylinder(CLR_DIA_14_20/2, drill_depth, True, 1, 50)
        mesh.Placement = obj.Mesh.Placement
        mesh.rotate(0, pi/2, 0)
        obj.Mesh = mesh

        mountOff = (0, 0, -INCH/2)
        part = Part.makeCylinder(CLR_DIA_14_20/2, drill_depth, App.Vector(*mountOff), App.Vector(0, 0, -1))
        # tempPart = Part.makeCylinder(CLR_DIA_14_20/2, drill_depth, App.Vector(*mountOff), App.Vector(0, 0, -1))
        # part = part.fuse(tempPart)

        # https://freecad-python-stubs.readthedocs.io/en/latest/autoapi/Part/index.html#Part.TopoShape.rotate
        part.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)



        # tempPart = Part.makeCylinder(1, 3, App.Vector(*mountOff), App.Vector(0, 0, -1))
        # tempPart.translate(App.Vector(0, -5, 0))
        # part = part.fuse(tempPart)
        # tempPart.translate(App.Vector(0, 10, 0))
        # part = part.fuse(tempPart)

        self.DrillPart = part
        self.DrillPart.Placement=obj.Placement

        layout.redraw()

        # ## Holes for mounting baseplate to optical table
        # module screw_with_head_clear(xpos, ypos, head=true, threaded=false){
        #     color("red")
        #     mirror([0,0,1])
        #     translate([xpos, ypos , post_dz-0.01]){
        #         cylinder(d=(threaded ? screw_tap_dia_14_20 : screw_clear_dia_14_20), h = 100);
        #         if(head){
        #             cylinder(d=screw_washer_dia_14_20, h = 10);
        #         }
        #     }
        # }




''' AOM Mount '''

'''



module mod_mount_km100pm(dz=0,aom_rot = 0,hole_dz = 22.9-18.5, show=1, zoff=0, drill=true, use_nut=false, brimrose = false, head_depth_offset=15,
             upside_down=false, use_slots=true, show_km100pm=true){
    //
    // km100pm with AOM mount
    //
    // hole_dz = how far from bottom of AOM (closest side to baseplate) is from the AOM aperature, default specs for brimrose TEF6030461
    // modified km100pm mount, used for brimrose AOM
    // 12.7-(32.92-16 + 6.98) = 11.2 (depth of recess)
    // 30-1.8 =  height of bottom of KM100PM horizonal arm from optical axis
    //
    // use_slots: bool, true = use slots on brimrose AOM mount, allows sliding of AOM perpendicular to optical axis
    
    holedia = screw_tap_dia_8_32;
    stage_dz = 32.92-16;  
    stage_yoff = 17.5+13 ;// AOM 
    yoff =6.35 +screw_tap_dia_4_40/2; //Brimrose AOM dy offset to put optical axis at aperature
    xtheta = (upside_down ? 180 : 0);
    ud_zoff = (upside_down ? 30 : 0);
    
    if (show){
     translate([0, 0, -zoff]){     
          if (show_km100pm){
           translate([0, 0, ud_zoff])
            rotate([xtheta, 0, 0])
            rotate([0, 0, -90])
            translate([-51.8+25.8, 0, -stage_dz-1])
            translate([0, 14.2, 0])
            rotate([90, 0, 0]){
            import("thorlabs/KM100PM-Solidworks-modified.stl");
           }
          }
          //custom mount
          if(brimrose){
           if (upside_down){
            translate([0,yoff-7.5,zoff-11.2-12.7]){
                 post_upside_down_brim_km100pm();
                 //cylinder(d = screw_tap_dia_8_32, h= 100);
            } //Post for mounting KM100PM in the upside-down configuration
            
           }
           else{
            translate([51.8-25.8-10,0,-stage_dz])
                 mount_brim_km100pm(stage_dz=stage_dz+6.98 + 4+22.9-hole_dz, aom_rot=aom_rot, hole_dz = hole_dz, zoff=2.5, use_slots=use_slots);
           }
          }
          else{
           translate([51.8-25.8-8,0,-stage_dz])
            // mount_for_km100pm(stage_dz=stage_dz, hole_dz = hole_dz, use_slots=1);
            mount_for_km100pm(stage_dz=stage_dz, use_slots=1);
          }
     }
    }
    if (dz>0){
     union(){
          post(dz, stage_dz + zoff, drill=drill, use_nut=use_nut, holedia=holedia, head_depth_offset=head_depth_offset,
           post_dx=8+24+2, post_xoff = 8+2, post_dy = 53.5+aom_rot*3);
          //extra slot for knob
          post(dz, 26, drill=drill, use_nut=use_nut, holedia=0,
           post_dx=40, post_xoff = -15.5, post_dy = 13.5+2, post_yoff = -20+1);
     }
    }
}



module isomet_on_mount_km100pm(dz=0, show=1, optic_center=true, drill=true, use_nut=false, name="", name_xoff=0){
    
     poff = 51.8-25.7-12+15.17;
     yoff = -6.35 - screw_tap_dia_4_40/2;
     xoff = (optic_center ? poff : 0);
     translate([-xoff, yoff, 0]){
      text_label(name, 0 + name_xoff, 30, dz, rot=[0,0,0], show=show||drill);
      mod_mount_km100pm(dz, show=show, zoff=6.98, drill=drill, use_nut=use_nut);
      if (show){
            translate([poff,-yoff, 0])rotate([0,0,90])  // translate aom on platform
             isomet_1205c();
      }
     }
}



'''


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

        mountOff = (-(6.4+obj.MirrorThickness.Value), 0, -INCH/2)
        mesh = _orient_stl("isomet_1205c_on_km100pm.stl", (0, 0, 0), (0, 0, INCH/2), 1, mountOff)

        # temp = Mesh.createCylinder(INCH/4, obj.MirrorThickness.Value, True, 1, 50)
        # temp.rotate(0, 0, pi)
        # mesh.addMesh(temp)

        mesh.Placement = obj.Mesh.Placement
        obj.Mesh = mesh


        mesh_drill = _orient_stl("isomet_1205c_on_km100pm_drill.stl", (0, 0, 0), (0, 0, INCH/2), 1, mountOff)
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