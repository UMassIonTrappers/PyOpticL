from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
# Adding name and date to keep a track of the updates
name = "combiner"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

# Dimension of the baseplate
base_dx = 8.25*layout.inch
base_dy = 4.5*layout.inch
base_dz = layout.inch
gap = layout.inch/4

def Beam_Combiner_General(x=0, y=0, angle=270, mirror=optomech.mirror_mount_k05s2, x_split=False, thumbscrews=True):
    base_dz = layout.inch
    base_dx = 7 * layout.inch
    
    base_dy = 5 * layout.inch 
    gap = layout.inch/4
    mirror_angle = 45
    mount_holes= [(0,0),(0,2)]

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x , y=y , angle=angle ,
                                 gap=gap, mount_holes=[(0,1), (1,1), (2,1), (3,1), (4,1), (5,1), (0,3), (1,3), (2,3), (3,3), (5,3),(4,3)],
                                 name=name, label=label, x_splits=[0*layout.inch], y_offset =0, x_offset = -0.375 * layout.inch)
    
    beam_array = []
    for i in range(0,6):
        beam_array.append(baseplate.add_beam_path((0.5 + i * 1) * layout.inch, 0 * layout.inch , layout.cardinal['up']))
    baseplate.place_element_along_beam("Fiberport 1", optomech.fiberport_mount_hca3, beam_array[0],
                                       beam_index=0b1,  distance = gap , angle=layout.cardinal['up'], optional = True)
    baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam_array[0],
                                       beam_index=0b1, distance=.65 * layout.inch, angle=layout.cardinal['up'],
                                       mount_type=optomech.rotation_stage_rsp05_vertical)
    combine_element_1 = baseplate.place_element_along_beam("Combining Element", optomech.cube_splitter, beam_array[0],
                                        beam_index=0b1, distance=1.7 * layout.inch, angle=layout.cardinal['up'],
                                        mount_type=optomech.skate_mount_crossholes)
    baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam_array[0],
                                       beam_index=0b10, distance=1.5 * layout.inch, angle=layout.cardinal['down'],
                                       mount_type=optomech.rotation_stage_rsp05_vertical)
    baseplate.place_element_along_beam("Fiberport out 1", optomech.fiberport_mount_hca3, beam_array[0],
                                       beam_index=0b10,  distance = .65 * layout.inch , angle=layout.cardinal['down'], optional = True)
    for j in range(1,6):
        baseplate.place_element_along_beam("Fiberport " + str(j+1), optomech.fiberport_mount_hca3, beam_array[j],
                                       beam_index=0b1,  distance = gap , angle=layout.cardinal['up'], optional = True)
        baseplate.place_element_along_beam("Half waveplate A" + str(j + 1), optomech.waveplate, beam_array[j],
                                       beam_index=0b1, distance=.65 * layout.inch, angle=layout.cardinal['up'],
                                       mount_type=optomech.rotation_stage_rsp05_vertical)
        baseplate.place_element_along_beam("Input Mirror " + str(j + 1), optomech.circular_mirror, beam_array[j],
                                       beam_index=0b1, distance = 1.7 * layout.inch, angle=-135,
                                       mount_type=optomech.mirror_mount_k05s2, mount_args=dict(thumbscrews= False ), optional = True)
    
    beam_array_down = []
    for k in range(5):
        beam_array_down.append(baseplate.add_beam_path((1.5 + k * 1) * layout.inch, 5 * layout.inch , layout.cardinal['down']))
        fiberport = baseplate.place_element_along_beam("Fiberport out " + str(k+1), optomech.fiberport_mount_hca3, beam_array_down[k],
                                       beam_index=0b1,  distance = gap , angle=layout.cardinal['down'], optional = True)
        baseplate.place_element_relative("Half waveplate B" + str(k + 1),  optomech.waveplate, fiberport, #beam_array_down[k],beam_index=0b1, distance=.75 * layout.inch
                                       y_off = -.65 * layout.inch, angle=layout.cardinal['down'],
                                       mount_type=optomech.rotation_stage_rsp05_vertical)
        baseplate.place_element_along_beam("Input Mirror out" + str(k + 1), optomech.circular_mirror, beam_array_down[k],
                                       beam_index=0b1, distance = 2.15 * layout.inch, angle=135,
                                       mount_type=optomech.mirror_mount_k05s2, mount_args=dict(thumbscrews= False ),optional = True)
    for k in range(5):
        baseplate.place_element_relative("Combining Element " + str(k), optomech.cube_splitter, combine_element_1, x_off = (k + 1 ) * layout.inch, angle=layout.cardinal['left'], mount_type = optomech.skate_mount_crossholes)
    
    


    
if __name__ == "__main__":
    Beam_Combiner_General()
    layout.redraw()