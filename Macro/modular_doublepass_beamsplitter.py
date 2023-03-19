import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
from math import *

reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

gap = 0.5*INCH
base_dx = 5*INCH-gap
base_dy = 10*INCH-gap
base_dz = INCH

base_split = INCH/4

ddx = INCH
ddy = 1.5*INCH

aom_dy = 70


input_y = base_dy-3.5*INCH+gap/2


''' 'Cardinal' beam directions'''
left = -90
right = left + 180
up = 180
down = up - 180 

# Turns
up_right = 45
right_up = up_right-180
left_down = up_right
down_left = right_up
left_up = up_right +90
up_left = left_up-180
right_down = up_left

name = "baseplate_modular_doublepass"
layout.create_baseplate(base_dx, base_dy, base_dz, name=name)

beam = layout.add_beam_path(base_dx, input_y, -180)
# aom_beam_minus1 = layout.add_beam_path(19, input_y-10, left+0.026*180/pi)  #https://isomet.com/PDF%20acousto-optics_modulators/data%20sheets-moduvblue/M1250-T250L-0.45.pdf


layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, up_right, 15)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, right_up,  INCH)

layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, up, 55)
layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, up, 25)

layout.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam, 0b11, right, 35, diff_angle=0)
layout.place_element_along_beam("Quarter_waveplate", optomech.rotation_stage_rsp05, beam, 0b11, left, 60)
layout.place_element_along_beam("f_100_Collimation_Lens", optomech.lens_holder_l05g, beam_obj=beam, beam_index=0b11, angle=left, distance=40, foc_len=100)
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11, right, 15)
layout.place_element_along_beam("Retro_Mirror", optomech.mirror_mount_k05s2, beam, 0b11, right, 15)

layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b110, right_down, 30)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b110, down_left, 55)
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b110, right, 125)
layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b110, left, 70)
layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b110, right, y=0)

layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-0.5)*INCH-gap/2, (1-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (3-0.5)*INCH-gap/2, (3-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-0.5)*INCH-gap/2, (10-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (1-0.5)*INCH-gap/2, (8-0.5)*INCH-gap/2, 0)
# layout.place_element("Mount_Hole", optomech.baseplate_mount, (3-0.5)*INCH-gap/2, (3-0.5)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-0.5)*INCH-gap/2, (5-0.5)*INCH-gap/2, 0)

#set view
Gui.activeDocument().activeView().viewTop()
Gui.activeDocument().activeView().viewRotateRight()
Gui.SendMsgToActiveView("ViewFit")
Gui.runCommand('Std_ViewZoomIn',0)

#'compile the baseplate'
layout.redraw()

#prepare for export
import Mesh

filename = App.getUserMacroDir(True) + "stl/" + name + ".stl" #Filename for model
print(filename)
obj = App.ActiveDocument.getObject(name) 	# get baseplate object
Gui.Selection.addSelection(obj) 			# select baseplate
__objs__ = Gui.Selection.getSelection() 	# get selection for meshing
Mesh.export(__objs__, filename) 			#Mesh and export (as .stl given filename)

print('Done!')