from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
name = "OQC_grid_optics" ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

base_dx = 2.1 * layout.inch
base_dy = 2.1 * layout.inch
base_dz = 1. * layout.inch
input_x = 1 * layout.inch
input_y = 1 * layout.inch
input_z = 0.5  * layout.inch
mount_holes = [] #[(0, 1), (11,0) ,(12, 4), (8, 2)]
gap = 1/8 * layout.inch
extra_mount_holes = [] #[(2,1),(0, 5),(5, 2),(9,4),(8,3)]

def grid_beam_splitter(x=0, y=0, angle=0, Row_numnber = 6, Column_number = 6):
    baseplate = layout.baseplate(base_dx*Row_numnber, base_dy*Column_number, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits = False)
    # beam = baseplate.add_beam_path_general(input_x, input_y, input_z  , 0, 85, 0)
    for i in range(Row_numnber):
        for j in range(Column_number):
            baseplate.place_element_general('beam_splitter_' + str(i) + str(j), optomech.cube_splitter, x=(2 * i + 1.25) * layout.inch , y=(2 * j + 1.25) * layout.inch, z=-25.5, angle_x = 0, angle_y = 45, angle_z = 90 ,mount_type=optomech.skate_mount_lying_down)
    # beam_splitter = baseplate.place_element_along_beam("Beam Splitter", optomech.cube_splitter_rotate, beam,
    #                                    beam_index=0b1, distance=19, angle=layout.cardinal['right'],
    #                                    mount_type=optomech.skate_mount)

if __name__ == "__main__":
    grid_beam_splitter(Row_numnber=6, Column_number=6)
    layout.redraw()