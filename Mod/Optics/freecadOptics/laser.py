import FreeCAD as App
import Part
from math import *

INCH = 25.4

def is_mult(x, factor, tol=1e-5):
    return isclose((abs(x)+tol/2)%factor, 0, abs_tol=tol)

# calculate intersection between two lines given the origin and angle of both
def find_ref(x1, y1, a1, ref_obj):
    ref_angle = 0 # offset between placement angle and reflection angle
    inline = False # bool for if beam should pass without reflection

    if "mirror" in ref_obj.Proxy.Tags:
        ref_width = INCH/2 # width of reflection surface
    elif "split" in ref_obj.Proxy.Tags:
        ref_width = INCH/2
    elif "pbs" in ref_obj.Proxy.Tags:
        ref_width = sqrt(200)
        ref_angle = 3*pi/4
    elif "port" in ref_obj.Proxy.Tags:
        ref_width = sqrt(200)
    elif "rts" in ref_obj.Proxy.Tags:
        ref_width = INCH/2
        ref_angle = 0
        inline = True
    elif "aom" in ref_obj.Proxy.Tags:
        ref_width = 5
    else:
        return # non-optical element

    ref_angle = ref_obj.Proxy.ref_angle
    ref_limit = ref_obj.Proxy.ref_limit
    ref_width = ref_obj.Proxy.ref_width

    # get object placement
    (x2, y2, _) = ref_obj.Placement.Base
    a2 = ref_obj.Placement.Rotation.Angle
    a2 *= ref_obj.Placement.Rotation.Axis[2]
    a2 += ref_angle
    a1 %= 2*pi
    a2 %= 2*pi

    # angle between beam and reflector
    a_ref = abs(a1-a2)%(2*pi)
    if a_ref > pi:
        a_ref = 2*pi-a_ref
    # angle from beam start to component
    a_comp = abs(a1-atan2(y2-y1, x2-x1))%(2*pi)
    if a_comp > pi:
        a_comp = 2*pi-a_comp

    # check if beam is from current object
    if isclose(x1, x2, abs_tol=1e-5) and isclose(y1, y2, abs_tol=1e-5):
        return
    
    # check if placement is suitable for reflection
    if a_ref < ref_limit  or a_comp > pi/2:
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
    if isclose(ref_limit, 2*pi, abs_tol=1e-5):
        a = a1+ref_angle
    else:
        a = 2*a2-a1-pi

    # check if reflection within reflective surface
    if sqrt((x-x2)**2+(y-y2)**2) > ref_width/2:
        return

    return [x, y, a]

# beam path freecad object
class beam_path:

    def __init__(self, obj):

        obj.Proxy = self

        self.Tags = ("beam")
        self.components = [[]]

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
        App.ActiveDocument.Baseplate.touch()

    # compute full beam path given start point and angle
    def calculate_beam_path(self, x1, y1, a1, beam_index=1):
        if beam_index > 20:
            return
        ref_count = 0 # number of reflections per beam
        comp_index = 0 # index of current inline component
        pre_refs = 0 # current number of pre_refs for inline components
        refs_d = 0 # current pre_ref distance for inline components
        while True:
            min_len = 0
            for obj in App.ActiveDocument.Objects:
                # skip if unplaced inline component
                comp_check = True
                for beam in self.components:
                    for comp in beam:
                        if obj in comp and not obj in self.comp_track:
                            comp_check = False
                ref = find_ref(x1, y1, a1, obj) # check for reflection
                if ref != None and comp_check:
                    App.Console.PrintMessage("%.2f, %s, %d\n"%(a1, obj.Name, beam_index))
                    [x2, y2, a2] = ref
                    # check to find closest component
                    comp_d = sqrt((x2-x1)**2+(y2-y1)**2)
                    if comp_d < min_len or min_len == 0:
                        min_len = comp_d
                        xf, yf, af = x2, y2, a2
                        ref_obj = obj
            if beam_index < len(self.components) and len(self.components[beam_index]) > comp_index:
                inline_ref=False
                comp_obj, comp_pos, comp_pre_refs = self.components[beam_index][comp_index]

                # handle different constraint methods
                constraint = [i!=None for i in comp_pos].index(True)
                if constraint == 0:
                    comp_d = comp_pos[constraint]
                if constraint == 1:
                    comp_d = (comp_pos[constraint]-x1)/cos(a1)
                if constraint == 2:
                    comp_d = (comp_pos[constraint]-y1)/sin(a1)

                # check for closest component or satisfied pre_refs
                if (comp_d < min_len or min_len == 0) and pre_refs >= comp_pre_refs:
                    if pre_refs > comp_pre_refs:
                        comp_d -= refs_d # account for pre_ref distance
                    # inline placement
                    x2 = x1+comp_d*cos(a1)
                    y2 = y1+comp_d*sin(a1)
                    comp_obj.Placement.Base = App.Vector(x2, y2, 0)
                    # check for valid reflection
                    ref = find_ref(x1, y1, a1, comp_obj)
                    if ref != None:
                        [xf, yf, af] = ref
                        self.comp_track.append(comp_obj)
                        ref_obj = comp_obj
                        min_len = comp_d
                        # increment index and reset counters
                        comp_index += 1
                        pre_refs = 0
                        refs_d = 0
                        inline_ref=True
                    else:
                        comp_obj.Placement.Base = App.Vector(0, 0, 0)
                # accumulate pre_ref info
                if not inline_ref:
                    pre_refs += 1
                    if pre_refs > comp_pre_refs:
                        refs_d += min_len

            # end if no reflection found
            if min_len == 0:
                beam_len = 50
            else:
                beam_len = min_len
            
            # add beam segment
            temp = Part.makeCylinder(0.5, beam_len, App.Vector(x1, y1, 0), App.Vector(1, 0, 0))
            temp.rotate(App.Vector(x1, y1, 0),App.Vector(0, 0, 1), degrees(a1))
            self.part = self.part.fuse(temp)

            # continue beam if reflection was found
            if min_len != 0 and not "port" in ref_obj.Proxy.Tags:
                if "pbs" in ref_obj.Proxy.Tags or "split" in ref_obj.Proxy.Tags:
                    self.calculate_beam_path(xf, yf, a1, beam_index<<1)
                    beam_index = (beam_index<<1)+1
                    comp_index = 0
                x1, y1, a1 = xf, yf, af
                ref_count += 1
            else:
                return
                    
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
        for i in App.ActiveDocument.Objects:
            if i != feature.Object:
                App.ActiveDocument.removeObject(i.Name)
        return True

    def onChanged(self, vp, prop):
        #App.Console.PrintMessage("Change property: " + str(prop) + "\n")
        pass

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