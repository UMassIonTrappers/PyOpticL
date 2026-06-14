from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import hardware, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import fix_relative_imports

fix_relative_imports()

from ecdl.components import ecdl_box, grating_adapter, mount_plate


class km100pm_ecdl:
    """
    A custom laser assembly using the Thorlabs km100pm
    """

    object_group = "mounts"
    object_color = (0.7, 0.5, 0.5)

    def __init__(
        self,
        littrow_angle: float = 45,
        adapter_offset: tuple[dim, dim] = (dim(0, "mm"), dim(7, "mm")),
        adapter_dimensions: tuple[dim, dim, dim] = (
            dim(20, "mm"),
            dim(45, "mm"),
            dim(26, "mm"),
        ),
        grating_dimensions: tuple[dim, dim, dim] = (
            dim(6, "mm"),
            dim(0.5, "in"),
            dim(0.5, "in"),
        ),
        pzt_dimensions: tuple[dim, dim, dim] = (
            dim(2, "mm"),
            dim(8, "mm"),
            dim(8, "mm"),
        ),
        mirror_dimensions: tuple[dim, dim, dim] = (
            dim(3, "mm"),
            dim(0.5, "in"),
            dim(0.5, "in"),
        ),
        optic_distance: dim = dim(1, "in"),
        slot_length: dim = dim(20, "mm"),
        box_dimensions: tuple[dim, dim, dim] = (
            dim(150, "mm"),
            dim(100, "mm"),
            dim(100, "mm"),
        ),
        box_wall_thickness: dim = dim(0.5, "in"),
    ):
        self.littrow_angle = littrow_angle
        self.adapter_offset = adapter_offset
        self.adapter_dimensions = adapter_dimensions
        self.grating_dimensions = grating_dimensions
        self.pzt_dimensions = pzt_dimensions
        self.mirror_dimensions = mirror_dimensions
        self.optic_distance = optic_distance
        self.slot_length = slot_length
        self.box_dimensions = box_dimensions
        self.box_wall_thickness = box_wall_thickness

    def subcomponents(self):
        km_100pm_bore_depth = 7.874  # depth of bore in mounting holes
        lens_tube_dx = (
            thorlabs.Lens_Tube_SM05L05.mount_position[0]
            - thorlabs.Fixed_Mount_SMR05.threading_start[0]
        )
        side_mount_position = thorlabs.Prism_Mount_KM100PM_NoPlatform.side_bolt_position
        fixed_mount_position = thorlabs.Fixed_Mount_SMR05.mount_position
        diode_dx = 5
        lens_dx = 12
        mount_position = (
            lens_tube_dx + diode_dx - side_mount_position[0],
            -fixed_mount_position[2] - side_mount_position[1] + km_100pm_bore_depth,
            -side_mount_position[2],
        )
        km100pm_mount_position = thorlabs.Prism_Mount_KM100PM_NoPlatform.mount_position
        mount_plate_thickness = dim(0.25, "in")
        mount_plate_position = (
            mount_position[0] + km100pm_mount_position[0],
            mount_position[1] + km100pm_mount_position[1],
            mount_position[2] + km100pm_mount_position[2],
        )
        components = [
            Subcomponent(
                component=Component(
                    label="Thorlabs KM100PM",
                    definition=thorlabs.Prism_Mount_KM100PM_NoPlatform(
                        drill_depth=mount_plate_thickness
                    ),
                ),
                position=mount_position,
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Fixed Mount", definition=thorlabs.Fixed_Mount_SMR05()
                ),
                position=(lens_tube_dx + diode_dx, 0, 0),
                rotation=(90, 0, 0),
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
            Subcomponent(
                component=Component(
                    label="Grating Adapter",
                    definition=grating_adapter(
                        littrow_angle=self.littrow_angle,
                        adapter_offset=self.adapter_offset,
                        adapter_dimensions=self.adapter_dimensions,
                        grating_dimensions=self.grating_dimensions,
                        pzt_dimensions=self.pzt_dimensions,
                        mirror_dimensions=self.mirror_dimensions,
                        optic_distance=self.optic_distance,
                        slot_length=self.slot_length,
                    ),
                ),
                position=(
                    mount_position[0]
                    + self.adapter_dimensions[0] / 2
                    - self.adapter_offset[0],
                    0,
                    -3,
                ),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Bracket Bolt",
                    definition=hardware.Bolt(
                        types=["4_40", "M3"],
                        clear_depth=self.adapter_dimensions[0],
                        drill_depth=dim(5, "mm"),
                    ),
                ),
                position=(
                    mount_position[0] + self.adapter_dimensions[0],
                    mount_position[1],
                    mount_position[2],
                ),
                rotation=(0, 90, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Bracket Bolt",
                    definition=hardware.Bolt(
                        types=["4_40", "M3"],
                        clear_depth=self.adapter_dimensions[0],
                        drill_depth=dim(5, "mm"),
                    ),
                ),
                position=(
                    mount_position[0]
                    + thorlabs.Prism_Mount_KM100PM_NoPlatform.bracket_hole_position[0]
                    + self.adapter_dimensions[0],
                    mount_position[1]
                    + thorlabs.Prism_Mount_KM100PM_NoPlatform.bracket_hole_position[1],
                    mount_position[2]
                    + thorlabs.Prism_Mount_KM100PM_NoPlatform.bracket_hole_position[2],
                ),
                rotation=(0, 90, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Upper Mount Plate",
                    definition=mount_plate(
                        dimensions=(
                            dim(40, "mm"),
                            dim(40, "mm"),
                            mount_plate_thickness,
                        )
                    ),
                ),
                position=mount_plate_position,
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="TEC",
                    definition=thorlabs.TEC_TECH8(),
                ),
                position=(
                    mount_plate_position[0],
                    mount_plate_position[1],
                    mount_plate_position[2] - mount_plate_thickness,
                ),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Lower Mount Plate",
                    definition=mount_plate(
                        dimensions=(
                            dim(70, "mm"),
                            dim(70, "mm"),
                            mount_plate_thickness,
                        )
                    ),
                ),
                position=(
                    mount_plate_position[0],
                    mount_plate_position[1],
                    mount_plate_position[2]
                    - mount_plate_thickness
                    - thorlabs.TEC_TECH8().thickness,
                ),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Box",
                    definition=ecdl_box(
                        dimensions=self.box_dimensions,
                        wall_thickness=self.box_wall_thickness,
                    ),
                ),
                position=(
                    mount_plate_position[0],
                    mount_plate_position[1],
                    mount_plate_position[2]
                    - 2 * mount_plate_thickness
                    - thorlabs.TEC_TECH8().thickness,
                ),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Brewster Window",
                    definition=thorlabs.Brewster_Window_Mount_BW20M(),
                ),
                position=(
                    mount_plate_position[0]
                    + self.box_dimensions[0] / 2
                    - thorlabs.Brewster_Window_Mount_BW20M.mount_position[0],
                    self.optic_distance,
                    0,
                ),
                rotation=(0, 0, 0),
            ),
        ]
        for x, y in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mounting Bolt",
                        definition=hardware.Bolt(
                            types=["8_32", "M4"],
                            clear_depth=dim(10, "mm"),
                            drill_depth=dim(5, "mm"),
                        ),
                    ),
                    position=(
                        mount_plate_position[0] + x * dim(1, "in"),
                        mount_plate_position[1] + y * dim(1, "in"),
                        mount_plate_position[2]
                        - mount_plate_thickness
                        - thorlabs.TEC_TECH8().thickness,
                    ),
                    rotation=(0, 0, 0),
                )
            )
        return components


def ecdl():
    return Component(label="ECDL", definition=km100pm_ecdl())


if __name__ == "__main__":
    component = ecdl()
    component.recompute()
