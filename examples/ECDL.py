from PyOptic import layout, optomech
from datetime import datetime
import numpy as np

name = "ECDL"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " + date_time

wavelength = 422e-6 #wavelength in mm
grating_pitch_d = 1/3600
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
print(littrow_angle)

base_dx = 6*layout.inch
base_dy = 5*layout.inch
base_dz = layout.inch
gap = layout.inch/8

input_x = 38
input_y = 32

mount_holes=[[2,0],[2,4],[5,0],[4,4]]

def ECDL(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes, name=name, label=label)

    beam = baseplate.add_beam_path(x=input_x, y=input_y, angle=layout.cardinal['right'])

    baseplate.place_element("Laser_diode_LT230P-B", optomech.km05_50mm_laser,
                            x=input_x, y=input_y, angle=layout.cardinal['right'])

    baseplate.place_element_along_beam("Grating Mount", optomech.grating_mount_on_km05pm, beam,
                                       beam_index=0b1, distance=40, angle=layout.cardinal['right'],
                                       littrow_angle=littrow_angle, mount_args=dict(thumbscrews=True))

    baseplate.place_element_along_beam("Input_Mirror_1", optomech.circular_mirror, beam,
                                       beam_index=0b1, x=5.5*layout.inch, angle=layout.turn['right-up'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=True))
    baseplate.place_element_along_beam("Input_Mirror_2", optomech.circular_mirror, beam,
                                       beam_index=0b1, y=3.5*layout.inch, angle=layout.turn['up-left'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=True))
    
    baseplate.place_element_along_beam("Optical_Isolator", optomech.isolator_405, beam,
                                       beam_index=0b1, distance=45, angle=layout.cardinal['left'])

    baseplate.place_element_along_beam("Fiber Coupler", optomech.fiberport_mount_ks1t, beam,
                                       beam_index=0b1, x=1.25*layout.inch, angle=layout.cardinal['right'])

if __name__ == "__main__":
    ECDL()
    layout.redraw()