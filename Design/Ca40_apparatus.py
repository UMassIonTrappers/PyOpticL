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
from modular_beam_combiner import Beam_Combiner_General
from Repump_subsystem import repump_subsystem_ECDL_mirrored, repump_subsystem_ECDL
import numpy as np
# sr 88 and ca 40 have the same operation paradigm 
# defualt of littrow angle depandence is set by sr88
# the following is the ca40 specific littrow angle calculation by assuming same grating_pitch_d = 1/3600 
# cooling and detection -- 397 nm
# repumping -- 866 nm
# quench -- 854 nm 
# photoionization -- 423 nm(step one) and 375 nm(step two)
# optical qubit -- 729 nm

wl_cooling = 397e-6
wl_optical_qubit = 729e-6
wl_photoionization_step1 = 423e-6
wl_photoionization_step2 = 375e-6
wl_repump_cooling = 866e-6
wl_repump_quench = 854e-6
grating_pitch_d = 1/3600   # Lines per mm
grating_pitch_d_ = 1/1800
littrow_angle_cooling = np.arcsin(wl_cooling/(2*grating_pitch_d))*180/np.pi
littrow_angle_optical_qubit = np.arcsin(wl_optical_qubit/(2*grating_pitch_d))*180/np.pi
littrow_angle_photoionization_step1 = np.arcsin(wl_photoionization_step1/(2*grating_pitch_d))*180/np.pi
littrow_angle_photoionization_step2 = np.arcsin(wl_photoionization_step2/(2*grating_pitch_d))*180/np.pi
littrow_angle_repump_cooling = np.arcsin(wl_repump_cooling/(2*grating_pitch_d_))*180/np.pi
littrow_angle_repump_quench = np.arcsin(wl_repump_quench/(2*grating_pitch_d_))*180/np.pi

layout.table_grid(dx=72, dy=92)
# layout.place_element_on_table("chamber", optomech.Room_temp_chamber_Mechanical, x=28, y = 60, angle=0) 
# # there is a room temperature chamber in the center. it will largely increase loading time... 
laser_cooling_subsystem(x=-1, y=0, thumbscrews=True, littrow_angle = littrow_angle_cooling)
Raman_subsystem(x=1 , y=26.5, thumbscrews=True, littrow_angle = littrow_angle_cooling)
PI_subsystem_commercial(x=29 , y=8.5, angle = 0, thumbscrews=True)
PI_subsystem_ECDL(x=39 , y=8.5, thumbscrews=True, littrow_angle = littrow_angle_photoionization_step2) 
repump_subsystem_ECDL_mirrored(x=50 , y=8.5, thumbscrews=True, littrow_angle = littrow_angle_repump_cooling) 
repump_subsystem_ECDL(x=60 , y=8.5, thumbscrews=True, littrow_angle = littrow_angle_repump_quench) 
subsystem_spam(x=32 , y=50, thumbscrews=True, littrow_angle = littrow_angle_optical_qubit)
