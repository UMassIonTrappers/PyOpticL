from PyOpticL.beam_path import Stop
from PyOpticL.icons import thorlabs_icon
from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library import adapters, hardware
from PyOpticL.settings import get_measurement_system
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import (
    bounding_box_shape,
    box_shape,
    cylinder_shape,
    import_model,
    translate_shape,
)

####################
### Base Classes ###
####################


class polaris_mount:
    """
    A generic class for Thorlabs Polaris components
    Subclasses should define the mesh, mount_position, bolt_position, and pin_positions attributes

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    def __init__(self, drill_depth: dim = None, bolt_length: dim = None):
        self.drill_depth = drill_depth
        self.bolt_length = bolt_length

    def subcomponents(self):
        components = [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        length=self.bolt_length,
                        clear_depth=self.bolt_position[2] - self.mount_position[2],
                        drill_depth=self.drill_depth,
                        from_top=False,
                    ),
                ),
                position=self.bolt_position,
                rotation=(0, 0, 0),
            )
        ]
        for position in self.pin_positions:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Alignment Pin",
                        definition=hardware.alignment_pin(
                            diameter=dim(1.9, "mm"), length=dim(4, "mm")
                        ),
                    ),
                    position=position,
                    rotation=(0, 0, 0),
                )
            )
        return components


#####################
### Mirror Mounts ###
#####################


class mirror_mount_k05s1(polaris_mount):
    """
    Mirror mount, model K05S1

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("polaris-k05s1")
    part_numbers = ["K05S1"]
    mount_position = (-8.017, 0.000, -12.700)
    bolt_position = (-8.017, 0.000, -7.112)
    pin_positions = [(-8.017, 5.000, -10.795), (-8.017, -5.000, -10.795)]


class mirror_mount_km100:
    """
    Mirror mount, model KM100

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-km100")
    mount_position = (-8.496, -0.000, -25.400)
    bolt_position = (-8.496, -0.000, -21.082)
    part_numbers = ["KM100"] if get_measurement_system() == "imperial" else ["KM100/M"]

    def __init__(self, drill_depth: dim = None, bolt_length: dim = None):
        self.drill_depth = drill_depth
        self.bolt_length = bolt_length

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        length=self.bolt_length,
                        clear_depth=self.bolt_position[2] - self.mount_position[2],
                        drill_depth=self.drill_depth,
                        from_top=False,
                    ),
                ),
                position=self.bolt_position,
                rotation=(0, 0, 0),
            )
        ]

    def drill(self):
        part = bounding_box_shape(
            shape=self.mesh, padding=dim(5, "mm"), fillet=dim(5, "mm")
        )
        return part


class mirror_mount_km05:
    """
    Mirror mount, model KM05

    Args:
        bolt_distance (float): The distance from the head of the bolt to the mount threads
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-km05")
    part_numbers = ["KM05"] if get_measurement_system() == "imperial" else ["KM05/M"]
    mount_position = (-7.289, -0.000, -14.732)

    def __init__(self, bolt_distance: dim = dim(0.5, "in"), bolt_length: dim = None):
        self.bolt_distance = bolt_distance
        self.bolt_length = bolt_length

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        length=self.bolt_length,
                        clear_depth=self.bolt_distance,
                        from_top=False,
                    ),
                ),
                position=(
                    self.mount_position[0],
                    self.mount_position[1],
                    self.mount_position[2] - self.bolt_distance,
                ),
                rotation=(180, 0, 0),
            )
        ]

    def drill(self):
        part = bounding_box_shape(
            shape=self.mesh, padding=dim(5, "mm"), fillet=dim(5, "mm")
        )
        return part


#######################
### Splitter Mounts ###
#######################


