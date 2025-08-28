import FreeCAD as App
import Part
from math import *
import numpy as np

inch = 25.4

def is_mult(x, factor, tol=1e-5):
    return isclose((abs(x)+tol/2)%factor, 0, abs_tol=tol)

# calculate intersection between a beam and an optical component
def check_interaction(x1, y1, a1, ref_obj):

    # check if object is an optical component
    if not hasattr(ref_obj, "Proxy") or not (hasattr(ref_obj.Proxy, 'max_angle') and hasattr(ref_obj.Proxy, 'max_width')):
        return
    
    # get object placement
    x2, y2, _ = ref_obj.BasePlacement.Base
    a_norm = ref_obj.BasePlacement.Rotation.Angle
    a_norm *= ref_obj.BasePlacement.Rotation.Axis[2]

    # check if component is on the correct side of the beam
    a_rel = abs(a1-atan2(y2-y1, x2-x1))%(2*pi)
    if a_rel > pi:
        a_rel = 2*pi-a_rel
    if a_rel > pi/2:
        return

    # limits on incoming beam
    max_angle = radians(ref_obj.Proxy.max_angle)
    max_width = ref_obj.Proxy.max_width

    # two possible output beam angles
    angle1 = None
    angle2 = None

    # transmitted beam
    if hasattr(ref_obj.Proxy, 'transmission'):
        a_norm = (a_norm+pi)%(2*pi)
        angle1 = a1
    # diffracted beam
    if hasattr(ref_obj.Proxy, 'diffraction_angle'):
        a_norm = (a_norm+pi)%(2*pi)
        angle2 = a1+radians(ref_obj.Proxy.diffraction_angle)
    # reflected beam
    if hasattr(ref_obj.Proxy, 'reflection_angle'):
        a_norm = (a_norm+radians(ref_obj.Proxy.reflection_angle))%(2*pi)
        angle2 = 2*a_norm-a1-pi

    a2 = a_norm+pi/2 # angle of interaction surface

    # relative angle between the beam and component input normal
    a_in = abs(a1-a_norm+pi)%(2*pi)
    if a_in > pi:
        a_in = 2*pi-a_in
    
    if hasattr(ref_obj.Proxy, 'diffraction_dir'):
        if a_in < pi/2:
            angle2 = a1+radians(ref_obj.Proxy.diffraction_angle)*ref_obj.Proxy.diffraction_dir[0]
        else:
            angle2 = a1+radians(ref_obj.Proxy.diffraction_angle)*ref_obj.Proxy.diffraction_dir[1]

    # check for edge cases
    a1_vert = is_mult(a1-pi/2, pi)
    a2_vert = is_mult(a2-pi/2, pi)
    a12_hor = is_mult(a1, pi) and is_mult(a2, pi) or is_mult(a1-a2, pi)

    # calculate intersection of the beam and the surface
    if a1_vert:
        x = x1
    elif a2_vert or a12_hor:
        x = x2
    else:
        x = (y2-x2*tan(a2)-y1+x1*tan(a1))/(tan(a1)-tan(a2))
    if not a1_vert:
        y = x*tan(a1)+y1-x1*tan(a1)
    elif not a2_vert:
        y = x*tan(a2)+y2-x2*tan(a2)
    else:
        y = y2

    # total distance to interaction
    ref_d = sqrt((x-x2)**2+(y-y2)**2)

    # refracted beam
    if hasattr(ref_obj.Proxy, 'focal_length'):
        a_rel = abs(a2-atan2(y-y2, x-x2))%(2*pi)
        offset = pi/2-atan2(ref_obj.Proxy.focal_length, ref_d)
        if is_mult(a_rel, 2*pi):
            offset *= -1
        if a_in < pi/2:
            offset *= -1
        angle1 += offset

    # check if beam is from current object
    if isclose(x1, x, abs_tol=1e-5) and isclose(y1, y, abs_tol=1e-5):
        return

    # check against max width and blocking width
    block = False
    if ref_d > max_width/2:
        if hasattr(ref_obj.Proxy, "block_width"):
            if ref_d < ref_obj.Proxy.block_width/2:
                block = True
            else:
                return
        else:
            return
        
    # check against max angle
    if hasattr(ref_obj.Proxy, 'transmission'):
        if a_in > max_angle and pi-a_in > max_angle:
            block = True
    else:
        if a_in > max_angle:
            block = True
        
    return ref_obj, x, y, [angle1, angle2], block

