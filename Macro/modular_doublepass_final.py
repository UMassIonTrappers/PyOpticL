from freecadOptics import layout, optomech

from math import *
import datetime
from datetime import datetime

INCH = 25.4
aom_dy = 70
base_split = INCH/4
gap = 0.5*INCH
base_dx = 10.0*INCH-gap
base_dy = 5.15*INCH-gap
base_dz = INCH
split_dx = 86
grid_offset = INCH/2
input_x = 6*INCH+grid_offset

name = "Doublepass_Resin"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

#layout.create_baseplate(base_dx, base_dy, base_dz, name=name, label=label) # Full plate
layout.create_baseplate(split_dx-gap/4, base_dy, base_dz, name=name+'1', label=label)
layout.create_baseplate(base_dx-split_dx-gap/4, base_dy, base_dz, x=split_dx+gap/4, name=name+'2', label=label)

beam = layout.add_beam_path(input_x, 0, layout.cardinal['up'])

mirror_mounts = optomech.mirror_mount_km05
layout.place_element("Input_Fiberport", optomech.fiberport_holder, input_x, 0, layout.cardinal['up'])
layout.place_element_along_beam("Input_Mirror_1", mirror_mounts, beam, 0b1, layout.turn['up-right'], 18)
layout.place_element_along_beam("Input_Mirror_2", mirror_mounts, beam, 0b1, layout.turn['right-up'],  INCH)
layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, layout.cardinal['up'], 55, wave_plate_part_num = '') #421nm custom waveplates from CASIX
layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, layout.cardinal['right'], 27, invert=True)

layout.place_element_along_beam("Lens_f_30mm", optomech.lens_holder_l05g, beam, 0b11, layout.cardinal['right'], 10, foc_len=30)
layout.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam, 0b11, layout.cardinal['right'], 30,  diff_dir=(-1,1), exp=True)
layout.place_element_along_beam("Quarter_waveplate", optomech.rotation_stage_rsp05, beam, 0b110, layout.cardinal['left'], 74, wave_plate_part_num = '') #421nm custom waveplates from CASIX
lens = layout.place_element_along_beam("Lens_f_100mm_AB_coat", optomech.lens_holder_l05g, beam, 0b110, layout.cardinal['left'], 26, foc_len=100, lens_part_num='LA1213-AB')
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b111, layout.cardinal['right'], 7, pre_refs=2, drill_offset=-2)
layout.place_element_relative("Retro_Mirror", mirror_mounts, lens, layout.cardinal['right'], -30)

layout.place_element_along_beam("Output_Mirror_1", mirror_mounts, beam, 0b11110, layout.turn['right-down'], 25)
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11110, layout.cardinal['down'], 45)
layout.place_element_along_beam("Output_Mirror_2", mirror_mounts, beam, 0b11110, layout.turn['down-left'], 13)
layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b11110, layout.cardinal['left'], 100, wave_plate_part_num = '') #421nm custom waveplates from CASIX
layout.place_element_along_beam("Optional_Fiberport", optomech.fiberport_mount_km05, beam, 0b11110, layout.cardinal['right'], x=25, optional=True)
layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b11110, layout.cardinal['right'], x=0)

for i in [[0,0],[0,2],[7,1],[8,3]]:
    layout.place_element("Mount_Hole%s"%(str(i)), optomech.baseplate_mount, (i[0])*INCH+grid_offset, (i[1])*INCH+grid_offset, 0)

for i in [[2,0],[2,2],[4,0],[5,1]]:
    layout.place_element("Mount_Hole%s"%(str(i)), optomech.baseplate_mount, (i[0])*INCH+grid_offset, (i[1])*INCH+grid_offset, 0)

layout.redraw()