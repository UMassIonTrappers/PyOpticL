from PyOpticL import optomech
from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

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
        definition=optomech.spherical_lens(
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
        definition=optomech.spherical_lens(
            diameter=dim(1, "in"),
            thickness=dim(2, "mm"),
            focal_length=dim(50, "mm"),
        ),
    ),
    position=(0, dim(250, "mm"), 0),
    rotation=(0, 0, 90),
)

layout.recompute()
