from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import box_shape


class km05t_laser:
    """
    A custom laser assembly using the Thorlabs km05t
    """

    object_group = "mounts"
    object_color = (0.7, 0.5, 0.5)

    def __init__(self, optical_height: dim = None, post_width: dim = None):
        self.optical_height = optical_height
        self.post_width = post_width

    def subcomponents(self):
        lens_tube_dx = (
            thorlabs.Lens_Tube_SM05L05.mount_position[0]
            - thorlabs.Kinematic_Mount_KM05T.threading_start[0]
        )
        diode_dx = 5
        lens_dx = 12
        components = [
            Subcomponent(
                component=Component(
                    label="Thorlabs KM05T",
                    definition=thorlabs.Kinematic_Mount_KM05T(),
                ),
                position=(lens_tube_dx + diode_dx, 0, 0),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Lens Tube",
                    definition=thorlabs.Lens_Tube_SM05L05(),
                ),
                position=(diode_dx, 0, 0),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Diode Adapter",
                    definition=thorlabs.Diode_Adapter_S05LM56(),
                ),
                position=(0, 0, 0),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Lens Adapter",
                    definition=thorlabs.Lens_Adapter_S05TM09(),
                ),
                position=(lens_dx, 0, 0),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Lens",
                    definition=thorlabs.Mounted_Lens_C220TMDA(),
                ),
                position=(lens_dx, 0, 0),
                rotation=(0, 0, 0),
            ),
        ]
        if self.optical_height is not None and self.post_width is not None:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Post",
                        definition=simple_post(
                            height=self.optical_height
                            + thorlabs.Mirror_Mount_K05S1.mount_position[2],
                            width=self.post_width,
                        ),
                    ),
                    position=(
                        lens_tube_dx + diode_dx,
                        0,
                        thorlabs.Mirror_Mount_K05S1.mount_position[2],
                    ),
                    rotation=(0, 0, 0),
                )
            )
        return components


class simple_post:
    """
    A simple post for mounting optics
    """

    object_group = "adapters"
    object_color = (0.5, 0.5, 0.5)

    def __init__(self, height: dim, width: dim):
        self.height = height
        self.width = width

    def shape(self):
        part = box_shape(
            dimensions=(self.width, self.width, self.height),
            fillet=dim(5, "mm"),
            center=(0, 0, 1),
        )
        return part


class grid_optics_mount:
    """
    A custom mount for holding optics in a grid pattern
    """

    object_group = "optics"
    object_color = (0.5, 0.5, 0.5)

    def __init__(
        self,
        n_grid: int,
        component_definition: Component,
        optical_height: dim,
        component_rotation: tuple = (0, 0, 0),
        grid_spacing_y: dim = dim(2, "in"),
        grid_spacing_z: dim = dim(2, "in"),
    ):
        self.n_grid = n_grid
        self.component_definition = component_definition
        self.optical_height = optical_height
        self.grid_spacing_y = grid_spacing_y
        self.grid_spacing_z = grid_spacing_z
        self.component_rotation = component_rotation

    def subcomponents(self):
        components = []
        for y in range(self.n_grid):
            for z in range(self.n_grid):
                components.append(
                    Subcomponent(
                        component=Component(
                            label="Optic Mount",
                            definition=self.component_definition,
                        ),
                        position=(
                            0,
                            (y + 0.5) * self.grid_spacing_y
                            - self.n_grid * self.grid_spacing_y / 2,
                            (z + 0.5) * self.grid_spacing_z,
                        ),
                        rotation=self.component_rotation,
                    )
                )
        return components

    def shape(self):
        part = box_shape(
            dimensions=(
                dim(1, "in"),
                self.grid_spacing_y * self.n_grid,
                self.grid_spacing_z * self.n_grid + dim(0.5, "in"),
            ),
            fillet=dim(5, "mm"),
            center=(0, 0, -1),
        )
        for y in range(self.n_grid):
            for z in range(self.n_grid):
                part = part.cut(
                    box_shape(
                        dimensions=(dim(1, "in"), dim(1.5, "in"), dim(1.5, "in")),
                        center=(0, 0, -1),
                        position=(
                            0,
                            (y + 0.5) * self.grid_spacing_y
                            - self.n_grid * self.grid_spacing_y / 2,
                            (z + 0.5) * self.grid_spacing_z - self.optical_height,
                        ),
                    )
                )
        return part
