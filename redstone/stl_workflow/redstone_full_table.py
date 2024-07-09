from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
# import sys
# # print(sys.path)
# sys.path.append('C:\\Users\\ION\\Dropbox\\UMass Ions\\FreeCAD\\Baseplate Designs\\zhenyu_workspace\\redstone')
# from ECDL import *
# from grid_optics_fast import *

name = "OQC_grid_optics" ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

layout.table_no_grid(dx =106, dy= 70)
layout.place_element_on_table("grid optics", optomech.grid_optics,  x = 25, y = 8, z = 0, angle = 0)
# grid_mirror_light(Number_of_light_source=13, x = 25, y = 8)
layout.place_element_on_table("grid mirror_1", optomech.grid_mirror_lying_down,  x = 0, y = 13-0.2, z = 10.96, angle = 90)
layout.place_element_on_table("grid mirror_2", optomech.grid_mirror_lying_down,  x = 0, y = 44, z = 10.96, angle = 90)
layout.place_element_on_table("grid waveplate_1", optomech.grid_waveplate_lying_down,  x = 5-0.8 * 2.828, y = 10-0.9*2.828 + 0.1, z = 10.96, angle = 45)
layout.place_element_on_table("grid beam splitter_2", optomech.grid_beamsplitter_lying_down,  x = 12-1.2* 2.828, y = 5- 2.828 + 0.1, z = 10.96, angle = 45)
layout.place_element_on_table("grid beam splitter_0", optomech.grid_beamsplitter_lying_down,  x = 10, y = 35+1, z = 10.96, angle = 0)

layout.place_element_on_table("grid waveplate_2", optomech.grid_waveplate_lying_down,  x = 9 - 0.6 * 2.828 - 0.1, y = 63 + 0.65 * 2.828, z = 10.96, angle = -45)
layout.place_element_on_table("grid beam splitter_2", optomech.grid_beamsplitter_lying_down,  x = 16 - 0.9*2.828-0.2 - 0.1, y = 67 + 0.9 * 2.828 - 0.2, z = 10.96, angle = -45)

layout.place_element_on_table("grid waveplate_3", optomech.grid_waveplate_lying_down,  x = 20 + 0.6 * 2.828, y = 50-0.5 * 2.828, z = 10.96, angle = -45)
#####################################################################################################################################
# grid_mirror_light(Number_of_light_source=13, x = 89, y = 0, angle=90)
layout.place_element_on_table("grid optics", optomech.grid_optics,  x = 74, y = 5, z = 0, angle = 90)
layout.place_element_on_table("grid mirror_1_", optomech.grid_mirror_lying_down,  x = 96, y = 17, z = 10.96, angle = 90)
layout.place_element_on_table("grid mirror_2_", optomech.grid_mirror_lying_down,  x = 96, y = 40, z = 10.96, angle = 90)
layout.place_element_on_table("grid waveplate_1_", optomech.grid_waveplate_lying_down,  x = 82 + 2.828, y = 20 - 0.3 * 2.828 + 0.1, z = 10.96, angle = -45)
layout.place_element_on_table("grid beam splitter_2_", optomech.grid_beamsplitter_lying_down,  x = 77 + 2.828, y = 15 - 0.2* 2.828 + 0.1, z = 10.96, angle = -45)
layout.place_element_on_table("grid beam splitter_0_", optomech.grid_beamsplitter_lying_down,  x = 79 + 0.3 , y = 34 + 1.6, z = 10.96, angle = 0)

layout.place_element_on_table("grid waveplate_2_", optomech.grid_waveplate_lying_down,  x = 77 + 1.414, y = 55 + 1.414, z = 10.96, angle = 45)
layout.place_element_on_table("grid beam splitter_2_", optomech.grid_beamsplitter_lying_down,  x = 74 - 0.2 * 1.414 + 0.1, y = 60 - 0.2 * 1.414 + 0.2, z = 10.96, angle = 45)

layout.place_element_on_table("grid waveplate_3_", optomech.grid_waveplate_lying_down,  x = 74 - 1.1 * 2.828, y = 40 + 0.1, z = 10.96, angle = 45)