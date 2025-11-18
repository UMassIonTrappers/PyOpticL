from PyOpticL import optomech
from PyOpticL.beam_path import Beam_Path
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

layout = Layout("Example Layout")

layout.add(
    Component(
        label="mount",
        definition=optomech.mirror_mount_k05s1(),
    ),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
)

layout.recompute()
