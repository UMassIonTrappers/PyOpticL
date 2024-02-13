from PyOptic import layout
from ECDL import ECDL
#from Rb_SAS import Rb_SAS
from modular_doublepass import doublepass

layout.table_grid(dx=17, dy=21)

ECDL(x=8, y=7, angle=-90)
#Rb_SAS(x=0, y=7)
doublepass(x=6, y=11)
doublepass(x=7, y=16)

layout.redraw()