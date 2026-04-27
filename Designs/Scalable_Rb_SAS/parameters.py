from PyOpticL.library import optics, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from .components import rb_cell_cube, rb_cell_tube


def get_scale_parameters(scale: str):

    if scale == "half_inch_mounted":
        return dict(
            overall_scale=1,
            baseplate_height=dim(1, "in"),
            optical_height=dim(0.5, "in"),
            beam_waist=dim(1, "mm"),
            mirror=optics.circular_mirror(
                diameter=dim(0.5, "in"),
                mount_definition=thorlabs.mirror_mount_k05s1(),
            ),
            waveplate=optics.circular_waveplate(
                diameter=dim(0.5, "in"),
                mount_definition=thorlabs.rotation_mount_rsp05(),
            ),
            circular_sampler=optics.circular_sampler(
                diameter=dim(0.5, "in"),
                mount_definition=thorlabs.beamsplitter_mount_b05g(),
            ),
            beamsplitter=optics.beamsplitter_cube_on_surface_adapter(
                side_length=dim(10, "mm"),
                optical_height=dim(0.5, "in"),
            ),
            rb_cell_definition=rb_cell_tube(
                diameter=dim(25, "mm"),
                length=dim(80, "mm"),
            ),
            photodetector=thorlabs.photodetector_pda10a2(),
            photodetector_constraint=dict(distance=dim(2, "in") * 1),
        )

    elif scale == "one_inch_mounted":
        return dict(
            overall_scale=1.5,
            baseplate_height=dim(1, "in"),
            optical_height=dim(1, "in"),
            beam_waist=dim(1, "mm"),
            mirror=optics.circular_mirror(
                diameter=dim(1, "in"),
                mount_definition=thorlabs.mirror_mount_km100(),
            ),
            waveplate=optics.circular_waveplate(
                diameter=dim(1, "in"),
                mount_definition=thorlabs.rotation_mount_rsp1(),
            ),
            circular_sampler=optics.circular_sampler(
                diameter=dim(1, "in"),
                mount_definition=thorlabs.beamsplitter_mount_b1g(),
            ),
            beamsplitter=optics.beamsplitter_cube_on_surface_adapter(
                side_length=dim(20, "mm"),
                optical_height=dim(1, "in"),
            ),
            rb_cell_definition=rb_cell_tube(
                diameter=dim(25, "mm"),
                length=dim(80, "mm"),
            ),
            photodetector=thorlabs.photodetector_pda10a2(),
            photodetector_constraint=dict(distance=dim(2, "in") * 1.5),
        )

    elif scale == "half_inch_unmounted":
        return dict(
            overall_scale=0.5,
            baseplate_height=dim(1, "in"),
            optical_height=dim(-0.25, "in"),
            beam_waist=dim(1, "mm"),
            mirror=optics.circular_mirror(
                diameter=dim(0.5, "in"),
            ),
            waveplate=optics.circular_waveplate(
                diameter=dim(0.5, "in"),
            ),
            circular_sampler=optics.circular_sampler(
                diameter=dim(0.5, "in"),
            ),
            beamsplitter=optics.beamsplitter_cube(
                side_length=dim(10, "mm"),
            ),
            rb_cell_definition=rb_cell_cube(
                side_length=dim(10, "mm"),
            ),
            photodetector=thorlabs.photodiode_fds010(),
            photodetector_constraint=dict(x_position=dim(2, "mm")),
        )

    elif scale == "mini_optics":
        return dict(
            overall_scale=0.25,
            baseplate_height=dim(0.25, "in"),
            optical_height=dim(0.5, "mm"),
            beam_waist=dim(0.5, "mm"),
            mirror=optics.rectangular_mirror(
                width=dim(3, "mm"),
                height=dim(4, "mm"),
                thickness=dim(2, "mm"),
            ),
            waveplate=optics.circular_waveplate(
                diameter=dim(4, "mm"),
                thickness=dim(2, "mm"),
            ),
            circular_sampler=optics.circular_sampler(
                diameter=dim(4, "mm"),
                thickness=dim(2, "mm"),
            ),
            beamsplitter=optics.beamsplitter_cube(
                side_length=dim(3, "mm"),
                corner_drill_diameter=dim(1, "mm"),
            ),
            rb_cell_definition=rb_cell_cube(
                side_length=dim(10, "mm"),
            ),
            photodetector=thorlabs.photodiode_fds010(),
            photodetector_constraint=dict(x_position=dim(2, "mm")),
        )
