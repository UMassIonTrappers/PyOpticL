import math

from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import baseplate, optics, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from components import grid_optics_mount, km05t_laser, simple_post

redstone = Component(
    label="Baseplate",
    definition=baseplate(
        dimensions=(dim(120, "in"), dim(65, "in"), dim(1, "in")),
        optical_height=0,
    ),
)


for side in [-1, 1]:
    x = dim(60, "in") + side * dim(25, "in")
    y = dim(50, "in")

    grid = redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=km05t_laser(),
                optical_height=abs(thorlabs.kinematic_mount_km05t.mount_position[2]),
            ),
            recompute_priority=-1,
        ),
        position=(x, y, 0),
        rotation=(0, 0, -135 if side == -1 else -45),
    )

    for obj in grid.get_object().Children:
        obj.Proxy.add(
            BeamPath(
                label="Beam",
                bound_parent=redstone,
                final_distance=dim(2.5, "in"),
            ),
            position=(0, 0, 0),
            rotation=(0, 0, 0),
        )

    redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=optics.circular_waveplate(
                    diameter=dim(0.5, "in"),
                    fast_axis_angle=45,
                    mount_definition=thorlabs.rotation_mount_rsp05(),
                ),
                optical_height=dim(1, "in"),
            ),
        ),
        position=(x + side * dim(5, "in"), y - dim(5, "in"), 0),
        rotation=(0, 0, -135 if side == -1 else -45),
    )

    grid = redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=km05t_laser(),
                optical_height=abs(thorlabs.kinematic_mount_km05t.mount_position[2]),
            ),
            recompute_priority=-1,
        ),
        position=(x + side * dim(12.5, "in"), y + dim(7.5, "in"), 0),
        rotation=(0, 0, -135 if side == -1 else -45),
    )

    for obj in grid.get_object().Children:
        obj.Proxy.add(
            BeamPath(
                label="Beam",
                bound_parent=redstone,
                final_distance=dim(2.5, "in"),
            ),
            position=(0, 0, 0),
            rotation=(0, 0, 0),
        )

    redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=optics.circular_waveplate(
                    diameter=dim(0.5, "in"),
                    mount_definition=thorlabs.rotation_mount_rsp05(),
                ),
                optical_height=dim(1, "in"),
            ),
        ),
        position=(x + side * dim(15, "in"), y + dim(5, "in"), 0),
        rotation=(0, 0, -135 if side == -1 else -45),
    )

    redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=optics.circular_mirror(
                    diameter=dim(0.5, "in"),
                    mount_definition=thorlabs.mirror_mount_k05s1(),
                ),
                optical_height=dim(0.5, "in"),
                grid_spacing_y=dim(2, "in") * math.sqrt(2),
            ),
        ),
        position=(x + side * dim(25, "in"), y - dim(5, "in"), 0),
        rotation=(0, 0, 0 if side == -1 else 180),
    )

    redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=optics.beamsplitter_cube(
                    side_length=dim(0.5, "in"), ref_polarization=0
                ),
                optical_height=dim(0.25, "in"),
                component_rotation=(0, 0, -45),
                grid_spacing_y=dim(2, "in") * math.sqrt(2),
            ),
        ),
        position=(x + side * dim(15, "in"), y - dim(15, "in"), 0),
        rotation=(0, 0, -90),
    )

    redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=optics.circular_mirror(
                    diameter=dim(0.5, "in"),
                    mount_definition=thorlabs.mirror_mount_k05s1(),
                ),
                optical_height=dim(0.5, "in"),
                grid_spacing_y=dim(2, "in") * math.sqrt(2),
            ),
        ),
        position=(x + side * dim(25, "in"), y - dim(25, "in"), 0),
        rotation=(0, 0, 0 if side == -1 else 180),
    )

    redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=optics.circular_waveplate(
                    diameter=dim(0.5, "in"),
                    mount_definition=thorlabs.rotation_mount_rsp05(),
                ),
                optical_height=dim(1, "in"),
            ),
        ),
        position=(x + side * dim(17.5, "in"), y - dim(32.5, "in"), 0),
        rotation=(0, 0, -45 if side == -1 else -135),
    )

    redstone.add(
        Component(
            label="Grid Optics Mount",
            definition=grid_optics_mount(
                n_grid=6,
                component_definition=km05t_laser(),
                optical_height=abs(thorlabs.kinematic_mount_km05t.mount_position[2]),
            ),
        ),
        position=(x + side * dim(15, "in"), y - dim(35, "in"), 0),
        rotation=(0, 0, 135 if side == -1 else 45),
    )

n_lasers = 13
laser_spacing = dim(1.5, "in")
height_step = dim(5, "mm")

x_position = dim(60, "in")
y_position = dim(5, "in")

for side in [-1, 1]:
    for i in range(n_lasers):
        for dir in [0, 1]:
            side_offset = -side * (laser_spacing * n_lasers + dim(7, "in"))
            if dir == 0:
                position = [
                    x_position
                    + side_offset
                    + side * (i * laser_spacing + dim(2, "in")),
                    y_position,
                    i * height_step + dim(1.5, "in"),
                ]
                mirror_args = dict(
                    x_position=x_position
                    + side_offset
                    + side * (n_lasers * laser_spacing + dim(5, "in")),
                    rotation=(0, 0, 180 if side == 1 else 0),
                )
            else:
                position = [
                    x_position + side_offset,
                    y_position + i * laser_spacing + dim(2, "in"),
                    i * height_step + dim(1.5, "in"),
                ]
                mirror_args = dict(
                    y_position=y_position + n_lasers * laser_spacing + dim(5, "in"),
                    rotation=(0, 0, -90),
                )

            redstone.add(
                Component(
                    label="Laser",
                    definition=km05t_laser(
                        optical_height=position[2], post_width=dim(1, "in")
                    ),
                ),
                position=position,
                rotation=(0, 0, 45 if side == 1 else 135),
            )

            beam = redstone.add(
                BeamPath(label="Beam", final_distance=dim(45, "in")),
                position=position,
                rotation=(0, 0, 45 if side == 1 else 135),
            )

            mirror = beam.add(
                Component(
                    label="Mirror",
                    definition=optics.circular_mirror(
                        diameter=dim(0.5, "in"),
                        mount_definition=thorlabs.mirror_mount_k05s1(),
                    ),
                ),
                beam_index=0b1,
                **mirror_args,
            )

            post_height = position[2] - thorlabs.mirror_mount_k05s1.mount_position[2]
            mirror.add(
                Component(
                    label="Post",
                    definition=simple_post(height=post_height, width=dim(1, "in")),
                ),
                position=thorlabs.mirror_mount_k05s1.mount_position,
                rotation=(0, 0, 0 if side == 1 else 180),
            )

            if side == -1:
                redirect_angle = 180 if dir == 0 else 90
            else:
                redirect_angle = 0 if dir == 0 else 90
            beam.add(
                Component(
                    label="Redirect",
                    definition=optics.rectangular_mirror(
                        width=dim(5, "mm"), height=dim(5, "mm")
                    ),
                ),
                beam_index=0b1,
                distance=i * (dim(1, "in") + dim(3, "mm")) + dim(0.5, "in"),
                rotation=(0, 0, redirect_angle),
            )

if __name__ == "__main__":
    redstone.recompute()
