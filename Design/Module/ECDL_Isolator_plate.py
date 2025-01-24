from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np

##Adding name & date to the baseplate to keep a track of update
name = "ECDL"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " + date_time

## Calculating the littrow angle for the ECDL. THis part is not needed. It's here just to keep track of for what laser we are printing the isolation basplate
wavelength = 422e-6   #wavelength in mm
grating_pitch_d = 1/3600   # Lines per mm
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
print(littrow_angle)

# Define the dimension of the baseplet
base_dx = 6*layout.inch 
base_dy = 4*layout.inch 
base_dz = layout.inch
gap = layout.inch/4

# # Define the position from where the beam will enter into the baseplate
input_x = 0*layout.inch 
input_y = 0.5*layout.inch
input_y = base_dy - input_y

# Adding mount holes to bolt the baseplate to the optical table
mount_holes=[[3,0],[0,2],[0,4],[4,2]]

# Combining the baseplate with different optical components and the beam
def ECDL_isolator_baseplate(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05):
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=[(1,1),(5,3),(0,3), (4,3),(4,2)], y_offset  = 9)
    
    # Adding the beam to baseplate
    beam = baseplate.add_beam_path(x=input_x, y=input_y, angle=layout.cardinal['right'])

    # Adding the first mirror
    baseplate.place_element_along_beam("Input_Mirror_1", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=1*layout.inch, angle=layout.turn['right-down'] ,
                                       mount_type=mirror, mount_args=dict(thumbscrews=True))
    
    # Adding second mirror to make sure that there's enough dgree of freedom
    baseplate.place_element_along_beam("Input_Mirror_2", optomech.circular_mirror, beam,
                                       beam_index=0b1, distance=2*layout.inch, angle=layout.turn['down-right'] ,
                                       mount_type=mirror, mount_args=dict(thumbscrews=True))
    
    #Adding the cylindrical lense pair to make the beam more circular 
    baseplate.place_element_along_beam("Lens 1", optomech.cylindrical_lens, beam,
                                       beam_index=0b1, x=2.5*layout.inch, angle=layout.cardinal['right'],
                                       thickness=4, width=20, height=22, slots=True)
    baseplate.place_element_along_beam("Lens 2", optomech.cylindrical_lens, beam,
                                       beam_index=0b1, distance=35, angle=layout.cardinal['left'],  
                                       thickness=5.1, width=15, height=17, slots= True)
    
    #Adding the isolator to make sure there is no unwanted beam going back as feedback
    baseplate.place_element_along_beam("Optical_Isolator", optomech.isolator_405, beam,
                                       beam_index=0b1, distance=40, angle=layout.cardinal['left'])

# Done, print the baseplate
if __name__ == "__main__":
    ECDL_isolator_baseplate()
    layout.redraw()