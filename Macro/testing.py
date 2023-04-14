import FreeCAD as App
from freecadOptics import laser, layout, optomech

from importlib import reload
import math

reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

layout.create_baseplate(200, 200, layout.INCH)

beam = layout.add_beam_path(100, 200, 180)
#beam2 = layout.add_beam_path(104, 200, -90)
#beam3 = layout.add_beam_path(96, 200, -90)

layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, -90, 25)
layout.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam, 0b11, 90, 30,  diff_dir=(1,-1), exp=True)
layout.place_element_along_beam("Quarter_waveplate", optomech.rotation_stage_rsp05, beam, 0b110, -90, 70, wave_plate_part_num = '') #421nm custom waveplates from CASIX
layout.place_element_along_beam("Lens_f_100mm_AB_coat", optomech.lens_holder_l05g, beam, 0b110, -90, 30, foc_len=100, lens_part_num='LA1213-AB')
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b110, -90, 7)
layout.place_element_along_beam("Retro_Mirror", optomech.mirror_mount_km05, beam, 0b110, 90, 7)


#layout.place_element("AOM", optomech.isomet_1205c_on_km100pm, 50, 50, 0)

#layout.place_element("Input_Fiberport", optomech.fiberport_holder, 100, 200, -90)
#layout.place_element("Periscope1", optomech.periscope, -50, 50, 0, lower_dz=layout.INCH*3/2, upper_dz=80, table_mount=True, left_handed=True)
# layout.place_element("Periscope2", optomech.periscope, -50, 100, 0, lower_dz=layout.INCH*3/2, upper_dz=50, table_mount=True)

#layout.place_element("Periscope3", optomech.periscope, -50, 100, 0, lower_dz=layout.INCH*3/2, upper_dz=50+INCH, table_mount=True)
#layout.place_element("Periscope Fixed", optomech.periscope_fixed, -50, 200, 0, lower_dz=layout.INCH*3/2, upper_dz=50+INCH, table_mount=True)
# layout.place_element("Periscope4", optomech.periscope, -50, 300, 0, lower_dz=layout.INCH*3/2, upper_dz=50+INCH, table_mount=True,lower_mirror=layout.mirror_mount_c05g, upper_mirror=layout.mirror_mount_c05g)

#layout.place_element_along_beam("Testing2", optomech.lens_holder_l05g, beam_obj=beam, beam_index=0b1, angle=90, distance=100)
#layout.place_element_along_beam("Wavemeter_Mirror_1", optomech.pinhole_ida12, beam_obj=beam, beam_index=0b1, angle=-90, distance=25)
#layout.place_element_along_beam("Input_Rotation_Stage", optomech.rotation_stage_rsp05, beam_obj=beam, beam_index=0b1, angle=-90, distance=80)
#layout.place_element_along_beam("Beam_Splitter_1", optomech.pbs_on_skate_mount, beam, 0b1, -90, 50)

layout.redraw()