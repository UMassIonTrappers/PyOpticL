import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4
ddx = INCH
ddy = 1.5*INCH


# aom_dy = 70
# base_split = INCH/4


''' 'Cardinal' beam direction definitions'''
left = -90
right = left + 180
down = left + 90
up = down - 180
# up = 180
# down = up - 180 

# Turn angle definitions
up_right = 45
right_up = up_right-180
left_down = up_right
down_left = right_up
left_up = up_right +90
up_left = left_up-180
right_down = up_left


gap = 0.5*INCH
base_dx = 5.0*INCH-gap
base_dy = 8.0*INCH-gap
base_dz = INCH

input_y = base_dy-1.0*INCH+gap/2


name="baseplate_modular_noise_eater"

layout.create_baseplate(base_dx, base_dy, base_dz, name=name)

beam = layout.add_beam_path(base_dx, input_y, -180)
exit_beam = layout.add_beam_path(0, input_y, 0)


layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, up_left, 0.75*INCH)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_c05g, beam, 0b1, left_up-0*45/2, INCH)
layout.place_element_along_beam("Input_Mirror_3", optomech.mirror_mount_k05s2, beam, 0b1, up_left-0*45/2, INCH)

layout.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm_doublepass, beam, 0b1, right, 1.25*INCH)

layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b1, right, 2.75*INCH)

layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, left_up, INCH)
layout.place_element_along_beam("Pick_off", optomech.splitter_mount_c05g, beam, 0b1, up_left, INCH)
# layout.place_element_along_beam("PD_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b11, down_left, 15)

layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b10, up_right, INCH) 

layout.place_element_along_beam("Output_Mirror_3", optomech.mirror_mount_k05s2, beam, 0b10, right_up, 6*INCH)

offset_x = 0
offset_y = 0.5
layout.place_element("Mount_Hole", optomech.baseplate_mount, (1-offset_y)*INCH-gap/2, (2-offset_x)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (2-offset_y)*INCH-gap/2, (4-offset_x)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (1-offset_y)*INCH-gap/2, (7-offset_x)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-offset_y)*INCH-gap/2, (7-offset_x)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (5-offset_y)*INCH-gap/2, (1-offset_x)*INCH-gap/2, 0)

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