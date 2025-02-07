import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
from PyOpticL import layout, optomech
from ECDL_Isolator_plate import ECDL_isolator_baseplate
from modular_singlepass import singlepass, singlepass_mirrored
from modular_beam_pickoff import Beam_pickoff
from modular_sourcebox import sourcebox
from ECDL import ECDL
import numpy as np

#sr 1033(quench) / 1092(repump)
#ca 854(quench) / 866(repump)

wavelength = 866e-6   #wavelength in mm
grating_pitch_d = 1/3600   # Lines per mm
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))

def repump_subsystem_ECDL_mirrored(x=0, y=0, angle=0, thumbscrews=True, littrow_angle = littrow_angle):

    ECDL(x=4.3 + x, y=-4 + y, angle = 90 + angle, littrow_angle = littrow_angle) # modeling of a home-made laser
    ECDL_isolator_baseplate(x=7 + x, y=1 + y, angle=layout.cardinal['up'])
    singlepass_mirrored(x=7 + x, y=12 + y, angle = 180+angle, thumbscrews=thumbscrews)
    Beam_pickoff(x=7.5 + x, y= 12 + y, angle=90+angle, thumbscrews= thumbscrews)

def repump_subsystem_ECDL(x=0, y=0, angle=0, thumbscrews=True, littrow_angle = littrow_angle):

    ECDL(x=4.3 + x, y=-4 + y, angle = 90 + angle, littrow_angle = littrow_angle) # modeling of a home-made laser
    ECDL_isolator_baseplate(x=7 + x, y=1 + y, angle=layout.cardinal['up'])
    singlepass(x=0 + x, y=7 + y, angle = 0+angle, thumbscrews=thumbscrews)
    Beam_pickoff(x=7.5 + x, y= 12 + y, angle=90+angle, thumbscrews= thumbscrews)

if __name__ == "__main__":
    # repump_subsystem_ECDL(x = 10)
    repump_subsystem_ECDL_mirrored(x = 0)
    layout.redraw()