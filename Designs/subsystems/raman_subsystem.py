from PyOpticL.layout import Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports("../modules")

from beam_pickoff import beam_pickoff
from doublepass import doublepass
from ecdl.ecdl import ecdl
from ecdl.ecdl_isolator_plate import ecdl_isolator_plate

raman_subsystem = Layout("Raman Laser Qubit Subsystem")

x = 0
raman_subsystem.add(
    ecdl(),
    position=(-x, 0, 0),
    rotation=180,
)
x = x + 5

raman_subsystem.add(
    ecdl_isolator_plate(),
    position=(dim(-x, "grid"), dim(3, "grid"), 0),
    rotation=180,
)
x = x + 7

raman_subsystem.add(
    doublepass(),
    position=(dim(-x, "grid"), dim(-6, "grid"), 0),
    rotation=90,
)
x = x + 7

raman_subsystem.add(
    doublepass(),
    position=(dim(-x, "grid"), dim(-5, "grid"), 0),
    rotation=90,
)
x = x + 7

raman_subsystem.add(
    doublepass(),
    position=(dim(-x, "grid"), dim(-4, "grid"), 0),
    rotation=90,
)
x = x + 7

raman_subsystem.add(
    beam_pickoff(),
    position=(dim(-x, "grid"), dim(5, "grid"), 0),
    rotation=180,
)

if __name__ == "__main__":
    raman_subsystem.recompute()
