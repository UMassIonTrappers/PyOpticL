import csv
import math
import re
from inspect import cleandoc
from itertools import count
from pathlib import Path

import FreeCAD as App
import FreeCADGui as Gui
import ImportGui
import Mesh
import numpy as np
import Part
from PySide import QtCore, QtGui

from PyOpticL import beam_path, icons, layout, optomech, utils


class Rerun_Macro:

    def GetResources(self):
        return {
            "Pixmap": ":/icons/view-refresh.svg",
            "Accel": "Ctrl+Shift+R",
            "MenuText": "Clear Document and Re-run Last Macro",
        }

    def Activated(self):
        for i in App.ActiveDocument.Objects:
            App.ActiveDocument.removeObject(i.Name)
        Gui.runCommand("Std_RecentMacros", 0)
        return


class Toggle_Draw_Style:

    def GetResources(self):
        return {
            "Pixmap": ":/icons/DrawStyleWireFrame.svg",
            "Accel": "Shift+D",
            "MenuText": "Toggle Between Wireframe and As-Is Draw Styles",
        }

    def Activated(self):
        mw = Gui.getMainWindow()
        asis = mw.findChild(QtGui.QAction, "Std_DrawStyleAsIs")
        wire = mw.findChild(QtGui.QAction, "Std_DrawStyleWireframe")
        if asis.isChecked():
            wire.trigger()
        else:
            asis.trigger()
        return


### TODO update to work with refactored code
class Export_STLs:

    def GetResources(self):
        return {
            "Pixmap": ":/icons/LinkSelect.svg",
            "Accel": "Shift+E",
            "MenuText": "Export Baselplate and Adapter STLs to Downloads Folder",
        }

    def Activated(self):
        export_path = str(Path.home() / "Downloads" / "FreeCAD_Optics_Export_")
        n = 0
        while Path(export_path + str(n)).is_dir():
            n += 1

        path = Path(export_path + str(n))
        path.mkdir()
        doc = App.activeDocument()
        for obj in doc.Objects:
            if isinstance(obj.Proxy, layout.baseplate) or all(
                np.isclose(obj.ViewObject.ShapeColor[:3], optomech.adapter_color)
            ):
                if hasattr(obj, "Shape"):
                    exploded = obj.Shape.Solids
                    for i, shape in enumerate(exploded):
                        name = str(path / obj.Name)
                        if len(exploded) > 1:
                            name += "_" + str(i)
                        shape.exportStl(name + ".stl")
                else:
                    Mesh.export([obj], str(path / obj.Name) + ".stl")
        App.Console.PrintMessage("STLs Exported to '%s'\n" % (str(path)))
        return


### TODO update to work with refactored code
class Export_Cart:

    def GetResources(self):
        return {
            "Pixmap": ":/icons/edit-paste.svg",
            "Accel": "Shift+O",
            "MenuText": "Export Optomech Parts to Order List",
        }

    def Activated(self):
        export_path = str(Path.home() / "Downloads" / "FreeCAD_Optics_Cart_")
        n = 0
        while Path(export_path + str(n)).is_dir():
            n += 1

        path = Path(export_path + str(n))
        path.mkdir()

        doc = App.activeDocument()
        parts = []
        types = []
        objs = []
        for obj in doc.Objects:
            if hasattr(obj.Proxy, "part_numbers"):
                if "" in obj.Proxy.part_numbers:
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
                objs.extend([obj] * len(obj.Proxy.part_numbers))

        cart = open(str(path / "Thorlabs_Cart.csv"), "w", newline="")
        list = open(str(path / "Parts_List.csv"), "w", newline="")
        cart_w = csv.writer(cart)
        list_w = csv.writer(list)
        cart_w.writerow(["Part Number", "Qty"])
        list_w.writerow(["Part Class / Name", "Part Number", "Qty"])

        for i in set(parts):
            if i != "":
                number = i
                test1 = re.match(".*-P([0-9]+)$", i)
                test2 = re.match(".*\(P([0-9]+)\)$", i)
                pack = 1
                if test1 != None:
                    pack = int(test1.group(1))
                if test2 != None:
                    pack = int(test2.group(1))
                    number = number[: -(4 + len(test2.group(1)))]
                cart_w.writerow([number, math.ceil(parts.count(i) / pack)])
        for i in set(types):
            if i[1] != "":
                number = i[1]
                test1 = re.match(".*-P([0-9]+)$", i[1])
                test2 = re.match(".*\(P([0-9]+)\)$", i[1])
                pack = 1
                if test1 != None:
                    pack = int(test1.group(1))
                if test2 != None:
                    pack = int(test2.group(1))
                    number = number[: -(4 + len(test2.group(1)))]
                list_w.writerow([i[0], number, math.ceil(parts.count(i[1]) / pack)])
        for i in enumerate(parts):
            if i[1] == "":
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


