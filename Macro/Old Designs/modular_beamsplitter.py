import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

gap = 0.25*INCH
base_dx = 4*INCH-gap
base_dy = 7.5*INCH-gap
base_dz = INCH

base_split = INCH/4

ddx = INCH
ddy = 1.5*INCH

aom_dy = 70

input_y = base_dy-2*INCH+gap/2
input_y2 = base_dy-1*INCH+gap/2


''' 'Cardinal' beam directions'''
left = -90
right = left + 180
up = 180
down = up - 180 

# Turns
up_right = 45
right_up = up_right-180
left_down = up_right
down_left = right_up
left_up = up_right +90
up_left = left_up-180
right_down = up_left


layout.create_baseplate(base_dx, base_dy, base_dz, name="Modular_Splitter_Baseplate")

beam = layout.add_beam_path(base_dx, input_y, -180)

# layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_mk05, beam, 0b1, up_right, 25, uMountParam=[(20, 28, 10), (-10, 0)])
layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_km05, beam, 0b1, up_right, INCH)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_km05, beam, 0b1, right_up, INCH)

layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, up, 20)
layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, up, 20)

layout.place_element_along_beam("f_50_Input_Lens", optomech.lens_holder_l05g, beam, 0b11, left, 40)
layout.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam, 0b11, left, 50, diff_angle=0)
layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_km05, beam, 0b11, left_down, 25)
layout.place_element_along_beam("f_50_Output_Lens", optomech.lens_holder_l05g, beam, 0b11, down, 25)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_km05, beam, 0b11, down_left, 15)
layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b11, left, 20)
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11, left, 15)
layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b11, right, y=0)

layout.place_element("Mount_Hole", optomech.baseplate_mount, (1-0.5)*INCH-gap/2, (1-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (1-0.5)*INCH-gap/2, (7-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (4-0.5)*INCH-gap/2, (5-0.5)*INCH-gap/2, 0)

# for x in range(7):
# 	for y in range(11):
# 		layout.place_element("Mount_Hole", optomech.baseplate_mount, (x-0.5)*INCH-gap/2, (y-0.5)*INCH-gap/2, 0)


layout.redraw()