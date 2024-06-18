from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
# import sys
# # print(sys.path)
# sys.path.append('C:\\Users\\ION\\Dropbox\\UMass Ions\\FreeCAD\\Baseplate Designs\\zhenyu_workspace\\redstone')
# from ECDL import *
from grid_optics_fast import *

name = "OQC_grid_optics" ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

layout.table_no_grid(dx =106, dy= 60)
layout.place_element_on_table("grid mirror_1", optomech.grid_optics,  x = 25, y = 8, z = 0, angle = 0)
# grid_mirror_light(Number_of_light_source=13, x = 25, y = 8)
layout.place_element_on_table("grid mirror_1", optomech.grid_mirror_lying_down,  x = 0, y = 13, z = 10.96, angle = 90)
layout.place_element_on_table("grid mirror_2", optomech.grid_mirror_lying_down,  x = 0, y = 46, z = 10.96, angle = 90)
layout.place_element_on_table("grid waveplate_1", optomech.grid_waveplate_lying_down,  x = 5, y = 18, z = 10.96, angle = 45)
layout.place_element_on_table("grid beam splitter_2", optomech.grid_beamsplitter_lying_down,  x = 12, y = 18, z = 10.96, angle = 45)
layout.place_element_on_table("grid beam splitter_0", optomech.grid_beamsplitter_lying_down,  x = 10, y = 35, z = 10.96, angle = 0)

layout.place_element_on_table("grid waveplate_2", optomech.grid_waveplate_lying_down,  x = 16, y = 59, z = 10.96, angle = -45)
layout.place_element_on_table("grid beam splitter_2", optomech.grid_beamsplitter_lying_down,  x = 22, y = 59, z = 10.96, angle = -45)

layout.place_element_on_table("grid waveplate_3", optomech.grid_waveplate_lying_down,  x = 24, y = 49, z = 10.96, angle = -45)
#####################################################################################################################################
# grid_mirror_light(Number_of_light_source=13, x = 89, y = 0, angle=90)
layout.place_element_on_table("grid mirror_1", optomech.grid_optics,  x = 74, y = 0, z = 0, angle = 90)
layout.place_element_on_table("grid mirror_1_", optomech.grid_mirror_lying_down,  x = 96, y = 17, z = 10.96, angle = 90)
layout.place_element_on_table("grid mirror_2_", optomech.grid_mirror_lying_down,  x = 96, y = 40, z = 10.96, angle = 90)
layout.place_element_on_table("grid waveplate_1_", optomech.grid_waveplate_lying_down,  x = 82, y = 25, z = 10.96, angle = -45)
layout.place_element_on_table("grid beam splitter_2_", optomech.grid_beamsplitter_lying_down,  x = 77, y = 25, z = 10.96, angle = -45)
layout.place_element_on_table("grid beam splitter_0_", optomech.grid_beamsplitter_lying_down,  x = 79, y = 34, z = 10.96, angle = 0)

layout.place_element_on_table("grid waveplate_2_", optomech.grid_waveplate_lying_down,  x = 72, y = 50, z = 10.96, angle = 45)
layout.place_element_on_table("grid beam splitter_2_", optomech.grid_beamsplitter_lying_down,  x = 69, y = 50, z = 10.96, angle = 45)

layout.place_element_on_table("grid waveplate_3_", optomech.grid_waveplate_lying_down,  x = 66, y = 39, z = 10.96, angle = 45)