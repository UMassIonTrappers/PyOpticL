from PyOpticL import laser, layout, optomech
from datetime import datetime
import numpy as np

name = "Test Module"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

dx = 10*layout.inch
dy = 10*layout.inch
dz = layout.inch

#this file could be used for optomech new element development
def main():
    layout.place_element_on_table("cell", optomech.mirror_mount_k05s2, 0,0,0, thumbscrews = True)
    layout.redraw()

if __name__ == "__main__":
    main()
    # layout.redraw()