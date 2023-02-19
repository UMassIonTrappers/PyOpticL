import FreeCAD as App
import FreeCADGui as Gui

from freecadOptics import layout

class Create_Baseplate():

    def GetResources(self):
        return {"Pixmap"  : "My_Command_Icon",
                "Accel"   : "Shift+B",
                "MenuText": "Create Baseplate",
                "ToolTip" : "Add a new baseplate object"}

    def Activated(self):
        layout.create_baseplate(100, 100, layout.INCH)
        return

    def IsActive(self):
        return not "baseplate" in [i.Proxy.Tags for i in App.ActiveDocument.Objects]

Gui.addCommand("CreateBaseplate", Create_Baseplate())