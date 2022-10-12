import FreeCAD as App
import Part
from math import *

INCH = 25.4

def intersection(x1, y1, a1, x2, y2, a2):
    if (round(degrees(a1), 5)-90)%180 == 0:
        x = x1
    elif (round(degrees(a2), 5)-90)%180 == 0:
        x = x2
    else:
        x = (y2-x2*tan(a2)-y1+x1*tan(a1))/(tan(a1)-tan(a2))
    if (round(degrees(a1), 5)-90)%180 == 0:
        y = x*tan(a2)+y2-x2*tan(a2)
    else:
        y = x*tan(a1)+y1-x1*tan(a1)
    a = a1+2*(a2-a1)
    return (x, y, a)

def calculate_beam_path(part, x1, y1, a1, ref_list, rec=0):
    if rec > 5:
        return part
    cur = 0
    temp = 0
    count = 0
    refs = []
    while True:
        len = 0
        for i in App.ActiveDocument.Objects:
            if "mirror" in i.Proxy.Tags and cur != i:
                (x2, y2, z2) = i.Placement.Base
                a2 = i.Placement.Rotation.Angle-pi/2
                (x, y, a) = intersection(x1, y1, a1, x2, y2, a2)
                len1 = sqrt(pow(x-x1, 2)+pow(y-y1, 2))
                len2 = sqrt(pow(x-x2, 2)+pow(y-y2, 2))
                if len2 < INCH/4 and ((len1 < len and len1 != 0) or len == 0):
                    len = len1
                    xf, yf, af = x, y, a
                    temp = i
            elif "pbs" in i.Proxy.Tags and cur != i:
                (x2, y2, z2) = i.Placement.Base
                a2 = i.Placement.Rotation.Angle+pi/4
                (x, y, a) = intersection(x1, y1, a1, x2, y2, a2)
                len1 = sqrt(pow(x-x1, 2)+pow(y-y1, 2))
                len2 = sqrt(pow(x-x2, 2)+pow(y-y2, 2))
                if len2 < sqrt(200)/2 and ((len1 < len and len1 != 0) or len == 0):
                    len = len1
                    xf, yf, af = x, y, a
                    temp = i
        if len != 0:
            cur = temp
            if "pbs" in cur.Proxy.Tags:
                part = part.fuse(calculate_beam_path(part, xf, yf, a1, refs, rec+1))
            temp = Part.makeCylinder(0.5, len, App.Vector(x1, y1, 0), App.Vector(1, 0, 0))
            temp.rotate(App.Vector(x1, y1, 0),App.Vector(0, 0, 1), degrees(a1))
            part = part.fuse(temp)
            refs.append((xf, yf, af))
            x1, y1, a1 = xf, yf, af
            count += 1
        else:
            temp = Part.makeCylinder(0.5, 50, App.Vector(x1, y1, 0), App.Vector(1, 0, 0))
            temp.rotate(App.Vector(x1, y1, 0),App.Vector(0, 0, 1), degrees(a1))
            part = part.fuse(temp)
            ref_list.append(refs)
            return part

class beam_path:

    def __init__(self, obj, x, y, angle):

        obj.Proxy = self
        obj.addProperty('App::PropertyDistance', 'x').x = x
        obj.addProperty('App::PropertyDistance', 'y').y = y
        obj.addProperty('App::PropertyAngle', 'angle').angle = angle

        self.Tags = ("beam")
        self.Refs = []

    def execute(self, obj):
        x1 = obj.x.Value
        y1 = obj.y.Value
        a1 = radians(obj.angle.Value)
        part = Part.makeSphere(0)
        obj.Shape = calculate_beam_path(part, x1, y1, a1, self.Refs)
                    
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