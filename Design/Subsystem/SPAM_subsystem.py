import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
from PyOpticL import layout, optomech
from ECDL_Isolator_plate import ECDL_isolator_baseplate
from modular_doublepass import doublepass_f50
from modular_beam_pickoff import Beam_pickoff
from ECDL import ECDL
import numpy as np
wavelength = 674e-6   #wavelength in mm
grating_pitch_d = 1/3600   # Lines per mm
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))
def subsystem_674(x=0, y=0, angle=0, littrow_angle = littrow_angle):
    ECDL(6.7 + x, 32 + y, 270+angle, littrow_angle = littrow_angle)
    ECDL_isolator_baseplate(x=4+ x, y=26.5 + y, angle=270+angle)
    doublepass_f50(x=12+ x, y=20 + y, angle = 180+angle, thumbscrews=True)
    doublepass_f50(x=11+ x, y=14 + y, angle = 180+angle, thumbscrews=True)
    Beam_pickoff(x=2.5+ x, y= 8.5+y, angle=-90+angle, thumbscrews= True)

if __name__ == "__main__":
    subsystem_674()
    layout.redraw()