class beamsplitter_mount_b05g(polaris_mount):
    """
    Beamsplitter mount, model B05G

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("polaris-b05g")
    part_numbers = ["B05G"]
    mount_position = (-5.000, -0.000, -12.700)
    bolt_position = (-5.000, -0.000, -8.890)
    pin_positions = [(-5.000, 5.000, -12.700), (-5.000, -5.000, -12.700)]


class beamsplitter_mount_b1g(polaris_mount):
    """
    Beamsplitter mount, model B1G

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("polaris-b1g")
    part_numbers = ["B1G"]
    mount_position = (-5.000, -0.000, -19.050)
    bolt_position = (-5.000, -0.000, -15.240)
    pin_positions = [(-5.000, 5.000, -19.050), (-5.000, -5.000, -19.050)]


###################
### Lens Mounts ###
###################


class lens_mount_l05g(polaris_mount):
    """
    Lens mount, model L05G

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("polaris-l05g")
    part_numbers = ["L05G"]
    mount_position = (-8.000, -0.000, -12.536)
    bolt_position = (-8.000, -0.000, -9.839)
    pin_positions = [(-8.000, 5.000, -12.700), (-8.000, -5.000, -12.700)]


###################
### Misc Mounts ###
###################


class fixed_mount_smr05:
    """
    Fixed mount, model SMR05
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-smr05")
    part_numbers = ["SMR05"] if get_measurement_system() == "imperial" else ["SMR05/M"]
    mount_position = (0.093, 0.000, -16.002)
    mount_hole_end = (0.093, 0.000, -9.652)
    threading_start = (3.903, 0.000, 0.000)
    threading_end = (-3.903, 0.000, 0.000)


class kinematic_mount_km05t:
    """
    Kinematic mount, model KM05t

    Args:
        bolt_distance (float): The distance from the head of the bolt to the mount threads
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-km05t")
    part_numbers = ["KM05T"] if get_measurement_system() == "imperial" else ["KM05T/M"]
    mount_position = (-9.067, -0.000, -14.732)
    threading_end = (-3.556, -0.000, -0.000)
    threading_start = (3.556, -0.000, -0.000)

    def __init__(self, bolt_distance: dim = dim(0.5, "in"), bolt_length: dim = None):
        self.bolt_distance = bolt_distance
        self.bolt_length = bolt_length

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        length=self.bolt_length,
                        clear_depth=self.bolt_distance,
                        from_top=False,
                    ),
                ),
                position=(
                    self.mount_position[0],
                    self.mount_position[1],
                    self.mount_position[2] - self.bolt_distance,
                ),
                rotation=(180, 0, 0),
            )
        ]

    def drill(self):
        part = bounding_box_shape(
            shape=self.mesh, padding=dim(5, "mm"), fillet=dim(5, "mm")
        )
        return part


class rotation_mount_rsp05:
    """
    Rotation mount, model RSP05

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
        adapter_parameters (dict): A dictionary of parameters to override the default surface adapter parameters
        rotate_adapter (bool): Whether to rotate the adapter footprint by 90 degrees
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-rsp05")
    part_numbers = ["RSP05"] if get_measurement_system() == "imperial" else ["RSP05/M"]
    mount_position = (-0.635, -0.000, -13.975)
    mount_hole_end = (-0.635, -0.000, -7.521)

    def __init__(
        self,
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
        rotate_adapter: bool = False,
    ):
        self.adapter_parameters = dict(
            height=dim(10, "mm"),
            bolt_spacing=dim(25, "mm"),
            bolt_types=["8_32", "M4"],
            bolt_length=bolt_length,
            drill_depth=drill_depth,
        )
        self.adapter_parameters |= adapter_parameters
        self.rotate_adapter = rotate_adapter

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        clear_depth=self.adapter_parameters["height"],
                        drill_depth=self.mount_hole_end[2] - self.mount_position[2],
                    ),
                ),
                position=(
                    self.mount_position[0],
                    self.mount_position[1],
                    self.mount_position[2] - self.adapter_parameters["height"],
                ),
                rotation=(180, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Surface Adapter",
                    definition=adapters.surface_adapter(**self.adapter_parameters),
                ),
                position=self.mount_position,
                rotation=(0, 0, 90 if self.rotate_adapter else 0),
            ),
        ]

    def drill(self):
        part = bounding_box_shape(
            shape=self.mesh, padding=dim(5, "mm"), fillet=dim(5, "mm")
        )
        return part


