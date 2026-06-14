from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component, Layout
from PyOpticL.library import optics
from PyOpticL.utils import Dimension as dim

layout = Layout("Example Layout")

beam_path = layout.add(
    BeamPath(
        label="Beam Path",
        waist=dim(1, "mm"),
        wavelength=670,
    ),
    position=(0, 0, 0),
    rotation=(0, 0, 90),
)

layout.add(
    BeamPath(
        label="Beam Path",
        waist=dim(1, "mm"),
        wavelength=670,
    ),
    position=(dim(8, "mm"), 0, 0),
    rotation=(0, 0, 90),
)

layout.add(
    BeamPath(
        label="Beam Path",
        waist=dim(1, "mm"),
        wavelength=670,
    ),
    position=(dim(-8, "mm"), 0, 0),
    rotation=(0, 0, 90),
)

layout.add(
    Component(
        label="f=100mm lens",
        definition=optics.Spherical_Lens(
            diameter=dim(1, "in"),
            thickness=dim(2, "mm"),
            focal_length=dim(100, "mm"),
        ),
    ),
    position=(0, dim(100, "mm"), 0),
    rotation=(0, 0, 90),
)

layout.add(
    Component(
        label="f=50mm lens",
        definition=optics.Spherical_Lens(
            diameter=dim(1, "in"),
            thickness=dim(2, "mm"),
            focal_length=dim(50, "mm"),
        ),
    ),
    position=(0, dim(250, "mm"), 0),
    rotation=(0, 0, 90),
)

layout.recompute()
