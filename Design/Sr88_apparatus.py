import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Subsystem')))
from PyOpticL import layout, optomech
from SPAM_subsystem import subsystem_spam
from Laser_cooling_subsystem import laser_cooling_subsystem
from Raman_subsystem import Raman_subsystem
from Photoionization_subsystem import PI_subsystem_ECDL, PI_subsystem_commercial


layout.table_grid(dx=52, dy=92)
# layout.place_element_on_table("chamber", optomech.Room_temp_chamber_Mechanical, x=28, y = 60, angle=0) 
# # there is a room temperature chamber in the center. it will largely increase loading time... 
laser_cooling_subsystem(x=-1, y=0, thumbscrews=True)
Raman_subsystem(x=1 , y=26.5, thumbscrews=True)
PI_subsystem_commercial(x=29 , y=8, angle = 0, thumbscrews=True) #405 for sr88+ 
PI_subsystem_ECDL(x=38 , y=8, thumbscrews=True) # 461 for sr88+
subsystem_spam(x=32 , y=50, thumbscrews=True)
