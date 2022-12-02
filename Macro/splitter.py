import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

laser_input_height = 50

layout.create_baseplate(200, 100, laser_input_height+layout.INCH/2)

beam = layout.add_beam_path(0, 40, 0)

#layout.place_element_along_beam("Input_Rotation_Stage", optomech.rotation_stage_rsp05, beam, 0, 50, 0)

layout.place_element_along_beam("PBS_1", optomech.pbs_on_skate_mount, beam, 0, 25, 0)

layout.place_element_along_beam("Probe_Mirror_1", optomech.mirror_mount_k05s2, beam, 2, 25, -45)
layout.place_element_along_beam("Probe_Mirror_2", optomech.mirror_mount_k05s2, beam, 2, 35, -135)

layout.place_element_along_beam("Probe_Coupler", optomech.fiberport_holder, beam, 2, 65, 90)

layout.place_element_along_beam("Main_Mirror_1", optomech.mirror_mount_k05s2, beam, 1, 120, 157.5)
layout.place_element_along_beam("Main_Mirror_2", optomech.mirror_mount_k05s2, beam, 1, 35, -67.5)

layout.place_element_along_beam("Probe_Coupler", optomech.fiberport_holder, beam, 1, 65, 90)

layout.redraw()