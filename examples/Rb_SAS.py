"""Rb saturation absorption spectroscopy layout using the refactored API."""

from datetime import datetime

from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component, Layout
from PyOpticL.library import baseplate, optics, thorlabs
from PyOpticL.settings import hidden_object_groups, set_hidden_object_groups
from PyOpticL.types import Dimension as dim

set_hidden_object_groups(["hardware"])

mirror_definition = optics.circular_mirror(
    diameter=dim(0.5, "in"),
    mount_definition=thorlabs.mirror_mount_k05s1(),
)

waveplate_definition = optics.circular_waveplate(
    diameter=dim(0.5, "in"),
    retardance=0.5,
    fast_axis_angle=0,
    mount_definition=thorlabs.rotation_mount_rsp05(),
)

beamsplitter_definition = optics.beamsplitter_cube_on_surface_adapter(
    side_length=dim(10, "mm"),
    optical_height=dim(0.5, "in"),
)

rb_sas_baseplate = Component(
    label="Rb SAS",
    definition=baseplate(
        dimensions=(dim(15, "in"), dim(5, "in"), dim(1, "in")),
        optical_height=dim(0.5, "in"),
    ),
)

beam = rb_sas_baseplate.add(
    BeamPath(label="Beam", wavelength=780, waist=dim(1, "mm")),
    position=(dim(12.5, "in"), 0, 0),
    rotation=(0, 0, 90),
)

beam.add(
    Component(label="Input Mirror 1", definition=mirror_definition),
    beam_index=0b1,
    distance=dim(1.5, "in"),
    rotation=(0, 0, -45),
)

beam.add(
    Component(label="Input Mirror 2", definition=mirror_definition),
    beam_index=0b1,
    distance=dim(1, "in"),
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate 1", definition=waveplate_definition),
    beam_index=0b1,
    distance=dim(1.5, "in"),
    rotation=(0, 0, 90),
)

beam.add(
    Component(label="Half Waveplate Probe 1", definition=waveplate_definition),
    beam_index=0b11,
    distance=dim(3.5, "in"),
    rotation=(0, 0, 0),
)

beam.add(
    Component(
        label="Beam Splitter 1",
        definition=beamsplitter_definition,
    ),
    beam_index=0b1,
    distance=dim(2, "in"),
    rotation=(0, 0, 90),
)

beam.add(
    Component(label="Mirror 1", definition=mirror_definition),
    beam_index=0b11,
    distance=dim(1.75, "in"),
    rotation=(0, 0, -45),
)

beam.add(
    Component(
        label="Splitter",
        definition=optics.circular_sampler(
            diameter=dim(0.5, "in"),
            thickness=dim(3, "mm"),
            ref_ratio=0.5,
            mount_definition=thorlabs.beamsplitter_mount_b05g(),
        ),
    ),
    beam_index=0b11,
    distance=dim(0.75, "in"),
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate Probe 2", definition=waveplate_definition),
    beam_index=0b111,
    distance=dim(1.5, "in"),
    rotation=(0, 0, 0),
)

beam.add(
    Component(label="Probe Mirror 1", definition=mirror_definition),
    beam_index=0b111,
    distance=dim(1.5, "in"),
    rotation=(0, 0, -45),
)

beam.add(
    Component(label="Probe Mirror 2", definition=mirror_definition),
    beam_index=0b111,
    distance=dim(1.5, "in"),
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Pump Mirror 1", definition=mirror_definition),
    beam_index=0b110,
    distance=dim(3, "in"),
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate Pump", definition=waveplate_definition),
    beam_index=0b110,
    distance=dim(4, "in"),
    rotation=(0, 0, 180),
)

beam.add(
    Component(label="Pump Mirror 2", definition=mirror_definition),
    beam_index=0b110,
    distance=dim(5.5, "in"),
    rotation=(0, 0, 45),
)

beam.add(
    Component(
        label="Beam Splitter 2",
        definition=beamsplitter_definition,
    ),
    beam_index=0b110,
    distance=dim(1.625, "in"),
    rotation=(0, 0, 180),
)

beam.add(
    Component(
        label="Photodetector",
        definition=thorlabs.photodetector_pda10a2(),
    ),
    beam_index=0b1110,
    distance=dim(30, "mm"),
    rotation=(0, 0, 0),
)


rb_sas_baseplate.recompute()
