import time

start_time = time.time()
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Module"))
)
import numpy as np
from ECDL import ECDL
from ECDL_Isolator_plate import ECDL_isolator_baseplate
from modular_beam_pickoff import Beam_pickoff
from modular_doublepass import doublepass_f50

from PyOpticL import layout, optomech

wavelength = 674e-6  # wavelength in mm
grating_pitch_d = 1 / 1800  # Lines per mm
littrow_angle = np.arcsin(wavelength / (2 * grating_pitch_d)) * 180 / np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))


def subsystem_spam(x=0, y=0, angle=0, littrow_angle=littrow_angle, thumbscrews=True):
    ax = np.sin(np.deg2rad(angle))
    ay = np.cos(np.deg2rad(angle))
    p = lambda dx, dy: dict(x=x + dx * ay - dy * ax, y=y + dx * ax + dy * ay)

    ECDL(**p(6.7, 32), angle=270 + angle, littrow_angle=littrow_angle)
    ECDL_isolator_baseplate(**p(4, 27), angle=270 + angle)
    doublepass_f50(**p(12, 20), angle=180 + angle, thumbscrews=thumbscrews)
    doublepass_f50(**p(11, 14), angle=180 + angle, thumbscrews=thumbscrews)
    Beam_pickoff(**p(2.5, 8), angle=-90 + angle, thumbscrews=thumbscrews)


if __name__ == "__main__":
    subsystem_spam()
    layout.redraw()
