import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

left = -90
right = left + 180
up = 180
down = up - 180 
up_right = 45
right_up = up_right-180
left_down = up_right
down_left = right_up
left_up = 135
up_left = left_up-180
right_down = up_left

INCH = 25.4

base_dx = 4*INCH
base_dy = 5*INCH
base_dz = INCH

ddx = INCH
ddy = 1.5*INCH


layout.create_baseplate(base_dx, base_dy, base_dz)

# Offsets from table grid and positions for mounting holes
xoff = INCH/2
yoff = INCH/2

mount_holes = [[0*INCH, 0*INCH],
               [base_dx-INCH, 0*INCH],
               [base_dx-INCH, base_dy-INCH],
               [0*INCH, base_dy-INCH]]

R1_CC_PBS_pos = [7*INCH, INCH]

for xy in mount_holes:
	layout.place_element("Screw_hole_baseplate", optomech.baseplate_mount, xoff+xy[0], yoff+xy[1], 0)

beam = layout.add_beam_path(base_dx-ddy, 0, 90)



# Lens Options:
def f100cx_to_f030cx():
    layout.place_element_along_beam("f100cx", optomech.lens_holder_l05g, beam, 0b1, -90, 15)
    layout.place_element_along_beam("f030cx", optomech.lens_holder_l05g, beam, 0b1, 90, 130)

def f75cx_to_f030cc():
    layout.place_element_along_beam("f75cx", optomech.lens_holder_l05g, beam, 0b1, -90, 15)
    layout.place_element_along_beam("f030cc", optomech.lens_holder_l05g, beam, 0b1, 90, 45)


# Create Beam Path
layout.place_element("Input_Fiberport", optomech.fiberport_holder, base_dx-ddy, 0, 90)

layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, -135, 1*INCH)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, 45, 1*INCH)

#f100cx_to_f030cx()
f75cx_to_f030cc()

layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, -45, 15)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, 135, 1*INCH)

layout.place_element("Output_Fiberport", optomech.fiberport_holder, base_dx-ddy, base_dy, 270)



layout.redraw()