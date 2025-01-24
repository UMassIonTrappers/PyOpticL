import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
from PyOpticL import layout, optomech
from ECDL_Isolator_plate import ECDL_isolator_baseplate
from modular_singlepass import singlepass
from modular_beam_pickoff import Beam_pickoff
from modular_sourcebox import sourcebox

# 405 or 461 for 88Sr+
def PI_subsystem(x=0, y=0, angle=0, thumbscrews=True):

    sourcebox(x=3 + x, y=-6 + y, angle = 0 + angle) # modeling of a commercial laser
    layout.place_element_on_table("Periscope", optomech.periscope, x=5.5 + x, y=6 + y,z=0, angle=layout.cardinal['up'], mirror_args=dict(mount_type=optomech.mirror_mount_k05s1))
    # ECDL_isolator_baseplate(x=9 + x, y=7.5 + y, angle=90+angle) 
    singlepass(x=0 + x, y=8 + y, angle = 0+angle, thumbscrews=thumbscrews)
    Beam_pickoff(x=7.5 + x, y= 13 + y, angle=90+angle, thumbscrews= thumbscrews)

if __name__ == "__main__":
    PI_subsystem()
    layout.redraw()