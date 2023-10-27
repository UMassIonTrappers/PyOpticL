import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math

reload(optomech)
reload(layout)
reload(laser)

baseplate = layout.create_baseplate(100, 200, layout.inch)

beam = baseplate.add_beam_path(0, 50, layout.cardinal['right'])

baseplate.place_element_along_beam("Rotation Stage", optomech.rotation_stage_rsp05, beam, 0b1, layout.cardinal['right'], 30)
baseplate.place_element_along_beam("Splitter", optomech.splitter_mount_b05g, beam, 0b1, layout.turn['right-up'], 30)

layout.redraw()