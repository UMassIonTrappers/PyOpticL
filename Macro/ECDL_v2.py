from freecadOptics import layout, optomech

from math import *
import datetime
from datetime import datetime
import numpy as np



"""
Start BASEPLATE

References: http://strontiumbec.com/StrontiumLab/Theses/Tim_van_Leent_master_thesis.pdf

https://arxiv.org/ftp/arxiv/papers/2303/2303.01171.pdf
Thorlabs GH13-24V (1mm/2400)
PZT - Thorlabs AE0505D08F

"""

wavelength = 422e-6 #wavelength in mm (not nm)
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


name = "ECDL_v2"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time
print("label name date and time:",label)
label = ''

grid_offset = layout.INCH/2
gap = layout.INCH/2
base_dx = 7*layout.INCH-gap
base_dy = 4.5*layout.INCH-gap
base_dz = layout.INCH

layout.create_baseplate(base_dx, base_dy, base_dz, name=name, label=label)


'''
Add Beam(s)
'''
input_x = 40
input_y = 30
beam = layout.add_beam_path(input_x, input_y, layout.cardinal['right'])


"""
Add Optical Elements
"""

layout.place_element("Laser_diode_LT230P-B", optomech.km05_50mm_laser, input_x, input_y, layout.cardinal['right'])

layout.place_element_along_beam("Grating", optomech.grating_mount_on_mk05pm, beam, 0b1, layout.cardinal['left'], 40, littrow=littrow_angle)

if wavelength == 422e-6:
    layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, layout.turn['right-up'], 80)
    layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, layout.turn['up-left'], 40)
    layout.place_element_along_beam("Optical_Isolator", optomech.isolator_405, beam, 0b1, layout.cardinal['left'], 55, mount_hole_dy=45)
elif wavelength == 674e-6:
    layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, layout.turn['right-up'], 70)
    layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, layout.turn['up-left'], 40)
    layout.place_element_along_beam("Optical_Isolator", optomech.isolator_670, beam, 0b1, layout.cardinal['left'], 55, mount_hole_dy=45)

layout.place_element_along_beam("Optical_Isolator", optomech.fiberport_mount_km05, beam, 0b1, layout.cardinal['right'], 70)

for i in [[2,0],[2,3],[5,0],[4,3]]:
    layout.place_element("Mount_Hole%s"%(str(i)), optomech.baseplate_mount, (i[0])*layout.INCH+grid_offset, (i[1])*layout.INCH+grid_offset, 0)

layout.redraw()