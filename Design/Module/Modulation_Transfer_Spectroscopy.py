from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
# from modular_doublepass_std import doublepass_f50

INCH = 25.4

def modified_doublepass_old(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, x_split=False, thumbscrews=True):
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

    mount_holes = [(0, 0), (8, 3), (0, 1)]
    extra_mount_holes = [(2, 0), (1, 2), (4, 0),(4,4), (6, 2)]
    
    # Difining the baseplate
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits=[3.6*layout.inch])
    
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
                                       beam_index=0b111, distance=14.5, angle=layout.cardinal['right'],
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
    
    # Fixed output mirror
    baseplate.place_element("Final Mirror", optomech.circular_mirror,  x=(1.5)*INCH, y=(2.5)*INCH,
                                       angle=-45, mount_type=optomech.mirror_mount_c05g, optional=True)
    
    # Fiberport to fiber the beam                                 
    baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_mount_hca3, beam,
                                      beam_index=0b11110, x=gap, angle=layout.cardinal['right'])

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
                                 name=name, label=label, x_splits=np.linspace(6.1*layout.inch, 7.6*layout.inch, 10).tolist())
    
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

def Rb_SAS(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, thumbscrews=True, only_lower_half = False, only_upper_half = False):
    name = "Rb SAS"
    date_time = datetime.now().strftime("%m/%d/%Y")
    label = name + " " +  date_time

    base_dx = 12*layout.inch
    base_dy = 4.5*layout.inch
    base_dz = layout.inch
    gap = layout.inch/8

    extra_cover_lower = np.linspace(0, 2.5 * layout.inch, 30)
    extra_cover_upper = np.linspace(2.5 * layout.inch, base_dx, 60)
    splits_baseplate = [2.5*layout.inch]

    if only_lower_half:
        splits_baseplate = np.concatenate([splits_baseplate, extra_cover_upper]).tolist()

    if only_upper_half:
        splits_baseplate = np.concatenate([splits_baseplate, extra_cover_lower]).tolist()

    # splits_baseplate *= x_split

    mount_holes = [(1,0),(0,3),(1,2), (3,3), (8,0), (7,2), (10,0), (11,3)]
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, name=name, label=label, mount_holes=mount_holes, x_splits=splits_baseplate)

    beam = baseplate.add_beam_path(x=base_dx-2.5*layout.inch, y=0, angle=90)

    baseplate.place_element_along_beam("input_mirror_1", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=1.5*layout.inch, angle=layout.turn['up-right'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
     
    baseplate.place_element_along_beam("input_mirror_2", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=1*layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 

    baseplate.place_element_along_beam("Half_waveplate_1", optomech.waveplate, beam,
                                       beam_index=0b1, distance=1*layout.inch, angle=layout.cardinal['up'], mount_type=optomech.rotation_stage_rsp05)
    
    baseplate.place_element_along_beam("Beam_Splitter", optomech.cube_splitter, beam,
                                       beam_index=0b1, distance=1.25*layout.inch, angle=layout.cardinal['up'],
                                        mount_type=optomech.skate_mount, invert=False)
    
    baseplate.place_element_along_beam("Half_waveplate_probe", optomech.waveplate, beam,
                                       beam_index=0b11, distance=1.5*layout.inch, angle=layout.cardinal['left'], mount_type=optomech.rotation_stage_rsp05)

    baseplate.place_element_along_beam("probe_mirror_1", optomech.circular_mirror, beam,
                                       beam_index=0b11, distance=1.5*layout.inch, angle=layout.turn['left-down'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 
    
    baseplate.place_element_along_beam("probe_mirror_2", optomech.circular_mirror, beam,
                                       beam_index=0b11, distance=2.25*layout.inch, angle=layout.turn['down-left'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 

    # baseplate.place_element_along_beam("splitter", optomech.circular_splitter, beam,
    #                                    beam_index=0b11, distance=1.5*layout.inch, angle=layout.turn['left-up'], 
    #                                    mount_type = optomech.splitter_mount_b05g)

    # baseplate.place_element_along_beam("probe_mirror_3", optomech.circular_mirror, beam,
    #                                    beam_index=0b111, distance=1.5*layout.inch, angle=layout.turn['right-down'],
    #                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))    

    baseplate.place_element_along_beam("Rb_gas_cell", optomech.rb_cell, beam,
                                       beam_index=0b11, distance=2.75*layout.inch, angle=layout.cardinal['right'])

    baseplate.place_element_along_beam("Beam_Splitter_2", optomech.cube_splitter, beam,
                                       beam_index=0b11, distance=2.75*layout.inch, angle=layout.cardinal['right']+180,
                                       mount_type=optomech.skate_mount, invert=True)

    baseplate.place_element_along_beam("Photodetector", optomech.photodetector_pda10a2, beam,
                                       beam_index=0b110, distance=1*layout.inch, angle=layout.cardinal['right'])

    # baseplate.place_element_along_beam("Half_waveplate_pump", optomech.waveplate, beam,
    #                                    beam_index=0b110, distance=2.75*layout.inch, angle=layout.cardinal['left'],mount_type = optomech.rotation_stage_rsp05)
    
    baseplate.place_element_along_beam("pump_mirror_1", optomech.circular_mirror, beam,
                                       beam_index=0b111, distance=2.25*layout.inch, angle=layout.turn['up-right'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 
    
    baseplate.place_element_along_beam("pump_mirror_2", optomech.circular_mirror, beam,
                                       beam_index=0b111, distance=3.5*layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=False)) 


def modular_transfer_cell(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, x_split=False, thumbscrews=True):
    # Adding name and date to keep a track of the updates
    name = "Doublepass"
    date_time = datetime.now().strftime("%m/%d/%Y")
    label = "" #name + " " +  date_time

    # Dimension of the baseplate 
    base_dx = 14*layout.inch
    base_dy = 5*layout.inch
    base_dz = layout.inch
    gap = layout.inch/8

    input_x = 6.5*layout.inch # should be in integer of grid. it is 6.5 * inch due to the defining or world origin is 0.5 inch offset from table grid

    mount_holes = [(0, 0), (8, 3), (0, 2), (0, 1)]
    extra_mount_holes = [(2, 0), (1, 2), (4, 0),(4,4), (6, 2)]
    
    # Difining the baseplate
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits=[0*layout.inch]*x_split)
    
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
    
    # Probe Mirror 1
    baseplate.place_element_along_beam("Probe Mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=2*layout.inch, angle=layout.turn['left-down'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Probe Mirror 2
    baseplate.place_element_along_beam("Probe Mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=2*layout.inch, angle=layout.turn['down-left'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    


if __name__ == "__main__":
    Rb_SAS(only_upper_half=True)
    # modified_doublepass(x=4, y=5)
    layout.redraw()