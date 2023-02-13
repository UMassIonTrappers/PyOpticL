import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

layout.create_baseplate(200, 200, layout.INCH)

beam = layout.add_beam_path(20, 200, -90)

layout.place_element_along_beam("Splitter", optomech.pbs_on_skate_mount, beam_obj=beam, beam_index=0b1, angle=-90, distance=25)

layout.redraw()
