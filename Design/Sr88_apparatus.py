import time

start_time = time.time()
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Module"))
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "Subsystem")))
import numpy as np
from Doppler_Subsystem_with_MTS import laser_cooling_subsystem
from modular_beam_combiner import Beam_Combiner_General
from Photoionization_subsystem import PI_subsystem_commercial, PI_subsystem_ECDL
from Raman_subsystem import Raman_subsystem
from Repump_subsystem import repump_subsystem_ECDL, repump_subsystem_ECDL_mirrored
from SPAM_subsystem import subsystem_spam

from PyOpticL import layout, optomech

# layout.table_grid(dx=72, dy=92)
# layout.place_element_on_table("chamber", optomech.Room_temp_chamber_Mechanical, x=28, y = 60, angle=0)
# # there is a room temperature chamber in the center. it will largely increase loading time...
laser_cooling_subsystem(x=1, y=10, thumbscrews=True)
Raman_subsystem(x=1, y=26.5, thumbscrews=True)
PI_subsystem_commercial(x=29, y=8.5, angle=0, thumbscrews=True)  # 405 for sr88+
PI_subsystem_ECDL(x=39, y=8.5, thumbscrews=True)  # 461 for sr88+
repump_subsystem_ECDL_mirrored(x=50, y=8.5, thumbscrews=True)
repump_subsystem_ECDL(x=60, y=8.5, thumbscrews=True)
subsystem_spam(x=32, y=50, thumbscrews=True)
