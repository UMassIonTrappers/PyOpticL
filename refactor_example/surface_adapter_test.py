from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component, Layout
from PyOpticL.library import baseplate, optics, thorlabs
from PyOpticL.types import Dimension as dim

baseplate = Component(
    label="Baseplate",
    definition=baseplate(
        dimensions=(dim(100, "mm"), dim(100, "mm"), dim(1, "in")),
        optical_height=dim(0.5, "in"),
    ),
)

# baseplate = Layout("Baseplate")

# baseplate.add(
#     Component(
#         label="pbs",
#         definition=thorla.beamsplitter_cube_on_surface_adapter(
#             side_length=dim(10, "mm"), optical_height=dim(0.5, "in"), ref_ratio=0.5
#         ),
#     ),
#     position=(0, 0, 0),
#     rotation=(0, 0, 0),
# )

baseplate.add(
    Component(label="pd", definition=thorlabs.photodetector_pda10a2()),
    position=(40, 40, 0),
    rotation=(0, 0, 0),
)

baseplate.recompute()