# beam path freecad object
class beam_path:

    def __init__(self, obj, drill=True, width=0.5, drill_width=1.5):

        obj.Proxy = self
        obj.addProperty('App::PropertyBool', 'Drill').Drill = drill
        obj.addProperty('Part::PropertyPartShape', 'DrillPart')
        obj.addProperty('App::PropertyLength', 'Width').Width = width
        obj.addProperty('App::PropertyLength', 'DrillWidth').DrillWidth = drill_width
        self.components = [[]]

    def __getstate__(self):
        return None

    def execute(self, obj):
        # get placement
        self.x, self.y, _ = obj.BasePlacement.Base
        self.a = obj.BasePlacement.Rotation.Angle
        self.a *= obj.BasePlacement.Rotation.Axis[2]

        # calculate beam
        self.beams = []
        self.comp_track = []
        self.calculate_beam_path(obj, self.x, self.y, self.a)

        # draw beam
        shapes = []
        for i in self.beams:
            length = i[3]
            if length == 0:
                length = 50
            temp = Part.makeCylinder(obj.Width.Value, length, App.Vector(i[0], i[1], 0), App.Vector(cos(i[2]), sin(i[2]), 0))
            shapes.append(temp)
        comp = Part.Compound(shapes)
        self.comp = comp
        comp.translate(App.Vector(-self.x, -self.y, 0))
        comp.rotate(App.Vector(0, 0, 0),App.Vector(0, 0, 1), degrees(-self.a))
        comp = comp.fuse(comp)
        obj.Shape = comp

        part = Part.makeSphere(0)
        for i in self.beams:
            length = i[3]
            if length == 0:
                length = 50
            temp = Part.makeCylinder(obj.DrillWidth.Value, length, App.Vector(i[0], i[1], 0), App.Vector(cos(i[2]), sin(i[2]), 0))
            part = part.fuse(temp)

        part.translate(App.Vector(-self.x, -self.y, 0))
        part.rotate(App.Vector(0, 0, 0),App.Vector(0, 0, 1), degrees(-self.a))
        part = part.fuse(part)
        part.Placement = obj.Placement
        obj.DrillPart = part

    # compute full beam path given start point and angle
    def calculate_beam_path(self, selfobj, x1, y1, a1, beam_index=1):
        if beam_index > 200:
            return
        
        count = 0 # number of interactions per beam
        comp_index = 0 # index of current inline component
        pre_count = 0 # current number interactions since last inline interaction
        pre_d = 0 # previous interaction distance for inline components
        block = False # flag for a component obstructing a beam path

        while True:
            # get all inline components
            inline_comps = []
            for obj in selfobj.PathObjects:
                if obj.BeamIndex == beam_index:
                    inline_comps.append(obj)
            
            # get next inline component
            inline_obj = None
            if len(inline_comps) > comp_index:
                inline_obj = inline_comps[comp_index]
                if pre_count >= inline_obj.PreRefs:
                    self.comp_track.append(inline_obj)

                    # handle different constraint methods
                    if hasattr(inline_obj, "Distance"):
                        comp_d = inline_obj.Distance.Value
                    if hasattr(inline_obj, "xPos"):
                        x_pos = inline_obj.xPos.Value
                        comp_d = (x_pos-x1)/cos(a1)
                    if hasattr(inline_obj, "yPos"):
                        y_pos = inline_obj.yPos.Value
                        comp_d = (y_pos-y1)/sin(a1)

                    if pre_count > inline_obj.PreRefs:
                        comp_d -= pre_d # account for previous distance

                    # inline placement
                    inline_obj.BasePlacement.Base = App.Vector(x1+comp_d*cos(a1), y1+comp_d*sin(a1), 0)

            # get all valid objects
            check_objs = []
            for obj in App.ActiveDocument.Objects:
                if obj in selfobj.PathObjects and not obj in self.comp_track:
                    continue
                if hasattr(obj, "ParentObject"):
                    if obj.ParentObject in selfobj.PathObjects and not obj.ParentObject in self.comp_track:
                        continue
                if hasattr(obj, "Baseplate"):
                    if obj.Baseplate != selfobj.Baseplate:
                        continue
                check_objs.append(obj)
                
            # find all interactions
            refs = []
            comp_d =[]
            for obj in check_objs:
                ref = check_interaction(x1, y1, a1, obj)
                if ref != None:
                    refs.append(ref)
                    comp_d.append(sqrt((ref[1]-x1)**2+(ref[2]-y1)**2))
            
            # pick nearest valid interaction
            inline_ref = False
            if len(refs) > 0:
                index = np.argmin(comp_d)
                final_ref = refs[index]
                min_len = comp_d[index]

                if hasattr(final_ref[0], "ParentObject"):
                    check_comp = final_ref[0].ParentObject
                else:
                    check_comp = final_ref[0]

                if check_comp == inline_obj:
                    inline_ref = True
                    comp_index += 1
                    pre_count = 0
                    pre_d = 0
                elif len(inline_comps) > comp_index:
                    if self.comp_track[-1] == inline_obj:
                        self.comp_track.pop()
                    pre_count += 1
                    if pre_count > inline_obj.PreRefs:
                        pre_d += min_len
                
                ref_obj, xf, yf, af_arr, block = final_ref
                # restrict beam to baseplate
                if selfobj.Baseplate.dx != 0 and selfobj.Baseplate.dy != 0:
                    intersect = []
                    x_max = selfobj.Baseplate.dx.Value
                    y_max = selfobj.Baseplate.dy.Value
                    if x_max < xf:
                        intersect.append((x_max-x1)/cos(a1))
                    if y_max < yf:
                        intersect.append((y_max-y1)/sin(a1))
                    if xf < 0:
                        intersect.append((0-x1)/cos(a1))
                    if yf < 0:
                        intersect.append((0-y1)/sin(a1))
                    if len(intersect) > 0 and min_len > min(intersect):
                        min_len = min(intersect)
                        block = True
                self.beams.append([x1, y1, a1, min_len, beam_index])
            else:
                # restrict beam to baseplate
                if selfobj.Baseplate.dx != 0 and selfobj.Baseplate.dy != 0:
                    intersect = []
                    xf, yf = x1+500*cos(a1), y1+500*sin(a1) # TODO find a better way than this
                    x_max = selfobj.Baseplate.dx.Value
                    y_max = selfobj.Baseplate.dy.Value
                    if x_max < xf:
                        intersect.append((x_max-x1)/cos(a1))
                    if y_max < yf:
                        intersect.append((y_max-y1)/sin(a1))
                    if xf < 0:
                        intersect.append(-(x1-0)/cos(a1))
                    if yf < 0:
                        intersect.append(-(y1-0)/sin(a1))
                    if len(intersect) > 0: # sometimes intersect is empty ... skip to avoid ValueError exception
                        self.beams.append([x1, y1, a1, min(intersect), beam_index])
                return
            
            if block:
                return

            # handle recursion issues caused by conflicting beam paths
            if inline_ref:
                for i in self.beams[:]:
                    if i[4] != beam_index:
                        ref = check_interaction(i[0],i[1],i[2],ref_obj)
                        if ref != None:
                            beam_d = sqrt((ref[1]-i[0])**2+(ref[2]-i[1])**2)
                            if beam_d > i[3] or isclose(beam_d, i[3], rel_tol=1e-3):
                                continue
                            for beam in self.beams[::-1]:
                                if beam[4]>>int(abs(log2(beam[4]/i[4]))) == i[4]:
                                    last = beam[:]
                                    self.beams.remove(beam)
                            for comp in self.comp_track[:]:
                                if comp.BeamIndex>>int(abs(log2(comp.BeamIndex/i[4]))) == i[4]:
                                    comp.BasePlacement.Base = App.Vector(0, 0, 0)
                                    self.comp_track.remove(comp)
                            self.calculate_beam_path(selfobj, last[0], last[1], last[2], last[4])
                            break
            
            # compute next beam and handle recursion for beam splits
            if af_arr[0] != None and af_arr[1] != None:
                self.calculate_beam_path(selfobj, xf, yf, af_arr[0], (beam_index<<1))
                beam_index = (beam_index<<1)+1
                inline_comps = []
                for obj in selfobj.PathObjects:
                    if obj.BeamIndex == beam_index:
                        inline_comps.append(obj)
                comp_index = 0
            if af_arr[1] != None:
                x1, y1, a1 = xf, yf, af_arr[1]
                count += 1
            elif af_arr[0] != None:
                x1, y1, a1 = xf, yf, af_arr[0]
                count += 1
            else:
                return
                    
