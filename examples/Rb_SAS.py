# The baseplate is used for optical setup of the Rb atom's saturation absorbtion spectroscopy
# Nishat Edited 08/26

from PyOpticL import layout, optomech
from datetime import datetime

# Adding name and date to keep a track of the updates
name = "Rb SAS"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

# Dimension of the baseplate
base_dx = 15*layout.inch
base_dy = 5*layout.inch
base_dz = layout.inch
gap = layout.inch/8

mount_holes = [(0,0), (6,4), (5, 0), (8, 0), (14, 4), (11,2), (4,1), (4,4), (8,1), (14,3), (4,0), (2,3)]

# Combining the baseplate with the beam and all other optical componenets. 
def Rb_SAS(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, thumbscrews=True):
    
    # Difining the baseplate
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, name=name, label=label, mount_holes=mount_holes, x_splits=[7.5*layout.inch, 0*layout.inch])
    
    # Adding the beams to the baseplate
    beam = baseplate.add_beam_path(x=base_dx-2.5*layout.inch, y=0, angle=90)

    # Adding two mirrors to give the beam enough degree of freedom. Mirror 1
    baseplate.place_element_along_beam("input_mirror_1", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=1.25*layout.inch, angle=layout.turn['up-right'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Mirror 2 
    baseplate.place_element_along_beam("input_mirror_2", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=1*layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 
    
    # Adding a waveplate to control the ploarization and to control the power ratio of the beam on the baseplate and to the next baseplate. 
    baseplate.place_element_along_beam("Half_waveplate_1", optomech.waveplate, beam,
                                       beam_index=0b1, distance=1.25*layout.inch, angle=layout.cardinal['up'], mount_type=optomech.rotation_stage_rsp05)
    
    # Adding beam splitter to divide the beam to : to stay on the baseplate and to to send to the next baseplate
    baseplate.place_element_along_beam("Beam_Splitter", optomech.cube_splitter, beam,
                                       beam_index=0b1, distance=1.5*layout.inch, angle=layout.cardinal['up'],
                                        mount_type=optomech.skate_mount, invert=False)
    
    # Adding a waveplate to control the ploarization and to control the power ratio of the pump and probe beams. 
    baseplate.place_element_along_beam("Half_waveplate_probe", optomech.waveplate, beam,
                                       beam_index=0b11, distance=1.5*layout.inch, angle=layout.cardinal['left'], mount_type=optomech.rotation_stage_rsp05)

    # Adding splitter to split the beam into pump beam and probe beam
    baseplate.place_element_along_beam("splitter", optomech.circular_lens, beam,
                                       beam_index=0b11, distance=1.5*layout.inch, angle=layout.turn['left-down'], 
                                       mount_type = optomech.splitter_mount_b05g)

    # Adding mirror for probe beams to make sure it can be properly aligned with the pump beam.Mirror 1
    baseplate.place_element_along_beam("probe_mirror_1", optomech.circular_mirror, beam,
                                       beam_index=0b11, distance=1.5*layout.inch, angle=layout.turn['left-down'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 
    
    # Mirror 2
    baseplate.place_element_along_beam("probe_mirror_2", optomech.circular_mirror, beam,
                                       beam_index=0b11, distance=1*layout.inch, angle=layout.turn['down-left'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 
    
    # Adding waveplate to control the polarization
    baseplate.place_element_along_beam("Half_waveplate_probe2", optomech.waveplate, beam,
                                       beam_index=0b11, distance=1*layout.inch, angle=layout.cardinal['left'], mount_type=optomech.rotation_stage_rsp05)

    # Adding the Rb Gas cell   
    baseplate.place_element_along_beam("Rb_gas_cell", optomech.rb_cell, beam,
                                       beam_index=0b11, distance=3*layout.inch, angle=layout.cardinal['right'])

    # Adding beam cube to send the pump and probe beam to the photodiode and to the fiberport
    baseplate.place_element_along_beam("Beam_Splitter_2", optomech.cube_splitter, beam,
                                       beam_index=0b11, distance=3*layout.inch, angle=layout.cardinal['right'],
                                       mount_type=optomech.skate_mount, invert=False)
    # Adding photodetector to check the signal
    baseplate.place_element_along_beam("Photodetector", optomech.photodetector_pda10a2, beam,
                                       beam_index=0b110, distance=1*layout.inch, angle=layout.cardinal['right'])
#
    # Adding mirros for pump beam so that it can be properly pass through the gas cell overlapping to the max with the probe beam. Mirror 1
    baseplate.place_element_along_beam("pump_mirror_1", optomech.circular_mirror, beam,
                                       beam_index=0b111, distance=1.75*layout.inch, angle=layout.turn['left-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 
    
    # Adding waveplate to control the polarization
    baseplate.place_element_along_beam("Half_waveplate_pump", optomech.waveplate, beam,
                                       beam_index=0b111, distance=4.5*layout.inch, angle=layout.cardinal['left'], mount_type=optomech.rotation_stage_rsp05)
    
    # Mirror 2
    baseplate.place_element_along_beam("pump_mirror_2", optomech.circular_mirror, beam,
                                       beam_index=0b111, distance=4*layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)) 

if __name__ == "__main__":
    Rb_SAS()
    layout.redraw()