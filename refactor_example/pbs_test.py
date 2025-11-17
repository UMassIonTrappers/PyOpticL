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
        polarization=45,
    ),
    position=(0, 0, 0),
    rotation=(0, 0, 90),
)

beam_path.add(
    Component(
        label="PBS 1",
        definition=optomech.polarizing_beam_splitter_cube(
            size=dim(1, "in"), ref_polarization=0
        ),
    ),
    beam_index=0b1,
    distance=dim(100, "mm"),
    rotation=(0, 0, 90),
)

beam_path.add(
    Component(
        label="Mirror 1",
        definition=optomech.circular_mirror(
            diameter=dim(1, "in"),
        ),
    ),
    beam_index=0b11,
    distance=dim(100, "mm"),
    rotation=(0, 0, 135),
)

beam_path.add(
    Component(
        label="Mirror 2",
        definition=optomech.circular_mirror(
            diameter=dim(1, "in"),
        ),
    ),
    beam_index=0b11,
    distance=dim(100, "mm"),
    rotation=(0, 0, -135),
)

beam_path.add(
    Component(
        label="PBS 2",
        definition=optomech.polarizing_beam_splitter_cube(
            size=dim(1, "in"), ref_polarization=0
        ),
    ),
    beam_index=0b10,
    distance=dim(100, "mm"),
    rotation=(0, 0, 0),
)


layout.recompute()
