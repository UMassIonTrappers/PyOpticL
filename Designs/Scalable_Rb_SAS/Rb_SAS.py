"""Rb saturation absorption spectroscopy layout using the refactored API."""

from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import baseplate, optics, thorlabs
from PyOpticL.types import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from components import rb_cell, rb_cell_cube

scale = "one_inch_mounted"


if scale == "mini_optics":
    overall_scale = 0.25
    baseplate_height = dim(0.25, "in")
    optical_height = dim(0.5, "mm")
    beam_waist = dim(0.5, "mm")
    mirror = optics.rectangular_mirror(
        width=dim(3, "mm"),
        height=dim(4, "mm"),
        thickness=dim(2, "mm"),
    )
    waveplate = optics.circular_waveplate(
        diameter=dim(4, "mm"),
        thickness=dim(2, "mm"),
    )
    circular_sampler = optics.circular_sampler(
        diameter=dim(4, "mm"),
        thickness=dim(2, "mm"),
    )
    beamsplitter = optics.beamsplitter_cube(
        side_length=dim(3, "mm"),
        corner_drill_diameter=dim(1, "mm"),
    )
    rb_cell_definition = rb_cell_cube(
        side_length=dim(10, "mm"),
    )
    photodetector = thorlabs.photodiode_fds010()
    photodetector_constraint = dict(x_position=dim(2, "mm"))

elif scale == "half_inch_unmounted":
    overall_scale = 0.5
    baseplate_height = dim(1, "in")
    optical_height = dim(-0.25, "in")
    beam_waist = dim(1, "mm")
    mirror = optics.circular_mirror(
        diameter=dim(0.5, "in"),
    )
    waveplate = optics.circular_waveplate(
        diameter=dim(0.5, "in"),
    )
    circular_sampler = optics.circular_sampler(
        diameter=dim(0.5, "in"),
    )
    beamsplitter = optics.beamsplitter_cube(
        side_length=dim(10, "mm"),
    )
    rb_cell_definition = rb_cell_cube(
        side_length=dim(10, "mm"),
    )
    photodetector = thorlabs.photodiode_fds010()
    photodetector_constraint = dict(x_position=dim(2, "mm"))

elif scale == "half_inch_mounted":
    overall_scale = 1
    baseplate_height = dim(1, "in")
    optical_height = dim(0.5, "in")
    beam_waist = dim(1, "mm")
    mirror = optics.circular_mirror(
        diameter=dim(0.5, "in"),
        mount_definition=thorlabs.mirror_mount_k05s1(),
    )
    waveplate = optics.circular_waveplate(
        diameter=dim(0.5, "in"),
        mount_definition=thorlabs.rotation_mount_rsp05(),
    )
    circular_sampler = optics.circular_sampler(
        diameter=dim(0.5, "in"),
        mount_definition=thorlabs.beamsplitter_mount_b05g(),
    )
    beamsplitter = optics.beamsplitter_cube_on_surface_adapter(
        side_length=dim(10, "mm"),
        optical_height=dim(0.5, "in"),
    )
    rb_cell_definition = rb_cell(
        diameter=dim(25, "mm"),
        length=dim(80, "mm"),
    )
    photodetector = thorlabs.photodetector_pda10a2()
    photodetector_constraint = dict(distance=dim(2, "in") * overall_scale)

elif scale == "one_inch_mounted":
    overall_scale = 1.5
    baseplate_height = dim(1, "in")
    optical_height = dim(1, "in")
    beam_waist = dim(1, "mm")
    mirror = optics.circular_mirror(
        diameter=dim(1, "in"),
        mount_definition=thorlabs.mirror_mount_km100(),
    )
    waveplate = optics.circular_waveplate(
        diameter=dim(1, "in"),
        mount_definition=thorlabs.rotation_mount_rsp1(),
    )
    circular_sampler = optics.circular_sampler(
        diameter=dim(1, "in"),
        mount_definition=thorlabs.beamsplitter_mount_b1g(),
    )
    beamsplitter = optics.beamsplitter_cube_on_surface_adapter(
        side_length=dim(20, "mm"),
        optical_height=dim(1, "in"),
    )
    rb_cell_definition = rb_cell(
        diameter=dim(25, "mm"),
        length=dim(80, "mm"),
    )
    photodetector = thorlabs.photodetector_pda10a2()
    photodetector_constraint = dict(distance=dim(2, "in") * overall_scale)


