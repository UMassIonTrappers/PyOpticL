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

def Beam_Combiner_General(x = 0, y = 0, angle = 0):
    base_dz = layout.inch
    base_dx = 7 * layout.inch
    
    base_dy = 3 * layout.inch 
    gap = layout.inch/4
    
    

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=0 + x , y=0 + y , angle=0 + angle ,
                                 gap=gap, mount_holes=[],
                                 name=name, label=label, x_splits=[0*layout.inch], y_offset =0, x_offset = -0.375 * layout.inch)
    
    beam_array = []
    for i in range(6):
        beam_array.append(baseplate.add_beam_path((0.5 + i * 1) * layout.inch, 0 * layout.inch , layout.cardinal['up']))
    baseplate.place_element_along_beam("Fiberport 1", optomech.fiberport_mount_hca3, beam_array[0],
                                       beam_index=0b1,  distance = gap , angle=layout.cardinal['up'], optional = True)
    baseplate.place_element_along_beam("Combining Element", optomech.cube_splitter, beam_array[0],
                                        beam_index=0b1, distance=1.25 * layout.inch, angle=layout.cardinal['up'],
                                        mount_type=optomech.skate_mount_crossholes)
    baseplate.place_element_along_beam("Fiberport out 1", optomech.fiberport_mount_hca3, beam_array[0],
                                       beam_index=0b10,  distance = 1.25 * layout.inch , angle=layout.cardinal['down'], optional = True)
    for j in range(1,6):
        baseplate.place_element_along_beam("Fiberport " + str(j+1), optomech.fiberport_mount_hca3, beam_array[j],
                                       beam_index=0b1,  distance = gap , angle=layout.cardinal['up'], optional = True)
        baseplate.place_element_along_beam("Input Mirror " + str(j + 1), optomech.circular_mirror, beam_array[j],
                                       beam_index=0b1, distance = 1.25 * layout.inch, angle=-135,
                                       mount_type=optomech.mirror_mount_k05s2, mount_args=dict(thumbscrews= False ), optional = True)
    
    beam_array_down = []
    for k in range(5):
        beam_array_down.append(baseplate.add_beam_path((1.5 + k * 1) * layout.inch, 3 * layout.inch , layout.cardinal['down']))
        baseplate.place_element_along_beam("Fiberport out " + str(k+1), optomech.fiberport_mount_hca3, beam_array_down[k],
                                       beam_index=0b1,  distance = gap , angle=layout.cardinal['down'], optional = True)
        baseplate.place_element_along_beam("Input Mirror out" + str(k + 1), optomech.circular_mirror, beam_array_down[k],
                                       beam_index=0b1, distance = 1.25 * layout.inch, angle=135,
                                       mount_type=optomech.mirror_mount_k05s2, mount_args=dict(thumbscrews= False ),optional = True)
    beam_array_for_pbs = []
    for k in range(5):
        beam_array_for_pbs.append(baseplate.add_beam_path((1.5 + k * 1) * layout.inch, 3 * layout.inch , layout.cardinal['down']))
        baseplate.place_element_along_beam("Combining Element " + str(k), optomech.cube_splitter, beam_array_for_pbs[k],
                                            beam_index=0b1, distance=1.25 * layout.inch + gap, angle=layout.cardinal['left'],
                                            mount_type=optomech.skate_mount_crossholes)
    # beam_2 = baseplate.add_beam_path(54.7, 0 * layout.inch , layout.cardinal['up'])

    
if __name__ == "__main__":
    Beam_Combiner_General()
    layout.redraw()