class Reload_Modules:

    def GetResources(self):
        return {
            "Pixmap": ":/icons/preferences-import-export.svg",
            "Accel": "Shift+M",
            "MenuText": "Reload Freecad Optics Modules",
        }

    def Activated(self):
        from importlib import reload

        reload(beam_path)
        reload(icons)
        reload(layout)
        reload(optomech)
        reload(utils)
        App.Console.PrintMessage("Freecad Optics Modules Reloaded\n")
        return


def get_position_of_selected():
    selection = Gui.Selection.getSelectionEx()
    points = []
    for element in selection:
        for feature in element.SubObjects:
            if hasattr(feature, "Curve"):
                if hasattr(feature.Curve, "Center"):
                    points.append(feature.Curve.Center)
                else:
                    points.append(feature.CenterOfMass)
            elif hasattr(feature, "Point"):
                points.append(feature.Point)
    points = np.array(points)
    return np.mean(points, axis=0)


class Load_Model_Dialog(QtGui.QDialog):
    def __init__(self):
        super(Load_Model_Dialog, self).__init__()
        self.setWindowTitle("PyOpticL Model Conversion")

        # file selector
        self.filePathEdit = QtGui.QLineEdit()
        self.browseBtn = QtGui.QPushButton("Browse...")
        self.browseBtn.clicked.connect(self.selectFile)

        fileLayout = QtGui.QHBoxLayout()
        fileLayout.addWidget(self.filePathEdit)
        fileLayout.addWidget(self.browseBtn)

        # name input
        self.nameEdit = QtGui.QLineEdit()

        # checkbox
        self.externalSave = QtGui.QCheckBox("Save to external library (recommended)")
        self.externalSave.setChecked(True)

        # buttons
        self.btnBox = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
        )
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        # widget layout
        layout = QtGui.QFormLayout()
        layout.addRow("Select Model:", fileLayout)
        layout.addRow("Model Name:", self.nameEdit)
        layout.addRow(self.externalSave)
        layout.addRow(self.btnBox)

        self.setLayout(layout)

    def selectFile(self):
        filename, _ = QtGui.QFileDialog.getOpenFileName(self, "Select File")
        if filename:
            self.filePathEdit.setText(filename)


