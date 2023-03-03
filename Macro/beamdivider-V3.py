import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

base_dx = 10*INCH
base_dy = 14*INCH
base_dz = INCH

ddx = INCH
ddy = 1.5*INCH

layout.create_baseplate(base_dx, base_dy, base_dz, False)

input_y = base_dy-1.5*INCH
CC_out_d = 15
R1_out_d = 35
CC_out_dy = 0.5*(80+(R1_out_d-CC_out_d)*(1+math.sin(math.pi/30)-math.cos(math.pi/30))-CC_out_d)
R1_out_dy = 80-CC_out_dy+(R1_out_d-CC_out_d)*math.sin(math.pi/30)

beam = layout.add_beam_path(base_dx, input_y, -180)

layout.place_element("Input_Fiberport", optomech.fiberport_holder, base_dx, input_y, 180)

layout.place_element_along_beam("Filter_Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, 90, base_dx-50)
layout.place_element_along_beam("Input_Split", optomech.splitter_mount_c05g, beam, 0b10, -45, 30)

layout.place_element_along_beam("f_300_Input_Lens", optomech.lens_holder_l05g, beam, 0b101, -90, 75)

layout.place_element_along_beam("Half_waveplate_R2", optomech.rotation_stage_rsp05, beam, 0b101, -90, 60)
layout.place_element_along_beam("Beam_Splitter_R2", optomech.pbs_on_skate_mount, beam, 0b101, -90, 20)

layout.place_element_along_beam("Input_Mirror_R2_1", optomech.mirror_mount_c05g, beam, 0b1011, 135, 40)
layout.place_element_along_beam("Input_Mirror_R2_2", optomech.mirror_mount_c05g, beam, 0b1011, -45, 120)
layout.place_element_along_beam("AOM_R2", optomech.isomet_1205c_on_km100pm, beam, 0b1011, 0, 60)
layout.place_element_along_beam("Output_Mirror_R2_1", optomech.mirror_mount_c05g, beam, 0b1011, -135-3, 40)
layout.place_element_along_beam("Output_Mirror_R2_2", optomech.mirror_mount_k05s2, beam, 0b1011, 45, 110)
layout.place_element_along_beam("Output_Mirror_R2_3", optomech.mirror_mount_k05s2, beam, 0b1011, -135, 45)
layout.place_element_along_beam("f_300_R2_Output_Lens", optomech.lens_holder_l05g, beam, 0b1011, -90, 105)
layout.place_element_along_beam("Output_Mirror_R2_4", optomech.mirror_mount_c05g, beam, 0b1011, 45, 20)
#layout.place_element_along_beam("Output_Fiberport_R2", optomech.fiberport_holder, beam, 0b1011, 180, x=base_dx)

layout.place_element_along_beam("Half_waveplate_R4", optomech.rotation_stage_rsp05, beam, 0b1010, -90, 20)
layout.place_element_along_beam("Beam_Splitter_R4", optomech.pbs_on_skate_mount, beam, 0b1010, -90, 20)

layout.place_element_along_beam("Input_Mirror_R4_1", optomech.mirror_mount_c05g, beam, 0b10101, 135, 20)
layout.place_element_along_beam("Input_Mirror_R4_2", optomech.mirror_mount_c05g, beam, 0b10101, -45, 80)
layout.place_element_along_beam("AOM_R4", optomech.isomet_1205c_on_km100pm, beam, 0b10101, 0, 80)
layout.place_element_along_beam("Output_Mirror_R4_1", optomech.mirror_mount_c05g, beam, 0b10101, 135-3, 25)
layout.place_element_along_beam("Output_Mirror_R4_2", optomech.mirror_mount_k05s2, beam, 0b10101, -45, 95)
layout.place_element_along_beam("Output_Mirror_R4_3", optomech.mirror_mount_k05s2, beam, 0b10101, -135, 45)
layout.place_element_along_beam("f_300_R3_Output_Lens", optomech.lens_holder_l05g, beam, 0b10101, -90, 150)
layout.place_element_along_beam("Output_Mirror_R4_3", optomech.mirror_mount_c05g, beam, 0b10101, 45, 20)
#layout.place_element_along_beam("Output_Fiberport_R4", optomech.fiberport_holder, beam, 0b10101, 180, x=base_dx)

layout.place_element_along_beam("Half_waveplate_CC", optomech.rotation_stage_rsp05, beam, 0b10100, -90, 20)
layout.place_element_along_beam("Beam_Splitter_CC", optomech.pbs_on_skate_mount, beam, 0b10100, -90, 20)

layout.place_element_along_beam("Input_Mirror_CC_1", optomech.mirror_mount_c05g, beam, 0b101001, 135, 45)
layout.place_element_along_beam("Input_Mirror_CC_2", optomech.mirror_mount_c05g, beam, 0b101001, -45, 40)
layout.place_element_along_beam("AOM_CC", optomech.isomet_1205c_on_km100pm, beam, 0b101001, 0, 55)
layout.place_element_along_beam("Output_Mirror_CC_1", optomech.mirror_mount_c05g, beam, 0b101001, -135-3, CC_out_d)
layout.place_element_along_beam("Output_Mirror_CC_2", optomech.mirror_mount_k05s2, beam, 0b101001, 45, CC_out_dy)
#layout.place_element_along_beam("Output_Fiberport_CC", optomech.fiberport_holder, beam, 0b101001, 180, x=base_dx)

layout.place_element_along_beam("Half_waveplate_R1", optomech.rotation_stage_rsp05, beam, 0b101000, -90, 20)
layout.place_element_along_beam("Input_Mirror_R1", optomech.mirror_mount_c05g, beam, 0b101000, 45, 20)
layout.place_element_along_beam("AOM_R1", optomech.isomet_1205c_on_km100pm, beam, 0b101000, 0, 100)
layout.place_element_along_beam("Output_Mirror_R1", optomech.mirror_mount_k05s2, beam, 0b101000, 135-3, R1_out_d)

layout.place_element_along_beam("Beam_Splitter_CC_R1", optomech.pbs_on_skate_mount, beam, 0b101000, 0, R1_out_dy)
layout.place_element_along_beam("Output_Mirror_CC_R1_1", optomech.mirror_mount_k05s2, beam, 0b1010001, 135, 20)
layout.place_element_along_beam("Output_Mirror_CC_R1_2", optomech.mirror_mount_c05g, beam, 0b1010001, -45, 250-(R1_out_d+R1_out_dy))
layout.place_element_along_beam("Output_Mirror_CC_R1_3", optomech.mirror_mount_c05g, beam, 0b1010001, -135, 30)
layout.place_element_along_beam("f_300_R3_Output_Lens", optomech.lens_holder_l05g, beam, 0b1010001, -90, 20)
layout.place_element_along_beam("Output_Mirror_CC_R1_4", optomech.mirror_mount_c05g, beam, 0b1010001, 45, 20)
#layout.place_element_along_beam("Output_Fiberport_R1", optomech.fiberport_holder, beam, 0b101000, 180, x=base_dx)


layout.redraw()