from PyOpticL.layout import Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports("../subsystems")

from subsystems.laser_cooling_subsystem import laser_cooling_subsystem
from subsystems.photoionization_subsystem import (
    photoionization_subsystem_commercial,
    photoionization_subsystem_ecdl,
)
from subsystems.raman_subsystem import raman_subsystem
from subsystems.repump_subsystem import repump_subsystem, repump_subsystem_mirrored
from subsystems.spam_subsystem import spam_subsystem

### NOT YET ARRANGED


def sr88_apparatus():
    apparatus = Layout("Sr88 Apparatus")

    apparatus.add(
        laser_cooling_subsystem(),
        position=(dim(0, "grid"), dim(0, "grid"), dim(0, "grid")),
        rotation=0,
    )
    apparatus.add(
        raman_subsystem(),
        position=(dim(-60, "grid"), dim(-10, "grid"), dim(0, "grid")),
        rotation=180,
    )
    apparatus.add(
        photoionization_subsystem_ecdl(),
        position=(dim(-40, "grid"), dim(30, "grid"), dim(0, "grid")),
        rotation=0,
    )
    apparatus.add(
        photoionization_subsystem_commercial(),
        position=(dim(0, "grid"), dim(10, "grid"), dim(0, "grid")),
        rotation=0,
    )
    apparatus.add(
        spam_subsystem(),
        position=(dim(-40, "grid"), dim(40, "grid"), dim(0, "grid")),
        rotation=0,
    )
    apparatus.add(
        repump_subsystem(),
        position=(dim(0, "grid"), dim(20, "grid"), dim(0, "grid")),
        rotation=0,
    )
    apparatus.add(
        repump_subsystem_mirrored(),
        position=(dim(0, "grid"), dim(30, "grid"), dim(0, "grid")),
        rotation=0,
    )

    return apparatus


if __name__ == "__main__":
    apparatus = sr88_apparatus()
    apparatus.recompute()
