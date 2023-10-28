import FreeCAD as App
import FreeCADGui as Gui

import csv
import re
import math
import numpy as np
from pathlib import Path
from PyOptic import laser, layout, optomech

class Reload_Modules():

    def GetResources(self):
        return {"Pixmap"  : ":/icons/preferences-import-export.svg",
                "Accel"   : "Shift+M",
                "MenuText": "Reload Freecad Optics Modules"}

    def Activated(self):
        from importlib import reload
        reload(optomech)
        reload(layout)
        reload(laser)
        App.Console.PrintMessage("Freecad Optics Modules Reloaded\n")
        return

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
            if isinstance(obj.Proxy, layout.baseplate) or all(np.isclose(obj.ViewObject.ShapeColor[:3], optomech.adapter_color)):
                obj.Shape.exportStl(str(path / obj.Label) + ".stl")
        App.Console.PrintMessage("STLs Exported to '%s'\n"%(str(path)))
        return
    
class Top_View_Fit():

    def GetResources(self):
        return {"Pixmap"  : ":/icons/view-top.svg",
                "Accel"   : "Shift+T",
                "MenuText": "Switch to Auto-Fit Top View"}

    def Activated(self):
        Gui.activeDocument().activeView().viewTop()
        Gui.SendMsgToActiveView("ViewFit")
        Gui.runCommand('Std_ViewZoomIn',0)
        return
    
class Export_Cart():

    def GetResources(self):
        return {"Pixmap"  : ":/icons/edit-paste.svg",
                "Accel"   : "Shift+O",
                "MenuText": "Export Optomech Parts to Order List"}

    def Activated(self):
        export_path = str(Path.home() / "Downloads" / "FreeCAD_Optics_Cart_")
        n = 0
        while Path(export_path+str(n)).is_dir():
            n += 1

        path = Path(export_path+str(n))
        path.mkdir()

        doc = App.activeDocument()
        parts = []
        objs = []
        for obj in doc.Objects:
            if hasattr(obj.Proxy, 'part_numbers'):
                if '' in obj.Proxy.part_numbers:
                    App.Console.PrintMessage(obj.Name + " is missing an auxiliary part number\n")
                parts.extend(obj.Proxy.part_numbers)
                objs.extend([obj]*len(obj.Proxy.part_numbers))

        cart = open(str(path / "Thorlabs_Cart.csv"), 'w', newline='')
        list = open(str(path / "Parts_List.csv"), 'w', newline='')
        cart_w= csv.writer(cart)
        list_w= csv.writer(list)
        cart_w.writerow(["Part Number", "Qty"])
        list_w.writerow(["Part Class / Name", "Part Number", "Qty"])
        for i in enumerate(set(parts)):
            if i[1] != '':
                test = re.match(".*-P([0-9]+)$", i[1])
                pack = 1
                if test != None:
                    pack = int(test.group(1))
                cart_w.writerow([i[1], math.ceil(parts.count(i[1])/pack)])
                list_w.writerow([type(objs[i[0]].Proxy).__name__, i[1], math.ceil(parts.count(i[1])/pack)])
        for i in enumerate(parts):
            if i[1] == '':
                list_w.writerow([objs[i[0]].Label, "Unknown", 1])
            
        return
    

Gui.addCommand("ReloadModules", Reload_Modules())
Gui.addCommand("RecomputeBeam", Recompute_Beam())
Gui.addCommand("ShowComponents", Show_Components())
Gui.addCommand("ExportSTLs", Export_STLs())
Gui.addCommand("TopViewFit", Top_View_Fit())
Gui.addCommand("ExportCart", Export_Cart())