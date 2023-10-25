import FreeCAD as App
from freecadOptics import laser, layout, optomech

#layout.place_element("Input_Mirror_1", optomech.mount_mk05pm, 0, 0, 0)
layout.place_element("Input_Mirror_2", optomech.periscope, 0, 0, 0, lower_dz=3*layout.INCH/2, upper_dz=100, table_mount=True)

#testing

layout.redraw()