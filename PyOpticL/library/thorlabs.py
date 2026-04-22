from PyOpticL.beam_path import Stop
from PyOpticL.icons import thorlabs_icon
from PyOpticL.layout import Component, Subcomponent
from PyOpticL.library.adapters import surface_adapter
from PyOpticL.library.hardware import alignment_pin, bolt
from PyOpticL.types import Dimension as dim
from PyOpticL.utils import bounding_box_shape, cylinder_shape, import_model

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
                    definition=bolt(
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
                        definition=alignment_pin(
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

    def __init__(self, drill_depth: dim = None, bolt_length: dim = None):
        self.drill_depth = drill_depth
        self.bolt_length = bolt_length

    def subcomponents(self):
        return [
            Subcomponent(
                component=Component(
                    label="Mounting Bolt",
                    definition=bolt(
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
    mount_position = (-8.000, -0.000, -12.536)
    bolt_position = (-8.000, -0.000, -9.839)
    pin_positions = [(-8.000, 5.000, -12.700), (-8.000, -5.000, -12.700)]


###################
### Misc Mounts ###
###################


class rotation_mount_rsp05:
    """
    Rotation mount, model RSP05

    Args:
        drill_depth (float): The depth of the mounting hole
        bolt_length (float): The length of the mounting bolt (defaults to minimum required length)
        adapter_parameters (dict): A dictionary of parameters to override the default surface adapter parameters
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-rsp05")
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
                    definition=bolt(
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
                    definition=surface_adapter(**self.adapter_parameters),
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
    """

    object_group = "mounts"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-rsp1")
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
                    definition=bolt(
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
                    definition=surface_adapter(**self.adapter_parameters),
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


###########################
### Sensors / Detectors ###
###########################


class photodetector_pda10a2:
    """
    Photodetector, model PDA10A2
    """

    object_group = "misc"
    object_icon = thorlabs_icon
    object_color = (0.25, 0.25, 0.25)

    mesh = import_model("thorlabs-pda10a2")
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
                    definition=bolt(
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
                    definition=surface_adapter(**self.adapter_parameters),
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
