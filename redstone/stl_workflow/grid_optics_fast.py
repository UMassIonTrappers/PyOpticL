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

def grid_mirror_light(Number_of_light_source = 13, x=0, y=0, angle=0, mirror=optomech.mirror_mount_k05s1, x_split=False, thumbscrews=True):

    base_dx = Number_of_light_source* 1.5 * layout.inch + 2 + 1 * layout.inch
    base_dy = Number_of_light_source* 1.5 * layout.inch + 2 + 1 * layout.inch
    
    base_dz = 1 * layout.inch
    input_x = 1.0 * layout.inch
    input_y = 0.3 * layout.inch
    baseplate = layout.baseplate(base_dx+17, base_dy+17, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits=[3.6*layout.inch,9*layout.inch]*x_split)
    
    for i in 1 + np.arange(Number_of_light_source):
        # beam = baseplate.add_beam_path(x=input_x, y=input_y + i * 2.1 * layout.inch,name = str(i), angle=layout.turn['left-up'])

        baseplate.place_element('Laser_diode_LT230P-B_' + str(i), optomech.km05_50mm_laser_no_pad,
                                x=input_x, y=input_y + i * 1.5 * layout.inch, angle=layout.turn['left-up'])
        baseplate.place_element('Laser_diode_LT230P-B_' + str(i), optomech.km05_50mm_laser_no_pad,
                                y=input_x, x=input_y + i * 1.5 * layout.inch, angle=layout.turn['left-up'])
        
        baseplate.place_element('mirror_' + str(i), optomech.circular_mirror, 
                                    x=base_dx -5, y=input_y + i * 1.5 * layout.inch , angle=180,  #layout.turn['up-right'],
                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
        
        baseplate.place_element('mirror__' + str(i), optomech.circular_mirror, y=base_dx - 5, x=input_y + i * 1.5 * layout.inch  , angle=-90,  #layout.turn['up-right'],
                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
        
        


if __name__ == "__main__":
    grid_mirror_light(Number_of_light_source=13)
    layout.redraw()