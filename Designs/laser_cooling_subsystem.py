from PyOpticL.layout import Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from ecdl.ecdl import ecdl
from ecdl.ecdl_isolator_plate import ecdl_isolator_plate
from scalable_rb_sas.scalable_rb_sas import rb_sas
from singlepass import singlepass
from doublepass import doublepass

laser_cooling_subsystem = Layout("Laser Cooling Subsystem")

length=0
laser_cooling_subsystem.add(
    ecdl(),
    position=(0, 0, 0),
    rotation=180,
)

length=length+5
laser_cooling_subsystem.add(
    ecdl_isolator_plate(),
    position=(dim(-length, "grid"), dim(3, "grid"), 0),
    rotation=180,
)

length=length+8
laser_cooling_subsystem.add(
    rb_sas(),
    position=(dim(-length, "grid"), dim(-15, "grid"), 0),
    rotation=90,
)

length=length+7
laser_cooling_subsystem.add(
    singlepass(),
    position=(dim(-length, "grid"), dim(-4, "grid"), 0),
    rotation=90,
)

length=length+6
laser_cooling_subsystem.add(
    doublepass(),
    position=(dim(-length, "grid"), dim(-4, "grid"), 0),
    rotation=90,
)

if __name__ == "__main__":
    laser_cooling_subsystem.recompute()