class ViewProvider:

    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        return
    
    def getDefaultDisplayMode(self):
        return "Shaded"
    
    def updateData(self, obj, prop):
        if str(prop) == "BasePlacement":
            obj.Placement.Base = obj.BasePlacement.Base + obj.Baseplate.Placement.Base
            obj.Placement = App.Placement(obj.Placement.Base, obj.Baseplate.Placement.Rotation, -obj.BasePlacement.Base)
            obj.Placement.Rotation = obj.Placement.Rotation.multiply(obj.BasePlacement.Rotation)
        return

    def onDelete(self, feature, subelements):
        return True

    def getIcon(self):
        return """
        /* XPM */
        static char *_0ddddfe6a2d42f3d616a62ec3bb0f7c8Jp52mHVQRFtBmFY[] = {
        /* columns rows colors chars-per-pixel */
        "16 16 6 1 ",
        "  c #ED1C24",
        ". c #ED5C5E",
        "X c #ED9092",
        "o c #EDBDBD",
        "O c #EDDFDF",
        "+ c None",
        /* pixels */
        "+++++++++..XooOO",
        "++++++..+..XXooO",
        "++++++++++. XXoo",
        "+++++++.++  .XXo",
        "++++++.++  .  XX",
        "++++++++  .  ..X",
        "+++++++  .  ++..",
        "++++++  .  +++++",
        "+++++  .  ++.+.+",
        "++++  .  ++.++.+",
        "+++  .  ++++++++",
        "++  .  +++++++++",
        "+  .  ++++++++++",
        "  .  +++++++++++",
        " .  ++++++++++++",
        ".  +++++++++++++"
        };
        """

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None