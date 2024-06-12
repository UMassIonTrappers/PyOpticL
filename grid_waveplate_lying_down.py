from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
name = "OQC_grid_optics" ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

base_dx = 2.1 * layout.inch
base_dy = 2.1 * layout.inch
base_dz = 1 * layout.inch
input_x = 1 * layout.inch
input_y = 1 * layout.inch
input_z = 0.5  * layout.inch
mount_holes = [] #[(0, 1), (11,0) ,(12, 4), (8, 2)]
gap = 1/8 * layout.inch
extra_mount_holes = [] #[(2,1),(0, 5),(5, 2),(9,4),(8,3)]

def grid_waveplate_lying_down(x=0, y=0, angle=0, mount_=optomech.rotation_stage_rsp05_lying_down, Row_numnber = 6, Column_number = 6):
    baseplate = layout.baseplate(base_dx*Row_numnber, base_dy*Column_number, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits = False)
    # beam = baseplate.add_beam_path_general(input_x, input_y, input_z  , 0, 85, 0)
    for i in range(Row_numnber):
        for j in range(Column_number):
            baseplate.place_element_general('waveplate_' + str(i) + str(j), optomech.waveplate, x=(2 * i + 1.25) * layout.inch, y=(2 * j + 1.25) * layout.inch, z=-26, angle_x=layout.cardinal['up'], angle_y = -90, angle_z = 0 ,mount_type=mount_)

# baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam,
#                                        beam_index=0b1, distance=1.3 * layout.inch - 10, angle=layout.cardinal['down'],
#                                        mount_type=optomech.rotation_stage_rsp05)

if __name__ == "__main__":
    grid_waveplate_lying_down(Row_numnber=6, Column_number=6)
    layout.redraw()