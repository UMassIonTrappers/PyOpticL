from PyOpticL import optomech
from PyOpticL.beam_path import Beam_Path
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

example_layout = Layout("Example Layout")

wavelengths = [350, 450, 550]
offset = [dim(100, "mm"), dim(50, "mm"), dim(25, "mm")]
beam_offset = dim(2.5, "mm")
mirror_distance = dim(50, "mm")

for i, wavelength in enumerate(wavelengths):
    beam_path = example_layout.add(
        Beam_Path(
            label=f"Beam Path {wavelength}nm",
            position=(i * beam_offset, 0, 0),
            rotation=(0, 0, 90),
            waist=dim(2, "mm"),
            wavelength=wavelength,
        )
    )

    beam_path.add(
        Component(
            label=f"Longpass Dichroic Mirror {i+1}",
            definition=optomech.circular_dichroic_mirror(
                ref_wavelengths=[[None, wavelength + 50]],
                diameter=dim(1, "in"),
            ),
            rotation=(0, 0, -135),
        ),
        beam_index=0b1,
        distance=(i + 1) * mirror_distance,
    )

example_layout.recompute()
