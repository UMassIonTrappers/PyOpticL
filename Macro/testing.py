import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math

reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

layout.create_baseplate(200, 200, layout.INCH)

beam = layout.add_beam_path(100, 200, -90)
#beam2 = layout.add_beam_path(104, 200, -90)
#beam3 = layout.add_beam_path(96, 200, -90)

layout.place_element_along_beam("AOM_R2", optomech.isomet_1205c_on_km100pm, beam, 0b11, -90, 50, diff_dir=(-1,1))

#layout.place_element("Input_Fiberport", optomech.fiberport_holder, 100, 200, -90)
# layout.place_element("Periscope1", optomech.periscope, -50, 50, 0, lower_dz=layout.INCH*3/2, upper_dz=80, table_mount=True)
# layout.place_element("Periscope2", optomech.periscope, -50, 100, 0, lower_dz=layout.INCH*3/2, upper_dz=50, table_mount=True)

#layout.place_element("Periscope3", optomech.periscope, -50, 100, 0, lower_dz=layout.INCH*3/2, upper_dz=50+INCH, table_mount=True)
#layout.place_element("Periscope Fixed", optomech.periscope_fixed, -50, 200, 0, lower_dz=layout.INCH*3/2, upper_dz=50+INCH, table_mount=True)
# layout.place_element("Periscope4", optomech.periscope, -50, 300, 0, lower_dz=layout.INCH*3/2, upper_dz=50+INCH, table_mount=True,lower_mirror=layout.mirror_mount_c05g, upper_mirror=layout.mirror_mount_c05g)

#layout.place_element_along_beam("Testing2", optomech.lens_holder_l05g, beam_obj=beam, beam_index=0b1, angle=90, distance=100)
#layout.place_element_along_beam("Wavemeter_Mirror_1", optomech.pinhole_ida12, beam_obj=beam, beam_index=0b1, angle=-90, distance=25)
#layout.place_element_along_beam("Input_Rotation_Stage", optomech.rotation_stage_rsp05, beam_obj=beam, beam_index=0b1, angle=-90, distance=80)
#layout.place_element_along_beam("Beam_Splitter_1", optomech.pbs_on_skate_mount, beam, 0b1, -90, 50)

layout.redraw()
