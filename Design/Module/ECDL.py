from PyOpticL import layout, optomech
import numpy as np
# calculation of littrow angle
wavelength = 422e-6   #wavelength in mm
grating_pitch_d = 1/3600   # Lines per mm
littrow_angle = np.arcsin(wavelength/(2*grating_pitch_d))*180/np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))
def ECDL(x = 0,y = 0, angle = 0, littrow_angle = littrow_angle):
    layout.place_element_on_table("ecdl",  optomech.ECDL, x = 0 + x, y = 0 + y, angle= angle, littrow_angle = littrow_angle)#, x_ = 0, y_=0,z_=0)

## This code will generate the ECDL with cover. If you want to change anything to the cover or the ECDL design then it has to be #
# done in laser_mount_km100pm part of the optomech file 

if __name__ == "__main__":
    ECDL()
    layout.redraw()