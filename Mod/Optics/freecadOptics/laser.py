import FreeCAD as App
import Part
from math import *

INCH = 25.4

def is_mult(x, factor, tol=1e-5):
    return isclose((abs(x)+tol/2)%factor, 0, abs_tol=tol)

# calculate intersection between two lines given the origin and angle of both
def find_interaction(x1, y1, a1, ref_obj):

    # check if object is an optical component
    if not (hasattr(ref_obj.Proxy, 'in_limit') and hasattr(ref_obj.Proxy, 'in_width')):
        return
    
    # get object placement
    (x2, y2, _) = ref_obj.Placement.Base
    a_comp = ref_obj.Placement.Rotation.Angle
    a_comp *= ref_obj.Placement.Rotation.Axis[2]
    a1 %= 2*pi

    # check if beam is from current object
    if isclose(x1, x2, abs_tol=1e-5) and isclose(y1, y2, abs_tol=1e-5):
        return

    # limits on incomming beam
    in_limit = ref_obj.Proxy.in_limit
    in_width = ref_obj.Proxy.in_width

    a_norm = a_comp
    output = [None, None, [None, None]]

    # transmitted beam
    if hasattr(ref_obj.Proxy, 'tran_angle'):
        a_norm = (a_comp+pi)%(2*pi)
        output[2][1] = a1+ref_obj.Proxy.tran_angle

    # reflected beam
    if hasattr(ref_obj.Proxy, 'ref_angle'):
        a_norm = (a_comp+ref_obj.Proxy.ref_angle)%(2*pi)
        output[2][0] = 2*a_norm-a1-pi

    a2 = a_norm+pi/2

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
    
    if sqrt((x-x2)**2+(y-y2)**2) > in_width/2:
        return

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
        (self.x, self.y, _) = obj.Placement.Base
        self.a = obj.Placement.Rotation.Angle
        self.a *= obj.Placement.Rotation.Axis[2]
        self.part = Part.makeSphere(0)
        self.comp_track = []
        self.calculate_beam_path(self.x, self.y, self.a)
        self.part.translate(App.Vector(-self.x, -self.y, 0))
        self.part.rotate(App.Vector(0, 0, 0),App.Vector(0, 0, 1), degrees(-self.a))
        self.part = self.part.fuse(self.part)
        obj.Shape = self.part

    # compute full beam path given start point and angle
    def calculate_beam_path(self, x1, y1, a1, beam_index=1):
        if beam_index > 200:
            return
        count = 0 # number of reflections per beam
        comp_index = 0 # index of current inline component
        pre_count = 0 # current number of previous interactions for inline components
        pre_d = 0 # current previous interaction distance for inline components
        while True:
            min_len = 0
            for obj in App.ActiveDocument.Objects:
                # skip if unplaced inline component
                comp_check = True
                for beam in self.components:
                    for comp in beam:
                        if obj in comp and not obj in self.comp_track:
                            comp_check = False

                ref = find_interaction(x1, y1, a1, obj) # check for reflection
                if ref != None and comp_check:
                    [x2, y2, a2_arr] = ref
                    # check to find closest component
                    comp_d = sqrt((x2-x1)**2+(y2-y1)**2)
                    if comp_d < min_len or min_len == 0:
                        min_len = comp_d
                        xf, yf, af_arr = x2, y2, a2_arr

            if beam_index < len(self.components) and len(self.components[beam_index]) > comp_index:
                inline_ref=False
                comp_obj, comp_pos, comp_pre_count = self.components[beam_index][comp_index]

                # handle different constraint methods
                constraint = [i!=None for i in comp_pos].index(True)
                if constraint == 0:
                    comp_d = comp_pos[constraint]
                if constraint == 1:
                    comp_d = (comp_pos[constraint]-x1)/cos(a1)
                if constraint == 2:
                    comp_d = (comp_pos[constraint]-y1)/sin(a1)

                # check for closest component or satisfied pre_count
                if (comp_d < min_len or min_len == 0) and pre_count >= comp_pre_count:
                    if pre_count > comp_pre_count:
                        comp_d -= pre_d # account for previous distance
                    # inline placement
                    x2 = x1+comp_d*cos(a1)
                    y2 = y1+comp_d*sin(a1)
                    comp_obj.Placement.Base = App.Vector(x2, y2, 0)
                    # check for valid reflection
                    ref = find_interaction(x1, y1, a1, comp_obj)
                    if ref != None:
                        [xf, yf, af_arr] = ref
                        self.comp_track.append(comp_obj)
                        min_len = comp_d
                        # increment index and reset counters
                        comp_index += 1
                        pre_count = 0
                        pre_d = 0
                        inline_ref=True
                    else:
                        comp_obj.Placement.Base = App.Vector(0, 0, 0)
                # previous interaction info
                if not inline_ref:
                    pre_count += 1
                    if pre_count > comp_pre_count:
                        pre_d += min_len

            # end if no reflection found
            if min_len == 0:
                beam_len = 100
            else:
                beam_len = min_len
            
            # add beam segment
            temp = Part.makeCylinder(0.5, beam_len, App.Vector(x1, y1, 0), App.Vector(1, 0, 0))
            temp.rotate(App.Vector(x1, y1, 0),App.Vector(0, 0, 1), degrees(a1))
            self.part = self.part.fuse(temp)

            # continue beam if reflection was found
            if min_len != 0:
                # splitter case
                if af_arr[0] != None and af_arr[1] != None:
                    self.calculate_beam_path(xf, yf, af_arr[1], beam_index<<1)
                    beam_index = (beam_index<<1)+1
                    comp_index = 0
                # reflections
                if af_arr[0] != None:
                    x1, y1, a1 = xf, yf, af_arr[0]
                    count += 1
                # transmission
                elif af_arr[1] != None:
                    x1, y1, a1 = xf, yf, af_arr[1]
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
        for i in App.ActiveDocument.Objects:
            if i != feature.Object:
                App.ActiveDocument.removeObject(i.Name)
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