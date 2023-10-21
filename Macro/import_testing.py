import FreeCAD as App
from freecadOptics import laser, layout, optomech

#layout.place_element("Input_Mirror_1", optomech.mount_mk05pm, 0, 0, 0)
layout.place_element("Input_Mirror_2", optomech.example_component, 0, 0, 0)

layout.redraw()