# Jacob Myers, Ryland Yurow, Chris Caron - 10/20/23

from PyOptic import layout, optomech
from datetime import datetime

name = "Rb SAS"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

base_dx = 16*layout.inch
base_dy = 4*layout.inch
base_dz = layout.inch
gap = layout.inch/8

mount_holes = [(0,0), (3, 2), (0, 3), (3, 3),
               (4, 0), (8, 0), (4, 3), (8, 3),
               (9, 0), (13, 0), (10, 3), (15, 3)]

def Rb_SAS(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, thumbscrews=True):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes,
                                 name=name, label=label, x_splits=[4*layout.inch, 9*layout.inch])

    beam = baseplate.add_beam_path(x=base_dx-2.5*layout.inch, y=0, angle=90)

    baseplate.place_element_along_beam("input mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=30, angle=layout.turn['up-right'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 
    baseplate.place_element_along_beam("input mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=1*layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 

    baseplate.place_element_along_beam("Half waveplate 1", optomech.waveplate, beam,
                                       beam_index=0b1, distance=22, angle=layout.cardinal['up'],
                                       mount_type=optomech.rotation_stage_rsp05)
    baseplate.place_element_along_beam("Beam Splitter 1", optomech.cube_splitter, beam,
                                       beam_index=0b1, distance=30, angle=layout.cardinal['up'],
                                       mount_type=optomech.skate_mount)


    baseplate.place_element_along_beam("Half waveplate 2", optomech.waveplate, beam,
                                       beam_index=0b11, distance=35, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05, mount_args=dict(invert=True))
    baseplate.place_element_along_beam("input mirror 3", optomech.circular_mirror, beam,
                                       beam_index=0b11, distance=30, angle=layout.turn['left-down'],
                                       mount_type=optomech.mirror_mount_c05g)
    baseplate.place_element_along_beam("splitter", optomech.circular_splitter, beam,
                                       beam_index=0b11, distance=15, angle=layout.turn['down-left'],
                                       mount_type=optomech.splitter_mount_b05g)


    baseplate.place_element_along_beam("Half waveplate Probe", optomech.waveplate, beam,
                                       beam_index=0b111, distance=20, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05)
    baseplate.place_element_along_beam("probe mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b111, distance=30, angle=layout.turn['left-down'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    baseplate.place_element_along_beam("probe mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b111, distance=18, angle=layout.turn['down-left'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 
    baseplate.place_element_along_beam("Rb gas cell", optomech.rb_cell, beam,
                                       beam_index=0b111, x=6.5*layout.inch, angle=layout.cardinal['right'])


    baseplate.place_element_along_beam("pump mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b110, distance=45, angle=layout.turn['down-left'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    baseplate.place_element_along_beam("Half_waveplate_pump", optomech.waveplate, beam,
                                       beam_index=0b110, x=3.5*layout.inch, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05)
    baseplate.place_element_along_beam("pump mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b110, x=2.5*layout.inch, angle=layout.turn['left-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))


    baseplate.place_element_along_beam("Beam_Splitter_2", optomech.cube_splitter, beam,
                                       beam_index=0b111, x=2.5*layout.inch, angle=layout.cardinal['left'],
                                       mount_type=optomech.skate_mount)

    baseplate.place_element_along_beam("Photodetector", optomech.photodetector_pda10a2, beam,
                                       beam_index=0b1110, distance=30, angle=layout.cardinal['right'])
    
    baseplate.place_element_along_beam("Pump Fiberport", optomech.fiberport_mount_hca3, beam,
                                       beam_index=0b11010, x=base_dx-gap, angle=layout.cardinal['left'])


if __name__ == "__main__":
    Rb_SAS()
    layout.redraw()