class rotation_mount_rsp1:
    """
    Rotation mount, model RSP1

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
        adapter_parameters (dict): A dictionary of parameters to override the default surface adapter parameters
        rotate_adapter (bool): Whether to rotate the adapter footprint by 90 degrees
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-rsp1")
    part_numbers = ["RSP1"] if get_measurement_system() == "imperial" else ["RSP1/M"]
    mount_position = (6.350, -0.000, -27.732)
    mount_hole_end = (7.450, -0.000, -15.853)

    def __init__(
        self,
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
        rotate_adapter: bool = False,
    ):
        self.adapter_parameters = dict(
            height=dim(10, "mm"),
            bolt_spacing=dim(40, "mm"),
            bolt_types=["8_32", "M4"],
            bolt_length=bolt_length,
            drill_depth=drill_depth,
        )
        self.adapter_parameters |= adapter_parameters
        self.rotate_adapter = rotate_adapter

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        clear_depth=self.adapter_parameters["height"],
                        drill_depth=self.mount_hole_end[2] - self.mount_position[2],
                    ),
                ),
                position=(
                    self.mount_position[0],
                    self.mount_position[1],
                    self.mount_position[2] - self.adapter_parameters["height"],
                ),
                rotation=(180, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Surface Adapter",
                    definition=adapters.surface_adapter(**self.adapter_parameters),
                ),
                position=self.mount_position,
                rotation=(0, 0, 90 if self.rotate_adapter else 0),
            ),
        ]

    def drill(self):
        part = bounding_box_shape(
            shape=self.mesh, padding=dim(5, "mm"), fillet=dim(5, "mm")
        )
        return part


class prism_mount_km100pm_noplatform:
    """
    Prism mount, model KM100PM without the platform or bracket
    Origin is at the center of the inner mounting hole

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    drill_groups = ["baseplate"]

    mesh = import_model("thorlabs-km100pm-noplatform")
    part_numbers = (
        ["KM100PM"] if get_measurement_system() == "imperial" else ["KM100PM/M"]
    )
    mount_position = (-13.957, -10.160, -6.731)
    bolt_position = (-13.957, -10.160, -2.413)
    side_bolt_position = (-13.957, 10.922, 18.669)
    bracket_hole_position = (0.000, -22.860, -0.000)

    def __init__(self, drill_depth: dim = None, bolt_length: dim = None):
        self.drill_depth = drill_depth
        self.bolt_length = bolt_length

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        length=self.bolt_length,
                        clear_depth=self.bolt_position[2] - self.mount_position[2],
                        drill_depth=self.drill_depth,
                        from_top=False,
                    ),
                ),
                position=self.bolt_position,
                rotation=(0, 0, 0),
            )
        ]

    def drill(self):
        part = bounding_box_shape(
            self.mesh,
            padding=dim(4, "mm"),
            fillet=dim(4, "mm"),
            pad_z=True,
            max_offset=(dim(-18, "mm"), dim(-38, "mm"), 0),
        )
        part = part.fuse(
            bounding_box_shape(
                self.mesh,
                padding=dim(4, "mm"),
                fillet=dim(4, "mm"),
                min_offset=(dim(-17, "mm"), 0, 0),
            )
        )
        return part


