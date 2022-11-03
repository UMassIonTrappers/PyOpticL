import FreeCAD as App
import Part
from math import *

INCH = 25.4

# calculate intersection between two lines given the origin and angle of both
def find_ref(x1, y1, a1, ref_obj):
    App.Console.PrintMessage(ref_obj.Name+":")
    if "mirror" in ref_obj.Proxy.Tags:
        ref_width = INCH/2
        ref_angle = 0
    elif "pbs" in ref_obj.Proxy.Tags:
        ref_width = sqrt(200)
        ref_angle = 3*pi/4
    else:
        App.Console.PrintMessage("Not a reflector\n")
        return

    (x2, y2, _) = ref_obj.Placement.Base
    a2 = ref_obj.Placement.Rotation.Angle+ref_angle
    a2 *= ref_obj.Placement.Rotation.Axis[2]
    a2 -= a2//(2*pi) * 2*pi
    a1 -= a1//(2*pi) * 2*pi

    App.Console.PrintMessage("a1=%f,a2=%f"%(a1, a2))

    if (isclose(x1, x2, abs_tol=1e-5) and isclose(y1, y2, abs_tol=1e-5)) or abs(a1-a2) < pi/2:
        App.Console.PrintMessage("Same component\n")
        return

    if (round(degrees(a1), 5)-90)%180 == 0:
        x = x1
    elif (round(degrees(a2), 5)-90)%180 == 0:
        x = x2
    else:
        x = (y2-x2*tan(a2)-y1+x1*tan(a1))/(tan(a1)-tan(a2))
    if (round(degrees(a1), 5)-90)%180 != 0:
        y = x*tan(a1)+y1-x1*tan(a1)
    elif (round(degrees(a2), 5)-90)%180 != 0:
        y = x*tan(a2)+y2-x2*tan(a2)
    else:
        App.Console.PrintMessage("Angles are bad\n")
        return

    a = 2*a2-a1-pi

    ref_d = sqrt((x-x2)**2+(y-y2)**2)
    if ref_d > ref_width/2:
        App.Console.PrintMessage("Hit too far\n")
        return

    return [x, y, a]

# beam path freecad object
class beam_path:

    def __init__(self, obj, x, y, angle):

        obj.Proxy = self
        obj.addProperty('App::PropertyDistance', 'x').x = x
        obj.addProperty('App::PropertyDistance', 'y').y = y
        obj.addProperty('App::PropertyAngle', 'angle').angle = angle

        self.Tags = ("beam")
        self.components = [[]]

    def execute(self, obj):
        self.refs = []
        x1 = obj.x.Value
        y1 = obj.y.Value
        a1 = radians(obj.angle.Value)
        self.part = Part.makeSphere(0)
        self.calculate_beam_path(x1, y1, a1)
        obj.Shape = self.part

    # compute full beam path given start point and angle
    def calculate_beam_path(self, x1, y1, a1, beam_index=0):
        if beam_index > 20:
            return
        ref_count = 0
        comp_index = 0
        while True:
            min_len = 0
            for obj in App.ActiveDocument.Objects:
                ref = find_ref(x1, y1, a1, obj)
                if ref != None:
                    App.Console.PrintMessage("Ref Happened:")
                    App.Console.PrintMessage(str(beam_index)+"\n")
                    [x, y, a] = ref
                    comp_d = sqrt((x-x1)**2+(y-y1)**2)
                    if comp_d < min_len or min_len == 0:
                        min_len = comp_d
                        xf, yf, af = x, y, a
                        ref_obj = obj
            App.Console.PrintMessage("len=%f,index=%f\n"%(len(self.components[beam_index]), comp_index))
            if len(self.components[beam_index]) > comp_index:
                comp_obj = self.components[beam_index][comp_index][0]
                comp_d = self.components[beam_index][comp_index][1]
                if comp_d < min_len or min_len == 0:
                    x2 = x1+comp_d*cos(a1)
                    y2 = y1+comp_d*sin(a1)
                    comp_obj.Placement.Base = App.Vector(x2, y2, 0)
                    ref = find_ref(x1, y1, a1, comp_obj)
                    App.Console.PrintMessage("x2=%f,y2=%f"%(x2, y2))
                    if ref != None:
                        App.Console.PrintMessage("Inline Ref Happened\n")
                        [xf, yf, af] = ref
                        ref_obj = comp_obj
                        min_len = comp_d
                        comp_index += 1
            if min_len != 0:
                if "pbs" in ref_obj.Proxy.Tags:
                    self.components.append([])
                    self.components.append([])
                    self.calculate_beam_path(xf, yf, a1, beam_index+1)
                    beam_index += 2
                    comp_index = 0
                temp = Part.makeCylinder(0.5, min_len, App.Vector(x1, y1, 0), App.Vector(1, 0, 0))
                temp.rotate(App.Vector(x1, y1, 0),App.Vector(0, 0, 1), degrees(a1))
                self.part = self.part.fuse(temp)
                self.refs.append((xf, yf, af))
                x1, y1, a1 = xf, yf, af
                ref_count += 1
            else:
                temp = Part.makeCylinder(0.5, 50, App.Vector(x1, y1, 0), App.Vector(1, 0, 0))
                temp.rotate(App.Vector(x1, y1, 0),App.Vector(0, 0, 1), degrees(a1))
                self.part = self.part.fuse(temp)
                return
            if ref_count > 100:
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
        App.Console.PrintMessage("Change property: " + str(prop) + "\n")

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