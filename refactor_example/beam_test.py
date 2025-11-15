from PyOpticL import optomech
from PyOpticL.beam_path import Beam_Path
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

example_layout = Layout("Example Layout")

print("Created layout")

beam_path = example_layout.add(
    Beam_Path(
        label="Beam Path",
        position=(10, 20, 0),
        rotation=(0, 0, 60),
        waist=dim(2, "mm"),
        wavelength=350,
    )
)

print("Created beam path")

beam_path.add(
    Component(
        label="Mirror 1",
        definition=optomech.circular_mirror(
            diameter=dim(1, "in"),
        ),
        rotation=(0, 0, -135),
    ),
    beam_index=1,
    distance=dim(150, "mm"),
)

print("Added first mirror")

beam_path.add(
    Component(
        label="Mirror 2",
        definition=optomech.circular_sampler(
            ref_ratio=0.25,
            diameter=dim(1, "in"),
        ),
        rotation=(0, 0, 45),
    ),
    beam_index=1,
    distance=dim(100, "mm"),
)

example_layout.recompute()
