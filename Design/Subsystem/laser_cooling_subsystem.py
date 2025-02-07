## This code generate a our Lab's optical table setup with all the baseplate, laser and vacuum system.
## You just have to place the baseplate in the right position to make your own set up for optical table

import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
import numpy as np                
from PyOpticL import layout, optomech
from Rb_SAS import Rb_SAS
from modular_doublepass import doublepass_f50
from input_telescope import telescope
from modular_sourcebox import sourcebox
from ECDL import ECDL
from ECDL_Isolator_plate import ECDL_isolator_baseplate
#A full table has dx=44 and dy=92
#layout.table_grid(dx=28, dy=55)

# # #422nm and RB Cell
wavelength = 422e-6   #wavelength in mm
grating_pitch_d = 1/3600   # Lines per mm
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))
def laser_cooling_subsystem(x=0, y=0, angle=0, thumbscrews=True, littrow_angle = littrow_angle, **args_for_doublepass):

    ECDL(x=21.3 + x,y=4 + y, angle=90+angle, littrow_angle = littrow_angle)
    ECDL_isolator_baseplate(x=24 + x, y= 9 + y, angle=layout.cardinal['up']+angle)
    telescope(x=24 + x, y=16 + y, angle=90+angle)
    Rb_SAS(x=10 + x, y=20 + y, thumbscrews=thumbscrews)
    doublepass_f50(x=17 + x, y=26 + y, thumbscrews=thumbscrews, **args_for_doublepass)

    # this version is for commercial laser
    # sourcebox(x=20 + x,y=2 + y, angle=0+angle) # model for toptica
    # layout.place_element_on_table("Periscope", optomech.periscope, x=22.5 + x, y= 14 + y,z=0, angle=layout.cardinal['up']+angle, mirror_args=dict(mount_type=optomech.mirror_mount_k05s1))
    # periscope only apply with source box
    # telescope(x=24 + x, y=16 + y, angle=90+angle)
    # Rb_SAS(x=10 + x, y=20 + y, thumbscrews=thumbscrews)
    # doublepass_f50(x=17 + x, y=26.5 + y, thumbscrews=thumbscrews)

if __name__ == "__main__":
    laser_cooling_subsystem()
    layout.redraw()