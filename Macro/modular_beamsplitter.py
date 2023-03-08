import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

base_dx = 4.25*INCH
base_dy = 7.25*INCH
base_dz = INCH

base_split = INCH/4

ddx = INCH
ddy = 1.5*INCH

aom_dy = 70

input_y = base_dy-50

layout.create_baseplate(base_dx, base_dy, base_dz, name="AOM_Splitter_Baseplate")

beam = layout.add_beam_path(base_dx, input_y, -180)

layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_mk05, beam, 0b1, 45, 25, uMountParam=[(20, 28, 10), (-10, 0)])
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, -135, INCH)

layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, 180, 20)
layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, 180, 20)

layout.place_element_along_beam("f_50_Input_Lens", optomech.lens_holder_l05g, beam, 0b11, -90, 40)
layout.place_element_along_beam("AOM_R2", optomech.isomet_1205c_on_km100pm, beam, 0b11, -90, 50)
layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b11, 45-3, 25)
layout.place_element_along_beam("f_50_Output_Lens", optomech.lens_holder_l05g, beam, 0b11, 0, 25)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b11, -135, 20)
layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b11, -90, 20)
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11, -90, 15)
layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b11, 90, y=0)

layout.redraw()