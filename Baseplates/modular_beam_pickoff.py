## this baseplate is used to take a little amount of beam, fiber it and send it to the wavemeter.##

from PyOpticL import layout, optomech
from datetime import datetime

# Adding name and date to keep track of updates
name = "Beam_Combiner"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

# Dimension of the baseplate
base_dx = 4.5*layout.inch
base_dy = 12*layout.inch
base_dz = layout.inch
gap = layout.inch/8

input_x1 = 4.5*layout.inch
input_x2 = 0*layout.inch

# Combining the baseplate with the beam and all optical components
def Beam_pickoff(x=0, y=-0.5, angle=0, mirror=optomech.mirror_mount_km05, x_split=False, thumbscrews=True):
    # Define baseplate, mount holes
    baseplate = layout.baseplate(dx = 4.9 * layout.inch, dy = 4 * layout.inch, dz = 1 * layout.inch, x=x, y=y, angle=angle,
                                 gap=layout.inch/4, mount_holes=[(1,0.5),(2,1.5),(2,2.5)],
                                 name=name, label=label, y_splits=[6*layout.inch]*x_split)
    
    #Adding the beam to the baseplate
    beam1 = baseplate.add_beam_path(0 * layout.inch, 1 *layout.inch, layout.cardinal['right'])

    #Adding mirros to make sure that the beam is getting enough degree of freedom
    angle1 =60
    baseplate.place_element_along_beam("Input Mirror 1", optomech.circular_mirror, beam1,
                                         beam_index=0b1, distance=2*layout.inch+5, angle=angle1+90,
                                         mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    baseplate.place_element_along_beam("Input Mirror 2", optomech.circular_mirror, beam1,
                                         beam_index=0b1, distance=2*layout.inch-5, angle=  angle1-90,
                                         mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    # Adding fiberport which will send the beam to the wavemeter
    baseplate.place_element_along_beam("Fiberport", optomech.fiberport_mount_ks1t, beam1,
                                      beam_index=0b1,  distance=53, angle=layout.cardinal['left'])
   
     
if __name__ == "__main__":
    Beam_pickoff()
    layout.redraw()