class prism_mount_km100pm_custom:
    """
    A km100pm prism mount with a custom stage

    Args:
        stage_dimensions (tuple): Stage (x, y, z) dimensions
        arm_dimensions (tuple): Arm (x, y, z) dimensions
        slot_length (float): Slot length used for adapter mounting
        adapter_offset (tuple): (x, y) offset applied to the custom adapter
    """

    object_group = "adapters"
    object_color = (0.5, 0.7, 0.5)

    def __init__(
        self,
        stage_dimensions: tuple = (21, 47.5, 6),
        arm_dimensions: tuple = (10, 47.5, 16.92),
        slot_length: dim = dim(0, "mm"),
        adapter_offset: tuple[dim, dim] = (dim(0, "mm"), dim(10, "mm")),
    ):
        self.stage_dimensions = stage_dimensions
        self.arm_dimensions = arm_dimensions
        self.slot_length = slot_length
        self.adapter_offset = adapter_offset

    def subcomponents(self):
        components = [
            Subcomponent(
                component=Component(
                    label="Mount",
                    definition=prism_mount_km100pm_noplatform(),
                ),
                position=(
                    -self.stage_dimensions[0] / 2,
                    -self.adapter_offset[0],
                    -self.adapter_offset[1],
                ),
                rotation=(0, 0, 0),
            )
        ]
        for position in [
            (0, 0, 0),
            prism_mount_km100pm_noplatform.bracket_hole_position,
        ]:
            components.append(
                Subcomponent(
                    component=Component(
                        label="Mounting Bolt",
                        definition=hardware.bolt(
                            types=["4_40", "M3"],
                            clear_depth=self.arm_dimensions[1],
                            drill_depth=dim(5, "mm"),
                            slot_length=self.slot_length,
                        ),
                    ),
                    position=(
                        -self.stage_dimensions[0] / 2
                        + position[0]
                        + self.arm_dimensions[0],
                        -self.adapter_offset[0] + position[1],
                        -self.adapter_offset[1] + position[2],
                    ),
                    rotation=(0, 90, 0),
                ),
            )
        return components

    def shape(self):
        stage = box_shape(
            dimensions=self.stage_dimensions,
            position=(0, 0, 0),
            center=(0, 0, 1),
        )
        arm = box_shape(
            dimensions=self.arm_dimensions,
            position=(-self.stage_dimensions[0] / 2, 0, -self.stage_dimensions[2]),
            center=(-1, 0, 1),
        )
        part = stage.fuse(arm)
        return part

    def drill(self):
        part = bounding_box_shape(
            self.shape(), padding=dim(5, "mm"), fillet=dim(5, "mm")
        )
        return part


class brewster_window_mount_bw20m:
    """
    Brewster window mount, model BW20M
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("thorlabs-bw20m")
    part_numbers = ["BW20M"]
    mount_position = (-26.047, 0.000, -1.073)

    def drill(self):
        part = cylinder_shape(
            diameter=dim(1.25, "in"),
            height=dim(0.5, "in"),
            position=self.mount_position,
            rotation=(0, -90, 0),
        )
        return part


######################
### Mounted Optics ###
######################


class mounted_lens_c220tmda:
    """
    Mounted lens, model C220TMD-A
    """

    object_group = "optics"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("thorlabs-c220tmd-a")
    part_numbers = ["C220TMD-A"]


#############################
### Adapters / Connectors ###
#############################


class diode_adapter_s05lm56:
    """
    Diode adapter, model S05LM56
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("thorlabs-s05lm56")


class lens_tube_sm05l05:
    """
    Lens tube, model SM05L05
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("thorlabs-sm05l05")
    part_numbers = ["SM05L05"]
    mount_position = (-1.143, 0.000, 0.000)


class lens_adapter_s05tm09:
    """
    Lens adapter, model S05TM09
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("thorlabs-s05tm09")
    part_numbers = ["S05TM09"]


###########################
### Sensors / Detectors ###
###########################


class photodetector_pda10a2:
    """
    Photodetector, model PDA10A2

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
        adapter_parameters (dict): A dictionary of parameters to override the default surface adapter parameters
        rotate_adapter (bool): Whether to rotate the adapter footprint by 90 degrees
    """

    object_group = "misc"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-pda10a2")
    part_numbers = ["PDA10A2"]
    mount_position = (-10.544, 0.000, -25.000)
    mount_hole_end = (-10.544, 0.000, -18.142)

    def __init__(
        self,
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
        rotate_adapter: bool = False,
    ):
        self.adapter_parameters = dict(
            height=dim(10, "mm"),
            min_length=dim(20, "mm"),
            bolt_spacing=dim(40, "mm"),
            bolt_types=["8_32", "M4"],
            bolt_length=bolt_length,
            drill_depth=drill_depth,
        )
        self.adapter_parameters |= adapter_parameters
        self.rotate_adapter = rotate_adapter

    def interfaces(self):
        return [
            Stop(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=dim(2, "mm"),
                single_sided=True,
            )
        ]

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        clear_depth=self.adapter_parameters["height"],
                        drill_depth=self.mount_hole_end[2] - self.mount_position[2],
                    ),
                ),
                position=(
                    self.mount_position[0],
                    self.mount_position[1],
                    self.mount_position[2] - self.adapter_parameters["height"],
                ),
                rotation=(180, 0, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Surface Adapter",
                    definition=adapters.surface_adapter(**self.adapter_parameters),
                ),
                position=self.mount_position,
                rotation=(0, 0, 90 if self.rotate_adapter else 0),
            ),
        ]

    def drill(self):
        part = bounding_box_shape(
            shape=self.mesh, padding=dim(5, "mm"), fillet=dim(5, "mm")
        )
        return part


