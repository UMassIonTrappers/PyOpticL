from PyOpticL.layout import Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports("../modules")

from beam_pickoff import beam_pickoff
from ecdl.ecdl import ecdl
from ecdl_isolator import ecdl_isolator
from singlepass import singlepass, singlepass_mirrored


def repump_subsystem():

    subsystem = Layout(label="Repump Subsystem")

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
        singlepass(),
        position=(dim(-x, "grid"), dim(-6, "grid"), 0),
        rotation=90,
    )

    x += 6
    subsystem.add(
        beam_pickoff(),
        position=(dim(-x, "grid"), dim(2, "grid"), 0),
        rotation=180,
    )

    return subsystem


def repump_subsystem_mirrored():

    subsystem = Layout(label="Repump Subsystem")

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
        singlepass_mirrored(),
        position=(dim(-x, "grid"), dim(-3, "grid"), 0),
        rotation=90,
    )

    x += 6
    subsystem.add(
        beam_pickoff(),
        position=(dim(-x, "grid"), dim(0, "grid"), 0),
        rotation=180,
    )

    return subsystem


if __name__ == "__main__":
    subsystem = repump_subsystem_mirrored()
    subsystem.recompute()
