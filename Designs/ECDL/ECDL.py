from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component, Layout
from PyOpticL.library import baseplate
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import cardinal_angle, fix_relative_imports, turn_angle

fix_relative_imports()

from components import km100pm_ecdl

layout = Layout(label="ECDL")

layout.add(
    Component(label="Testing", definition=km100pm_ecdl()),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
)

layout.recompute()
