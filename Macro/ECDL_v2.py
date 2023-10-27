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

base_dx = 7*layout.inch
base_dy = 5*layout.inch
base_dz = layout.inch

baseplate = layout.baseplate(base_dx, base_dy, base_dz, gap=layout.inch/8, mount_holes=[[3,0],[0,4],[6,0],[4,4]], name=name, label=label)

layout.table_grid(10, 10, -3/2*layout.inch)

'''
Add Beam(s)
'''
input_x = 45
input_y = 35
beam = baseplate.add_beam_path(input_x, input_y, layout.cardinal['right'])


"""
Add Optical Elements
"""

baseplate.place_element("Laser_diode_LT230P-B", optomech.km05_50mm_laser, input_x, input_y, layout.cardinal['right'])

baseplate.place_element_along_beam("Grating", optomech.grating_mount_on_mk05pm, beam, 0b1, layout.cardinal['left'], 40, littrow_angle=littrow_angle)

if wavelength == 422e-6:
    baseplate.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_km05, beam, 0b1, layout.turn['right-up'], 80)
    baseplate.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_km05, beam, 0b1, layout.turn['up-left'], 40)
    baseplate.place_element_along_beam("Optical_Isolator", optomech.isolator_405, beam, 0b1, layout.cardinal['left'], 55, adapter_args=dict(mount_hole_dy=45))
elif wavelength == 674e-6:
    baseplate.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_km05, beam, 0b1, layout.turn['right-up'], 70)
    baseplate.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_km05, beam, 0b1, layout.turn['up-left'], 40)
    baseplate.place_element_along_beam("Optical_Isolator", optomech.isolator_670, beam, 0b1, layout.cardinal['left'], 55, adapter_args=dict(mount_hole_dy=45))

baseplate.place_element_along_beam("Fiber Coupler", optomech.fiberport_mount_km05, beam, 0b1, layout.cardinal['right'], 65)

#for i in [[2,0],[2,3],[5,0],[4,3]]:
#    baseplate.place_element("Mount_Hole%s"%(str(i)), optomech.baseplate_mount, (i[0])*layout.inch+grid_offset, (i[1])*layout.inch+grid_offset, 0)

layout.redraw()