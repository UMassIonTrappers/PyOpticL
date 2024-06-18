from PyOpticL import layout, optomech
# layout.table_grid(dx=10, dy=12)
import numpy as np
from datetime import datetime
name = "OQC_grid_optics" ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

base_dx = 5*layout.inch
base_dy = 5*layout.inch
base_dz = 1*layout.inch
gap = 1/8*layout.inch
def grid_pariscope(x=0, y=0, angle=0):
    baseplate = layout.baseplate(base_dx,base_dy,base_dz, x=x, y=y, angle=angle,
                                 gap=gap)
    baseplate.place_element("Periscope", optomech.periscope,
                        x=60, y=80, angle=layout.cardinal['right'])#,
                        #lower_dz=36.5, upper_dz=76, mirror_args=dict(thumbscrews=True),
                        #mirror_type=optomech.mirror_mount_k05s1, invert=True)

if __name__ == "__main__":
    grid_pariscope()
    layout.redraw()