from PyOptic import layout, optomech
from datetime import datetime

name = "Doublepass"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

base_dx = 10*layout.inch
base_dy = 5*layout.inch
base_dz = layout.inch
gap = layout.inch/8

input_x = 6.5*layout.inch

mount_holes = [(0, 0), (1, 4), (9, 0), (9, 3)]

split_x = 4*layout.inch
extra_mount_holes = [(3, 0), (3, 2), (4, 0), (6, 2)]

def doublepass(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, x_split=0, thumbscrews=False):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, x_split=x_split, mount_holes=mount_holes+extra_mount_holes, name=name, label=label)

    beam = baseplate.add_beam_path(input_x, gap, layout.cardinal['up'])

    baseplate.place_element("Input Fiberport", optomech.fiberport_holder,
                            x=input_x, y=gap, angle=layout.cardinal['up'])
    baseplate.place_element_along_beam("Input Mirror 1", mirror, beam,
                                       beam_index=0b1, distance=18, angle=layout.turn['up-right'],
                                       thumbscrews=thumbscrews)
    baseplate.place_element_along_beam("Input Mirror 2", mirror, beam,
                                       beam_index=0b1, distance=layout.inch, angle=layout.turn['right-up'],
                                       thumbscrews=thumbscrews)
    baseplate.place_element_along_beam("Half waveplate", optomech.rotation_stage_rsp05, beam,
                                       beam_index=0b1, distance=60, angle=layout.cardinal['up'])
    baseplate.place_element_along_beam("Beam Splitter", optomech.pbs_on_skate_mount, beam,
                                       beam_index=0b1, distance=22, angle=layout.cardinal['right'],
                                       invert=True)

    baseplate.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam,
                                       beam_index=0b11, distance=35, angle=layout.cardinal['right'],
                                       forward_direction=-1, backward_direction=1)
    baseplate.place_element_along_beam("Quarter waveplate", optomech.rotation_stage_rsp05, beam,
                                       beam_index=0b110, distance=74, angle=layout.cardinal['left'])
    lens = baseplate.place_element_along_beam("Lens f100mm AB coat", optomech.lens_holder_l05g, beam,
                                              beam_index=0b110, distance=26, angle=layout.cardinal['left'],
                                              lens_args=dict(focal_length=100, part_number='LA1213-AB'))
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam,
                                       beam_index=0b111, distance=9, angle=layout.cardinal['right'],
                                       pre_refs=2, adapter_args=dict(drill_offset=-2))
    baseplate.place_element_relative("Retro Mirror", mirror, lens,
                                     x_off=-30, angle=layout.cardinal['right'],
                                     thumbscrews=thumbscrews)

    baseplate.place_element_along_beam("Output Mirror 1", mirror, beam,
                                       beam_index=0b11110, distance=30, angle=layout.turn['right-down'],
                                       thumbscrews=thumbscrews)
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam,
                                       beam_index=0b11110, distance=42, angle=layout.cardinal['down'])
    baseplate.place_element_along_beam("Output Mirror 2", mirror, beam,
                                       beam_index=0b11110, distance=16, angle=layout.turn['down-left'],
                                       thumbscrews=thumbscrews)
    baseplate.place_element_along_beam("Half waveplate Out", optomech.rotation_stage_rsp05, beam,
                                       beam_index=0b11110, distance=110, angle=layout.cardinal['left'])
    baseplate.place_element_along_beam("Optional Fiberport", optomech.fiberport_mount_km05, beam,
                                       beam_index=0b11110,  x=40, angle=layout.cardinal['right'],
                                       optional=True, mount_args=dict(thumbscrews=thumbscrews))
    baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_holder, beam,
                                       beam_index=0b11110, x=gap, angle=layout.cardinal['right'])

if __name__ == "__main__":
    doublepass()
    layout.redraw()