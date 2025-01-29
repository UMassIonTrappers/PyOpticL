import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
from PyOpticL import layout, optomech
from ECDL_Isolator_plate import ECDL_isolator_baseplate
from modular_singlepass import singlepass
from modular_beam_pickoff import Beam_pickoff
from modular_beam_combiner import Beam_Combiner_General
from ECDL import ECDL
import numpy as np
wavelength = 422e-6   #wavelength in mm
grating_pitch_d = 1/3600   # Lines per mm
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))
def Raman_subsystem(x=0, y=0, angle=0, thumbscrews=True, littrow_angle = littrow_angle):
# # #422 Raman 
    ECDL(x = 6.7 + x, y = 26 + y, angle= 270 + angle, littrow_angle = littrow_angle)    
    
    ECDL_isolator_baseplate(x=4 + x, y=20.5 + y, angle=270+angle)
    singlepass(x=11 + x, y=14 + y, angle = 180+angle, thumbscrews=thumbscrews)
    singlepass(x=10+x, y=9+y, angle = 180+angle, thumbscrews=thumbscrews)
    Beam_Combiner_General(x=11+x, y=13.5+y, angle = -90+angle)
    singlepass(x=9+x, y=4+y, angle = 180+angle, thumbscrews=thumbscrews)
    Beam_Combiner_General(x=11+x, y=6.5+y, angle = -90+angle)
    Beam_pickoff(x=1.5+x, y= -1.5+y, angle=-90+angle, thumbscrews= thumbscrews)

if __name__ == "__main__":
    Raman_subsystem()
    layout.redraw()