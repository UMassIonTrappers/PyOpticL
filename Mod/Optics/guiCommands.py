import FreeCAD as App
import FreeCADGui as Gui

from freecadOptics import layout

class Recompute_Beam():

    def GetResources(self):
        return {"Pixmap"  : ":/icons/view-refresh.svg",
                "Accel"   : "Shift+R",
                "MenuText": "Recompute Beam Path"}

    def Activated(self):
        layout.redraw()
        return
    
class Show_Components():

    def __init__(self):
        self.state = True

    def GetResources(self):
        return {"Pixmap"  : ":/icons/dagViewVisible.svg",
                "Accel"   : "Shift+V",
                "MenuText": "Toggle Component Visibility"}

    def Activated(self):
        self.state = not self.state
        layout.hide_components(self.state)
        return

Gui.addCommand("RecomputeBeam", Recompute_Beam())
Gui.addCommand("ShowComponents", Show_Components())