import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

layout.create_baseplate(200, 200, layout.INCH)

beam = layout.add_beam_path(20, 0, 90)

layout.place_element_along_beam("Input_Rotation_Stage", optomech.rotation_stage_rsp05, beam, 0, 25, 90)

layout.redraw()
