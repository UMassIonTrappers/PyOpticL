from PyOpticL import optomech
from PyOpticL.beam_path import Beam_Path
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

mirror = optomech.circular_mirror(
    diameter=dim(0.5, "in"),
    thickness=dim(5, "mm"),
    mount_definition=optomech.mirror_mount_k05s1(drill_depth=dim(10, "mm")),
)

layout = Layout("Example Layout")

layout.add(
    Component(label="mount", definition=mirror),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
)

layout.recompute()
