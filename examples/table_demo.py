from PyOpticL import layout
from Rb_SAS import Rb_SAS
from modular_doublepass import doublepass_f50
# to check out table layout.
# loading time would be long if multiple modules are imported
layout.table_grid(dx=18, dy=15)

Rb_SAS(x=0, y=2)
doublepass_f50(x=7, y=7)


layout.redraw()