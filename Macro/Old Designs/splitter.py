import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

laser_input_height = 50
baseplate_posts = layout.INCH/2

mount_off_x = -5
mount_off_y = -layout.INCH/2

layout.create_baseplate(300, 100, laser_input_height-layout.INCH/2-baseplate_posts)

beam = layout.add_beam_path(0, 40, 0)

layout.place_element("Baseplate_Mount_1", optomech.baseplate_mount, layout.INCH*1+mount_off_x, layout.INCH+mount_off_y, 0)
layout.place_element("Baseplate_Mount_2", optomech.baseplate_mount, layout.INCH*2+mount_off_x, layout.INCH*4+mount_off_y, 0)
layout.place_element("Baseplate_Mount_3", optomech.baseplate_mount, layout.INCH*11+mount_off_x, layout.INCH*4+mount_off_y, 0)
layout.place_element("Baseplate_Mount_4", optomech.baseplate_mount, layout.INCH*9+mount_off_x, layout.INCH+mount_off_y, 0)

layout.place_element_along_beam("Input_Split", optomech.splitter_mount_c05g, beam_obj=beam, beam_index=0b1, angle=135, distance=25)

layout.place_element_along_beam("Wavemeter_Mirror_1", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=0b11, angle=-45, distance=25)
layout.place_element_along_beam("Wavemeter_Mirror_2", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=0b11, angle=-135, distance=40)
layout.place_element_along_beam("Wavemeter_Coupler", optomech.fiberport_holder, beam_obj=beam, beam_index=0b11, angle=90, y=0)

layout.place_element_along_beam("Input_Rotation_Stage", optomech.rotation_stage_rsp05, beam_obj=beam, beam_index=0b10, angle=0, distance=80)

layout.place_element_along_beam("PBS_1", optomech.pbs_on_skate_mount, beam_obj=beam, beam_index=0b10, angle=0, distance=25)

layout.place_element_along_beam("Probe_Mirror_1", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=0b101, angle=-45, distance=25)
layout.place_element_along_beam("Probe_Mirror_2", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=0b101, angle=-135, distance=40)
layout.place_element_along_beam("Probe_Coupler", optomech.fiberport_holder, beam_obj=beam, beam_index=0b101, angle=90, y=0)

layout.place_element_along_beam("Main_Mirror_1", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=0b100, angle=160, distance=140)
layout.place_element_along_beam("Main_Mirror_2", optomech.mirror_mount_k05s2, beam_obj=beam, beam_index=0b100, angle=-65, distance=35)
layout.place_element_along_beam("Main_Coupler", optomech.fiberport_holder, beam_obj=beam, beam_index=0b100, angle=90, y=0)

layout.redraw()