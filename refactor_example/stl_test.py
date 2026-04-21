from PyOpticL import optomech
from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component, Layout
from PyOpticL.types import Dimension as dim

mirror = optomech.circular_mirror(
    diameter=dim(0.5, "in"),
    thickness=dim(5, "mm"),
    mount_definition=optomech.mirror_mount_k05s1(drill_depth=dim(10, "mm")),
)

layout = Layout("Example Layout")

layout.add(
    Component(label="mounts", definition=mirror),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
)

layout.recompute()
