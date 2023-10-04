from freecadOptics import layout, optomech

from math import *
import datetime
from datetime import datetime
import numpy as np



INCH = 25.4

aom_dy = 70
base_split = INCH/4

gap = 0.5*INCH
base_dx = 5.0*INCH-gap
base_dy = 8.0*INCH+10-gap #MAX size of resin printer
base_dz = INCH

input_y = base_dy-3.0*INCH+gap/2+5

''' 'Cardinal' beam directions'''
down = 0 
up = down+ 180
left = down - 90
right = left + 180

# Turns
up_right = 45
right_up = up_right-180
left_down = up_right
down_left = right_up
left_up = up_right +90
up_left = left_up-180
right_down = up_left


"""
Start BASEPLATE

References: http://strontiumbec.com/StrontiumLab/Theses/Tim_van_Leent_master_thesis.pdf

https://arxiv.org/ftp/arxiv/papers/2303/2303.01171.pdf
Thorlabs GH13-24V (1mm/2400)
PZT - Thorlabs AE0505D08F

"""

wavelength = 674e-6 #wavelength in mm (not nm)
grating_pitch_d = 1/2400
print(wavelength/(2*grating_pitch_d))
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
print(littrow_angle) #should be about 55 degrees
#for narrow linewith --> small pitch and large angle

"""
Linewidth narrowing (eta) : eta = (t_int/ (t_int + t_ext))**2
"""
l_int = 0.250 #mm
l_ext = 40.0 #mm 
eta = (l_int/ (l_int + l_ext))**2
print(1/eta)


name = "ECDL_Resin"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time
print("label name date and time:",label)
label = ''
layout.create_baseplate(base_dx, base_dy, base_dz, name=name, label=label)


'''
Add Beam(s)
'''
input_x = 2*INCH
input_y = 1*INCH
beam = layout.add_beam_path(input_x, input_y, right)

# AOM_location_x = 18.3
# aom_beam_minus1 = layout.add_beam_path(AOM_location_x, input_y-7, left+0.026*180/pi)  #https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf


"""
Add Optical Elements
"""

layout.place_element("Laser_diode_LT230P-B", optomech.laser_diode_mount, input_x, input_y, left)

layout.place_element_along_beam("Grating", optomech.laser_grating_mount, beam, 0b1, left+littrow_angle, 40)
layout.place_element_along_beam("Parallel_Mirror", optomech.mirror_mount_k05s1, beam, 0b1, left+littrow_angle+180, 15)

# layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s1, beam, 0b1, right_down, 40)
# layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s1, beam, 0b1, left_up, 20)

layout.place_element_along_beam("Optical_Isolator", optomech.isolator_670, beam, 0b1, right, 2*INCH)


layout.redraw()