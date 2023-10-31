# Jacob Myers, Ryland Yurow, Chris Caron - 10/20/23

from PyOptic import layout, optomech
from datetime import datetime

name = "Rb SAS"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

base_dx = 14*layout.inch
base_dy = 4*layout.inch
base_dz = layout.inch
gap = layout.inch/8

mount_holes = [(1,0), (0, 3), (6, 3), (7, 0), (13, 0), (13, 3)]

def Rb_SAS(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, name=name, label=label, mount_holes=mount_holes, x_split=base_dx/2)

    beam = baseplate.add_beam_path(x=base_dx-2.5*layout.inch, y=0, angle=90)

    baseplate.place_element_along_beam("input_mirror_1", mirror, beam,
                                       beam_index=0b1, distance=1.25*layout.inch, angle=layout.turn['up-right'])
    baseplate.place_element_along_beam("input_mirror_2", mirror, beam,
                                       beam_index=0b1, distance=1*layout.inch, angle=layout.turn['right-up'])

    baseplate.place_element_along_beam("Half_waveplate_1", optomech.rotation_stage_rsp05, beam,
                                       beam_index=0b1, distance=1*layout.inch, angle=layout.cardinal['up'])
    baseplate.place_element_along_beam("Beam_Splitter_1", optomech.pbs_on_skate_mount, beam,
                                       beam_index=0b1, distance=0.75*layout.inch, angle=layout.cardinal['up'])

    baseplate.place_element_along_beam("probe_mirror_1", mirror, beam,
                                       beam_index=0b11, distance=3*layout.inch, angle=layout.turn['left-down'])
    baseplate.place_element_along_beam("probe_mirror_2", mirror, beam,
                                       beam_index=0b11, distance=1.5*layout.inch, angle=layout.turn['down-left'])
    baseplate.place_element_along_beam("Half_waveplate_probe", optomech.rotation_stage_rsp05, beam,
                                       beam_index=0b11, distance=1*layout.inch, angle=layout.cardinal['left'])

    baseplate.place_element_along_beam("splitter", optomech.splitter_mount_b05g, beam,
                                       beam_index=0b11, distance=1*layout.inch, angle=layout.turn['left-up'])

    baseplate.place_element_along_beam("Rb_gas_cell", optomech.rb_cell, beam,
                                       beam_index=0b110, distance=2.75*layout.inch, angle=layout.cardinal['left'])

    baseplate.place_element_along_beam("Beam_Splitter_2", optomech.pbs_on_skate_mount, beam,
                                       beam_index=0b110, distance=2.75*layout.inch, angle=layout.cardinal['left'],
                                       invert=True)

    baseplate.place_element_along_beam("Photodetector", optomech.photodetector_pda10a2, beam,
                                       beam_index=0b1100, distance=0.75*layout.inch, angle=layout.cardinal['right'])

    baseplate.place_element_along_beam("pump_mirror_1", mirror, beam,
                                       beam_index=0b111, distance=1.5*layout.inch, angle=layout.turn['up-left'])
    baseplate.place_element_along_beam("Half_waveplate_pump", optomech.rotation_stage_rsp05, beam,
                                       beam_index=0b111, distance=2.5*layout.inch, angle=layout.cardinal['left'],
                                       invert=True)
    baseplate.place_element_along_beam("pump_mirror_2", mirror, beam,
                                       beam_index=0b111, distance=3*layout.inch, angle=layout.turn['left-down'])

if __name__ == "__main__":
    Rb_SAS()
    layout.redraw()