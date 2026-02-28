## This code generate a our Lab's optical table setup with all the baseplate, laser and vacuum system.
## You just have to place the baseplate in the right position to make your own set up for optical table

import time
start_time=time.time()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
import numpy as np                
from PyOpticL import layout, optomech
from Rb_SAS import Rb_SAS
# from modular_doublepass import doublepass_f50, doublepass_f100
from input_telescope import telescope
from modular_sourcebox import sourcebox
# from ECDL import ECDL
from ECDL_Isolator_plate import ECDL_isolator_baseplate

# from Modulation_Transfer_Spectroscopy import modified_doublepass
from Modulation_Transfer_Spectroscopy import Rb_SAS
from Modulation_Transfer_Spectroscopy import modular_transfer_cell

#A full table has dx=44 and dy=92
#layout.table_grid(dx=28, dy=55)

# # #422nm and RB Cell
wavelength = 422e-6   #wavelength in mm
grating_pitch_d = 1/3600   # Lines per mm
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
## The baseplate works as a doublepass. The beam passes through the AOM twice and sweep/change the frequebcy twice. 
# The design has two different style for 50mm focus and for 100mm focus. Both work in the same way expect the added distant for the 100mm lens. 

from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np

INCH = layout.inch
#1/2 inch shorter for f50 since we are using shorter focal length
# Combining the baseplate with the beam and all other optical componenets. 
# def doublepass_f50(x=0, y=0, angle=0, mirror=optomech.mirror_mount_k05s2, x_split=True, thumbscrews=True):
    
#     # Adding name and date to keep a track of the updates
#     name = "Doublepass"
#     date_time = datetime.now().strftime("%m/%d/%Y")
#     label = "" #name + " " +  date_time

#     # Dimension of the baseplate 
#     base_dx = 9.5*layout.inch
#     base_dy = 5*layout.inch
#     base_dz = layout.inch
#     gap = layout.inch/8

#     input_x = 6.5*layout.inch

#     mount_holes = [(0, 0),   (8, 3)]
#     extra_mount_holes = [(2, 0), (1, 2), (4, 0),(4,4), (6, 2)]
    
#     # Difining the baseplate
#     baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
#                                  gap=gap, mount_holes=mount_holes+extra_mount_holes,
#                                  name=name, label=label, x_splits=[3.6*layout.inch]*x_split)
    
#     # Adding the beam to the baseplate
#     beam = baseplate.add_beam_path(input_x, gap, layout.cardinal['up'])

#     # Adding input fiberport to send the beam into the baseplate
#     baseplate.place_element("Input Fiberport", optomech.fiberport_mount_hca3, x = 165.10,y=2.6,
#                                        angle=layout.cardinal['up'])
    
#     ## Adding two mirrors to give the beam enough degree of freedom. Mirror 1
#     baseplate.place_element_along_beam("Input Mirror 1", optomech.circular_mirror, beam,
#                                        beam_index=0b1, distance=18-4+3, angle=layout.turn['up-right'],
#                                        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
#     # Miror 2
#     baseplate.place_element_along_beam("Input Mirror 2", optomech.circular_mirror, beam,
#                                        beam_index=0b1, distance=layout.inch, angle=layout.turn['right-up'],
#                                        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
#     # Adding a waveplate to control the ploarization
#     baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam,
#                                        beam_index=0b1, distance=50+4-3, angle=layout.cardinal['up'],
#                                        mount_type=optomech.rotation_stage_rsp05)
    
#     # Adding beam splitter to divide the beam to : to saty on the baseplate and to to send to the next baseplate
#     baseplate.place_element_along_beam("Beam Splitter", optomech.cube_splitter, beam,
#                                        beam_index=0b1, distance=32, angle=layout.cardinal['up'],
#                                        mount_type=optomech.skate_mount)
    
#     # Adding AOM
#     baseplate.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam,
#                                        beam_index=0b11, distance=55, angle=layout.cardinal['left'],
#                                        forward_direction=-1, backward_direction=1)
    
#     # Adding lens make collimated beam. 
#     lens = baseplate.place_element_along_beam("Lens f50mm AB coat", optomech.circular_lens, beam,
#                                               beam_index=0b110, distance=50, angle=layout.cardinal['right'],
#                                               focal_length=50, part_number='LA1213-AB', mount_type=optomech.lens_holder_l05g)
    
#     # Adding half waveplate to control the polarization
#     baseplate.place_element_along_beam("Quarter waveplate", optomech.waveplate, beam,
#                                        beam_index=0b110, distance=24, angle=layout.cardinal['left'],
#                                        mount_type=optomech.rotation_stage_rsp05)
    
#     # Adding iris to select the right order of beam
#     baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam,
#                                        beam_index=0b111, distance=50- 24 - 13.5+5, angle=layout.cardinal['right'],
#                                        pre_refs=2, adapter_args=dict(drill_offset=-2))
    
