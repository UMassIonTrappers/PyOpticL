# This code is to generate 2D drawing of the baseplate indicating threaded and non-threaded holes with their size.
# Once the 3D baseplate is generated in the FreeCAD go to macro, select create_drawings and excute. 
# The 2D drawing will be generated. They can be used when you are ording Al version of the baseplate from companies like Xometry. 
# Please Don't change thing on this code. 

import FreeCAD
import TechDraw
import Part
from PySide import QtCore
from math import isclose
from PyOpticL import layout

inch = 25.4
bolt_4_40 = {
    "name": "4-40",
    "clear_dia": 0.120 * inch,
    "tap_dia": 0.089 * inch,
    "head_dia": 5.50,
    "head_dz": 2.5,
    "clear_dia_string": '3.05 mm, unthreaded'
}

bolt_8_32 = {
    "name": "8-32",
    "clear_dia": 0.172 * inch,
    "tap_dia": 0.136 * inch,
    "head_dia": 7,
    "head_dz": 4.4,
    "clear_dia_string": '4.37 mm, unthreaded'
}

bolt_14_20 = {
    "name": "1/4-20",
    "clear_dia": 0.260 * inch,
    "tap_dia": 0.201 * inch,
    "head_dia": 9.8,
    "head_dz": 8,
    "washer_dia": 9 / 16 * inch,
    "clear_dia_string": '6.60 mm, unthreaded'
}

bolts = [bolt_4_40, bolt_8_32, bolt_14_20]

doc = FreeCAD.ActiveDocument
FreeCAD.Console.SetStatus("Console", "Err", False)

for obj in doc.Objects:
    if isinstance(obj.Proxy, layout.baseplate):
        baseplate = obj
        break

if baseplate is None:
    print("Baseplate object not found in the document.")
else:
    # Create a TechDraw page
    directions = [
        ("Top", (0, 0, 1)),
        # ("Front", (0, -1, 0)),
        # ("Back", (0, 1, 0)),
        # ("Left", (-1, 0, 0)),
        # ("Right", (1, 0, 0)),
    ]

    for name, direction in directions:
        page = doc.addObject("TechDraw::DrawPage", f"{name} View")
        # Create a default template for the page
        template = doc.addObject("TechDraw::DrawSVGTemplate", "Template")
        template.Template = (
            FreeCAD.getResourceDir()
            + "Mod/TechDraw/Templates/A3_Landscape_Blank.svg"
        )
        page.Template = template

        # Create a TechDraw view for the baseplate and add it to the page
        view = doc.addObject("TechDraw::DrawViewPart", f"Baseplate{name}View")
        view.Source = [baseplate]
        view.Direction = direction
        page.addView(view)
        doc.recompute()
        page.ViewObject.show()
        view.X = template.Width.Value / 2
        view.Y = template.Height.Value / 2

        # wait for threads to complete before checking result
        loop = QtCore.QEventLoop()

        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)

        timer.start(2000)  # 2 second delay
        loop.exec_()

        edges = view.getVisibleEdges()
        for i, edge in enumerate(edges):
            if isinstance(edge.Curve, Part.Circle):
                radius = edge.Curve.Radius
                label = None
                for bolt in bolts:
                    if isclose(bolt["tap_dia"], 2 * radius):
                        label = bolt["name"] + "\n(thread)"
                        break
                    if isclose(bolt["clear_dia"], 2 * radius):
                        label = bolt["clear_dia_string"]#bolt["name"] + "\n(clear)"
                        break
                    if isclose(bolt_14_20["clear_dia"], 2 * radius): # these large bolts are only for bolts into optical table
                        label = "A"
                        break
                    if isclose(bolt_8_32["clear_dia"], 2 * radius):
                        label = "B"
                        break
                    if isclose(bolt_8_32["tap_dia"], 2 * radius):
                        label = "C"
                        break
                if label != None:
                    x, y, _ = edge.Curve.Center
                    balloon = FreeCAD.ActiveDocument.addObject(
                        "TechDraw::DrawViewBalloon", "Balloon"
                    )
                    balloon.SourceView = view
                    balloon.OriginX = x
                    balloon.OriginY = -y
                    balloon.X = x - 10
                    balloon.Y = -y + 10
                    balloon.Text = label
                    balloon.BubbleShape = "Line"
                    balloon.KinkLength = 0
                    balloon.ShapeScale = 0.75
                    balloon.ViewObject.Font = "MS Sans Serif"
                    balloon.ViewObject.Fontsize = 4
                    page.addView(balloon)

    #    # Create an annotation object
    #     blockObj = FreeCAD.ActiveDocument.addObject('TechDraw::DrawRichAnno','DrawRichAnno')
    #     page.addView(blockObj)
    #     blockObj.X = 45
    #     blockObj.Y = 145
    #     blockObj.ShowFrame = False
    #     blockObj.Scale = 15
    #     # print(vars(blockObj.AnnoText))
    #     # blockObj.Fontsize = 8
    #     blockObj.AnnoText = "dd \n dd"
        anno = FreeCAD.ActiveDocument.addObject('TechDraw::DrawViewAnnotation','Symbol Annotation')
        anno.Text = ['A -- \u00F8 6.60mm, \u2334 \u00F8 13.20mm, \u2193 10mm', 'B -- \u00F8 4.37 mm, through',  'C -- 8-32, thread']
        anno.TextStyle = 'Bold'
        anno.X = 45
        anno.Y = 145
        anno.MaxWidth = 115
        rc = page.addView(anno)
        print(anno.Content)
        view.touch()
        view.recompute()
        doc.recompute()
