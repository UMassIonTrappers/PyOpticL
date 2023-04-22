import FreeCAD as App
import FreeCADGui as Gui
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
from math import *
import os
import datetime
from datetime import datetime

reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

aom_dy = 70
base_split = INCH/4

gap = 0.5*INCH
base_dx = 8.0*INCH+10-gap #MAX size of resin printer
base_dy = 5.0*INCH-gap
base_dz = INCH

input_x = base_dx-3.0*INCH+gap/2+5

''' 'Cardinal' beam directions'''
down = -90 
up = down+ 180
left = down - 90
right = left + 180

# Turns
up_right = -45
right_up = up_right-180
left_down = up_right
down_left = right_up
left_up = up_right +90
up_left = left_up-180
right_down = up_left


"""
Start BASEPLATE
"""

name = "Doublepass_Resin"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time
print("label name date and time:",label)
layout.create_baseplate(base_dx, base_dy, base_dz, name=name, label=label)


'''
Add Beam(s)
'''
beam = layout.add_beam_path(input_x, 0, up)

"""
Add Optical Elements
"""
mirror_mounts = optomech.mirror_mount_km05
layout.place_element_along_beam("Input_Mirror_1", mirror_mounts, beam, 0b1, up_right, 16)
layout.place_element_along_beam("Input_Mirror_2", mirror_mounts, beam, 0b1, right_up,  INCH)
layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, up, 55, wave_plate_part_num = '') #421nm custom waveplates from CASIX
layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, up, 25)

layout.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam, 0b11, right, 30,  diff_dir=(1,-1), exp=True)
layout.place_element_along_beam("Quarter_waveplate", optomech.rotation_stage_rsp05, beam, 0b110, left, 70, wave_plate_part_num = '') #421nm custom waveplates from CASIX
lens = layout.place_element_along_beam("Lens_f_100mm_AB_coat", optomech.lens_holder_l05g, beam, 0b110, left, 30, foc_len=100, lens_part_num='LA1213-AB')
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b111, right, 7, pre_refs=2, drill_offset=2)
layout.place_element_relative("Retro_Mirror", mirror_mounts, lens, right, -7)

layout.place_element_along_beam("Output_Mirror_1", mirror_mounts, beam, 0b11110, right_down, 25)
layout.place_element_along_beam("Output_Mirror_2", mirror_mounts, beam, 0b11110, down_left, 55)
layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b11110, left, 100, wave_plate_part_num = '') #421nm custom waveplates from CASIX
layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b11110, right, x=0)


"""
Add holes to baseplate to mount to optical table 
 >>> Make sure to align laser beam above bolt holes so plates line up together <<<
"""
offset = -15/INCH # arbitrary shift to make sure laser is over bolt holes
for i in [[1,0],[3,3],[4,1],[7,2]]:
    layout.place_element("Mount_Hole", optomech.baseplate_mount, (i[0]-offset)*INCH-gap/2, (i[1]-offset)*INCH-gap/2, 0)

"""
Set view and compute baseplate
"""
#Gui.runCommand('TopViewFit',0)
layout.redraw()