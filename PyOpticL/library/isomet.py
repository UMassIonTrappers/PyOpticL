from PyOpticL.beam_path import AcoustoOptic
from PyOpticL.icons import thorlabs_icon
from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import adapters, hardware, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import bounding_box_shape, cylinder_shape, import_model

############
### AOMs ###
############


class aom_1205c:
    """
    AOM, model 1205C

    Args:
        dimensions (tuple): The (x, y, z) dimensions of the baseplate
    """

    object_group = "misc"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("isomet-1205c")
    mount_positions = [(0, -26.65, -6.980), (0.000, 11.42, -6.98)]

    def interfaces(self):
        return [
            AcoustoOptic(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                sound_velocity=3630,
                rf_frequencies=[100e6],
                order_powers=[0.2, 0.8],
                diameter=dim(2, "mm"),
            ),
        ]


class aom_1205c_on_km100pm:
    """
    AOM, model 1205C

    Args:
        stage_dimensions (tuple): Stage (x, y, z) dimensions for the custom KM100PM mount
        arm_dimensions (tuple): Arm (x, y, z) dimensions for the custom KM100PM mount
        slot_length (float): Slot length used for adapter mounting
        adapter_offset (tuple): (x, y) offset applied to the custom adapter
        aom_offset (tuple): (x, y) offset applied to position the AOM body
    """

    object_group = "misc"
    object_icon = thorlabs_icon

    def __init__(
        self,
        stage_dimensions=(24, 47.5, 6),
        arm_dimensions=(8, 47.5, 10),
        slot_length=dim(0, "mm"),
        adapter_offset=(dim(-12, "mm"), dim(12, "mm")),
        aom_offset: tuple[dim, dim] = (dim(0, "mm"), dim(8, "mm")),
    ):
        self.stage_dimensions = stage_dimensions
        self.arm_dimensions = arm_dimensions
        self.slot_length = slot_length
        self.adapter_offset = adapter_offset
        self.aom_offset = aom_offset

    def subcomponents(self):
        components = [
            Subcomponent(
                component=Component(
                    label="Mount",
                    definition=thorlabs.prism_mount_km100pm_custom(
                        stage_dimensions=self.stage_dimensions,
                        arm_dimensions=self.arm_dimensions,
                        slot_length=self.slot_length,
                        adapter_offset=self.adapter_offset,
                    ),
                ),
                position=(
                    -self.aom_offset[0],
                    -self.aom_offset[1],
                    aom_1205c.mount_positions[0][2],
                ),
                rotation=(0, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="AOM",
                    definition=aom_1205c(),
                ),
                position=(0, 0, 0),
                rotation=(0, 0, 0),
            ),
        ]
        for position in aom_1205c.mount_positions:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mounting Bolt",
                        definition=hardware.bolt(
                            types=["4_40"],
                            clear_depth=self.stage_dimensions[2],
                            drill_depth=dim(5, "mm"),
                        ),
                    ),
                    position=(
                        position[0],
                        position[1],
                        position[2] - self.stage_dimensions[2],
                    ),
                    rotation=(180, 0, 0),
                ),
            )
        return components
