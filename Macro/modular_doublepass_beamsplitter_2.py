import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
from math import *

reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

gap = 0.25*INCH
base_dx = 5*INCH-gap
base_dy = 10*INCH-gap
base_dz = INCH

base_split = INCH/4

ddx = INCH
ddy = 1.5*INCH

aom_dy = 70

input_offset = 80

input_y = base_dy-input_offset


left = -90
right = left + 180
up = 180
down = up - 180 
up_right = 45
right_up = up_right-180
left_down = up_right
down_left = right_up
left_up = 135
up_left = left_up-180
right_down = up_left

layout.create_baseplate(base_dx, base_dy, base_dz, name="AOM_Splitter_Baseplate")

beam = layout.add_beam_path(base_dx, input_y, -180)
#aom_beam_plus1 = layout.add_beam_path(INCH, input_y-10, left-0.026*180/pi)  #https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf
#aom_beam_minus1 = layout.add_beam_path(INCH, input_y-10, left+0.026*180/pi)  #https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf
#aom_beam_plus2 = layout.add_beam_path(INCH, input_y-10, right+0.026*180/pi)  #https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf
#aom_beam_minus2 = layout.add_beam_path(INCH, input_y-10, right-0.026*180/pi)  #https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf


layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, up_right, 15)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, right_up, INCH)

layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, up, 55)
layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, up, x=25)

layout.place_element_along_beam("AOM_R2", optomech.isomet_1205c_on_km100pm, beam, 0b11, right, 35, diff_dir=(-1,1))
layout.place_element("Quarter_waveplate", optomech.rotation_stage_rsp05, 25, input_y+INCH-35-70, left)
layout.place_element("f_100_Collimation_Lens", optomech.lens_holder_l05g, 25, input_y+INCH-35-100, left, foc_len=100)
layout.place_element("Iris", optomech.pinhole_ida12, 25, input_y+INCH-35-100-15, right)
layout.place_element("Retro_Mirror", optomech.mirror_mount_k05s2, 25, input_y+INCH-35-100-30, right)

layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b110, right_down, 30)
# layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b110, down, 25)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b110, down_left, 50)


layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b110, left, 150)

layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b110, right, y=0)


layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-0.5)*INCH-gap/2, (1-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (3-0.5)*INCH-gap/2, (1-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-0.5)*INCH-gap/2, (10-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (2-0.5)*INCH-gap/2, (10-0.5)*INCH-gap/2, 0)
# layout.place_element("Mount_Hole", optomech.baseplate_mount, (3-0.5)*INCH-gap/2, (3-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-0.5)*INCH-gap/2, (5-0.5)*INCH-gap/2, 0)

# for x in range(7):
# 	for y in range(11):
# 		layout.place_element("Mount_Hole", optomech.baseplate_mount, (x-0.5)*INCH-gap/2, (y-0.5)*INCH-gap/2, 0)


# layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, 45, 25)


# layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b11, -135, 20)
# layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b11, -90, 20)
# layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11, -90, 15)
# layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b11, 90, y=0)

layout.redraw()