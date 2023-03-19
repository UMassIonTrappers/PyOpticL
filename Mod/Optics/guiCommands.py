import FreeCAD as App
import FreeCADGui as Gui

from pathlib import Path
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
        layout.show_components(self.state)
        return
    
class Export_STLs():

    def __init__(self):
        self.state = True

    def GetResources(self):
        return {"Pixmap"  : ":/icons/LinkSelect.svg",
                "Accel"   : "Shift+E",
                "MenuText": "Export Baselplate and Adapter STLs to Downloads Folder"}

    def Activated(self):
        export_path = str(Path.home() / "Downloads" / "FreeCAD_Optics_Export_")
        n = 0
        while Path(export_path+str(n)).is_dir():
            n += 1

        path = Path(export_path+str(n))
        path.mkdir()
        doc = App.activeDocument()
        for obj in doc.Objects:
            if isinstance(obj.Proxy, layout.baseplate) or "Adapter" in obj.Name:
                obj.Shape.exportStl(str(path / obj.Name) + ".stl")
        App.Console.PrintMessage("STLs Exported to '%s'\n"%(str(path)))
        return
    
class Top_View_Fit():

    def __init__(self):
        self.state = True

    def GetResources(self):
        return {"Pixmap"  : ":/icons/view-top.svg",
                "Accel"   : "Shift+T",
                "MenuText": "Switch to Auto-Fit Top View"}

    def Activated(self):
        Gui.activeDocument().activeView().viewTop()
        Gui.activeDocument().activeView().viewRotateRight()
        Gui.SendMsgToActiveView("ViewFit")
        Gui.runCommand('Std_ViewZoomIn',0)
        return

Gui.addCommand("RecomputeBeam", Recompute_Beam())
Gui.addCommand("ShowComponents", Show_Components())
Gui.addCommand("ExportSTLs", Export_STLs())
Gui.addCommand("TopViewFit", Top_View_Fit())