from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
name = "OQC_light_source" ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time
Number_of_light_source = 1
base_dx = 8 * layout.inch
base_dy = 4.5 * layout.inch
base_dz = 1 * layout.inch
input_x = 1.5 * layout.inch
input_y = 1.5 * layout.inch
mount_holes = [] #[(0, 1), (11,0) ,(12, 4), (8, 2)]
gap = 1/8 * layout.inch
extra_mount_holes = [] #[(2,1),(0, 5),(5, 2),(9,4),(8,3)]
def OQC_unit_source_left(x=0 , y=0 , angle=0, mirror=optomech.mirror_mount_k05s1, thumbscrews=True):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y , angle=angle,
                                gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                name=name, label=label)
    beam = baseplate.add_beam_path(x=input_x, y=input_y, angle=layout.cardinal['right'])

    baseplate.place_element("Laser_diode_LT230P-B", optomech.km05_50mm_laser,
                            x=input_x, y=input_y, angle=layout.cardinal['right'])
    
    baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam,
                                    beam_index=0b1, distance= 2.5 * layout.inch, angle=layout.cardinal['left'],
                                    mount_type=optomech.rotation_stage_rsp05)

    baseplate.place_element_along_beam("Input Mirror", optomech.circular_mirror, beam,
                                    beam_index=0b1, distance= 2.5 * layout.inch , angle=layout.turn['right-up'],
                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    baseplate.place_element_along_beam("Beam Splitter", optomech.cube_splitter, beam,
                                    beam_index=0b1, distance= 2 * layout.inch, angle=layout.cardinal['down'],
                                    mount_type=optomech.skate_mount)

    baseplate.place_element_along_beam("Quarter waveplate", optomech.waveplate, beam,
                                    beam_index=0b11, distance= 2 * layout.inch, angle=layout.cardinal['left'],
                                    mount_type=optomech.rotation_stage_rsp05)
    #there should be a non-linear optical medium to generate squeezed state here
    #I need to confirm this first, and see if we can actually import some thorlab's model 
    #For now, I just use another waveplate as a place holder

    baseplate.place_element_along_beam("place holder", optomech.waveplate, beam,
                                    beam_index=0b11, distance= 2 * layout.inch, angle=layout.cardinal['left'],
                                    mount_type=optomech.rotation_stage_rsp05)

    baseplate.place_element_along_beam("retro mirror", optomech.circular_mirror, beam,
                                    beam_index=0b11, distance= 1 * layout.inch , angle=layout.cardinal['right'],
                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))

def OQC_unit_source_right(x=0 , y=0 , angle=0, mirror=optomech.mirror_mount_k05s1, thumbscrews=True):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y , angle=angle,
                                gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                name=name, label=label)
    beam = baseplate.add_beam_path(x= base_dx - input_x, y=input_y, angle=layout.cardinal['left'])

    baseplate.place_element("Laser_diode_LT230P-B", optomech.km05_50mm_laser,
                            x=base_dx - input_x, y=input_y, angle=layout.cardinal['right'])
    
    baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam,
                                    beam_index=0b1, distance= 2.5 * layout.inch, angle=layout.cardinal['left'],
                                    mount_type=optomech.rotation_stage_rsp05)

    baseplate.place_element_along_beam("Input Mirror", optomech.circular_mirror, beam,
                                    beam_index=0b1, distance= 2.5 * layout.inch , angle=layout.turn['left-up'],
                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    baseplate.place_element_along_beam("Beam Splitter", optomech.cube_splitter, beam,
                                    beam_index=0b1, distance= 2 * layout.inch, angle=layout.cardinal['left'],
                                    mount_type=optomech.skate_mount)

    baseplate.place_element_along_beam("Quarter waveplate", optomech.waveplate, beam,
                                    beam_index=0b11, distance= 2 * layout.inch, angle=layout.cardinal['left'],
                                    mount_type=optomech.rotation_stage_rsp05)
    #there should be a non-linear optical medium to generate squeezed state here
    #I need to confirm this first, and see if we can actually import some thorlab's model 
    #For now, I just use another waveplate as a place holder

    baseplate.place_element_along_beam("place holder", optomech.waveplate, beam,
                                    beam_index=0b11, distance= 2 * layout.inch, angle=layout.cardinal['left'],
                                    mount_type=optomech.rotation_stage_rsp05)

    baseplate.place_element_along_beam("retro mirror", optomech.circular_mirror, beam,
                                    beam_index=0b11, distance= 1 * layout.inch , angle=layout.cardinal['left'],
                                    mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
def OQC_combine_4(x=0 , y=0 , angle=0, mirror=optomech.mirror_mount_k05s1, thumbscrews=True, input_light_1 = [1 * layout.inch, 1* layout.inch], input_light_2 = [1 * layout.inch, 3* layout.inch]):
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y , angle=angle,
                                gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                name=name, label=label)
if __name__ == "__main__":

    # for i in 4.7 * np.arange(Number_of_light_source): 
        # OQC_unit_source(x = 0 , y = i )
    for i in 4.7 * np.arange(Number_of_light_source): 
        OQC_unit_source_right(x = 10, y = i)
        OQC_unit_source_left(y = i)
    layout.redraw()