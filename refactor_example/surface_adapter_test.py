from PyOpticL import optomech
from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.types import Dimension as dim
from PyOpticL.layout import Layout

baseplate = Component(
    label="Baseplate",
    definition=optomech.baseplate(
        dimensions=(dim(100, "mm"), dim(100, "mm"), dim(20, "mm")),
        optical_height=dim(20, "mm"),
    ),
)

# baseplate = Layout("Baseplate")

mount = baseplate.add(
    Component(
        label="Surface Adapter",
        definition=optomech.surface_adapter(
            height=dim(10, "mm"), min_length=dim(20, "mm"), bolt_spacing=dim(40, "mm")
        ),
    ),
    position=(50, 50, -25),
    rotation=(0, 0, 0),
)

mount.add(
    Component(
        label="pbs",
        definition=optomech.polarizing_beam_splitter_cube(size=dim(10, "mm")),
    ),
    position=(0, 0, 4),
    rotation=(0, 0, 0),
)

baseplate.add(
    Component(label="test", definition=optomech.rotation_mount_rsp05()),
    position=(20, 20, -10),
    rotation=(0, 0, 0),
)

baseplate.recompute()
