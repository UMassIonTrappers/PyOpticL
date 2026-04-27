from PyOpticL.layout import Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from doublepass import doublepass
from ecdl.ecdl import ecdl
from scalable_rb_sas.scalable_rb_sas import rb_sas
from singlepass import singlepass

laser_cooling_subsystem = Layout("Laser Cooling Subsystem")

laser_cooling_subsystem.add(ecdl, position=(0, 0, 0), rotation=180)
laser_cooling_subsystem.add(
    rb_sas, position=(dim(-6, "grid"), dim(-17, "grid"), 0), rotation=90
)
laser_cooling_subsystem.add(
    singlepass, position=(dim(-14, "grid"), dim(-6, "grid"), 0), rotation=90
)
laser_cooling_subsystem.add(
    doublepass, position=(dim(-20, "grid"), dim(-5, "grid"), 0), rotation=90
)

if __name__ == "__main__":
    laser_cooling_subsystem.recompute()
