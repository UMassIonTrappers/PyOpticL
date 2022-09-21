import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

## Delete old components
try:
    for ShapeNameObj in FreeCAD.ActiveDocument.Objects:
            App.ActiveDocument.removeObject(ShapeNameObj.Name)        # remove objects not selecteds
except Exception:
    None


INCH = 25.4

base_dx = 7*INCH
base_dy = 12*INCH
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

for xy in mount_holes:
	layout.place_element("Screw_hole_baseplate", optomech.baseplate_mount, xoff+xy[0], yoff+xy[1], 0)

input_x = INCH

layout.add_beam_path(input_x, base_dy, -90)

beampos = [input_x,base_dy]

layout.place_element_pos("Input_Fiberport", optomech.fiberport_holder, beampos, -90)

beampos[1] += -ddy
layout.place_element_pos("Input_Mirror_1", optomech.mirror_mount_k05s2, beampos, 45)

beampos[0] += +ddx
layout.place_element_pos("Input_Mirror_2", optomech.mirror_mount_k05s2, beampos,  -135)

beampos[1] += -ddy
layout.place_element_pos("Half_waveplate", optomech.rotation_stage_rsp05, beampos, -90)

beampos[1] += -1*ddy
layout.place_element_pos("Beam_Splitter_1", optomech.pbs_on_skate_mount, beampos, -90)

# 1st split
beampos2 = beampos.copy()

beampos2[0] += +3*ddx
layout.place_element_pos("AOM_1", optomech.isomet_1205c_on_km100pm, beampos2, 0)

beampos2[0] += +ddx
layout.place_element_pos("Output_Mirror_1", optomech.mirror_mount_k05s2, beampos2, -135)

beampos2[1] += -1.25*ddy
layout.place_element_pos("Output_Mirror_2", optomech.mirror_mount_k05s2, beampos2,  135)

layout.place_element("Output_Fiberport", optomech.fiberport_holder, 0, beampos2[1], 0)

# 2nd split
beampos3 = beampos.copy()
beampos3[1] = beampos2[1] # update y

beampos3[1] += -0.5*ddy
layout.place_element_pos("Half_waveplate_2", optomech.rotation_stage_rsp05, beampos3, -90)

beampos3[1] += -1*ddy
layout.place_element_pos("Beam_Splitter_2", optomech.pbs_on_skate_mount, beampos3, -90)

beampos3[0] += +3*ddx
layout.place_element_pos("AOM_2", optomech.isomet_1205c_on_km100pm, beampos3, 0)

beampos3[0] += +ddx
layout.place_element_pos("Output_2_Mirror_1", optomech.mirror_mount_k05s2, beampos3, -135)

beampos3[1] += -1.25*ddy
layout.place_element_pos("Output_2_Mirror_2", optomech.mirror_mount_k05s2, beampos3,  135)

layout.place_element("Output_Fiberport_2", optomech.fiberport_holder, 0, beampos3[1], 0)

#layout.redraw()


#layout.place_element("Probe_Mirror_2", optomech.mirror_mount_c05g, 80, pm_axis_y-10, 45+pm_ang_off)


