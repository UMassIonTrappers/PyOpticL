import sys
sys.path.append("%USERPROFILE%/Dropbox/UMass Ions/FreeCAD/Macro/optics")

import FreeCAD as App

from optics import laser, layout, optomech

from importlib import reload
import math
reload(optomech)
reload(layout)
reload(laser)

INCH = 25.4

base_dx = 7.25*INCH
base_dy = 4.25*INCH
base_dz = INCH

pr_axis_x = 20
pr_axis_y = base_dy-83
pm_axis_x = base_dx-20
pm_axis_y = base_dy-38

hcl_xpos = (pm_axis_x+pr_axis_x)/2

pm_beam_ang = 3
pm_ang_off = 0.5*pm_beam_ang
pm_y_off = (hcl_xpos-pm_axis_x)*math.tan(math.radians(pm_beam_ang))

layout.create_baseplate(base_dx, base_dy, base_dz)

layout.add_beam_path(pr_axis_x, base_dy, -90)

layout.place_element("Fiberport", optomech.fiberport_holder, pr_axis_x, base_dy, -90)

layout.place_element("Input_Rotation_Stage", optomech.rotation_stage_rsp05, pr_axis_x, base_dy-15, -90)

layout.place_element("Input_Beam_Splitter", optomech.pbs_on_skate_mount, pr_axis_x, pm_axis_y, -90)

layout.place_element("Probe_Mirror_1", optomech.mirror_mount_k05s2, pr_axis_x, pr_axis_y, 45)

layout.place_element("Pump_Mirror_1", optomech.mirror_mount_k05s2, pm_axis_x+3, pm_axis_y-3, -135)

layout.place_element("Pump_Mirror_2", optomech.mirror_mount_k05s2, pm_axis_x, pr_axis_y+pm_y_off, 135-pm_ang_off)

layout.place_element("Pump_Rotation_Stage", optomech.rotation_stage_rsp05, 50, pm_axis_y, 0)

layout.place_element("Probe_Mirror_2", optomech.mirror_mount_c05g, 80, pm_axis_y-10, 45+pm_ang_off)