class Import_Model_Dialog(QtGui.QDialog):
    def __init__(self, import_object, import_name, external_save):
        super(Import_Model_Dialog, self).__init__()

        self.import_object = import_object
        self.import_name = import_name
        self.external_save = external_save

        self.setWindowTitle("PyOpticL Model Conversion")
        self.setModal(False)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

        self.instructions = QtGui.QLabel(
            cleandoc(
                """
                Please define the optical center and orientation for the model.
                To do this, select one or more edges whose centers match or frame the desired origin,
                then orient the camera such as to view the model exactly from the desired front.
                In general, optics should be centered at the optical center
                and mounts should be centered on the optic or other logical mounting surface.
                When ready, press 'Orient' to apply the new orientation.
                When complete, the origin should be as desired and the front of the model should face +X (right).
                If the orientation is incorrect, you may press 'Reset' to try again.
                """
            )
        )
        self.orient_button = QtGui.QPushButton("Orient")
        self.orient_button.clicked.connect(self.orient)
        self.reset_button = QtGui.QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        self.save_button = QtGui.QPushButton("Confirm and Save")
        self.save_button.clicked.connect(self.save)
        self.save_button.setEnabled(False)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.instructions)
        layout.addWidget(self.orient_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def orient(self):
        # get rotation from view
        rotation = Gui.ActiveDocument.ActiveView.viewPosition().Rotation.inverted()
        rotation = App.Rotation("XYZ", 90, 0, 90) * rotation
        rotation = App.Placement(App.Vector(0, 0, 0), rotation, App.Vector(0, 0, 0))

        # get translation from selected features
        translation = -get_position_of_selected()
        translation = App.Placement(
            App.Vector(App.Vector(*translation)),
            App.Rotation("XYZ", 0, 0, 0),
            App.Vector(0, 0, 0),
        )

        # update object placement
        self.import_object.Placement = rotation * translation

        self.save_button.setEnabled(True)

    def reset(self):
        self.save_button.setEnabled(False)
        self.import_object.Placement = App.Placement()

    def save(self):
        # select folder
        if self.external_save:
            save_path = QtGui.QFileDialog.getExistingDirectory(
                None, "Select Folder to Save Model"
            )

            # validate path
            if not save_path:
                App.Console.PrintError("No folder selected. Model not saved.\n")
                return
            output_path = Path(save_path) / self.import_name
        else:
            output_path = (
                Path(App.getUserAppDataDir())
                / "Mod"
                / "PyOpticL"
                / "PyOpticL"
                / "models"
                / self.import_name
            )

        # check if folder already exists
        if output_path.is_dir():
            App.Console.PrintError("Folder already exists. Model not saved.\n")
            return

        # create output folder and save STEP file
        output_path.mkdir()
        step_path = output_path / (self.import_name + ".step")
        Part.export([self.import_object], str(step_path))

        self.close()


class Convert_Model:

    def GetResources(self):
        return {
            "Pixmap": ":/icons/Std_DemoMode.svg",
            "Accel": "Shift+G",
            "MenuText": "Create PyOpticL Model from STEP File",
        }

    def Activated(self):
        dialog = Load_Model_Dialog()
        result = dialog.exec_()

        if result:
            # retrieve values when user presses OK
            selected_file = Path(dialog.filePathEdit.text())
            name_value = dialog.nameEdit.text()
            external_save = dialog.externalSave.isChecked()

            # check for valid inputs
            if not selected_file.is_file():
                App.Console.PrintError("Invalid file selected.\n")
                return
            if not name_value:
                App.Console.PrintError("Model name cannot be empty.\n")
                return

            # create / clean new document
            if "PyOpticL Model Conversion" in App.listDocuments():
                App.setActiveDocument("PyOpticL Model Conversion")
                for obj in App.ActiveDocument.Objects:
                    App.ActiveDocument.removeObject(obj.Name)
            else:
                App.newDocument("PyOpticL Model Conversion")
            document = App.ActiveDocument

            # import selected file
            shape = Part.read(str(selected_file))
            import_object = document.addObject("Part::Feature", name_value)
            import_object.Shape = shape

            # show confirm orientation dialog
            global confirm_dialog
            confirm_dialog = Import_Model_Dialog(
                import_object, name_value, external_save
            )
            confirm_dialog.show()

            Gui.ActiveDocument.ActiveView.setAxisCross(True)  # show axis cross
            Gui.ActiveDocument.ActiveView.fitAll()

        return


class Get_Position:

    def GetResources(self):
        return {
            "Pixmap": ":/icons/view-measurement.svg",
            "Accel": "Shift+P",
            "MenuText": "Get Position of Part Features",
        }

    def Activated(self):
        position = get_position_of_selected()

        print(f"Position: ({position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f})")
        return


Gui.addCommand("RerunMacro", Rerun_Macro())
Gui.addCommand("ToggleDrawStyle", Toggle_Draw_Style())
Gui.addCommand("ExportSTLs", Export_STLs())
Gui.addCommand("ExportCart", Export_Cart())
Gui.addCommand("ReloadModules", Reload_Modules())
Gui.addCommand("ConvertModel", Convert_Model())
Gui.addCommand("GetPosition", Get_Position())
