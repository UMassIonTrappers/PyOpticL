from PyOpticL import *
from datetime import datetime
import numpy as np

# Append the general path to the system path list  

# import sys
# sys.path.append("/Applications/FreeCAD.app/Contents/Resources/Mod/PyOpticL")
# print(sys.path)
from grid_optics import *


name = "Periscope"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " + date_time

basedx = 16*layout.inch
basedy = 16*layout.inch
basedy = layout.inch

# mountholes = np.array()

def periscope():
    pass


if __name__ == "__main__":
    layout.table_grid(dx=85, dy=50)
    layout.place_element_on_table("grid mirror_1", optomech.grid_mirror_lying_down,  x = 0, y = 7, z = 10.96, angle = 90)
    layout.place_element_on_table("grid mirror_2", optomech.grid_mirror_lying_down,  x = 0, y = 30, z = 10.96, angle = 90)
    layout.place_element_on_table("grid waveplate_1", optomech.grid_waveplate_lying_down,  x = 5, y = 5, z = 10.96, angle = 45)
    layout.place_element_on_table("grid beam splitter_2", optomech.grid_beamsplitter_lying_down,  x = 10, y = 5, z = 10.96, angle = 45)
    layout.place_element_on_table("grid beam splitter_0", optomech.grid_beamsplitter_lying_down,  x = 5, y = 24, z = 10.96, angle = 0)

    layout.place_element_on_table("grid waveplate_2", optomech.grid_waveplate_lying_down,  x = 5, y = 45, z = 10.96, angle = -45)
    layout.place_element_on_table("grid beam splitter_2", optomech.grid_beamsplitter_lying_down,  x = 10, y = 45, z = 10.96, angle = -45)

    layout.place_element_on_table("grid waveplate_3", optomech.grid_waveplate_lying_down,  x = 15, y = 35, z = 10.96, angle = -45)

    # grid_mirror_light(Number_of_light_source=6, x = 64, y = 20, angle=180)
    layout.place_element_on_table("grid mirror_1_", optomech.grid_mirror_lying_down,  x = 83, y = 7, z = 10.96, angle = 90)
    layout.place_element_on_table("grid mirror_2_", optomech.grid_mirror_lying_down,  x = 83, y = 30, z = 10.96, angle = 90)
    layout.place_element_on_table("grid waveplate_1_", optomech.grid_waveplate_lying_down,  x = 71, y = 15, z = 10.96, angle = -45)
    layout.place_element_on_table("grid beam splitter_2_", optomech.grid_beamsplitter_lying_down,  x = 66, y = 15, z = 10.96, angle = -45)
    layout.place_element_on_table("grid beam splitter_0_", optomech.grid_beamsplitter_lying_down,  x = 64, y = 24, z = 10.96, angle = 0)

    layout.place_element_on_table("grid waveplate_2_", optomech.grid_waveplate_lying_down,  x = 67, y = 40, z = 10.96, angle = 45)
    layout.place_element_on_table("grid beam splitter_2_", optomech.grid_beamsplitter_lying_down,  x = 62, y = 40, z = 10.96, angle = 45)

    layout.place_element_on_table("grid waveplate_3_", optomech.grid_waveplate_lying_down,  x = 55, y = 30, z = 10.96, angle = 45)

    # print("test")