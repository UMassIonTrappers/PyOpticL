from freecadOptics import layout, optomech

from math import *
import datetime
from datetime import datetime

INCH = 25.4
base_split = INCH/4

split_dx = 86
input_x = 6.5*INCH

name = "Doublepass_Resin"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

base_dx = 10*INCH
base_dy = 5*INCH
base_dz = INCH

gap = INCH/8

mirror_mounts = optomech.mirror_mount_km05
#layout.create_baseplate(split_dx-gap/4, base_dy, base_dz, name=name+'1', label=label)
#layout.create_baseplate(base_dx-split_dx-gap/4, base_dy, base_dz, x=split_dx+gap/4, name=name+'2', label=label)

def modular_double_pass(x=0, y=0):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, gap=gap, name=name, x=x, y=y) # Full plate

    beam = baseplate.add_beam_path(input_x, gap, layout.cardinal['up'])

    baseplate.place_element("Input_Fiberport", optomech.fiberport_holder, input_x, gap, layout.cardinal['up'])
    baseplate.place_element_along_beam("Input_Mirror_1", mirror_mounts, beam, 0b1, layout.turn['up-right'], 18)
    baseplate.place_element_along_beam("Input_Mirror_2", mirror_mounts, beam, 0b1, layout.turn['right-up'],  INCH)
    baseplate.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, layout.cardinal['up'], 55, wave_plate_part_num = '') #421nm custom waveplates from CASIX
    baseplate.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, layout.cardinal['right'], 27, invert=True)

    #baseplate.place_element_along_beam("Lens_f_30mm", optomech.lens_holder_l05g, beam, 0b11, layout.cardinal['right'], 10, foc_len=30)
    baseplate.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam, 0b11, layout.cardinal['right'], 35,  forward_direction=-1, backward_direction=1)
    baseplate.place_element_along_beam("Quarter_waveplate", optomech.rotation_stage_rsp05, beam, 0b110, layout.cardinal['left'], 74, wave_plate_part_num = '') #421nm custom waveplates from CASIX
    lens = baseplate.place_element_along_beam("Lens_f_100mm_AB_coat", optomech.lens_holder_l05g, beam, 0b110, layout.cardinal['left'], 26, lens_args=dict(focal_length=100, part_number='LA1213-AB'))
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b111, layout.cardinal['right'], 7, pre_refs=2, adapter_args=dict(drill_offset=-2))
    baseplate.place_element_relative("Retro_Mirror", mirror_mounts, lens, layout.cardinal['right'], -30)

    baseplate.place_element_along_beam("Output_Mirror_1", mirror_mounts, beam, 0b11110, layout.turn['right-down'], 30)
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11110, layout.cardinal['down'], 45)
    baseplate.place_element_along_beam("Output_Mirror_2", mirror_mounts, beam, 0b11110, layout.turn['down-left'], 13)
    baseplate.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b11110, layout.cardinal['left'], 100, wave_plate_part_num = '') #421nm custom waveplates from CASIX
    baseplate.place_element_along_beam("Optional_Fiberport", optomech.fiberport_mount_km05, beam, 0b11110, layout.cardinal['right'], x=40, optional=True)
    baseplate.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b11110, layout.cardinal['right'], x=gap)

modular_double_pass()

layout.redraw()