import FreeCAD as App
import Part
from math import *

INCH = 25.4

def is_mult(x, factor, tol=1e-5):
    return isclose((abs(x)+tol/2)%factor, 0, abs_tol=tol)

# calculate intersection between two lines given the origin and angle of both
def find_interaction(x1, y1, a1, ref_obj, len=0):

    # check if object is an optical component
    if not (hasattr(ref_obj.Proxy, 'in_limit') and hasattr(ref_obj.Proxy, 'in_width')):
        return
    
    # get object placement
    x2, y2, _ = ref_obj.Placement.Base
    a_comp = ref_obj.Placement.Rotation.Angle
    a_comp *= ref_obj.Placement.Rotation.Axis[2]
    a1 %= 2*pi

    # limits on incomming beam
    in_limit = ref_obj.Proxy.in_limit
    in_width = ref_obj.Proxy.in_width

    a_norm = a_comp
    output = [None, None, [None, None], False]

    # transmitted beam
    if hasattr(ref_obj.Proxy, 'tran'):
        a_norm = (a_comp+pi)%(2*pi)
        output[2][0] = a1
    # diffracted beam
    if hasattr(ref_obj.Proxy, 'diff_angle'):
        a_norm = (a_comp+pi)%(2*pi)
        output[2][1] = a1+ref_obj.Proxy.diff_angle
    # reflected beam
    if hasattr(ref_obj.Proxy, 'ref_angle'):
        a_norm = (a_comp+ref_obj.Proxy.ref_angle)%(2*pi)
        output[2][1] = 2*a_norm-a1-pi

    a2 = a_norm+pi/2 # tangent angle to reflection surface
    # relative angle between the beam and component input normal
    a_in = abs(a1-a_norm)%(2*pi)
    if a_in > pi:
        a_in = 2*pi-a_in
    # relative angle between beam angle and direction of the component from the beam
    a_rel = abs(a1-atan2(y2-y1, x2-x1))%(2*pi)
    if a_rel > pi:
        a_rel = 2*pi-a_rel

    # check if placement is suitable for reflection
    if a_in < in_limit or a_rel > pi/2:
        return
    
    if hasattr(ref_obj.Proxy, 'diff_dir') and output[2][1] != None:
        if a_in > pi/2:
            output[2][1] = a1+ref_obj.Proxy.diff_angle*ref_obj.Proxy.diff_dir[0]
        else:
            output[2][1] = a1+ref_obj.Proxy.diff_angle*ref_obj.Proxy.diff_dir[1]

    # check for edge cases
    a1_vert = is_mult(a1-pi/2, pi)
    a2_vert = is_mult(a2-pi/2, pi)
    a12_hor = is_mult(a1, pi) and is_mult(a2, pi) or is_mult(a1-a2, pi)

    # calculate position and angle of reflection
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

    # check if beam is from current object
    if isclose(x1, x, abs_tol=1e-5) and isclose(y1, y, abs_tol=1e-5):
        return

    # distance from optical center to intersection point
    ref_d = sqrt((x-x2)**2+(y-y2)**2)
    if ref_d > in_width/2:
        if ref_d < INCH/2:
            output[3] = True
        else:
            return
        
    # distance from beam start to intersection point
    beam_d = sqrt((x2-x1)**2+(y2-y1)**2)
    if len != 0:
        if beam_d > len:
            return
        if isclose(beam_d, len, rel_tol=1e-3):
            return

    # transmitted beam
    if hasattr(ref_obj.Proxy, 'foc_len'):
        a_rel = abs(a2-atan2(y-y2, x-x2))%(2*pi)
        offset = pi/2-atan2(ref_obj.Proxy.foc_len, ref_d)
        if is_mult(a_rel, 2*pi):
            offset *= -1
        if a_in > pi/2:
            offset *= -1
        output[2][0] += offset
        
    output[0], output[1] = x, y
    return output

