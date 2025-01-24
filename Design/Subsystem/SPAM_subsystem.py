import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
from PyOpticL import layout, optomech
from ECDL_Isolator_plate import ECDL_isolator_baseplate
from modular_doublepass import doublepass_f50
from modular_beam_pickoff import Beam_pickoff

def subsystem_674(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, x_split=False, thumbscrews=True):
    
    layout.place_element_on_table("test", optomech.laser_mount_km100pm, 6.7 + x, 32 + y, 270+angle, z=0)
    ECDL_isolator_baseplate(x=4+ x, y=26.5 + y, angle=270+angle)
    doublepass_f50(x=12+ x, y=20 + y, angle = 180+angle, thumbscrews=True)
    doublepass_f50(x=11+ x, y=14 + y, angle = 180+angle, thumbscrews=True)
    Beam_pickoff(x=2.5+ x, y= 8.5+y, angle=-90+angle, thumbscrews= True)

if __name__ == "__main__":
    subsystem_674()
    layout.redraw()