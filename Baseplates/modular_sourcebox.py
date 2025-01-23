#This code is to make a rectangular box, So that we can place it on the optical table as a pseudo part of wavemeter, and different laser box. 

from PyOpticL import layout, optomech
from datetime import datetime

base_dx = 5*layout.inch
base_dy = 10*layout.inch
base_dz = 4*layout.inch
gap = layout.inch/8

input_x1 = 4*layout.inch
input_x2 = 0*layout.inch

mount_holes = [(0, 0), (3, 4)]*0

extra_mount_holes = [(3, 0), (3, 2), (4, 0), (6, 2)]*0

def sourcebox(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, x_split=False, thumbscrews=True):

    # define and place baseplate object
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 x_splits=[0*layout.inch])
    


if __name__ == "__main__":
    sourcebox()
    layout.redraw()    
