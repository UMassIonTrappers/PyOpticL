from PyOpticL.layout import Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports
fix_relative_imports("../modules")

from doublepass import doublepass
from ecdl.ecdl import ecdl
from ecdl.ecdl_isolator_plate import ecdl_isolator_plate
from scalable_rb_sas.scalable_rb_sas import rb_sas
from singlepass import singlepass

def laser_cooling_subsystem():

    subsystem = Layout("Laser Cooling Subsystem")
    x = 0
    subsystem.add(ecdl(),                   position=(0, 0, 0),rotation=180,); x += 5
    subsystem.add(ecdl_isolator_plate(),    position=(dim(-x, "grid"), dim(3, "grid"), 0),  rotation=180,)  ; x += 8
    subsystem.add(rb_sas(),                 position=(dim(-x, "grid"), dim(-15, "grid"), 0),rotation=90,)   ; x += 7
    subsystem.add(singlepass(),             position=(dim(-x, "grid"), dim(-4, "grid"), 0), rotation=90,)   ; x += 6
    subsystem.add(doublepass(),             position=(dim(-x, "grid"), dim(-4, "grid"), 0), rotation=90,)
    return subsystem

if __name__ == "__main__":
    subsystem = laser_cooling_subsystem()
    subsystem.recompute()
