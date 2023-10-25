# Chris Caron & Ryland Yurow - 10/20/23

from freecadOptics import layout, optomech
from math import *
import datetime
from datetime import datetime

INCH = 25.4

gap = 0.25*INCH
base_dx = 8*INCH-gap
base_dy = 7*INCH-gap
base_dz = INCH

name = "Rb SAS - MWE"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

layout.create_baseplate(base_dx, base_dy, base_dz, name=name, label=label)
beam = layout.add_beam_path(base_dx -1.5*INCH - 0.5*INCH, 0, 90)

mirror = optomech.mirror_mount_km05
fiberport = optomech.fiberport_holder
splitter = optomech.splitter_mount_c05g
fiberport = optomech.fiberport_holder
mirror2 = optomech.mirror_mount_c05g

# Input mirrors
layout.place_element_along_beam("input_mirror_1", mirror, beam, 0b1, layout.turn['up-right'], 1 * INCH)
layout.place_element_along_beam("input_mirror_2", mirror, beam, 0b1, layout.turn['right-up'], 1 * INCH)

# Add HWP and PBS for pickoff
layout.place_element_along_beam("Half_waveplate_1", optomech.rotation_stage_rsp05, beam, 0b1, layout.cardinal['up'], 1 * INCH)
layout.place_element_along_beam("Beam_Splitter_1", optomech.pbs_on_skate_mount, beam, 0b1, layout.cardinal['up'], 0.5 * INCH)

# Probe mirrors
layout.place_element_along_beam("probe_mirror_1", mirror, beam, 0b11, layout.turn['left-up'], 2 * INCH)
layout.place_element_along_beam("probe_mirror_2", mirror, beam, 0b11, layout.turn['up-left'], 3.5 * INCH)

# Splitter
layout.place_element_along_beam("splitter", optomech.splitter_mount_c05g, beam, 0b11, layout.turn['left-down'], 2.5 * INCH)

# Rb Cell
layout.place_element_along_beam("Rb_gas_cell", optomech.rb_cell, beam, 0b111, layout.cardinal['down'], 2.5 * INCH)

#PBS (by doing this one at 2.5 inches, FreeCad breaks?)
layout.place_element_along_beam("Beam_Splitter_2", optomech.pbs_on_skate_mount, beam, 0b111, layout.cardinal['down'], 3 * INCH)

#extra mirror to unbreak FreeCad?
layout.place_element_along_beam("extra_mirror_1", mirror, beam, 0b1111, layout.turn['right-down'], 1.5 * INCH)

#TODO: ADD PHOTODIODE!

# Pump mirrors
layout.place_element_along_beam("pump_mirror_1", mirror, beam, 0b110, layout.turn['left-down'], 1.5 * INCH)
layout.place_element_along_beam("pump_mirror_2", mirror, beam, 0b110, layout.turn['down-right'], 5 * INCH)

# Output mirrors
layout.place_element_along_beam("output_mirror_1", mirror, beam, 0b10, layout.turn['up-left'], 2 * INCH)
layout.place_element_along_beam("output_mirror_2", mirror, beam, 0b10, layout.turn['left-up'], 1 * INCH)

layout.redraw()
