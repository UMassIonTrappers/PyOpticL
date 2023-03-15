import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
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

input_offset = 1*INCH

input_y = base_dy-input_offset

left = -90
right = left + 180
up = 180 
up_right = 45
right_up = -135
left_down = up_right
left_up = 135
up_left = left_up-180

layout.create_baseplate(base_dx, base_dy, base_dz, name="AOM_Noise_eater_Baseplate")

beam = layout.add_beam_path(base_dx, input_y, -180)
exit_beam = layout.add_beam_path(0, input_y, 0)



layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, up_left, 20)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_c05g, beam, 0b1, left_up-0*45/2, 20)
layout.place_element_along_beam("Input_Mirror_3", optomech.mirror_mount_k05s2, beam, 0b1, up_left-0*45/2, 25)

# layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, up, 30)
# layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, up, 30)

# layout.place_element_along_beam("f_50_Input_Lens", optomech.lens_holder_l05g, beam, 0b11, left, 40)
layout.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm_doublepass, beam, 0b1, left, 55)

layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b1, left, 80)

layout.place_element_along_beam("Pick_off", optomech.splitter_mount_c05g, beam, 0b1, left_up, 20)
layout.place_element_along_beam("PD_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b11, up_left, 20)

layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b10, left_up, 25)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b10, up_right, 55)
layout.place_element_along_beam("Output_Mirror_3", optomech.mirror_mount_k05s2, beam, 0b10, right_up, 200)
# layout.place_element("Output_Mirror_3_fixed", optomech.mirror_mount_k05s2, 0.5*INCH, 9*INCH, right_up)

# layout.place_element_along_beam("f_50_Output_Lens", optomech.lens_holder_l05g, beam, 0b11, 0, 25)
# layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b11, -135, 20)
# layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b11, -90, 20)
# layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11, -90, 15)
# layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b11, 90, y=0)


layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-0.5)*INCH-gap/2, (1-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (1-0.5)*INCH-gap/2, (2-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-0.5)*INCH-gap/2, (10-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (1-0.5)*INCH-gap/2, (10-0.5)*INCH-gap/2, 0)
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