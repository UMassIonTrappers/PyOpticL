from PyOpticL.library import optics, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from scalable_rb_sas.components import rb_cell_cube, rb_cell_tube


def get_scale_parameters(scale: str):

    if scale == "half_inch_mounted":
        return dict(
            overall_scale=1,
            baseplate_height=dim(1, "in"),
            optical_height=dim(0.5, "in"),
            mount_holes=[
                (1, 1),
                (6, 1),
                (10, 1),
                (16, 1),
                (12, 3),
                (15, 3),
                (1, 6),
                (6, 6),
                (11, 6),
                (15, 6),
            ],
            beam_waist=dim(1, "mm"),
            mirror=optics.Circular_Mirror(
                diameter=dim(0.5, "in"),
                mount_definition=thorlabs.Mirror_Mount_K05S1(),
            ),
            waveplate=optics.Circular_Waveplate(
                diameter=dim(0.5, "in"),
                mount_definition=thorlabs.Rotation_Mount_RSP05(),
            ),
            circular_sampler=optics.Circular_Sampler(
                diameter=dim(0.5, "in"),
                mount_definition=thorlabs.Beamsplitter_Mount_B05G(),
            ),
            beamsplitter=optics.Beamsplitter_Cube_on_Surface_Adapter(
                side_length=dim(10, "mm"),
                optical_height=dim(0.5, "in"),
            ),
            rb_cell_definition=rb_cell_tube(
                diameter=dim(25, "mm"),
                length=dim(80, "mm"),
            ),
            photodetector=thorlabs.Photodetector_PDA10A2(),
            photodetector_constraint=dict(distance=dim(2, "in") * 1),
        )

    elif scale == "one_inch_mounted":
        return dict(
            overall_scale=1.5,
            baseplate_height=dim(1, "in"),
            optical_height=dim(1, "in"),
            mount_holes=[],
            beam_waist=dim(1, "mm"),
            mirror=optics.Circular_Mirror(
                diameter=dim(1, "in"),
                mount_definition=thorlabs.Mirror_Mount_KM100(),
            ),
            waveplate=optics.Circular_Waveplate(
                diameter=dim(1, "in"),
                mount_definition=thorlabs.Rotation_Mount_RSP1(),
            ),
            circular_sampler=optics.Circular_Sampler(
                diameter=dim(1, "in"),
                mount_definition=thorlabs.beamsplitter_mount_b1g(),
            ),
            beamsplitter=optics.Beamsplitter_Cube_on_Surface_Adapter(
                side_length=dim(20, "mm"),
                optical_height=dim(1, "in"),
            ),
            rb_cell_definition=rb_cell_tube(
                diameter=dim(25, "mm"),
                length=dim(80, "mm"),
            ),
            photodetector=thorlabs.Photodetector_PDA10A2(),
            photodetector_constraint=dict(distance=dim(2, "in") * 1.5),
        )

    elif scale == "half_inch_unmounted":
        return dict(
            overall_scale=0.5,
            baseplate_height=dim(1, "in"),
            optical_height=dim(-0.25, "in"),
            mount_holes=[],
            beam_waist=dim(1, "mm"),
            mirror=optics.Circular_Mirror(
                diameter=dim(0.5, "in"),
            ),
            waveplate=optics.Circular_Waveplate(
                diameter=dim(0.5, "in"),
            ),
            circular_sampler=optics.Circular_Sampler(
                diameter=dim(0.5, "in"),
            ),
            beamsplitter=optics.Beamsplitter_Cube(
                side_length=dim(10, "mm"),
            ),
            rb_cell_definition=rb_cell_cube(
                side_length=dim(10, "mm"),
            ),
            photodetector=thorlabs.Photodiode_FDS010(),
            photodetector_constraint=dict(x_position=dim(2, "mm")),
        )

    elif scale == "mini_optics":
        return dict(
            overall_scale=0.25,
            baseplate_height=dim(0.25, "in"),
            optical_height=dim(0.5, "mm"),
            mount_holes=[],
            beam_waist=dim(0.5, "mm"),
            mirror=optics.Rectangular_Mirror(
                width=dim(3, "mm"),
                height=dim(4, "mm"),
                thickness=dim(2, "mm"),
            ),
            waveplate=optics.Circular_Waveplate(
                diameter=dim(4, "mm"),
                thickness=dim(2, "mm"),
            ),
            circular_sampler=optics.Circular_Sampler(
                diameter=dim(4, "mm"),
                thickness=dim(2, "mm"),
            ),
            beamsplitter=optics.Beamsplitter_Cube(
                side_length=dim(3, "mm"),
                corner_drill_diameter=dim(1, "mm"),
            ),
            rb_cell_definition=rb_cell_cube(
                side_length=dim(10, "mm"),
            ),
            photodetector=thorlabs.Photodiode_FDS010(),
            photodetector_constraint=dict(x_position=dim(2, "mm")),
        )
