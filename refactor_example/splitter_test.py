from PyOpticL import optomech
from PyOpticL.beam_path import Beam_Path
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

layout = Layout("Example Layout")

beam_path = layout.add(
    Beam_Path(
        label="Beam Path",
        waist=dim(2, "mm"),
        wavelength=670,
    ),
    position=(0, 0, 0),
    rotation=(0, 0, 90),
)

beam_path.add(
    Component(
        label="Mirror 2",
        definition=optomech.circular_sampler(
            ref_ratio=0.5,
            diameter=dim(1, "in"),
        ),
    ),
    beam_index=0b1,
    distance=dim(50, "mm"),
    rotation=(0, 0, -45),
)

beam_path.add(
    Component(
        label="Mirror 2",
        definition=optomech.circular_sampler(
            ref_ratio=0.5,
            diameter=dim(1, "in"),
        ),
    ),
    beam_index=0b10,
    distance=dim(50, "mm"),
    rotation=(0, 0, -45),
)

layout.recompute()
