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
                if hasattr(obj, "Shape"):
                    exploded = obj.Shape.Solids
                    for i, shape in enumerate(exploded):
                        name = str(path / obj.Name)
                        if len(exploded) > 1:
                            name += "_" + str(i)
                        shape.exportStl(name + ".stl")
                else:
                    Mesh.export([obj], str(path / obj.Name) + ".stl")
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
        types = []
        objs = []
        for obj in doc.Objects:
            if hasattr(obj.Proxy, 'part_numbers'):
                if '' in obj.Proxy.part_numbers:
                    name = obj.Label
                    temp = obj
                    while True:
                        if hasattr(temp, "ParentObject"):
                            name = temp.ParentObject.Label + " - " + name
                            temp = temp.ParentObject
                        else:
                            break
                    App.Console.PrintMessage(name + " is missing a part number\n")
                parts.extend(obj.Proxy.part_numbers)
                for num in obj.Proxy.part_numbers:
                    types.append((type(obj.Proxy).__name__, num))
                objs.extend([obj]*len(obj.Proxy.part_numbers))

        cart = open(str(path / "Thorlabs_Cart.csv"), 'w', newline='')
        list = open(str(path / "Parts_List.csv"), 'w', newline='')
        cart_w= csv.writer(cart)
        list_w= csv.writer(list)
        cart_w.writerow(["Part Number", "Qty"])
        list_w.writerow(["Part Class / Name", "Part Number", "Qty"])

        for i in set(parts):
            if i != '':
                number = i
                test1 = re.match(".*-P([0-9]+)$", i)
                test2 = re.match(".*\(P([0-9]+)\)$", i)
                pack = 1
                if test1 != None:
                    pack = int(test1.group(1))
                if test2 != None:
                    pack = int(test2.group(1))
                    number = number[:-(4+len(test2.group(1)))]
                cart_w.writerow([number, math.ceil(parts.count(i)/pack)])
        for i in set(types):
            if i[1] != '':
                number = i[1]
                test1 = re.match(".*-P([0-9]+)$", i[1])
                test2 = re.match(".*\(P([0-9]+)\)$", i[1])
                pack = 1
                if test1 != None:
                    pack = int(test1.group(1))
                if test2 != None:
                    pack = int(test2.group(1))
                    number = number[:-(4+len(test2.group(1)))]
                list_w.writerow([i[0], number, math.ceil(parts.count(i[1])/pack)])
        for i in enumerate(parts):    
            if i[1] == '':
                name = objs[i[0]].Label
                temp = objs[i[0]]
                while True:
                    if hasattr(temp, "ParentObject"):
                        name = temp.ParentObject.Label + " - " + name
                        temp = temp.ParentObject
                    else:
                        break
                list_w.writerow([name, "Unknown", 1])
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
        if hasattr(obj, "Group"):
            translate = obj.Placement.multVec(App.Vector(*translate))

        translate = np.round(translate, 3)

        print("(%.4g, %.4g, %.4g)"%(translate[0], translate[1], translate[2]))
        return

Gui.addCommand("RerunMacro", Rerun_Macro())
Gui.addCommand("RedrawBaseplate", Redraw_Baseplate())
Gui.addCommand("ShowComponents", Show_Components())
Gui.addCommand("ToggleDrawStyle", Toggle_Draw_Style())
Gui.addCommand("ExportSTLs", Export_STLs())
Gui.addCommand("ExportCart", Export_Cart())
Gui.addCommand("ReloadModules", Reload_Modules())
Gui.addCommand("GetOrientation", Get_Orientation())
Gui.addCommand("GetPosition", Get_Position())