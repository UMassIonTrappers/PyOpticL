"""Rb saturation absorption spectroscopy layout using the refactored API."""

from PyOpticL.beam_path import BeamPath, Interface
from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import baseplate, hardware, optics, thorlabs
from PyOpticL.settings import set_hidden_object_groups
from PyOpticL.types import Dimension as dim
from PyOpticL.utils import box_shape, cylinder_shape, import_model

scale = "mini_optics"  # "mini_optics" or "half_inch_mounted"


class rb_cell_holder:
    """
    A surface mount holder for the RB cell
    """

    object_group = "adapters"
    object_color = (0.5, 0.7, 0.5)
    mesh = import_model("rb_cell_holder", "./models")

    def __init__(self, bolt_length: dim = None, drill_depth: dim = None):
        self.bolt_length = bolt_length
        self.drill_depth = drill_depth

    def subcomponents(self):
        components = []
        for x, y in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mounting Bolt",
                        definition=hardware.bolt(
                            types=["8_32", "M4"],
                            length=self.bolt_length,
                            clear_depth=dim(1 / 2, "in"),
                            drill_depth=self.drill_depth,
                        ),
                    ),
                    position=(
                        x * dim(45, "mm"),
                        y * dim(15.7, "mm"),
                        dim(1 / 2, "in"),
                    ),
                    rotation=(0, 0, 0),
                )
            )
        return components


class rb_cell:
    """
    A model of a cylindrical Rb cell
    """

    object_group = "optics"
    object_color = (0.5, 0.5, 0.7)

    def __init__(
        self,
        diameter: dim,
        length: dim,
        bolt_length: dim = None,
        drill_depth: dim = None,
    ):
        self.diameter = diameter
        self.length = length
        self.bolt_length = bolt_length
        self.drill_depth = drill_depth

    def interfaces(self):
        return [
            Interface(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.diameter,
            )
        ]

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Rb Cell Holder",
                    definition=rb_cell_holder(
                        bolt_length=self.bolt_length,
                        drill_depth=self.drill_depth,
                    ),
                ),
                position=(0, 0, 0),
                rotation=(0, 0, 0),
            )
        ]

    def shape(self):
        part = cylinder_shape(
            diameter=self.diameter,
            height=self.length,
            rotation=(0, 90, 0),
            center=0,
        )
        # end caps
        for i in [-1, 1]:
            part = part.fuse(
                cylinder_shape(
                    diameter=self.diameter + dim(2, "mm"),
                    height=dim(2, "mm"),
                    center=i,
                    position=(i * self.length / 2, 0, 0),
                    rotation=(0, 90, 0),
                )
            )
        return part


class rb_cell_cube:
    """
    A cube-shaped Rb cell for testing purposes
    """

    object_group = "optics"
    object_color = (0.5, 0.5, 0.7)

    def __init__(
        self,
        side_length: dim,
        bolt_length: dim = None,
        drill_depth: dim = None,
    ):
        self.side_length = side_length
        self.bolt_length = bolt_length
        self.drill_depth = drill_depth

    def interfaces(self):
        return [
            Interface(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=self.side_length,
            )
        ]

    def shape(self):
        part = box_shape(
            dimensions=(self.side_length, self.side_length, self.side_length),
        )
        return part


if scale == "mini_optics":
    overall_scale = 0.25
    baseplate_height = dim(0.25, "in")
    optical_height = dim(1, "mm")
    beam_waist = dim(0.5, "mm")
    mirror_definition = optics.rectangular_mirror(
        width=dim(3, "mm"),
        height=dim(4, "mm"),
        thickness=dim(2, "mm"),
    )
    waveplate_definition = optics.circular_waveplate(
        diameter=dim(4, "mm"),
        thickness=dim(2, "mm"),
    )
    circular_sampler_definition = optics.circular_sampler(
        diameter=dim(4, "mm"),
        thickness=dim(2, "mm"),
    )
    beamsplitter_definition = optics.beamsplitter_cube(
        side_length=dim(3, "mm"),
        corner_drill_diameter=dim(1, "mm"),
    )
    rb_cell_definition = rb_cell_cube(
        side_length=dim(10, "mm"),
    )
    photodetector_definition = thorlabs.photodiode_fds010()

