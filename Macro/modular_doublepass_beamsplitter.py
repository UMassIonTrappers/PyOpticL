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

input_offset = 80

input_y = base_dy-input_offset

vert = -90
horz = 180 

layout.create_baseplate(base_dx, base_dy, base_dz, name="AOM_Splitter_Baseplate")

beam = layout.add_beam_path(base_dx, input_y, -180)

layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, 45, 15)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, -135, INCH)

layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, horz, 60)
layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, horz, 25)

layout.place_element_along_beam("AOM_R2", optomech.isomet_1205c_on_km100pm_doublepass, beam, 0b11, -vert, 35)

layout.place_element_along_beam("Quarter_waveplate", optomech.rotation_stage_rsp05, beam, 0b11, -90, 70)

layout.place_element_along_beam("f_100_Collimation_Lens", optomech.lens_holder_l05g, beam, 0b11, vert, 30)

layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11, vert, 15)

layout.place_element_along_beam("Retro_Mirror", optomech.mirror_mount_k05s2, beam, 0b11, -vert, 15)

layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b110, -45, 30)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b110, -45-90, 60)


layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b110, vert, 150)
layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b110, vert, 30)

layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b110, 90, y=0)


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