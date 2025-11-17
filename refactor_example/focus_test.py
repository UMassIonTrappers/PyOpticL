from PyOpticL import optomech
from PyOpticL.beam_path import Beam_Path
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

layout = Layout("Example Layout")

beam_path = layout.add(
    Beam_Path(
        label="Beam Path",
        waist=dim(5, "mm"),
        wavelength=670,
    ),
    position=(0, 0, 0),
    rotation=(0, 0, 90),
)

layout.add(
    Beam_Path(
        label="Beam Path",
        waist=dim(5, "mm"),
        wavelength=670,
    ),
    position=(dim(8, "mm"), 0, 0),
    rotation=(0, 0, 90),
)

layout.add(
    Beam_Path(
        label="Beam Path",
        waist=dim(5, "mm"),
        wavelength=670,
    ),
    position=(dim(-8, "mm"), 0, 0),
    rotation=(0, 0, 90),
)

layout.add(
    Component(
        label="Mirror 1",
        definition=optomech.circular_lens(
            diameter=dim(1, "in"),
            focal_length=dim(100, "mm"),
        ),
    ),
    position=(0, dim(100, "mm"), 0),
    rotation=(0, 0, 90),
)

layout.add(
    Component(
        label="Mirror 1",
        definition=optomech.circular_lens(
            diameter=dim(1, "in"),
            focal_length=dim(50, "mm"),
        ),
    ),
    position=(0, dim(250, "mm"), 0),
    rotation=(0, 0, 90),
)

layout.recompute()
