from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
name = "OQC_grid_optics" ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

def test_element():
    base_dx = 7.6 * layout.inch
    base_dy = 13 * layout.inch
    
    base_dz = 1 * layout.inch
    input_x = 5 * layout.inch
    input_y = 3 * layout.inch
    baseplate = layout.baseplate(base_dx+17, base_dy+17, base_dz, x=0, y=0, angle=0,
                                 
                                 name=name, label=label)
    baseplate.place_element_general('test_1', optomech.periscope_for_redstone,
                                x=input_x, y=input_y ,z = 0, angle_x = 0, angle_y = 0, angle_z  = 0)

if __name__ == "__main__":
    test_element()
    layout.redraw()