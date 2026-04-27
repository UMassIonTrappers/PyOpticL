from PyOpticL.beam_path import BeamPath, linear_polarization
from PyOpticL.layout import Component, Layout
from PyOpticL.library import optics
from PyOpticL.utils import Dimension as dim

layout = Layout("Example Layout")

beam_path = layout.add(
    BeamPath(
        label="Beam Path",
        waist=dim(1, "mm"),
        wavelength=670,
        polarization=linear_polarization(45),
    ),
    position=(0, 0, 0),
    rotation=(0, 0, 90),
)

beam_path.add(
    Component(
        label="PBS 1",
        definition=optics.beamsplitter_cube(
            side_length=dim(10, "mm"), optical_height=dim(0.5, "in")
        ),
    ),
    beam_index=0b1,
    distance=dim(100, "mm"),
    rotation=(0, 0, 90),
)

# beam_path.add(
#     Component(
#         label="Mirror 1",
#         definition=optomech.circular_mirror(
#             diameter=dim(1, "in"),
#             thickness=dim(5, "mm"),
#         ),
#     ),
#     beam_index=0b11,
#     distance=dim(100, "mm"),
#     rotation=(0, 0, 135),
# )

# beam_path.add(
#     Component(
#         label="Mirror 2",
#         definition=optomech.circular_mirror(
#             diameter=dim(1, "in"),
#             thickness=dim(5, "mm"),
#         ),
#     ),
#     beam_index=0b11,
#     distance=dim(100, "mm"),
#     rotation=(0, 0, -135),
# )

# beam_path.add(
#     Component(
#         label="PBS 2",
#         definition=optomech.polarizing_beam_splitter_cube(
#             size=dim(1, "in"), ref_polarization=0
#         ),
#     ),
#     beam_index=0b10,
#     distance=dim(100, "mm"),
#     rotation=(0, 0, 0),
# )


layout.recompute()
