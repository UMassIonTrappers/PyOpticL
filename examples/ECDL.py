from PyOptic import layout, optomech
from datetime import datetime
import numpy as np

name = "ECDL"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " + date_time

wavelength = 422e-6 #wavelength in mm
grating_pitch_d = 1/2400
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi

base_dx = 7*layout.inch
base_dy = 5*layout.inch
base_dz = layout.inch
gap = layout.inch/8

input_x = 45
input_y = 35

mount_holes=[[3,0],[0,4],[6,0],[4,4]]

if wavelength == 422e-6:
    isolator = optomech.isolator_405
elif wavelength == 674e-6:
    isolator = optomech.isolator_670

def ECDL(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes, name=name, label=label)

    beam = baseplate.add_beam_path(x=input_x, y=input_y, angle=layout.cardinal['right'])

    baseplate.place_element("Laser_diode_LT230P-B", optomech.km05_50mm_laser,
                            x=input_x, y=input_y, angle=layout.cardinal['right'])

    baseplate.place_element_along_beam("Grating", optomech.grating_mount_on_mk05pm, beam,
                                       beam_index=0b1, distance=40, angle=layout.cardinal['left'],
                                       littrow_angle=littrow_angle)

    baseplate.place_element_along_beam("Input_Mirror_1", mirror, beam,
                                       beam_index=0b1, x=6*layout.inch, angle=layout.turn['right-up'])
    baseplate.place_element_along_beam("Input_Mirror_2", mirror, beam,
                                       beam_index=0b1, y=3.5*layout.inch, angle=layout.turn['up-left'])
    
    baseplate.place_element_along_beam("Optical_Isolator", isolator, beam,
                                       beam_index=0b1, distance=55, angle=layout.cardinal['left'],
                                       adapter_args=dict(mount_hole_dy=45))

    baseplate.place_element_along_beam("Fiber Coupler", optomech.fiberport_mount_km05, beam,
                                       beam_index=0b1, distance=65, angle=layout.cardinal['right'])

if __name__ == "__main__":
    ECDL()
    layout.redraw()