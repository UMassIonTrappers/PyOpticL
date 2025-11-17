from PyOpticL import optomech
from PyOpticL.beam_path import Beam_Path
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

example_layout = Layout("Example Layout")

beam_path1 = example_layout.add(
    Beam_Path(
        label="Beam Path",
        waist=dim(2, "mm"),
        wavelength=350,
    ),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
)

beam_path2 = example_layout.add(
    Beam_Path(
        label="Beam Path",
        waist=dim(2, "mm"),
        wavelength=350,
    ),
    position=(0, 0, 0),
    rotation=(0, 0, 90),
)

beam_path1.add(
    Component(
        label="Mirror 1",
        definition=optomech.circular_mirror(
            diameter=dim(1, "in"),
        ),
    ),
    beam_index=0b1,
    distance=dim(100, "mm"),
    rotation=(0, 0, 135),
)

beam_path1.add(
    Component(
        label="Mirror 1",
        definition=optomech.circular_mirror(
            diameter=dim(1, "in"),
        ),
    ),
    beam_index=0b10,
    distance=dim(200, "mm"),
    rotation=(0, 0, -45),
)

beam_path2.add(
    Component(
        label="Mirror 1",
        definition=optomech.circular_mirror(
            diameter=dim(1, "in"),
        ),
    ),
    beam_index=0b1,
    distance=dim(100, "mm"),
    rotation=(0, 0, -45),
)

beam_path2.add(
    Component(
        label="Mirror 2",
        definition=optomech.circular_sampler(
            ref_ratio=0.5,
            diameter=dim(1, "in"),
        ),
    ),
    beam_index=0b1,
    distance=dim(100, "mm"),
    rotation=(0, 0, -45),
)

example_layout.recompute()
