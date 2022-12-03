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

layout.place_element_along_beam("Input_Rotation_Stage", optomech.rotation_stage_rsp05, beam_obj=beam, beam_index=0, angle=0, distance=25)

layout.place_element_along_beam("PBS_1", optomech.pbs_on_skate_mount, beam_obj=beam, beam_index=0, angle=0, distance=25)

layout.place_element_along_beam("Probe_Mirror_1", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=2, angle=-45, distance=25)
layout.place_element_along_beam("Probe_Mirror_2", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=2, angle=-135, distance=25)

layout.place_element_along_beam("Probe_Coupler", optomech.fiberport_holder, beam_obj=beam, beam_index=2, angle=90, y=0)

layout.place_element_along_beam("Main_Mirror_1", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=1, angle=150, distance=120)
layout.place_element_along_beam("Main_Mirror_2", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=1, angle=-75, distance=35)

layout.place_element_along_beam("Probe_Coupler", optomech.fiberport_holder, beam_obj=beam, beam_index=1, angle=90, y=0)

layout.redraw()