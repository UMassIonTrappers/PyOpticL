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
from modular_beam_combiner import Beam_Combiner_General
from modular_beam_pickoff import Beam_pickoff
from modular_singlepass import singlepass

from PyOpticL import layout, optomech

wavelength = 422e-6  # wavelength in mm
grating_pitch_d = 1 / 3600  # Lines per mm
littrow_angle = np.arcsin(wavelength / (2 * grating_pitch_d)) * 180 / np.pi
print("current wavelength is " + str(wavelength * 1e6) + " nm")
print("current littrow angle is " + str(littrow_angle))


def Raman_subsystem(
    x=0,
    y=0,
    angle=0,
    thumbscrews=True,
    littrow_angle=littrow_angle,
    beam_combiner=False,
):
    # # #422 Raman
    ax = np.sin(np.deg2rad(angle))
    ay = np.cos(np.deg2rad(angle))
    p = lambda dx, dy: dict(x=x + dx * ay - dy * ax, y=y + dx * ax + dy * ay)

    ECDL(**p(6.7, 26), angle=270 + angle, littrow_angle=littrow_angle)
    ECDL_isolator_baseplate(**p(4, 21), angle=270 + angle)
    singlepass(**p(11, 14.5), angle=180 + angle, thumbscrews=thumbscrews)
    singlepass(**p(10, 9.5), angle=180 + angle, thumbscrews=thumbscrews)
    singlepass(**p(9, 4.5), angle=180 + angle, thumbscrews=thumbscrews)
    Beam_pickoff(**p(1.5, -1), angle=-90 + angle, thumbscrews=thumbscrews)
    if beam_combiner:
        Beam_Combiner_General(**p(11, 13.5), angle=-90 + angle)
        Beam_Combiner_General(**p(11, 6.5), angle=-90 + angle)


if __name__ == "__main__":
    Raman_subsystem()
    layout.redraw()