#     # Adding another mirror to send the beam back into the AOM
#     baseplate.place_element_relative("Retro Mirror", optomech.circular_mirror, lens,
#                                      x_off=-50, angle=layout.cardinal['right'],
#                                      mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
#     # Adding output mirror to send the beam properly to the fiberport. Mirror 1
#     baseplate.place_element_along_beam("Output Mirror 1", optomech.circular_mirror, beam,
#                                        beam_index=0b11110, distance=30, angle=layout.turn['right-down'],
#                                        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
#     # Mirror 2
#     baseplate.place_element_along_beam("Output Mirror 2", optomech.circular_mirror, beam,
#                                        beam_index=0b11110, distance=16 + 42-10, angle=layout.turn['down-left'], 
#                                        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
#     # Adding half waveplate to control the polarization
#     baseplate.place_element_along_beam("Half waveplate Out", optomech.waveplate, beam,
#                                        beam_index=0b11110, distance=110, angle=layout.cardinal['left'],
#                                        mount_type=optomech.rotation_stage_rsp05)
    
#     # Fiberport to fiber the beam
#     baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_mount_hca3, beam,
#                                       beam_index=0b11110, x=gap-1, angle=layout.cardinal['right'])
    # baseplate.add_cover(dz=45)

# If we use a 100mm lens instead of 50 mm
#same input and output position
# Combining the baseplate with the beam and all other optical componenets. 
def doublepass_f100(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, x_split=False, thumbscrews=True):
    
    # Adding name and date to keep a track of the updates
    name = "Doublepass"
    date_time = datetime.now().strftime("%m/%d/%Y")
    label = name + " " +  date_time

    # Dimension of the baseplate
    base_dx = 13.5*layout.inch
    base_dy = 5*layout.inch
    base_dz = layout.inch
    gap = layout.inch/8

    input_x = 10.5*layout.inch

    mount_holes = [(0, 0),   (8, 3)]
    extra_mount_holes = [(2, 0), (1, 2), (4, 0), (6, 2)]

    # Difining the baseplate
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits=[4*layout.inch]*x_split)
    
    # Adding the beam to the baseplate
    beam = baseplate.add_beam_path(input_x, gap, layout.cardinal['up'])
    
    # Adding input fiberport to send the beam into the baseplate
    baseplate.place_element("Input Fiberport", optomech.fiberport_mount_hca3, x = 266.7,y=2.6,
                                       angle=layout.cardinal['up'])
    
    # Adding two mirrors to give the beam enough degree of freedom. Mirror 1
    baseplate.place_element_along_beam("Input Mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=18, angle=layout.turn['up-right'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Mirror 2
    baseplate.place_element_along_beam("Input Mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Adding a waveplate to control the ploarization
    baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam,
                                       beam_index=0b1, distance=50, angle=layout.cardinal['up'],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    # Adding beam splitter to divide the beam to : to saty on the baseplate and to to send to the next baseplate
    baseplate.place_element_along_beam("Beam Splitter", optomech.cube_splitter, beam,
                                       beam_index=0b1, distance=32, angle=layout.cardinal['up'],
                                       mount_type=optomech.skate_mount)
    
    # Adding AOM
    baseplate.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam,
                                       beam_index=0b11, distance=60, angle=layout.cardinal['left'],
                                       forward_direction=-1, backward_direction=1)
    
    #Adding lens make collimated beam. 
    lens = baseplate.place_element_along_beam("Lens f100mm AB coat", optomech.circular_lens, beam,
                                              beam_index=0b110, distance=100, angle=layout.cardinal['right'],
                                              focal_length=100, part_number='LA1213-AB', mount_type=optomech.lens_holder_l05g)
    
    # Adding half waveplate to control the polarization
    baseplate.place_element_along_beam("Quarter waveplate", optomech.waveplate, beam,
                                       beam_index=0b110, distance=40, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    # Adding iris to select the right order of beam
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam,
                                       beam_index=0b111, distance=46, angle=layout.cardinal['right'],
                                       pre_refs=2, adapter_args=dict(drill_offset=-2))
    
    # Adding another mirror to send the beam back into the AOM
    baseplate.place_element_relative("Retro Mirror", optomech.circular_mirror, lens,
                                     x_off=-100, angle=layout.cardinal['right'],
                                     mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))

    # Adding output mirror to send the beam properly to the fiberport. Mirror 1
    baseplate.place_element_along_beam("Output Mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b11110, distance=30, angle=layout.turn['right-down'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Mirror 2
    baseplate.place_element_along_beam("Output Mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b11110, distance=58-10, angle=layout.turn['down-left'],  
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    ## Adding half waveplate to control the polarization
    baseplate.place_element_along_beam("Half waveplate Out", optomech.waveplate, beam,
                                       beam_index=0b11110, distance=110, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    # Adding Iris to select the beam of right order
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam,
                                       beam_index=0b11110, distance=42, angle=layout.cardinal['right'])  

    # Fiberport to fiber the beam                                 
    baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_mount_hca3, beam,
                                      beam_index=0b11110, x=gap, angle=layout.cardinal['right'])
    
    # Cover for the baseplate
    #baseplate.add_cover(dz=45)
def modified_doublepass(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, x_split=False, thumbscrews=True):
    
    # Adding name and date to keep a track of the updates
    name = "Doublepass"
    date_time = datetime.now().strftime("%m/%d/%Y")
    label = ""
    # Dimension of the baseplate
    base_dx = 13.5*layout.inch
    base_dy = 5*layout.inch
    base_dz = layout.inch
    gap = layout.inch/8

    input_x = 10.5*layout.inch
    
    mount_holes = [(0, 0), (8+4, 3), (0, 1)]
    extra_mount_holes = [(2, 0), (1, 2), (4+4, 0),(4+4,4), (6+4, 2)]

    # Difining the baseplate
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits=np.linspace(6.1*layout.inch, 7.6*layout.inch, 10).tolist()*x_split)
    
    # Adding the beam to the baseplate
    beam = baseplate.add_beam_path(input_x, gap, layout.cardinal['up'])
    
    # Adding input fiberport to send the beam into the baseplate
    baseplate.place_element("Input Fiberport", optomech.fiberport_mount_hca3, x = 266.1, y=2.6,
                                       angle=layout.cardinal['up'])
    
    ## Adding two mirrors to give the beam enough degree of freedom. Mirror 1
    baseplate.place_element_along_beam("Input Mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=17, angle=layout.turn['up-right'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Miror 2
    baseplate.place_element_along_beam("Input Mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Adding a waveplate to control the ploarization
    baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam,
                                       beam_index=0b1, distance=55, angle=layout.cardinal['up'],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    # Adding beam splitter to divide the beam to : to saty on the baseplate and to to send to the next baseplate
    baseplate.place_element_along_beam("Beam Splitter", optomech.cube_splitter, beam,
                                       beam_index=0b1, distance=28, angle=layout.cardinal['up'],
                                       mount_type=optomech.skate_mount)
    
    # Adding AOM
    baseplate.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam,
                                       beam_index=0b11, distance=55, angle=layout.cardinal['left'],
                                       forward_direction=-1, backward_direction=1)
    #-----
    #Adding lens make collimated beam. 
    lens = baseplate.place_element_along_beam("Lens f100mm AB coat", optomech.circular_lens, beam,
                                              beam_index=0b110, distance=100, angle=layout.cardinal['right'],
                                              focal_length=100, part_number='LA1213-AB', mount_type=optomech.lens_holder_l05g)
    #----
    
    baseplate.place_element_along_beam("Quarter waveplate", optomech.waveplate, beam,
                                       beam_index=0b110, distance=40, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    # Adding iris to select the right order of beam
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam,
                                       beam_index=0b111, distance=46, angle=layout.cardinal['right'],
                                       pre_refs=2, adapter_args=dict(drill_offset=-2))
    
    # Adding another mirror to send the beam back into the AOM
    baseplate.place_element_relative("Retro Mirror", optomech.circular_mirror, lens,
                                     x_off=-100, angle=layout.cardinal['right'],
                                     mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Adding output mirror to send the beam properly to the fiberport. Mirror 1
    baseplate.place_element_along_beam("Output Mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b11110, distance=30, angle=layout.turn['right-down'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Mirror 2
    baseplate.place_element_along_beam("Output Mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b11110, distance=39.3, angle=layout.turn['down-left'], 
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Adding half waveplate to control the polarization
    baseplate.place_element_along_beam("Half waveplate Out", optomech.waveplate, beam,
                                       beam_index=0b11110, distance=110, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05)
    

    baseplate.place_element("Final Mirror", optomech.circular_mirror,  x=(1.5+4)*INCH, y=(2.5)*INCH,
                                        angle=-45, mount_type=optomech.mirror_mount_c05g, optional=True)
    
    # Fiberport to fiber the beam                                 
    baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_mount_hca3, beam,
                                      beam_index=0b11110, x=gap, angle=layout.cardinal['right'])
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))

def laser_cooling_subsystem(x=0, y=0, angle=0, thumbscrews=True, littrow_angle = littrow_angle, **args_for_doublepass):
    ax = np.sin(np.deg2rad(angle))
    ay = np.cos(np.deg2rad(angle))
    p = lambda dx, dy: dict(x=x + dx * ay - dy * ax, y=y + dx * ax + dy * ay)

    sourcebox(**p(8, 1), angle=0 + angle)  # model for toptica
    layout.place_element_on_table("Periscope", optomech.periscope, **p(10.5, 12.5), z=0, 
                        angle=layout.cardinal['up'] + angle, mirror_args=dict(mount_type=optomech.mirror_mount_k05s1))
    telescope(**p(12, 14), angle=90 + angle)
    Rb_SAS(**p(1, 17), angle=0+angle, mirror=optomech.mirror_mount_km05, thumbscrews=True)
    modified_doublepass(**p(1, 22), angle=0+angle, mirror=optomech.mirror_mount_km05, x_split=True, thumbscrews=True)
    doublepass_f50(**p(6, 28), angle=0+angle, thumbscrews=thumbscrews, x_split=True)
    doublepass_f50(**p(7, 34), angle=0+angle, thumbscrews=thumbscrews, x_split=True)

def doublepass_f50(x=0, y=0, angle=0, mirror=optomech.mirror_mount_k05s2, x_split=False, thumbscrews=True):
    
    # Adding name and date to keep a track of the updates
    name = "Doublepass"
    date_time = datetime.now().strftime("%m/%d/%Y")
    label = "" #name + " " +  date_time

    # Dimension of the baseplate 
    base_dx = 9.5*layout.inch
    base_dy = 5*layout.inch
    base_dz = layout.inch
    gap = layout.inch/8

    input_x = 6.5*layout.inch # should be in integer of grid. it is 6.5 * inch due to the defining or world origin is 0.5 inch offset from table grid

    mount_holes = [(0, 0), (8, 3), ]
    extra_mount_holes = [(2, 0), (1, 2), (4, 0),(4,4), (6, 2)]
    
    # Difining the baseplate
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits=[3.6*layout.inch]*x_split)
    
    # Adding the beam to the baseplate
    beam = baseplate.add_beam_path(input_x, gap, layout.cardinal['up'])

    # Adding input fiberport to send the beam into the baseplate
    baseplate.place_element("Input Fiberport", optomech.fiberport_mount_hca3, x = 165.10, y=2.6,
                                       angle=layout.cardinal['up'])
    
    ## Adding two mirrors to give the beam enough degree of freedom. Mirror 1
    baseplate.place_element_along_beam("Input Mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=17, angle=layout.turn['up-right'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Miror 2
    baseplate.place_element_along_beam("Input Mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Adding a waveplate to control the ploarization
    baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam,
                                       beam_index=0b1, distance=55, angle=layout.cardinal['up'],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    # Adding beam splitter to divide the beam to : to saty on the baseplate and to to send to the next baseplate
    baseplate.place_element_along_beam("Beam Splitter", optomech.cube_splitter, beam,
                                       beam_index=0b1, distance=28, angle=layout.cardinal['up'],
                                       mount_type=optomech.skate_mount)
    
    # Adding AOM
    baseplate.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam,
                                       beam_index=0b11, distance=55, angle=layout.cardinal['left'],
                                       forward_direction=-1, backward_direction=1)
    
    # Adding lens make collimated beam. 
    lens = baseplate.place_element_along_beam("Lens f50mm AB coat", optomech.circular_lens, beam,
                                              beam_index=0b110, distance=50, angle=layout.cardinal['right'],
                                              focal_length=50, part_number='LA1213-AB', mount_type=optomech.lens_holder_l05g)
    
    # Adding half waveplate to control the polarization
    baseplate.place_element_along_beam("Quarter waveplate", optomech.waveplate, beam,
                                       beam_index=0b110, distance=24, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    # Adding iris to select the right order of beam
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam,
                                       beam_index=0b111, distance=17.5, angle=layout.cardinal['right'],
                                       pre_refs=2, adapter_args=dict(drill_offset=-2))
    
    # Adding another mirror to send the beam back into the AOM
    baseplate.place_element_relative("Retro Mirror", optomech.circular_mirror, lens,
                                     x_off=-50, angle=layout.cardinal['right'],
                                     mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Adding output mirror to send the beam properly to the fiberport. Mirror 1
    baseplate.place_element_along_beam("Output Mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b11110, distance=30, angle=layout.turn['right-down'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Mirror 2
    baseplate.place_element_along_beam("Output Mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b11110, distance=39.3, angle=layout.turn['down-left'], 
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Adding half waveplate to control the polarization
    baseplate.place_element_along_beam("Half waveplate Out", optomech.waveplate, beam,
                                       beam_index=0b11110, distance=110, angle=layout.cardinal['left'],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    # Fiberport to fiber the beam
    baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_mount_hca3, beam,
                                      beam_index=0b11110, x=gap-1, angle=layout.cardinal['right'])
if __name__ == "__main__":
    layout.table_grid(dx=17, dy=40)
    laser_cooling_subsystem()
    layout.redraw()