from PyOpticL import optomech
from PyOpticL.beam_path import Beam_Path
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

mirror = optomech.circular_mirror(
    diameter=dim(0.5, "in"),
    thickness=dim(5, "mm"),
    mount_definition=optomech.mirror_mount_k05s1(drill_depth=dim(1, "in")),
)

baseplate = Component(
    label="Baseplate",
    definition=optomech.baseplate(
        dimensions=(dim(8, "in"), dim(5, "in"), dim(1, "in")),
        optical_height=dim(0.5, "in"),
    ),
)

beam_path = baseplate.add(
    Beam_Path(
        label="Beam Path",
        waist=dim(1, "mm"),
        wavelength=670,
    ),
    position=(dim(2, "in"), 0, 0),
    rotation=(0, 0, 90),
)

beam_path.add(
    Component(label="Mirror 1", definition=mirror),
    beam_index=0b1,
    distance=dim(1, "in"),
    rotation=(0, 0, -45),
)

beam_path.add(
    Component(label="Mirror 2", definition=mirror),
    beam_index=0b1,
    distance=dim(4, "in"),
    rotation=(0, 0, 135),
)

beam_path.add(
    Component(label="Mirror 3", definition=mirror),
    beam_index=0b1,
    distance=dim(2, "in"),
    rotation=(0, 0, -135),
)

beam_path.add(
    Component(label="Mirror 4", definition=mirror),
    beam_index=0b1,
    distance=dim(4, "in"),
    rotation=(0, 0, 45),
)

baseplate.recompute()
