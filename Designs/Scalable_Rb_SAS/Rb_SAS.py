from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import baseplate
from PyOpticL.types import Dimension as dim
from PyOpticL.types import cardinal_angle, turn_angle
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from parameters import get_scale_parameters

scale_params = get_scale_parameters("half_inch_mounted")

rb_sas_baseplate = Component(
    label="Rb SAS",
    definition=baseplate(
        dimensions=(
            dim(18, "in") * scale_params["overall_scale"],
            dim(6, "in") * scale_params["overall_scale"],
            scale_params["baseplate_height"],
        ),
        optical_height=scale_params["optical_height"],
    ),
)

beam = rb_sas_baseplate.add(
    BeamPath(label="Beam", wavelength=780, waist=scale_params["beam_waist"]),
    position=(dim(15.5, "in") * scale_params["overall_scale"], 0, 0),
    rotation=cardinal_angle["up"],
)

beam.add(
    Component(label="Input Mirror 1", definition=scale_params["mirror"]),
    beam_index=0b1,
    distance=dim(1.5, "in") * scale_params["overall_scale"],
    rotation=turn_angle["up-right"],
)

beam.add(
    Component(label="Input Mirror 2", definition=scale_params["mirror"]),
    beam_index=0b1,
    distance=dim(1, "in") * scale_params["overall_scale"],
    rotation=turn_angle["right-up"],
)

beam.add(
    Component(label="Input Half Waveplate", definition=scale_params["waveplate"]),
    beam_index=0b1,
    distance=dim(1.5, "in") * scale_params["overall_scale"],
    rotation=cardinal_angle["up"],
)

beam.add(
    Component(label="Beam Splitter 1", definition=scale_params["beamsplitter"]),
    beam_index=0b1,
    distance=dim(2, "in") * scale_params["overall_scale"],
    rotation=cardinal_angle["up"],
)


beam.add(
    Component(label="Input Mirror 3", definition=scale_params["mirror"]),
    beam_index=0b11,
    distance=dim(3.5, "in") * scale_params["overall_scale"],
    rotation=turn_angle["left-down"],
)

beam.add(
    Component(label="Pump/Probe Splitter", definition=scale_params["circular_sampler"]),
    beam_index=0b11,
    distance=dim(0.75, "in") * scale_params["overall_scale"],
    rotation=turn_angle["down-left"],
)

beam.add(
    Component(label="Probe Half Waveplate", definition=scale_params["waveplate"]),
    beam_index=0b111,
    distance=dim(1.75, "in") * scale_params["overall_scale"],
    rotation=cardinal_angle["left"],
)

beam.add(
    Component(label="Probe Mirror 1", definition=scale_params["mirror"]),
    beam_index=0b111,
    distance=dim(1.25, "in") * scale_params["overall_scale"],
    rotation=turn_angle["left-down"],
)

beam.add(
    Component(label="Probe Mirror 2", definition=scale_params["mirror"]),
    beam_index=0b111,
    y_position=dim(3, "in") * scale_params["overall_scale"],
    rotation=turn_angle["down-left"],
)

beam.add(
    Component(label="Rb Cell", definition=scale_params["rb_cell_definition"]),
    beam_index=0b111,
    distance=dim(3.5, "in") * scale_params["overall_scale"],
    rotation=cardinal_angle["right"],
)

beam.add(
    Component(label="Pump Mirror 1", definition=scale_params["mirror"]),
    beam_index=0b110,
    distance=dim(3, "in") * scale_params["overall_scale"],
    rotation=turn_angle["down-left"],
)

beam.add(
    Component(label="Pump Half Waveplate", definition=scale_params["waveplate"]),
    beam_index=0b110,
    distance=dim(4, "in") * scale_params["overall_scale"],
    rotation=cardinal_angle["left"],
)

beam.add(
    Component(label="Pump Mirror 2", definition=scale_params["mirror"]),
    beam_index=0b110,
    distance=dim(5.5, "in") * scale_params["overall_scale"],
    rotation=turn_angle["left-up"],
)

beam.add(
    Component(label="Beam Splitter 2", definition=scale_params["beamsplitter"]),
    beam_index=0b110,
    y_position=dim(3, "in") * scale_params["overall_scale"],
    rotation=cardinal_angle["left"],
)

beam.add(
    Component(label="Photodetector", definition=scale_params["photodetector"]),
    beam_index=0b1110,
    **scale_params["photodetector_constraint"],
    rotation=cardinal_angle["right"],
)

if __name__ == "__main__":
    rb_sas_baseplate.recompute()
