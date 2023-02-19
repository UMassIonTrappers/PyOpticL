import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

base_dx = 12*INCH
base_dy = 12*INCH
base_dz = INCH

ddx = INCH
ddy = 1.5*INCH


layout.create_baseplate(base_dx, base_dy, base_dz)

# Offsets from table grid and positions for mounting holes
xoff = INCH/2
yoff = INCH/2

mount_holes = [[0*INCH, 0*INCH],
               [base_dx-INCH, 0*INCH],
               [base_dx-INCH, base_dy-INCH],
               [0*INCH, base_dy-INCH]]

for xy in mount_holes:
	layout.place_element("Screw_hole_baseplate", optomech.baseplate_mount, xoff+xy[0], yoff+xy[1], 0)

input_x = INCH

beam = layout.add_beam_path(input_x, base_dy, -90)

layout.place_element("Input_Fiberport", optomech.fiberport_holder, input_x, base_dy, -90)

layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, 45, 30)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, -135, 20)

layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, -90, 30)
layout.place_element_along_beam("Beam_Splitter_1", optomech.pbs_on_skate_mount, beam, 0b1, -90, 30)

layout.place_element_along_beam("AOM_1", optomech.isomet_1205c_on_km100pm, beam, 0b11, 0, 220)
layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b11, -135-3, 20)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b11, 45, 40)
#layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b11, 0, x=0)

layout.place_element_along_beam("Half_waveplate_2", optomech.rotation_stage_rsp05, beam, 0b10, -90, 30)
layout.place_element_along_beam("Beam_Splitter_2", optomech.pbs_on_skate_mount, beam, 0b10, -90, 30)

layout.place_element_along_beam("AOM_2", optomech.isomet_1205c_on_km100pm, beam, 0b101, 0, 140)
layout.place_element_along_beam("Output_2_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b101, -135-3, 20)
layout.place_element_along_beam("Output_2_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b101, 45, 40)
#layout.place_element_along_beam("Output_Fiberport_2", optomech.fiberport_holder, beam, 0b101, 0, x=0)

layout.place_element_along_beam("Half_waveplate_3", optomech.rotation_stage_rsp05, beam, 0b100, -90, 30)
layout.place_element_along_beam("Beam_Splitter_3", optomech.pbs_on_skate_mount, beam, 0b100, -90, 30)

layout.place_element_along_beam("AOM_3", optomech.isomet_1205c_on_km100pm, beam, 0b1001, 0, 80)
layout.place_element_along_beam("Output_3_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1001, -135-3, 20)
layout.place_element_along_beam("Output_3_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1001, 45, 40)
#layout.place_element_along_beam("Output_Fiberport_3", optomech.fiberport_holder, beam, 0b1001, 0, x=0)

layout.place_element_along_beam("AOM_4", optomech.isomet_1205c_on_km100pm, beam, 0b1000, -90, 80)
layout.place_element_along_beam("Output_4_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1000, 45-3, 20)

layout.redraw()