rb_sas_baseplate = Component(
    label="Rb SAS",
    definition=baseplate(
        dimensions=(
            dim(18, "in") * overall_scale,
            dim(6, "in") * overall_scale,
            baseplate_height,
        ),
        optical_height=optical_height,
    ),
)

beam = rb_sas_baseplate.add(
    BeamPath(label="Beam", wavelength=780, waist=beam_waist),
    position=(dim(15.5, "in") * overall_scale, 0, 0),
    rotation=(0, 0, 90),
)

beam.add(
    Component(label="Input Mirror 1", definition=mirror),
    beam_index=0b1,
    distance=dim(1.5, "in") * overall_scale,
    rotation=(0, 0, -45),
)

beam.add(
    Component(label="Input Mirror 2", definition=mirror),
    beam_index=0b1,
    distance=dim(1, "in") * overall_scale,
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate 1", definition=waveplate),
    beam_index=0b1,
    distance=dim(1.5, "in") * overall_scale,
    rotation=(0, 0, 90),
)

beam.add(
    Component(
        label="Beam Splitter 1",
        definition=beamsplitter,
    ),
    beam_index=0b1,
    distance=dim(2, "in") * overall_scale,
    rotation=(0, 0, 90),
)


beam.add(
    Component(label="Mirror 1", definition=mirror),
    beam_index=0b11,
    distance=dim(3.5, "in") * overall_scale,
    rotation=(0, 0, -45),
)

beam.add(
    Component(
        label="Splitter",
        definition=circular_sampler,
    ),
    beam_index=0b11,
    distance=dim(0.75, "in") * overall_scale,
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate Probe 2", definition=waveplate),
    beam_index=0b111,
    distance=dim(1.75, "in") * overall_scale,
    rotation=(0, 0, 0),
)

beam.add(
    Component(label="Probe Mirror 1", definition=mirror),
    beam_index=0b111,
    distance=dim(1.25, "in") * overall_scale,
    rotation=(0, 0, -45),
)

beam.add(
    Component(label="Probe Mirror 2", definition=mirror),
    beam_index=0b111,
    y_position=dim(3, "in") * overall_scale,
    rotation=(0, 0, 135),
)

beam.add(
    Component(
        label="Rb Cell",
        definition=rb_cell_definition,
    ),
    beam_index=0b111,
    distance=dim(3.5, "in") * overall_scale,
    rotation=(0, 0, 0),
)

beam.add(
    Component(label="Pump Mirror 1", definition=mirror),
    beam_index=0b110,
    distance=dim(3, "in") * overall_scale,
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate Pump", definition=waveplate),
    beam_index=0b110,
    distance=dim(4, "in") * overall_scale,
    rotation=(0, 0, 180),
)

beam.add(
    Component(label="Pump Mirror 2", definition=mirror),
    beam_index=0b110,
    distance=dim(5.5, "in") * overall_scale,
    rotation=(0, 0, 45),
)

beam.add(
    Component(
        label="Beam Splitter 2",
        definition=beamsplitter,
    ),
    beam_index=0b110,
    y_position=dim(3, "in") * overall_scale,
    rotation=(0, 0, 180),
)

beam.add(
    Component(
        label="Photodetector",
        definition=photodetector,
    ),
    beam_index=0b1110,
    **photodetector_constraint,
    rotation=(0, 0, 0),
)


rb_sas_baseplate.recompute()
