from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
name = "OQC_grid_optics" ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time
Number_of_light_source = 13

mount_holes = [] #[(0, 1), (11,0) ,(12, 4), (8, 2)]
gap = 1/8 * layout.inch
extra_mount_holes = [] #[(2,1),(0, 5),(5, 2),(9,4),(8,3)]

def grid_mirror_light(Number_of_light_source = 10, x=0, y=0, angle=0, mirror=optomech.mirror_mount_k05s1, x_split=False, thumbscrews=True):
    if Number_of_light_source > 8:
        base_dx = Number_of_light_source* 2.9 * layout.inch + 3
        base_dy = Number_of_light_source* 2.9 * layout.inch + 3
    else:
        base_dx = Number_of_light_source* 3.3 * layout.inch + 3
        base_dy = Number_of_light_source* 3.3 * layout.inch + 3
    base_dz = 1 * layout.inch
    input_x = 1.5 * layout.inch
    input_y = 2.9 * layout.inch
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits=[3.6*layout.inch,9*layout.inch]*x_split)
    for i in 1 + np.arange(Number_of_light_source):
        beam = baseplate.add_beam_path(x=input_x, y=input_y + i * 2.2 * layout.inch,name = str(i), angle=layout.turn['left-up'])

        baseplate.place_element('Laser_diode_LT230P-B_' + str(i), optomech.km05_50mm_laser,
                                x=input_x, y=input_y + i * 2.2 * layout.inch, angle=layout.turn['left-up'])
        
        baseplate.place_element_along_beam('mirror_' + str(i), optomech.circular_mirror, beam,
                                    beam_index=0b1, distance=1.41421356 * (2.5 * Number_of_light_source-2.2 * i) * layout.inch , angle=layout.cardinal['down'],  #layout.turn['up-right'],
                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
        baseplate.place_element_along_beam('mirror__' + str(i), optomech.circular_mirror, beam,
                                    beam_index=0b1, distance=1.41421356 * (2.2 * i+1) * layout.inch , angle=layout.cardinal['left'],  #layout.turn['up-right'],
                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
        baseplate.place_element_along_beam('Laser_diode_LT230P-B__' + str(i), optomech.km05_50mm_laser, beam,
                                beam_index=0b1, distance=1.41421356 * (2.5 * Number_of_light_source-2.2 * i) * layout.inch ,angle=layout.turn['left-up'])


if __name__ == "__main__":
    grid_mirror_light(Number_of_light_source=6)
    layout.redraw()