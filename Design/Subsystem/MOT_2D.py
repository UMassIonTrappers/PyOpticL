import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))

import numpy as np                
from PyOpticL import layout, optomech
from Rb_SAS import Rb_SAS
from modular_doublepass import doublepass_f50
from input_telescope import telescope
from modular_sourcebox import sourcebox
from ECDL import ECDL
from ECDL_Isolator_plate import ECDL_isolator_baseplate

# Magneto Optical Trap (MOT) setup
# under construction

# using 780.24 nm for Rb85 D2 line
# cooling transition is 5S1/2 F=3 -> 5P3/2 F=4
# Frequency: 384.230 THz

# repumping transition is 5S1/2 F=2 -> 5P3/2 F=3
# Frequency: 384.230 THz - 3.035 GHz ≈ 384.227 THz

# wavelength = 780.24e-6   #wavelength in mmS
# grating_pitch_d = 1/3600   # Lines per mm
# littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi

# layout.table_grid(dx=10, dy=20)

################################################## laser system ######################################
# ECDL(x=11.3 ,y=4 , angle=90, littrow_angle = littrow_angle) # ECDL for 780.24 nm
# ECDL_isolator_baseplate(x=14, y= 9 , angle=layout.cardinal['up'])
# telescope(x=14 , y=16 , angle=90) # reduce beam size
# Rb_SAS(x=0 , y=20, thumbscrews=True) # lock scheme
# telescope(x=0 , y=0 , angle=0) # expand beam size

# sourcebox(x=0 , y=0, angle=0) # sourcebox for 780.24 nm repumping
# periscope 
# doublepass_f50
# telescope
############################################## beam routing around chamber ######################
# retro unit
def retro_unit(x, y, angle, mirror_mount_type = optomech.mirror_mount_km05):
    baseplate = layout.baseplate(dx = 2.3 * layout.inch, dy = 2 * layout.inch, dz =1 *layout.inch , x=x, y=y, angle=angle, mount_holes=[(1,1),(0,1)], x_offset=0.2*layout.inch, y_offset=0.5*layout.inch, gap=1/8 * layout.inch)
    baseplate.place_element("quarter_waveplate", optomech.waveplate, x=0.9 * layout.inch, y=1.5 * layout.inch, angle=0, mount_type = optomech.rotation_stage_rsp05)
    baseplate.place_element("retro mirror", optomech.circular_mirror, x=1.75 * layout.inch, y=1.5 * layout.inch, angle=180, mount_type = mirror_mount_type)
    baseplate.add_beam_path(x = 0 *layout.inch, y = 1.5 *layout.inch, angle = 0)

# turn unit
def turn_unit(x, y, angle, type = 'left', mirror_mount_type = optomech.mirror_mount_km05):
    baseplate = layout.baseplate(dx = 3.1 * layout.inch, dy = 2.2 * layout.inch, dz =1 *layout.inch , x=x, y=y, angle=angle, mount_holes=[(3,0),(1,0)], x_offset=1.2*layout.inch, y_offset=0.1*layout.inch, gap = layout.inch/8)
    if type == 'left': angle_ = 135
    elif type == 'right': angle_ = -135
    baseplate.place_element("turn mirror", optomech.circular_mirror, x=2.5 * layout.inch, y=1.5 * layout.inch, angle=angle_, mount_type = mirror_mount_type)   
    baseplate.place_element("quarter_waveplate", optomech.waveplate, x=1.8 * layout.inch, y=1.5 * layout.inch, angle=0, mount_type = optomech.rotation_stage_rsp05)
    baseplate.add_beam_path(x = 0 *layout.inch, y = 1.5 *layout.inch, angle = 0) 

# input baseplate
def input_baseplate(x, y, angle, mirror_mount_type = optomech.mirror_mount_km05, addition_length = 0):
    baseplate = layout.baseplate(dx = 4 * layout.inch, dy = 5 * layout.inch + addition_length, dz =1 *layout.inch , x=x, y=y, angle=angle, mount_holes=[(1,0), (1,2), (3,0), (3,4)], gap=layout.inch/8, x_offset=0.5*layout.inch)
    beam = baseplate.add_beam_path(x = 1.5 *layout.inch, y = 5*layout.inch, angle = -90)
    baseplate.place_element_along_beam("input mirror 1", optomech.circular_mirror, beam,beam_index=0b1, distance=1 * layout.inch, angle=45, mount_type = mirror_mount_type)
    baseplate.place_element_along_beam("input mirror 2", optomech.circular_mirror, beam,beam_index=0b1, distance=1 * layout.inch + addition_length, angle=-135, mount_type = mirror_mount_type)
    baseplate.place_element_along_beam("pbs", optomech.cube_splitter, beam,beam_index=0b1, distance=1.5 * layout.inch, angle=90, mount_type = optomech.skate_mount_crossholes)
    baseplate.place_element_along_beam("output mirror 1", optomech.circular_mirror, beam,beam_index=0b10, distance=1.5 * layout.inch, angle=135, mount_type = mirror_mount_type)
    baseplate.place_element_along_beam("output mirror 2", optomech.circular_mirror, beam,beam_index=0b10, distance=1 * layout.inch + addition_length, angle=-45, mount_type = mirror_mount_type)

    baseplate.place_element_along_beam("output mirror 3", optomech.circular_mirror, beam,beam_index=0b11, distance=1 * layout.inch, angle=-135, mount_type = mirror_mount_type)
    
# check mount hole for additional length
def MOT_2D_routing(x, y, angle, X = 0, Y = 0):
    '''
    X and Y for additional distance between retro unit and turn unit for chamber volunm, also in unit of inch
    '''

    ##
    input_baseplate(x=5 +x, y=7+y, angle=0+angle, addition_length = X*layout.inch)
    retro_unit(x=5+x, y=2+y - Y, angle=-90+angle) 

    ##
    turn_unit(x=6 + x + X, y=3+y, angle=0+angle, type='left')
    retro_unit(x=6+x - X, y=6+y, angle=180+angle)
    

MOT_2D_routing(x=0, y=0, angle=0, X = 0.2, Y = 0.2)
layout.redraw() # perform drilling in this step

