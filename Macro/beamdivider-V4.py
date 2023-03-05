import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

base_dx = 5*INCH
base_dy = 12*INCH
base_dz = INCH

base_split = INCH/4

ddx = INCH
ddy = 1.5*INCH

aom_dy = 70

input_y = base_dy-35
CC_out_d = 60
R1_out_d = 45
CC_out_dy = 0.5*(aom_dy+(CC_out_d-R1_out_d)*(math.cos(math.pi/30)-math.sin(math.pi/30)-1))
R1_out_dy = aom_dy-CC_out_dy-(CC_out_d-R1_out_d)*math.sin(math.pi/30)


layout.create_baseplate(base_dx, base_dy, base_dz, name="AOM_Splitter_Baseplate")
layout.create_baseplate(base_dx, base_dy, base_dz, name="AOM_Output_Baseplate", x=base_dx+base_split)

beam = layout.add_beam_path(base_dx*2+base_split, input_y, -180)

layout.place_element("Input_Fiberport", optomech.fiberport_holder, base_dx*2+base_split, input_y, 180)
layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, 45, 55)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, -135, 15)

layout.place_element_along_beam("Filter_Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, 90, x=50)
layout.place_element_along_beam("Input_Split", optomech.splitter_mount_c05g, beam, 0b10, -45, 30)

layout.place_element_along_beam("f_300_Input_Lens", optomech.lens_holder_l05g, beam, 0b101, -90, 30)

layout.place_element_along_beam("Half_waveplate_R2", optomech.rotation_stage_rsp05, beam, 0b101, -90, 210-aom_dy*7/4)
layout.place_element_along_beam("Beam_Splitter_R2", optomech.pbs_on_skate_mount, beam, 0b101, -90, aom_dy/4)

layout.place_element_along_beam("Input_Mirror_R2_1", optomech.mirror_mount_c05g, beam, 0b1011, 135, 45)
layout.place_element_along_beam("Input_Mirror_R2_2", optomech.mirror_mount_c05g, beam, 0b1011, -45, aom_dy*3/2)
layout.place_element_along_beam("AOM_R2", optomech.isomet_1205c_on_km100pm, beam, 0b1011, 0, 45)
layout.place_element_along_beam("Output_Mirror_R2_1", optomech.mirror_mount_k05s2, beam, 0b1011, -135-3, 45)
layout.place_element_along_beam("Output_Mirror_R2_2", optomech.mirror_mount_k05s2, beam, 0b1011, 45, 10)
layout.place_element_along_beam("Output_Mirror_R2_3", optomech.mirror_mount_c05g, beam, 0b1011, -135, 57.5)
layout.place_element_along_beam("f_300_R2_Output_Lens", optomech.lens_holder_l05g, beam, 0b1011, -90, 182.5)
layout.place_element_along_beam("Output_Mirror_R2_4", optomech.mirror_mount_c05g, beam, 0b1011, 45, 15)
layout.place_element_along_beam("Half_waveplate_R2_Out", optomech.rotation_stage_rsp05, beam, 0b1011, 0, 27.5)
layout.place_element_along_beam("Iris_R2", optomech.pinhole_ida12, beam, 0b1011, 0, 15)
layout.place_element_along_beam("Output_Fiberport_R2", optomech.fiberport_holder, beam, 0b1011, 180, x=base_dx*2+base_split)

layout.place_element_along_beam("Half_waveplate_R4", optomech.rotation_stage_rsp05, beam, 0b1010, -90, aom_dy/4)
layout.place_element_along_beam("Beam_Splitter_R4", optomech.pbs_on_skate_mount, beam, 0b1010, -90, aom_dy/4)

layout.place_element_along_beam("Input_Mirror_R4_1", optomech.mirror_mount_c05g, beam, 0b10101, 135, 20)
layout.place_element_along_beam("Input_Mirror_R4_2", optomech.mirror_mount_c05g, beam, 0b10101, -45, aom_dy)
layout.place_element_along_beam("AOM_R4", optomech.isomet_1205c_on_km100pm, beam, 0b10101, 0, 70)
layout.place_element_along_beam("Output_Mirror_R4_1", optomech.mirror_mount_k05s2, beam, 0b10101, -135-3, 45)
layout.place_element_along_beam("Output_Mirror_R4_2", optomech.mirror_mount_k05s2, beam, 0b10101, 45, 20)
layout.place_element_along_beam("Output_Mirror_R4_3", optomech.mirror_mount_c05g, beam, 0b10101, 135, 25)
layout.place_element_along_beam("Output_Mirror_R4_4", optomech.mirror_mount_c05g, beam, 0b10101, -45, 60)
layout.place_element_along_beam("Output_Mirror_R4_5", optomech.mirror_mount_c05g, beam, 0b10101, -135, 45)
layout.place_element_along_beam("f_300_R3_Output_Lens", optomech.lens_holder_l05g, beam, 0b10101, -90, 100)
layout.place_element_along_beam("Output_Mirror_R4_6", optomech.mirror_mount_c05g, beam, 0b10101, 45, 20)
layout.place_element_along_beam("Half_waveplate_R4_Out", optomech.rotation_stage_rsp05, beam, 0b10101, 0, 15)
layout.place_element_along_beam("Iris_R4", optomech.pinhole_ida12, beam, 0b10101, 0, 15)
layout.place_element_along_beam("Output_Fiberport_R4", optomech.fiberport_holder, beam, 0b10101, 180, x=base_dx*2+base_split)

layout.place_element_along_beam("Half_waveplate_CC", optomech.rotation_stage_rsp05, beam, 0b10100, -90, aom_dy/4)
layout.place_element_along_beam("Beam_Splitter_CC", optomech.pbs_on_skate_mount, beam, 0b10100, -90, aom_dy/4)

layout.place_element_along_beam("Input_Mirror_CC_1", optomech.mirror_mount_c05g, beam, 0b101001, 135, 45)
layout.place_element_along_beam("Input_Mirror_CC_2", optomech.mirror_mount_c05g, beam, 0b101001, -45, aom_dy/2)
layout.place_element_along_beam("AOM_CC", optomech.isomet_1205c_on_km100pm, beam, 0b101001, 0, 45)
layout.place_element_along_beam("Output_Mirror_CC_1", optomech.mirror_mount_k05s2, beam, 0b101001, -135-3, CC_out_d)

layout.place_element_along_beam("Half_waveplate_R1", optomech.rotation_stage_rsp05, beam, 0b101000, -90, aom_dy/4)
layout.place_element_along_beam("Input_Mirror_R1", optomech.mirror_mount_c05g, beam, 0b101000, 45, aom_dy/4)
layout.place_element_along_beam("AOM_R1", optomech.isomet_1205c_on_km100pm, beam, 0b101000, 0, 90)
layout.place_element_along_beam("Output_Mirror_R1_1", optomech.mirror_mount_k05s2, beam, 0b101000, 135-3, R1_out_d)
layout.place_element_along_beam("Output_Mirror_R1_2", optomech.mirror_mount_k05s2, beam, 0b101000, -45, R1_out_dy)

layout.place_element_along_beam("Beam_Splitter_CC_R1", optomech.pbs_on_skate_mount, beam, 0b101001, 0, CC_out_dy, invert=True)
layout.place_element_along_beam("Output_Mirror_CC_R1_1", optomech.mirror_mount_c05g, beam, 0b1010011, -135, 15)
layout.place_element_along_beam("Output_Mirror_CC_R1_2", optomech.mirror_mount_c05g, beam, 0b1010011, 45, 55)
layout.place_element_along_beam("Output_Mirror_CC_R1_3", optomech.mirror_mount_c05g, beam, 0b1010011, 135, 15)
layout.place_element_along_beam("f_300_R3_Output_Lens", optomech.lens_holder_l05g, beam, 0b1010011, 90, 215-CC_out_d-CC_out_dy)
layout.place_element_along_beam("Output_Mirror_CC_R1_4", optomech.mirror_mount_c05g, beam, 0b1010011, -45, 60)
layout.place_element_along_beam("Half_waveplate_CC_R1_Out", optomech.rotation_stage_rsp05, beam, 0b1010011, 0, 40)
layout.place_element_along_beam("Iris_R2", optomech.pinhole_ida12, beam, 0b1010011, 0, 15)
layout.place_element_along_beam("Output_Fiberport_CC_R1", optomech.fiberport_holder, beam, 0b1010011, 180, x=base_dx*2+base_split)

layout.redraw()