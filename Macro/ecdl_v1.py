import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
from math import *
import os
import datetime
from datetime import datetime
import numpy as np

reload(optomech)
reload(layout)
reload(laser)


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


# layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, right, 50, wave_plate_part_num = '') #421nm custom waveplates from CASIX


# layout.place_element("Laser_diode_LT230P-B", optomech.laser_diode_mount, beam, 0b1, left, 10) #Mounted in LT230P-B (but check wavelength coating! B is red, A is blue)





# layout.place_element_along_beam("Input_Mirror_1", mirror_mounts, beam, 0b1, up_right, 16)
# layout.place_element_along_beam("Input_Mirror_2", mirror_mounts, beam, 0b1, right_up,  INCH)
# layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, up, 55, wave_plate_part_num = '') #421nm custom waveplates from CASIX
# layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, up, 25)

# layout.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam, 0b11, right, 30, diff_angle=0)
# layout.place_element_along_beam("Quarter_waveplate", optomech.rotation_stage_rsp05, beam, 0b11, left, 70, wave_plate_part_num = '') #421nm custom waveplates from CASIX
# layout.place_element_along_beam("Lens_f_100mm_AB_coat", optomech.lens_holder_l05g, beam, 0b11, left, 30, foc_len=100, lens_part_num='LA1213-AB')
# layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11, right, 7)
# layout.place_element_along_beam("Retro_Mirror", mirror_mounts, beam, 0b11, right, 7)

# layout.place_element_along_beam("Output_Mirror_1", mirror_mounts, beam, 0b110, right_down, 20)
# # layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b110, down, 25)
# layout.place_element_along_beam("Output_Mirror_2", mirror_mounts, beam, 0b110, down_left, 55)
# layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b110, left, 100, wave_plate_part_num = '') #421nm custom waveplates from CASIX
# layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b110, right, y=0)


"""
Add holes to baseplate to mount to optical table 
 >>> Make sure to align laser beam above bolt holes so plates line up together <<<
"""
offset = -15/INCH # arbitrary shift to make sure laser is over bolt holes
# layout.place_element("Mount_Hole", optomech.baseplate_mount, (2-offset)*INCH-gap/2, (1-offset)*INCH-gap/2, 0)
# layout.place_element("Mount_Hole", optomech.baseplate_mount, (4-offset)*INCH-gap/2, (1-offset)*INCH-gap/2, 0)
# layout.place_element("Mount_Hole", optomech.baseplate_mount, (3-offset)*INCH-gap/2, (4-offset)*INCH-gap/2, 0)
# layout.place_element("Mount_Hole", optomech.baseplate_mount, (3-offset)*INCH-gap/2, (6-offset)*INCH-gap/2, 0)
# layout.place_element("Mount_Hole", optomech.baseplate_mount, (2-offset)*INCH-gap/2, (7-offset)*INCH-gap/2, 0)


#set view
Gui.activeDocument().activeView().viewTop()
Gui.activeDocument().activeView().viewRotateRight()
Gui.SendMsgToActiveView("ViewFit")
Gui.runCommand('Std_ViewZoomIn',0)

#'compile the baseplate'
layout.redraw()

# #prepare for export
# import Mesh

# filename = App.getUserMacroDir(True) + "stl/" + name + ".stl" #Filename for model
# print(filename)
# obj = App.ActiveDocument.getObject(name) 	# get baseplate object
# Gui.Selection.addSelection(obj) 			# select baseplate
# __objs__ = Gui.Selection.getSelection() 	# get selection for meshing
# Mesh.export(__objs__, filename) 			#Mesh and export (as .stl given filename)

print('Done!')