# beam path freecad object
class beam_path:

    def __init__(self, obj):

        obj.Proxy = self
        self.components = [[]]

    def __getstate__(self):
        return None

    def execute(self, obj):
        self.x, self.y, _ = obj.Placement.Base
        self.a = obj.Placement.Rotation.Angle
        self.a *= obj.Placement.Rotation.Axis[2]
        self.beams = []
        self.comp_track = []
        self.calculate_beam_path(obj, self.x, self.y, self.a)
        shapes = []
        for i in self.beams:
            len = i[3]
            if len == 0:
                len = 50
            temp = Part.makeCylinder(0.5, len, App.Vector(i[0], i[1], 0), App.Vector(cos(i[2]), sin(i[2]), 0))
            shapes.append(temp)
        comp = Part.Compound(shapes)
        comp.translate(App.Vector(-self.x, -self.y, 0))
        comp.rotate(App.Vector(0, 0, 0),App.Vector(0, 0, 1), degrees(-self.a))
        comp = comp.fuse(comp)
        obj.Shape = comp

    # compute full beam path given start point and angle
    def calculate_beam_path(self, selfobj, x1, y1, a1, beam_index=1):
        if beam_index > 200:
            return
        count = 0 # number of reflections per beam
        comp_index = 0 # index of current inline component
        pre_count = 0 # current number of previous interactions for inline components
        pre_d = 0 # current previous interaction distance for inline components
        block = False # flag for a component obstructing a beam path
        while True:
            beam_comps = []
            for obj in selfobj.PathObjects:
                if obj.BeamIndex == beam_index:
                    beam_comps.append(obj)
            min_len = 0
            for obj in App.ActiveDocument.Objects:

                # skip if unplaced inline component
                comp_check = True
                for comp_obj in selfobj.PathObjects:
                    if obj == comp_obj and not obj in self.comp_track:
                        comp_check = False

                ref = find_interaction(x1, y1, a1, obj) # check for reflection
                if ref != None and comp_check:
                    x2, y2, a2_arr, comp_block = ref

                    # check to find closest component
                    comp_d = sqrt((x2-x1)**2+(y2-y1)**2)
                    if comp_d < min_len or min_len == 0:
                        min_len = comp_d
                        ref_obj = obj
                        xf, yf, af_arr = x2, y2, a2_arr
                        block = comp_block

            if len(beam_comps) > comp_index:
                inline_ref=False
                comp_obj = beam_comps[comp_index]

                # handle different constraint methods
                if hasattr(comp_obj, "Distance"):
                    comp_d = comp_obj.Distance.Value
                if hasattr(comp_obj, "xPos"):
                    comp_d = (comp_obj.xPos.Value-x1)/cos(a1)
                if hasattr(comp_obj, "yPos"):
                    comp_d = (comp_obj.yPos.Value-y1)/sin(a1)

                #comp_d -= pre_d

                # check for closest component or satisfied pre_count
                if (comp_d < min_len or min_len == 0) and pre_count >= comp_obj.PreRefs:
                    if pre_count > comp_obj.PreRefs:
                        comp_d -= pre_d # account for previous distance
                    # inline placement
                    x2 = x1+comp_d*cos(a1)
                    y2 = y1+comp_d*sin(a1)
                    comp_obj.Placement.Base = App.Vector(x2, y2, 0)
                    # check for valid reflection
                    ref = find_interaction(x1, y1, a1, comp_obj)
                    if ref != None:
                        ref_obj = comp_obj
                        xf, yf, af_arr, _ = ref
                        self.comp_track.append(comp_obj)
                        min_len = comp_d
                        # increment index and reset counters
                        comp_index += 1
                        pre_count = 0
                        pre_d = 0
                        inline_ref = True
                        block = False
                        # place any objects defined relative to the inline object
                        if hasattr(comp_obj, "RelativeObjects"):
                            for obj in comp_obj.RelativeObjects:
                                x, y = comp_obj.Placement.Base[0]+obj.RelativeX.Value, comp_obj.Placement.Base[1]+obj.RelativeY.Value
                                obj.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(obj.Angle.Value, 0, 0), App.Vector(x, y, 0))
                                obj.Placement.Base = App.Vector(x+obj.RelativeX.Value, y+obj.RelativeY.Value, 0)
                    else:
                        comp_obj.Placement.Base = App.Vector(0, 0, 0)
                # previous interaction info
                if not inline_ref:
                    pre_count += 1
                    if pre_count > comp_obj.PreRefs:
                        pre_d += min_len

            self.beams.append([x1, y1, a1, min_len, beam_index])

            # continue beam if reflection was found
            if min_len != 0 and not block:
                if "inline_ref" in locals() and inline_ref and ref_obj == self.comp_track[-1]:
                    for i in self.beams[:]:
                        if i[4] != beam_index:
                            ref = find_interaction(i[0],i[1],i[2],ref_obj,i[3])
                            if ref != None:
                                for beam in self.beams[::-1]:
                                    if beam[4]>>int(abs(log2(beam[4]/i[4]))) == i[4]:
                                        last = beam[:]
                                        self.beams.remove(beam)
                                for comp in self.comp_track[:]:
                                   if comp.BeamIndex>>int(abs(log2(comp.BeamIndex/i[4]))) == i[4]:
                                        comp.Placement.Base = App.Vector(0, 0, 0)
                                        self.comp_track.remove(comp)
                                self.calculate_beam_path(selfobj, last[0], last[1], last[2], last[4])
                                break
                if af_arr[0] != None and af_arr[1] != None:
                    self.calculate_beam_path(selfobj, xf, yf, af_arr[0], (beam_index<<1))
                    beam_index = (beam_index<<1)+1
                    beam_comps = []
                    for obj in selfobj.PathObjects:
                        if obj.BeamIndex == beam_index:
                            beam_comps.append(obj)
                    comp_index = 0
                if af_arr[1] != None:
                    x1, y1, a1 = xf, yf, af_arr[1]
                    count += 1
                elif af_arr[0] != None:
                    x1, y1, a1 = xf, yf, af_arr[0]
                    count += 1
                else:
                    return
            else:
                return
                    
class ViewProvider:

    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        return
    
    def getDefaultDisplayMode(self):
        return "Shaded"

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
        "+ c white",
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