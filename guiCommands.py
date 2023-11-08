import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui
import Mesh

import csv
import re
import math
import numpy as np
from pathlib import Path
from PyOptic import laser, layout, optomech

class Rerun_Macro():
    def GetResources(self):
        return {"Pixmap"  : ":/icons/view-refresh.svg",
                "Accel"   : "Ctrl+Shift+R",
                "MenuText": "Clear Document and Re-run Last Macro"}

    def Activated(self):
        for i in App.ActiveDocument.Objects:
            App.ActiveDocument.removeObject(i.Name)
        Gui.runCommand('Std_RecentMacros',0)
        return

class Redraw_Baseplate():

    def GetResources(self):
        return {"Pixmap"  : ":/icons/tree-sync-pla.svg",
                "Accel"   : "Shift+B",
                "MenuText": "Redraw Baseplate After Editing Parameters in GUI"}

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
    
class Toggle_Draw_Style():

    def GetResources(self):
        return {"Pixmap"  : ":/icons/DrawStyleWireFrame.svg",
                "Accel"   : "Shift+D",
                "MenuText": "Toggle Between Wireframe and As-Is Draw Styles"}

    def Activated(self):
        mw = Gui.getMainWindow()
        asis = mw.findChild(QtGui.QAction, "Std_DrawStyleAsIs")
        wire = mw.findChild(QtGui.QAction, "Std_DrawStyleWireframe")
        if asis.isChecked():
            wire.trigger()
        else:
            asis.trigger()
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
    
class Get_Orientation():

    def GetResources(self):
        return {"Pixmap"  : ":/icons/Std_DemoMode.svg",
                "Accel"   : "Shift+G",
                "MenuText": "Get Orientation Parameters for Part"}

    def Activated(self):
        for obj in App.ActiveDocument.Objects:
            if obj.TypeId == "App::Part":
                break

        mw = Gui.getMainWindow()
        actions = mw.findChildren(QtGui.QAction)
        for action in actions:
            text = action.text()
            if "1" in text and ".step" in text:
                break
        obj.Label = text[2:-5]

        Mesh.export([obj], "%sMod/PyOptic/PyOptic/stl/%s.stl"%(App.getUserAppDataDir(), obj.Label))

        view_rot = Gui.ActiveDocument.ActiveView.viewPosition().Rotation
        rot1 = view_rot.inverted()
        rot2 = App.Rotation(App.Vector(0, 0, 1), 90)
        rot3 = App.Rotation(App.Vector(0, 1, 0), 90)
        final_rot = rot3*rot2*rot1

        rot_xyz = np.round(final_rot.getYawPitchRoll()[::-1], 3)

        selection = Gui.Selection.getSelectionEx()
        translate = np.zeros(3)
        count = 0
        for element in selection:
            for feature in element.SubObjects:
                if hasattr(feature, "Curve"):
                    if hasattr(feature.Curve, "Center"):
                        translate += feature.Curve.Center
                    else:
                        translate += feature.CenterOfMass
                elif hasattr(feature, "Point"):
                    translate += feature.Point
                count += 1
        translate /= count
        final_translate = final_rot.multVec(-App.Vector(*translate))

        final_placement = App.Placement(final_translate, final_rot, App.Vector(0, 0, 0))
        obj.Placement = final_placement

        translate = np.round(final_placement.Base, 3)

        print('_import_stl("%s.stl", (%.4g, %.4g, %.4g), (%.4g, %.4g, %.4g))'%(obj.Label, *rot_xyz, *translate))
        return
    
class Get_Position():

    def GetResources(self):
        return {"Pixmap"  : ":/icons/view-measurement.svg",
                "Accel"   : "Shift+P",
                "MenuText": "Get Position of Part Features"}

    def Activated(self):
        for obj in App.ActiveDocument.Objects:
            if obj.TypeId == "App::Part":
                break

        selection = Gui.Selection.getSelectionEx()
        translate = np.zeros(3)
        count = 0
        for element in selection:
            for feature in element.SubObjects:
                if hasattr(feature, "Curve"):
                    if hasattr(feature.Curve, "Center"):
                        translate += feature.Curve.Center
                    else:
                        translate += feature.CenterOfMass
                elif hasattr(feature, "Point"):
                    translate += feature.Point
                count += 1
        translate /= count

        center = App.Placement(App.Vector(*translate), App.Rotation(0, 0, 0), App.Vector(0, 0, 0))
        final_placement = obj.Placement*center

        translate = np.round(final_placement.Base, 3)

        print("(%.4g, %.4g, %.4g)"%(translate[0], translate[1], translate[2]))
        return

Gui.addCommand("RerunMacro", Rerun_Macro())
Gui.addCommand("RedrawBaseplate", Redraw_Baseplate())
Gui.addCommand("ShowComponents", Show_Components())
Gui.addCommand("TopViewFit", Top_View_Fit())
Gui.addCommand("ToggleDrawStyle", Toggle_Draw_Style())
Gui.addCommand("ExportSTLs", Export_STLs())
Gui.addCommand("ExportCart", Export_Cart())
Gui.addCommand("ReloadModules", Reload_Modules())
Gui.addCommand("GetOrientation", Get_Orientation())
Gui.addCommand("GetPosition", Get_Position())