class photodiode_fds010:
    """
    Photodiode, model FDS010
    """

    object_group = "misc"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-fds010")
    part_numbers = ["FDS010"]
    mount_position = (-2.300, -0.007, -0.004)

    def interfaces(self):
        return [
            Stop(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=dim(2, "mm"),
                single_sided=True,
            )
        ]

    def drill(self):
        part = cylinder_shape(
            diameter=dim(8.5, "mm"),
            height=dim(4, "mm"),
            position=self.mount_position,
            rotation=(0, 90, 0),
        )
        return part


#######################
### Misc Components ###
#######################


class iris_ida12:
    """
    Iris, model IDA12 on a slide adapter

    Args:
        pinhole_diameter (float): Diameter of the pinhole opening
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
        adapter_parameters (dict): A dictionary of parameters to override the default slide adapter parameters
        bore_depth (float): Depth of the counterbore for the mounting bolt
    """

    object_group = "misc"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("thorlabs-ida12")
    part_numbers = (
        ["IDA12-P5"] if get_measurement_system() == "imperial" else ["IDA12/M-P5"]
    )
    mount_position = (1.828, -12.827, -0.000)

    def __init__(
        self,
        pinhole_diameter: dim = dim(1, "mm"),
        drill_depth: dim = None,
        bolt_length: dim = None,
        adapter_parameters: dict = dict(),
        bore_depth: dim = dim(3, "mm"),
    ):
        self.drill_depth = drill_depth
        self.bolt_length = bolt_length
        self.pinhole_diameter = pinhole_diameter
        self.adapter_parameters = dict(
            post_thickness=dim(8, "mm"),
        )
        self.adapter_parameters |= adapter_parameters
        self.bore_depth = bore_depth

    def interfaces(self):
        return [
            Stop(
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                diameter=dim(0.5, "in"),
                pinhole_diameter=self.pinhole_diameter,
            )
        ]

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Slide Adapter",
                    definition=adapters.slide_adapter(**self.adapter_parameters),
                ),
                position=self.mount_position,
                rotation=(0, 0, 90),
            ),
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=hardware.bolt(
                        types=["8_32", "M4"],
                        clear_depth=self.adapter_parameters["post_thickness"],
                        drill_depth=dim(5, "mm"),
                        from_top=False,
                    ),
                ),
                position=(
                    self.mount_position[0],
                    self.mount_position[1]
                    - self.adapter_parameters["post_thickness"]
                    + self.bore_depth,
                    0,
                ),
                rotation=(90, 0, 0),
            ),
        ]

    def drill(self):
        part = bounding_box_shape(
            shape=self.mesh,
            padding=dim(5, "mm"),
            fillet=dim(2, "mm"),
            pad_z=True,
            max_offset=(0, dim(-12, "mm"), 0),
            min_offset=(0, dim(-8, "mm"), 0),
        )
        return part


class tec_tech8:
    """
    Thermoelectric cooler, model TECH8
    """

    object_group = "misc"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("thorlabs-tech8")
    part_numbers = ["TECH8"]
    thickness = dim(3.5, "mm")

    object_group = "misc"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)
    mesh = import_model("thorlabs-tech8")
    thickness = dim(3.5, "mm")
