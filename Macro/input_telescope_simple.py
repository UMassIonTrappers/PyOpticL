import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

gap = 0.25*INCH
base_dx = 3*INCH-gap
base_dy = 3*INCH-gap
base_dz = INCH

ddx = INCH
ddy = 1.5*INCH


layout.create_baseplate(base_dx, base_dy, base_dz)

beam = layout.add_beam_path(base_dx/2, 0, 90)

layout.place_element_along_beam("f75cx", optomech.lens_holder_l05g, beam, 0b1, -90, (3*INCH-gap-45)/2)
layout.place_element_along_beam("f030cc", optomech.lens_holder_l05g, beam, 0b1, 90, 45)

offset = -1/2 # arbitrary shift to make sure laser is over bolt holes
for i in [[0,0],[0,2],[2,0],[2,2]]:
    layout.place_element("Mount_Hole", optomech.baseplate_mount, (i[0]-offset)*INCH-gap/2, (i[1]-offset)*INCH-gap/2, 0)

layout.redraw()