elif scale == "half_inch_mounted":
    overall_scale = 1
    baseplate_height = dim(1, "in")
    optical_height = dim(0.5, "in")
    beam_waist = dim(1, "mm")
    mirror_definition = optics.circular_mirror(
        diameter=dim(0.5, "in"),
        mount_definition=thorlabs.mirror_mount_k05s1(),
    )
    waveplate_definition = optics.circular_waveplate(
        diameter=dim(0.5, "in"),
        mount_definition=thorlabs.rotation_mount_rsp05(),
    )
    circular_sampler_definition = optics.circular_sampler(
        diameter=dim(0.5, "in"),
        mount_definition=thorlabs.beamsplitter_mount_b05g(),
    )
    beamsplitter_definition = optics.beamsplitter_cube_on_surface_adapter(
        side_length=dim(10, "mm"),
        optical_height=dim(0.5, "in"),
    )
    rb_cell_definition = rb_cell(
        diameter=dim(25, "mm"),
        length=dim(80, "mm"),
    )
    photodetector_definition = thorlabs.photodetector_pda10a2()


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
    Component(label="Input Mirror 1", definition=mirror_definition),
    beam_index=0b1,
    distance=dim(1.5, "in") * overall_scale,
    rotation=(0, 0, -45),
)

beam.add(
    Component(label="Input Mirror 2", definition=mirror_definition),
    beam_index=0b1,
    distance=dim(1, "in") * overall_scale,
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate 1", definition=waveplate_definition),
    beam_index=0b1,
    distance=dim(1.5, "in") * overall_scale,
    rotation=(0, 0, 90),
)

beam.add(
    Component(
        label="Beam Splitter 1",
        definition=beamsplitter_definition,
    ),
    beam_index=0b1,
    distance=dim(2, "in") * overall_scale,
    rotation=(0, 0, 90),
)


beam.add(
    Component(label="Mirror 1", definition=mirror_definition),
    beam_index=0b11,
    distance=dim(3.5, "in") * overall_scale,
    rotation=(0, 0, -45),
)

beam.add(
    Component(
        label="Splitter",
        definition=circular_sampler_definition,
    ),
    beam_index=0b11,
    distance=dim(0.75, "in") * overall_scale,
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate Probe 2", definition=waveplate_definition),
    beam_index=0b111,
    distance=dim(1.75, "in") * overall_scale,
    rotation=(0, 0, 0),
)

beam.add(
    Component(label="Probe Mirror 1", definition=mirror_definition),
    beam_index=0b111,
    distance=dim(1.25, "in") * overall_scale,
    rotation=(0, 0, -45),
)

beam.add(
    Component(label="Probe Mirror 2", definition=mirror_definition),
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
    Component(label="Pump Mirror 1", definition=mirror_definition),
    beam_index=0b110,
    distance=dim(3, "in") * overall_scale,
    rotation=(0, 0, 135),
)

beam.add(
    Component(label="Half Waveplate Pump", definition=waveplate_definition),
    beam_index=0b110,
    distance=dim(4, "in") * overall_scale,
    rotation=(0, 0, 180),
)

beam.add(
    Component(label="Pump Mirror 2", definition=mirror_definition),
    beam_index=0b110,
    distance=dim(5.5, "in") * overall_scale,
    rotation=(0, 0, 45),
)

beam.add(
    Component(
        label="Beam Splitter 2",
        definition=beamsplitter_definition,
    ),
    beam_index=0b110,
    y_position=dim(3, "in") * overall_scale,
    rotation=(0, 0, 180),
)

beam.add(
    Component(
        label="Photodetector",
        definition=photodetector_definition,
    ),
    beam_index=0b1110,
    distance=dim(2, "in") * overall_scale,
    rotation=(0, 0, 0),
)


rb_sas_baseplate.recompute()
