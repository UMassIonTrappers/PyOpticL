from PyOpticL.layout import Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports("../modules")

from beam_pickoff import beam_pickoff
from doublepass import doublepass
from ecdl.ecdl import ecdl
from ecdl_isolator import ecdl_isolator


def spam_subsystem():

    subsystem = Layout(label="SPAM Subsystem")

    x = 0
    subsystem.add(
        ecdl(),
        position=(dim(-x, "grid"), 0, 0),
        rotation=180,
    )

    x += 5
    subsystem.add(
        ecdl_isolator(),
        position=(dim(-x, "grid"), dim(-3, "grid"), 0),
        rotation=90,
    )

    x += 7
    subsystem.add(
        doublepass(),
        position=(dim(-x, "in"), dim(-7, "grid"), 0),
        rotation=90,
    )

    x += 7
    subsystem.add(
        doublepass(),
        position=(dim(-x, "in"), dim(-6, "grid"), 0),
        rotation=90,
    )

    x += 7
    subsystem.add(
        beam_pickoff(),
        position=(dim(-x, "in"), dim(3, "grid"), 0),
        rotation=180,
    )

    return subsystem


if __name__ == "__main__":
    subsystem = spam_subsystem()
    subsystem.recompute()
