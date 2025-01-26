from PyOpticL import layout
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Subsystem')))
from Rb_SAS import Rb_SAS
from modular_doublepass import doublepass_f50
# an example to check out table layout.
# loading time would be long if multiple modules are imported
layout.table_grid(dx=18, dy=15)

Rb_SAS(x=0, y=2)
doublepass_f50(x=7, y=7)


layout.redraw()