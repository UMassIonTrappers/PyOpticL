from PyOpticL.layout import Layout
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports("../subsystems")

from subsystems.laser_cooling_subsystem import laser_cooling_subsystem      # 421.6 nm trapped ion cooling and detection
from subsystems.photoionization_subsystem import ( 
    photoionization_subsystem_commercial,
    photoionization_subsystem_ecdl,)                                        # 461 nm and 405 nm for photoionization of neutral Sr
from subsystems.raman_subsystem import raman_subsystem                      # 422 nm Raman laser for Zeeman Qubits
from subsystems.repump_subsystem import (
    repump_subsystem, repump_subsystem_mirrored,)                           # 1033 nm (D5/2 'quench') and 1092 nm D3/2 repump lasers
from subsystems.spam_subsystem import spam_subsystem                        # 674 nm qubit state and preparation laser

def sr88_apparatus():
    apparatus = Layout("Sr88 Apparatus")

    apparatus.add( laser_cooling_subsystem(),               position=(dim(0, "grid"),   dim(0, "grid"),     0), rotation=0,)
    apparatus.add( raman_subsystem(),                       position=(dim(-60, "grid"), dim(-10, "grid"),   0), rotation=180,)
    apparatus.add( photoionization_subsystem_ecdl(),        position=(dim(-40, "grid"), dim(20, "grid"),    0), rotation=0,)
    apparatus.add( spam_subsystem(),                        position=(dim(-40, "grid"), dim(30, "grid"),    0), rotation=0,)
    apparatus.add( photoionization_subsystem_commercial(),  position=(dim(0, "grid"),   dim(10, "grid"),    0), rotation=0,)
    apparatus.add( repump_subsystem(),                      position=(dim(0, "grid"),   dim(20, "grid"),    0), rotation=0,)
    apparatus.add( repump_subsystem_mirrored(),             position=(dim(0, "grid"),   dim(30, "grid"),    0), rotation=0,)

    return apparatus

if __name__ == "__main__":
    apparatus = sr88_apparatus()
    apparatus.recompute()
