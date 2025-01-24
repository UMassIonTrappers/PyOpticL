import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Subsystem')))
from PyOpticL import layout, optomech
from subsystem_674 import subsystem_674
from laser_cooling_subsystem import laser_cooling_subsystem
from Raman_subsystem import Raman_subsystem
from PI_subsystem import PI_subsystem

#A full table has dx=44 and dy=92
layout.table_grid(dx=50, dy=92)
# layout.place_element_on_table("chamber", optomech.Room_temp_chamber_Mechanical, x=28, y = 60, angle=0) # there is a room temperature chamber in the center
laser_cooling_subsystem(x=-3, y=0, thumbscrews=True)
Raman_subsystem(x=-1 , y=25, thumbscrews=True)
PI_subsystem(x=27 , y=8, angle = 0, thumbscrews=True) #405
PI_subsystem(x=36 , y=8, thumbscrews=True) # 461
subsystem_674(x=30 , y=50, thumbscrews=True)
