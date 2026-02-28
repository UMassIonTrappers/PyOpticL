import time

start_time = time.time()
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Module')))
import numpy as np
from ECDL import ECDL
from ECDL_Isolator_plate import ECDL_isolator_baseplate
from modular_beam_pickoff import Beam_pickoff
from modular_singlepass import singlepass, singlepass_mirrored
from modular_sourcebox import sourcebox

from PyOpticL import layout, optomech

# sr 1033(quench) / 1092(repump)
# ca 854(quench) / 866(repump)

wavelength = 1092e-6  # 866e-6   #wavelength in mm
grating_pitch_d = 1 / 1800  # Lines per mm
littrow_angle = np.arcsin(wavelength / (2 * grating_pitch_d)) * 180 / np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))


def repump_subsystem_ECDL_mirrored(
    x=4, y=0, angle=0, thumbscrews=True, littrow_angle=littrow_angle
):
    ax = np.sin(np.deg2rad(angle))
    ay = np.cos(np.deg2rad(angle))
    p = lambda dx, dy: dict(x=x + dx * ay - dy * ax, y=y + dx * ax + dy * ay)

    ECDL(
        **p(0.3, -4), angle=90 + angle, littrow_angle=littrow_angle
    )  # modeling of a home-made laser
    ECDL_isolator_baseplate(**p(3, 1), angle=layout.cardinal["up"] + angle)
    singlepass_mirrored(**p(7, 12.5), angle=180 + angle, thumbscrews=thumbscrews)
    Beam_pickoff(**p(1.5, 13), angle=90 + angle, thumbscrews=thumbscrews)


wavelength = 1033e-6  # 854e-6   #wavelength in mm
grating_pitch_d = 1 / 1800  # Lines per mm
littrow_angle = np.arcsin(wavelength / (2 * grating_pitch_d)) * 180 / np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))


def repump_subsystem_ECDL(
    x=0, y=0, angle=0, thumbscrews=True, littrow_angle=littrow_angle
):
    ax = np.sin(np.deg2rad(angle))
    ay = np.cos(np.deg2rad(angle))
    p = lambda dx, dy: dict(x=x + dx * ay - dy * ax, y=y + dx * ax + dy * ay)

    ECDL(
        **p(4.3, -4), angle=90 + angle, littrow_angle=littrow_angle
    )  # modeling of a home-made laser
    ECDL_isolator_baseplate(**p(7, 1), angle=layout.cardinal["up"] + angle)
    singlepass(**p(0, 7.5), angle=0 + angle, thumbscrews=thumbscrews)
    Beam_pickoff(**p(7.5, 13), angle=90 + angle, thumbscrews=thumbscrews)


if __name__ == "__main__":
    repump_subsystem_ECDL(x=10)
    repump_subsystem_ECDL_mirrored(x=0)
    layout.redraw()
