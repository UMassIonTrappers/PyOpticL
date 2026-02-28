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

layout.table_grid(dx=86, dy=44)
# layout.place_element_on_table("chamber", optomech.Room_temp_chamber_Mechanical, x=28, y = 60, angle=0)
# # there is a room temperature chamber in the center. it will largely increase loading time...
laser_cooling_subsystem(x=1, y=2, thumbscrews=True)
Raman_subsystem(x=28, y=32, angle=180, thumbscrews=True)
PI_subsystem_commercial(x=45, y=9, angle=0, thumbscrews=True)  # 405 for sr88+
PI_subsystem_ECDL(x=55, y=10, thumbscrews=True)  # 461 for sr88+
repump_subsystem_ECDL_mirrored(x=66, y=10, thumbscrews=True)
repump_subsystem_ECDL(x=76, y=10, thumbscrews=True)
subsystem_spam(x=41, y=38, angle=180, thumbscrews=True)

layout.redraw()
