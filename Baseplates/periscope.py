## The code generates a periscope in case we need to change the height of the beam. 
from PyOpticL import layout, optomech
import numpy as np

layout.table_grid(dx=10, dy=10)

layout.place_element_on_table("Periscope", optomech.periscope,
                              x=2.5, y=4.5, angle=layout.cardinal['right'],
                              lower_dz=36.5, upper_dz=76,
                              mirror_args=dict(mount_type=optomech.mirror_mount_k05s1), invert=True)

## Any chnage in perisopce dimension has to be done in the optomech.