import math

from PyOpticL.beam_path import BeamPath
from PyOpticL.layout import Component
from PyOpticL.library import baseplate, optics, thorlabs
from PyOpticL.types import Dimension as dim
from PyOpticL.types import cardinal_angle, turn_angle
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from components import grid_optics_mount, km05t_laser, simple_post

redstone = Component(
    label="Baseplate",
    definition=baseplate(
        dimensions=(dim(12, "in"), dim(12, "in"), dim(1, "in")),
        optical_height=0,
    ),
)

grid = redstone.add(
    Component(
        label="Grid Optics Mount",
        definition=grid_optics_mount(
            n_grid=6,
            component_definition=km05t_laser(),
            optical_height=abs(thorlabs.kinematic_mount_km05t.mount_position[2]),
        ),
    ),
    position=(0, 0, 0),
    rotation=(0, 0, -135),
)

# for obj in grid.get_object().Children:
#     obj.Proxy.add(
#         BeamPath(label="Beam", waist=dim(1, "mm"), bound_parent=redstone),
#         position=(0, 0, 0),
#         rotation=(0, 0, 0),
#     )

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
    position=(-dim(5, "in"), -dim(5, "in"), 0),
    rotation=(0, 0, -135),
)

grid = redstone.add(
    Component(
        label="Grid Optics Mount",
        definition=grid_optics_mount(
            n_grid=6,
            component_definition=km05t_laser(),
            optical_height=abs(thorlabs.kinematic_mount_km05t.mount_position[2]),
        ),
    ),
    position=(-dim(10, "in"), -dim(5, "in"), 0),
    rotation=(0, 0, -135),
)

# for obj in grid.get_object().Children:
#     obj.Proxy.add(
#         BeamPath(label="Beam", waist=dim(1, "mm"), bound_parent=redstone),
#         position=(0, 0, 0),
#         rotation=(0, 0, 0),
#     )

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
    position=(-dim(15, "in"), -dim(0, "in"), 0),
    rotation=(0, 0, -135),
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
            optical_height=dim(1, "in"),
            grid_spacing_y=dim(1.5, "in") * math.sqrt(2),
        ),
    ),
    position=(-dim(18, "in"), dim(-5, "in"), 0),
    rotation=(0, 0, 0),
)

redstone.add(
    Component(
        label="Grid Optics Mount",
        definition=grid_optics_mount(
            n_grid=6,
            component_definition=optics.beamsplitter_cube_on_surface_adapter(
                side_length=dim(0.5, "in"), optical_height=dim(0.5, "in")
            ),
            optical_height=dim(0.5, "in"),
            grid_spacing_y=dim(1.5, "in") * math.sqrt(2),
        ),
    ),
    position=(-dim(15, "in"), -dim(15, "in"), 0),
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
            optical_height=dim(1, "in"),
            grid_spacing_y=dim(1.5, "in") * math.sqrt(2),
        ),
    ),
    position=(-dim(18, "in"), dim(-15, "in"), 0),
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
    position=(-dim(10, "in"), -dim(25, "in"), 0),
    rotation=(0, 0, -45),
)

grid = redstone.add(
    Component(
        label="Grid Optics Mount",
        definition=grid_optics_mount(
            n_grid=6,
            component_definition=km05t_laser(),
            optical_height=abs(thorlabs.kinematic_mount_km05t.mount_position[2]),
        ),
    ),
    position=(-dim(15, "in"), -dim(30, "in"), 0),
    rotation=(0, 0, 135),
)

# n_lasers = 13
# laser_spacing = dim(1.5, "in")
# height_step = dim(5, "mm")

# x_position = dim(50, "in")
# y_position = dim(5, "in")

# for side in [-1, 1]:
#     for i in range(n_lasers):
#         for dir in [0, 1]:
#             side_offset = -side * (laser_spacing * n_lasers + dim(7, "in"))
#             if dir == 0:
#                 position = [
#                     x_position
#                     + side_offset
#                     + side * (i * laser_spacing + dim(2, "in")),
#                     y_position,
#                     i * height_step + dim(1.5, "in"),
#                 ]
#                 mirror_args = dict(
#                     x_position=x_position
#                     + side_offset
#                     + side * (n_lasers * laser_spacing + dim(5, "in")),
#                     rotation=(0, 0, 180 if side == 1 else 0),
#                 )
#             else:
#                 position = [
#                     x_position + side_offset,
#                     y_position + i * laser_spacing + dim(2, "in"),
#                     i * height_step + dim(1.5, "in"),
#                 ]
#                 mirror_args = dict(
#                     y_position=y_position + n_lasers * laser_spacing + dim(5, "in"),
#                     rotation=(0, 0, -90),
#                 )

#             baseplate.add(
#                 Component(
#                     label="Laser",
#                     definition=km05t_laser(
#                         optical_height=position[2], post_width=dim(1, "in")
#                     ),
#                 ),
#                 position=position,
#                 rotation=(0, 0, 45 if side == 1 else 135),
#             )

#             beam = baseplate.add(
#                 BeamPath(label="Beam", waist=dim(1, "mm")),
#                 position=position,
#                 rotation=(0, 0, 45 if side == 1 else 135),
#             )

#             mirror = beam.add(
#                 Component(
#                     label="Mirror",
#                     definition=optics.circular_mirror(
#                         diameter=dim(0.5, "in"),
#                         mount_definition=thorlabs.mirror_mount_k05s1(),
#                     ),
#                 ),
#                 beam_index=0b1,
#                 **mirror_args,
#             )

#             post_height = position[2] - thorlabs.mirror_mount_k05s1.mount_position[2]
#             mirror.add(
#                 Component(
#                     label="Post",
#                     definition=simple_post(height=post_height, width=dim(1, "in")),
#                 ),
#                 position=thorlabs.mirror_mount_k05s1.mount_position,
#                 rotation=(0, 0, 0 if side == 1 else 180),
#             )

#             beam.add(
#                 Component(
#                     label="Redirect",
#                     definition=optics.rectangular_mirror(
#                         width=dim(5, "mm"), height=dim(5, "mm")
#                     ),
#                 ),
#                 beam_index=0b1,
#                 distance=i * (dim(1, "in") + dim(3, "mm")) + dim(0.5, "in"),
#                 rotation=(0, 0, 0 if dir == 0 else 90),
#             )


redstone.recompute()
redstone.recompute()
redstone.recompute()
redstone.recompute()
