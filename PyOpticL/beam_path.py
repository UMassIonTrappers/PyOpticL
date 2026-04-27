from __future__ import annotations

from math import isclose

import FreeCAD as App
import numpy as np
import Part

from PyOpticL.icons import beam_icon
from PyOpticL.layout import Layout
from PyOpticL.settings import get_enable_beam_transparency
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import collect_children, cylinder_shape, wavelength_to_rgb

JonesComponent = tuple[float, float]  # (real, imag)
JonesState = tuple[JonesComponent, JonesComponent]  # ((Ex_re, Ex_im), (Ey_re, Ey_im))


def _normalize_jones_vector(
    jones_vector: JonesState | np.ndarray,
) -> np.ndarray:
    """Normalize a Jones vector to unit intensity."""

    raw = np.asarray(jones_vector)
    if raw.shape == (2,):
        vector = raw.astype(complex)
    elif raw.shape == (2, 2):
        pairs = raw.astype(float)
        vector = pairs[:, 0] + 1j * pairs[:, 1]
    else:
        raise ValueError(
            "Jones vector must be length-2 complex-like or ((re, im), (re, im))"
        )

    norm = np.linalg.norm(vector)
    if np.isclose(norm, 0, atol=1e-9):
        raise ValueError("Polarization Jones vector magnitude cannot be zero")
    return vector / norm


def _serialize_jones_vector(
    jones_vector: JonesState | np.ndarray,
) -> JonesState:
    """Convert any accepted Jones representation to plain nested float tuples."""

    normalized = _normalize_jones_vector(jones_vector)
    return (
        (float(np.real(normalized[0])), float(np.imag(normalized[0]))),
        (float(np.real(normalized[1])), float(np.imag(normalized[1]))),
    )


def linear_polarization(angle_deg: float = 0) -> JonesState:
    """Create a linear polarization Jones state at `angle_deg` in degrees."""

    angle_rad = np.radians(angle_deg)
    return ((float(np.cos(angle_rad)), 0.0), (float(np.sin(angle_rad)), 0.0))


def circular_polarization(handedness: str = "right") -> JonesState:
    """Create a circular polarization Jones state.

    Args:
        handedness (str): "right" or "left"
    """

    handedness_value = handedness.lower()
    if handedness_value == "right":
        ellipticity = 45.0
    elif handedness_value == "left":
        ellipticity = -45.0
    else:
        raise ValueError("Circular polarization handedness must be 'right' or 'left'")
    return elliptical_polarization(0, ellipticity)


def elliptical_polarization(
    azimuth_deg: float,
    ellipticity_deg: float,
    global_phase_deg: float = 0,
) -> JonesState:
    """Create an elliptical polarization Jones state from ellipse parameters."""

    psi = np.radians(azimuth_deg)
    chi = np.radians(ellipticity_deg)
    phase = np.exp(1j * np.radians(global_phase_deg))

    ex = np.cos(psi) * np.cos(chi) + 1j * np.sin(psi) * np.sin(chi)
    ey = np.sin(psi) * np.cos(chi) - 1j * np.cos(psi) * np.sin(chi)
    return _serialize_jones_vector((phase * ex, phase * ey))


class DeleteObserver:
    def __init__(self, names):
        self.names = names

    def slotRecomputedDocument(self, doc):
        for name in self.names:
            if doc.getObject(name):
                doc.removeObject(name)
        App.removeDocumentObserver(self)


class BeamSegment(Layout):
    """
    Class representing a beam segment

    Note: There are two options for defining the gaussian beam parameters:
        1. Specify waist and waist_position
        2. Specify rayleigh_range and waist_position

    Args:
        index (int): Index of the beam
        direction (tuple): (x, y, z) normalized direction vector
        wavelength (float): Wavelength of the beam in nm
        polarization (JonesState): Jones state ((Ex_re, Ex_im), (Ey_re, Ey_im))
        power (float): Power of the beam in W
        waist_position (float): Position of the beam waist in mm
        waist (float): Beam waist radius in mm
        rayleigh_range (float): Rayleigh range in mm
    """

    object_group = "beam_path"
    object_icon = beam_icon

    def __init__(
        self,
        index: int,
        direction: tuple[float],
        wavelength: float,
        polarization: JonesState,
        power: float,
        waist_position: dim,
        waist: dim = None,
        rayleigh_range: dim = None,
    ):

        super().__init__(
            label=f"Beam {bin(index)}",
        )

        self.index = index
        self.direction = tuple(direction)
        self.wavelength = wavelength
        self.set_polarization_state(polarization)
        self.power = power
        self.waist_position = waist_position
        self.distance = 0  # to be set during path calculation

        if rayleigh_range is not None:
            self.rayleigh_range = rayleigh_range
        elif waist is not None:
            self.rayleigh_range = np.pi * waist**2 / (wavelength * 1e-6)
        else:
            raise ValueError("Either waist or rayleigh_range must be specified")

        # add properties for displaying beam parameters in FreeCAD
        self.make_property("BeamWaist", "App::PropertyLength", visible=True)
        self.make_property("WaistPosition", "App::PropertyLength", visible=True)
        self.make_property("InitialRadius", "App::PropertyLength", visible=True)
        self.make_property("FinalRadius", "App::PropertyLength", visible=True)
        self.make_property("RayleighRange", "App::PropertyLength", visible=True)
        self.make_property("Wavelength", "App::PropertyLength", visible=True)
        self.make_property("PolarizationAngle", "App::PropertyAngle", visible=True)
        self.make_property("Power", "App::PropertyPower", visible=True)
        self.make_property("Distance", "App::PropertyLength", visible=True)

        # additional object links
        self.make_property("ChildObject", "App::PropertyLinkHidden")
        self.make_property("BoundParent", "App::PropertyLinkHidden")

    def set_polarization_state(self, polarization: JonesState):
        """Store Jones polarization state and derived angle readout."""

        if isinstance(polarization, np.ndarray):
            polarization = _serialize_jones_vector(polarization)
        self.polarization_jones = polarization
        ex, ey = _normalize_jones_vector(self.polarization_jones)
        s1 = np.abs(ex) ** 2 - np.abs(ey) ** 2
        s2 = 2 * np.real(ex * np.conjugate(ey))
        self.polarization = float(np.degrees(0.5 * np.arctan2(s2, s1)) % 180)

    def set_parent(self, parent: Layout):
        """
        Set the parent object of this component

        Args:
            parent (Layout): Parent object to set
        """

        super().set_parent(parent)
        obj = self.get_object()
        parent_obj = parent.get_object()
        obj.BoundParent = parent_obj.BoundParent

    def add(self, child: Layout, origin: tuple = (0, 0, 0)):
        """
        Add a child beam segment to this beam

        Args:
            child (Beam_Segment): Child beam segment to add
        """

        super().add(child, position=origin, rotation=(0, 0, 0))

    def get_constraint_position(
        self,
        type: str,
        value: float,
    ) -> np.ndarray[float]:
        """
        Get the position of the beam at a specified distance or coordinate

        Args:
            type (str): Type of constraint ('distance', 'xPosition', 'yPosition', 'zPosition')
            value (float): Value of the constraint in mm

        Returns:
            position (np.ndarray): (x, y, z) coordinates of the beam position
        """

        obj = self.get_object()

        # work in the bound parent's local frame to evaluate constraints
        bound_placement = obj.BoundParent.Placement
        bound_base = np.array(bound_placement.Base)
        bound_rotation = bound_placement.Rotation
        bound_inverse_rotation = bound_rotation.inverted()

        beam_position = np.array(obj.Placement.Base)
        beam_direction = np.array(
            obj.Placement.Rotation.multVec(App.Vector(*self.direction))
        )

        position = np.array(
            bound_inverse_rotation.multVec(App.Vector(*(beam_position - bound_base)))
        )
        direction = np.array(
            bound_inverse_rotation.multVec(App.Vector(*beam_direction))
        )

        # calculate position based on specified constraint
        if type == "distance":
            output = position + value * direction
        if type == "xPosition":
            if isclose(direction[0], 0):
                raise RuntimeError(
                    "Beam is parallel to yz plane, cannot constrain x position"
                )
            t = (value - position[0]) / direction[0]
            output = position + t * direction
        if type == "yPosition":
            if isclose(direction[1], 0):
                raise RuntimeError(
                    "Beam is parallel to xz plane, cannot constrain y position"
                )
            t = (value - position[1]) / direction[1]
            output = position + t * direction
        if type == "zPosition":
            if isclose(direction[2], 0):
                raise RuntimeError(
                    "Beam is parallel to xy plane, cannot constrain z position"
                )
            t = (value - position[2]) / direction[2]
            output = position + t * direction

        # convert constrained point back to global frame
        return np.array(bound_rotation.multVec(App.Vector(*output))) + bound_base

    def get_global_position(self) -> np.ndarray[float]:
        """
        Get the global position of the beam origin

        Returns:
            position (np.ndarray): (x, y, z) coordinates of the beam origin
        """

        obj = self.get_object()
        position = obj.Placement.Base
        return np.array(position)

    def get_global_direction(self) -> np.ndarray[float]:
        """
        Get the global direction of the beam

        Returns:
            direction (np.ndarray): (x, y, z) normalized direction vector
        """

        obj = self.get_object()
        rotation = obj.Placement.Rotation
        global_direction = rotation.multVec(App.Vector(*self.direction))
        return np.array(global_direction)

    def get_relative_position(
        self, global_position: np.ndarray[float]
    ) -> np.ndarray[float]:
        """
        Convert a global position to relative beam coordinates

        Args:
            global_position (np.ndarray): (x, y, z) coordinates in global frame

        Returns:
            position (np.ndarray): (x, y, z) coordinates relative to this beam
        """

        obj = self.get_object()
        placement = obj.Placement
        delta = np.array(global_position) - np.array(placement.Base)
        local_position = placement.Rotation.inverted().multVec(App.Vector(*delta))
        return np.array(local_position)

    def get_relative_direction(
        self, global_direction: np.ndarray[float]
    ) -> np.ndarray[float]:
        """Convert a global direction to relative beam direction

        Args:
            global_direction (np.ndarray): (x, y, z) normalized direction vector in global frame

        Returns:
            direction (np.ndarray): (x, y, z) normalized direction vector relative to this beam
        """

        obj = self.get_object()
        rotation = obj.Placement.Rotation
        relative_direction = rotation.inverted().multVec(App.Vector(*global_direction))
        return np.array(relative_direction)

    def get_q_parameter(self) -> complex:
        """
        Calculate the complex beam parameter

        Returns:
            q_param (complex): Complex beam parameter (mm units)
        """

        return complex(-self.waist_position, self.rayleigh_range)

    def get_beam_radius(self, q_param) -> float:
        """
        Calculate the beam radius at a given complex beam parameter

        Args:
            q_param (complex): Complex beam parameter (mm units)

        Returns:
            w_f (float): Beam radius at the given position in mm
        """

        z_f = q_param.real
        z_R = q_param.imag
        w_0 = np.sqrt(self.wavelength * 1e-6 * z_R / np.pi)  # beam waist
        w_f = w_0 * np.sqrt(1 + (z_f / z_R) ** 2)  # beam radius
        return w_f

    def get_next_beam_point(self, q_param, ddw: float) -> float:
        """
        Calculate the next beam point based on change in slope
        Useful for reducing number of conical sections needed for gaussian beam representation

        Args:
            q_param (complex): Current complex beam parameter
            ddw (float): Minimum change in beam slope

        Returns:
            dz (float): Distance to next beam point in meters
        """

        z_i = q_param.real
        z_R = q_param.imag
        w_0 = np.sqrt(self.wavelength * 1e-6 * z_R / np.pi)  # beam waist

        dw_max = w_0 / z_R - 1e-12  # far-field slope limit
        dw = w_0 * (z_i / z_R) / np.sqrt(z_i**2 + z_R**2)  # current slope
        dw_f = min(max(dw + ddw, -dw_max), dw_max)  # target slope

        if dw_f != 0:  # prevent division by zero if slope is exactly zero
            z_f = z_R / np.sqrt((w_0 / (z_R * dw_f)) ** 2 - 1) * np.sign(dw_f)
        else:
            z_f = 0.0

        return z_f - z_i

    def compute_shape(self):
        """
        Calculate the beam segment properties
        """

        obj = self.get_object()
        if obj.Parent != None and isinstance(obj.Parent.Proxy, BeamSegment):
            self.relative_power = (
                self.power / obj.Parent.Proxy.power
            ) * obj.Parent.Proxy.relative_power
        else:
            self.relative_power = 1.0

        # generate segment shape using conical sections
        shapes = []
        q_param = self.get_q_parameter()  # initial q parameter
        current_position = 0  # track position along beam segments
        while current_position < self.distance:
            # TODO: may want to make ddw a user-defined parameter
            dz = self.get_next_beam_point(q_param, 1e-3)  # get next segment distance
            dz = min(dz, self.distance - current_position)  # clip to remaining distance
            # calculate starting and ending radius for segment
            radius1 = self.get_beam_radius(q_param)
            radius2 = self.get_beam_radius(q_param + dz)
            # create conical section
            # freecad does not support cones with equal radii
            if isclose(radius1, radius2):
                shape = Part.makeCylinder(
                    radius1,
                    dz,
                    App.Vector(*self.direction) * current_position,
                    App.Vector(*self.direction),
                )
            else:
                shape = Part.makeCone(
                    radius1,
                    radius2,
                    dz,
                    App.Vector(*self.direction) * current_position,
                    App.Vector(*self.direction),
                )
            shapes.append(shape)
            # step q_param and update position
            q_param += dz
            current_position += dz
        # add sphere as cap for smoother beam transitions
        beam_radius = self.get_beam_radius(self.get_q_parameter() + self.distance)
        # sphere = Part.makeSphere(
        #     beam_radius,
        #     App.Vector(*self.direction) * self.distance,
        # )
        # shapes.append(sphere)
        # fuse all shapes together
        shape = shapes[0]
        for s in shapes[1:]:
            shape = shape.fuse(s)

        # apply placement and set shape
        shape.Placement = obj.Placement
        obj.Shape = shape
        # color and transparency based on wavelength and power
        obj.ViewObject.ShapeColor = wavelength_to_rgb(self.wavelength)
        if get_enable_beam_transparency():
            obj.ViewObject.Transparency = int(100 * (1 - self.relative_power))

        # get gaussian beam parameters
        q_param = self.get_q_parameter()
        waist = self.get_beam_radius(q_param + self.waist_position)
        initial_radius = self.get_beam_radius(q_param)
        final_radius = self.get_beam_radius(q_param + self.distance)
        # set readout properties
        obj.Wavelength = App.Units.Quantity(f"{self.wavelength} nm")
        obj.PolarizationAngle = App.Units.Quantity(f"{self.polarization} deg")
        obj.Power = App.Units.Quantity(f"{self.power} W")
        obj.Distance = self.distance
        obj.BeamWaist = App.Units.Quantity(f"{waist} mm")
        obj.InitialRadius = App.Units.Quantity(f"{initial_radius} mm")
        obj.FinalRadius = App.Units.Quantity(f"{final_radius} mm")
        obj.WaistPosition = App.Units.Quantity(f"{self.waist_position} mm")
        obj.RayleighRange = App.Units.Quantity(f"{self.rayleigh_range} mm")

        obj.purgeTouched()  # prevent triggering recompute

    def drill(self):
        """
        The drilling the beam applies to other objects
        """
        part = Part.makeSphere(
            dim(1.5, "mm"),
            App.Vector(0, 0, 0),
        )
        part = part.fuse(
            Part.makeCylinder(
                dim(1.5, "mm"),
                self.distance,
                App.Vector(0, 0, 0),
                App.Vector(*self.direction),
            )
        )
        return part

    def recompute(self):
        """
        Recompute the beam segment
        """

        super().compute_placement()
        self.compute_shape()


class BeamPath(Layout):
    """
    Class representing a beam path layout object

    Note: There are two options for defining the gaussian beam parameters:
        1. Specify waist and waist_position
        2. Specify rayleigh_range and waist_position

    Args:
        label (str): Label for the beam path
        wavelength (float): Wavelength of the beam in nm
        polarization (JonesState): Input Jones state
        power (float): Power of the beam in W
        waist_position (float): Position of the beam waist in mm
        waist (float): Beam waist radius in mm
        rayleigh_range (float): Rayleigh range in mm
        bound_parent (Layout): parent whose children this beam path should interact with
        final_distance (float): Propagation distance for beam segments that do not hit another interface
    """

    object_group = "beam_path"
    object_icon = beam_icon

    def __init__(
        self,
        label: str,
        wavelength: float = 635,
        polarization: JonesState = None,
        power: float = 1,
        waist_position: dim = dim(0, "mm"),
        waist: dim = None,
        rayleigh_range: dim = None,
        bound_parent: Layout = None,
        final_distance: dim = dim(50, "mm"),
    ):
        super().__init__(
            label=label,
            recompute_priority=-1,
        )

        obj = self.get_object()

        # bound parent represents the parent whose children this beam path interacts with
        self.make_property("BoundParent", "App::PropertyLinkHidden")
        if bound_parent is not None:
            bound_parent = bound_parent.get_object()
        obj.BoundParent = bound_parent

        # separate lists for beam children and beam segments
        self.make_property("BeamChildren", "App::PropertyLinkListHidden")
        self.make_property("BeamSegments", "App::PropertyLinkListHidden")

        self.waist = waist
        self.wavelength = wavelength
        if polarization is None:
            polarization = linear_polarization(0)
        self.polarization = polarization
        self.power = power
        self.waist_position = waist_position
        if rayleigh_range is not None:
            self.rayleigh_range = rayleigh_range
        elif waist is None:
            waist = dim(1, "mm")

        if waist is not None:
            self.rayleigh_range = np.pi * waist**2 / (wavelength * 1e-6)

        self.final_distance = final_distance

    def set_parent(self, parent: Layout):
        """
        Set the parent object of this component

        Args:
            parent (Layout): Parent object to set
        """

        super().set_parent(parent)
        obj = self.get_object()
        parent_obj = parent.get_object()
        # bound parent defaults to the parent object
        if obj.BoundParent is None:
            obj.BoundParent = parent_obj

    def add(
        self,
        child: Layout,
        beam_index: int,
        rotation: tuple | float,
        distance: dim = None,
        x_position: dim = None,
        y_position: dim = None,
        z_position: dim = None,
        offset: tuple[dim] = (0, 0),
        interface_index: int = 0,
    ) -> Layout:
        """
        Add a child layout to the beam path and assign beam index

        Args:
            child (Layout): Child layout to add
            beam_index (int): Index of the beam this child interacts with
            rotation (tuple | float): (angle_x, angle_y, angle_z) rotation in degrees or single angle for rotation around z-axis
            distance (float): Distance along the beam from the last component
            x_position (float): x-coordinate of the beam position
            y_position (float): y-coordinate of the beam position
            z_position (float): z-coordinate of the beam position
            offset (tuple): (y, z) offset from the center of the interface
            interface_index (int): Index of the interface on the child object to interact with

        Returns:
            child (Layout): The added child layout
        """

        super().add(child, position=(0, 0, 0), rotation=rotation)

        obj = self.get_object()
        obj.BeamChildren += [child.get_object()]

        if (distance != None) + (x_position != None) + (y_position != None) + (
            z_position != None
        ) != 1:
            raise ValueError(
                "Exactly one of distance, x_position, y_position, or z_position must be specified"
            )
        child.beam_index = beam_index
        child.interface_index = interface_index
        child.placed = False

        child_obj = child.get_object()
        child.make_property("ConstraintValue", "App::PropertyLength")
        child.make_property("ConstraintType", "App::PropertyEnumeration")
        child_obj.ConstraintType = ["distance", "xPosition", "yPosition", "zPosition"]
        if distance is not None:
            child_obj.ConstraintType = "distance"
            child_obj.ConstraintValue = distance
        if x_position is not None:
            child_obj.ConstraintType = "xPosition"
            child_obj.ConstraintValue = x_position
        if y_position is not None:
            child_obj.ConstraintType = "yPosition"
            child_obj.ConstraintValue = y_position
        if z_position is not None:
            child_obj.ConstraintType = "zPosition"
            child_obj.ConstraintValue = z_position
        child.make_property("Offset", "App::PropertyVector", editable=True)
        child_obj.Offset = App.Vector(0, offset[0], offset[1])

        return child

    def compute_path(self):
        """
        Calculate the beam path through the layout
        """

        obj = self.get_object()

        # reset rotation so that child placements are correct
        if obj.Parent != None:
            obj.Placement.Rotation = obj.Parent.Placement.Rotation
        else:
            obj.Placement.Rotation = App.Rotation("XYZ", 0, 0, 0)

        # clear previous beam segments
        if len(obj.BeamSegments) > 0:
            to_delete = [beam.Name for beam in obj.BeamSegments]
            App.addDocumentObserver(DeleteObserver(to_delete))
            obj.BeamSegments = []

        # add initial input beam
        direction = obj.BasePlacement.Rotation.multVec(App.Vector(1, 0, 0))
        input_beam = BeamSegment(
            index=1,
            direction=direction,
            wavelength=self.wavelength,
            polarization=self.polarization,
            power=self.power,
            waist_position=self.waist_position,
            rayleigh_range=self.rayleigh_range,
        )
        super().add(input_beam, position=(0, 0, 0), rotation=(0, 0, 0))
        obj.BeamSegments += [input_beam.get_object()]

        # check for loose ends and start simulation from there
        for beam in obj.BeamSegments:
            beam.Proxy.compute_placement()
            if len(beam.Children) == 0:
                self.step(beam.Proxy)

        obj.purgeTouched()  # prevent triggering recompute

    def recompute(self):
        """
        Recompute the beam path layout
        """

        super().compute_placement()
        self.compute_path()

    def get_next_global(self, input_beam: BeamSegment) -> tuple:
        """
        Get the next global object the beam will interact with

        Args:
            input_beam (Beam_Segment): Input beam segment to process

        Returns:
            next_object (App.DocumentObject): Next global object to interact with
            next_interface (Interface): Interface on the next object
            min_distance (float): Distance to the next interaction
        """

        obj = self.get_object()
        input_beam_obj = input_beam.get_object()

        next_object = None
        next_interface = None

        # gather all children of bound parent
        all_children = []
        collect_children(obj.BoundParent, all_children)

        # find closest global object
        min_distance = np.inf
        for child in all_children:
            proxy = child.Proxy
            # skip beam segments, unplaced beam children, and objects without interfaces
            if not hasattr(proxy, "interfaces") or (
                child in obj.BeamChildren and not proxy.placed
            ):
                continue
            # check all interfaces of the object
            for interface in proxy.interfaces():
                intercept = interface.get_intercept(input_beam)
                if intercept is not None:
                    distance = np.linalg.norm(intercept - input_beam_obj.Placement.Base)
                    # find closest intercept
                    if distance < min_distance:
                        min_distance = distance
                        next_object = child
                        next_interface = interface

        return next_object, next_interface, min_distance

    def get_next_child(self, input_beam: BeamSegment) -> tuple:
        """
        Get the next beam child object for placement

        Args:
            input_beam (Beam_Segment): Input beam segment to process

        Returns:
            next_object (App.DocumentObject): Next beam child object to interact with
            next_interface (Interface): Interface on the next object
            min_distance (float): Distance to the next interaction
        """

        obj = self.get_object()
        input_beam_obj = input_beam.get_object()

        next_object = None
        next_interface = None
        next_distance = np.inf

        # get next beam child for placement
        for child in obj.BeamChildren:
            proxy = child.Proxy
            if not proxy.placed and proxy.beam_index == input_beam.index:
                next_object = child
                break

        # get info for next beam child
        if next_object != None:
            next_interface = self.get_child_interface(next_object)

            # get position from provided constraint
            try:
                next_position = input_beam.get_constraint_position(
                    next_object.ConstraintType, next_object.ConstraintValue.Value
                )
            except RuntimeError as e:
                raise RuntimeError(
                    f"Error handling constraints for beam child {next_object.Label}: {str(e)}"
                )

            # get distance and interface for interaction
            next_distance = np.linalg.norm(
                next_position - input_beam_obj.Placement.Base
            )

        return next_object, next_interface, next_distance

    def get_child_interface(self, child_object: App.DocumentObject) -> Interface:
        """
        Get the selected interface on a child object

        Args:
            child_object (App.DocumentObject): Child object to check

        Returns:
            interface (Interface): Interface of the child object
        """
        child = child_object.Proxy
        # gather all interfaces associated with the object
        object_children = [child_object]
        collect_children(child_object, object_children)
        interfaces = []
        for obj in object_children:
            proxy = obj.Proxy
            if hasattr(proxy, "interfaces"):
                interfaces.extend(proxy.interfaces())

        if len(interfaces) == 0:
            raise RuntimeError(
                f"Child object {child_object.Label} does not have any interfaces"
            )
        # get specified interface
        return interfaces[child.interface_index]

    def handle_conflicts(self, last_beam: BeamSegment, placed_obj: App.DocumentObject):
        """
        Handle conflicts between placed object and previously computed beams

        Args:
            last_beam (Beam_Segment): Last beam segment placed
            placed_obj (App.DocumentObject): Object that was just placed
        """
        obj = self.get_object()

        # gather all previously placed beam segments
        bound_children = []
        collect_children(obj.BoundParent, bound_children)
        beam_paths = []
        for child in bound_children:
            if isinstance(child.Proxy, BeamPath):
                beam_paths.append(child)

        interface = self.get_child_interface(placed_obj)

        # check for conflicts
        deleted_objs = []
        for beam_path in beam_paths:
            proxy = beam_path.Proxy
            for beam_obj in beam_path.BeamSegments:
                if beam_obj == last_beam.get_object() or beam_obj in deleted_objs:
                    continue
                beam = beam_obj.Proxy
                if (
                    interface.get_intercept(beam) is not None
                    and beam_obj not in deleted_objs
                ):
                    beam_children = []
                    collect_children(beam_obj, beam_children)
                    # remove all children and recompute beam
                    for child in beam_children:
                        beam_path.BeamSegments.remove(child)
                        deleted_objs.append(child)
                        obj.Document.removeObject(child.Name)
                    proxy.step(beam)
                    beam_path.purgeTouched()

    def step(self, input_beam: BeamSegment):
        """
        Perform a single calculation step for the beam path

        Args:
            input_beam (Beam_Segment): Input beam segment to process
        """

        obj = self.get_object()
        beam_obj = input_beam.get_object()

        # get next global object
        next_global = self.get_next_global(input_beam)
        # get next beam child object
        next_child = self.get_next_child(input_beam)

        global_distance, child_distance = next_global[2], next_child[2]

        if global_distance == np.inf and child_distance == np.inf:
            # no more interactions, clip beam to bound parent

            input_beam.distance = self.final_distance
            input_beam.recompute()
            return

        if global_distance < child_distance:
            next_object, next_interface, next_distance = next_global
        else:
            next_object, next_interface, next_distance = next_child

            # get object placement
            intercept = input_beam.get_constraint_position(
                type="distance", value=next_distance
            )
            next_object.Proxy.compute_placement()  # update placement
            object_rotation = next_object.Placement.Rotation
            offset = np.array(object_rotation.multVec(next_object.Offset))
            interface_offset = next_interface.get_position_offset()
            object_position_global = intercept - interface_offset + offset

            # child base placement is stored in the beam path local frame
            beam_path_rotation = obj.Placement.Rotation
            delta = object_position_global - np.array(obj.Placement.Base)
            object_position = np.array(
                beam_path_rotation.inverted().multVec(App.Vector(*delta))
            )
            # apply placement
            next_object.BasePlacement.Base = App.Vector(*object_position)
            next_object.Proxy.placed = True
            next_object.Proxy.recompute()
            # check for conflicts with previously placed beams
            self.handle_conflicts(input_beam, next_object)

        # get output beams from interaction
        input_beam.distance = next_distance
        output_beams = next_interface.get_output_beams(input_beam)
        beam_obj.ChildObject = next_object
        input_beam.recompute()
        for beam in output_beams:
            new_beam_obj = beam.get_object()
            obj.BeamSegments += [new_beam_obj]
            beam.compute_placement()
            self.step(beam)


class Interface:
    """
    Base class for optical interface elements

    Args:
        position (tuple): (x, y, z) coordinates (relative to parent)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees (relative to parent)
        diameter (float): Diameter for circular interface
        width (float): Width for rectangular interface
        height (float): Height for rectangular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
        single_sided (bool): Whether the interface only interacts with beams from one side
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        diameter: dim = None,
        width: dim = None,
        height: dim = None,
        max_angle: float = 90,
        single_sided: bool = False,
    ):
        self.position = np.array(position)

        # calculate normal vector from rotation
        rotation_obj = App.Rotation("XYZ", *rotation)
        self.normal = np.array(rotation_obj.multVec(App.Vector(1, 0, 0)))
        self.transverse = np.array(rotation_obj.multVec(App.Vector(0, 1, 0)))

        self.abcd_matrix = [1, 0, 0, 1]  # identity matrix by default

        # define bound type
        if diameter != None:
            self.shape = "circular"
            self.diameter = diameter
        elif width != None and height != None:
            self.shape = "rectangular"
            self.width = width
            self.height = height
        else:
            raise ValueError("Either radius or width and height must be specified")

        self.max_angle = max_angle
        self.single_sided = single_sided
        self.parent = None  # to be set when initialized in parent object

    def get_position_offset(self) -> np.ndarray[float]:
        """
        Get the position offset of the interface relative to parent
        Returns:
            offset (np.ndarray): (x, y, z) coordinates of the interface relative to parent
        """
        parent_obj = self.parent.get_object()
        rotation = parent_obj.Placement.Rotation
        local_position = rotation.multVec(App.Vector(*self.position))
        return np.array(local_position)

    def get_global_position(self) -> np.ndarray[float]:
        """
        Get the global position of the interface

        Returns:
            position (np.ndarray): (x, y, z) coordinates of the interface
        """

        parent_obj = self.parent.get_object()
        position = parent_obj.Placement.Base
        local_position = self.get_position_offset()
        global_position = np.array(position) + local_position
        return global_position

    def get_global_normal(self) -> np.ndarray[float]:
        """
        Get the global normal vector of the interface

        Returns:
            normal (np.ndarray): (x, y, z) normalized normal vector
        """

        parent_obj = self.parent.get_object()
        rotation = parent_obj.Placement.Rotation
        global_normal = np.array(rotation.multVec(App.Vector(*self.normal)))
        return global_normal

    def get_global_transverse(self) -> np.ndarray[float]:
        """
        Get a horizontal transverse vector of the interface

        Returns:
            normal (np.ndarray): (x, y, z) normalized transverse vector
        """

        parent_obj = self.parent.get_object()
        rotation = parent_obj.Placement.Rotation
        global_transverse = np.array(rotation.multVec(App.Vector(*self.transverse)))
        return global_transverse

    def apply_abcd(self, incident_beam: BeamSegment) -> tuple[float, float]:
        """
        Apply the ABCD matrix of the interface to an incident beam
        Note: this also accounts for the distance traveled to the interface

        Args:
            incident_beam (Beam_Segment): Incident beam segment

        Returns:
            new_waist_position (float): New waist position relative to interface
            new_rayleigh_range (float): New Rayleigh range of beam
        """

        waist_position = incident_beam.waist_position - incident_beam.distance
        q_param = complex(-waist_position, incident_beam.rayleigh_range)
        A, B, C, D = self.abcd_matrix
        q_out = (A * q_param + B) / (C * q_param + D)
        return -q_out.real, q_out.imag

    def get_intercept(self, incident_beam: BeamSegment) -> np.ndarray[float] | None:
        """
        Get the intercept point of a beam with the interface plane

        Args:
            beam (Beam): Beam object

        Returns:
            intercept (np.ndarray): (x, y, z) coordinates of intercept point (None if no intercept)
        """

        global_position = self.get_global_position()
        global_normal = self.get_global_normal()
        beam_position = incident_beam.get_global_position()
        beam_direction = incident_beam.get_global_direction()

        # check if beam is within max angle
        incident_angle = abs(
            np.arccos(np.clip(np.dot(global_normal, -beam_direction), -1, 1))
        )
        if not self.single_sided and incident_angle > np.pi / 2:
            incident_angle -= np.pi
        if incident_angle > np.deg2rad(self.max_angle):
            return None

        denom = np.dot(global_normal, beam_direction)
        # check if beam is parallel to interface
        if np.abs(denom) < 1e-6:
            return None

        distance = np.dot(global_normal, global_position - beam_position) / denom
        # check if intercept is behind beam origin
        if distance < 0:
            return None
        # check if intercept is too close to origin
        if -1e-6 < distance < 1e-6:
            return None
        # check if intercept is within beam distance (if defined)
        beam_obj = incident_beam.get_object()
        if beam_obj.ChildObject != None and distance > incident_beam.distance:
            return None

        intercept = beam_position + distance * beam_direction

        # Check if intercept is within the interface bounds
        offset_vec = intercept - global_position
        if self.shape == "circular":
            if np.linalg.norm(offset_vec) > self.diameter / 2:
                return None
        elif self.shape == "rectangular":
            if (
                abs(offset_vec[0]) > self.width / 2
                or abs(offset_vec[1]) > self.height / 2
            ):
                return None

        return intercept

    def get_output_beams(self, incident_beam: BeamSegment) -> list[BeamSegment]:
        """
        Get the output beams from an incident beam interacting with the interface
        By default, the beam is transmitted with ABCD transformation and no change in polarization or power

        Args:
            incident_beam (Beam_Segment): Incident beam segment

        Returns:
            output_beams (list): List containing a single transmitted beam segment
        """

        intercept = self.get_intercept(incident_beam)
        local_origin = incident_beam.get_relative_position(intercept)
        waist_position, rayleigh_range = self.apply_abcd(incident_beam)

        output_beam = BeamSegment(
            index=incident_beam.index,
            direction=incident_beam.direction,
            wavelength=incident_beam.wavelength,
            polarization=incident_beam.polarization_jones,
            power=incident_beam.power,
            waist_position=waist_position,
            rayleigh_range=rayleigh_range,
        )
        incident_beam.add(output_beam, origin=local_origin)
        return [output_beam]


class Stop(Interface):
    """
    Class representing a beam termination (ie beam dump, fiber input, pinholes, or any other element that fully absorbs the beam)
    Any beam that intersects with this interface is terminated (no output beams)
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        pinhole_diameter: dim = None,
        diameter: dim = None,
        width: dim = None,
        height: dim = None,
        max_angle: float = 90,
        single_sided: bool = False,
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            diameter=diameter,
            width=width,
            height=height,
            max_angle=max_angle,
            single_sided=single_sided,
        )
        self.pinhole_diameter = pinhole_diameter

    def get_output_beams(self, incident_beam: BeamSegment) -> list[BeamSegment]:
        """
        Get the output beams from an incident beam interacting with the stop interface
        For a stop, there are no output beams unless a pinhole diameter is specified, in which case the beam is clipped to the pinhole size

        Args:
            incident_beam (Beam_Segment): Incident beam segment

        Returns:
            output_beams (list): Empty list (no output beams)
        """

        if self.pinhole_diameter is not None:

            intercept = self.get_intercept(incident_beam)
            radial_vector = intercept - self.get_global_position()
            radius = np.linalg.norm(radial_vector)  # distance from center in y-z plane
            if radius < self.pinhole_diameter / 2:
                return super().get_output_beams(incident_beam)

        return []


class Reflection(Interface):
    """
    Base class for reflection interfaces
    Supports mirrors, samplers, polarizing beamsplitters, and dichroic mirrors
    To use type other than basic mirror, use the appropriate ref_* parameter.

    Args:
        position (tuple): (x, y, z) coordinates
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        ref_ratio (float): Ratio of reflected to transmitted power
        ref_polarization (float): Polarization axis angle of reflected light in degrees
        ref_wavelengths (list): List of tuples specifying (min, max) wavelength ranges
                                for reflection in nm. Use None to indicate an open range
        diameter (float): Diameter for circular interface
        width (float): x-distance for rectangular interface
        height (float): y-distance for rectangular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
        single_sided (bool): Whether the interface only interacts with beams from one side
        refractive_index_ratio (float): ratio of refractive index before interface to refractive index after interface
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        ref_ratio: float = None,
        ref_polarization: float = None,
        ref_wavelengths: list = None,
        diameter: dim = None,
        width: dim = None,
        height: dim = None,
        max_angle: float = 90,
        single_sided: bool = False,
        refractive_index_ratio: float = 1,
    ):

        super().__init__(
            position=position,
            rotation=rotation,
            diameter=diameter,
            width=width,
            height=height,
            max_angle=max_angle,
            single_sided=single_sided,
        )

        if (ref_ratio != None and ref_ratio != 1) + (ref_polarization != None) + (
            ref_wavelengths != None
        ) > 1:
            raise ValueError(
                "Only one of ref_ratio, ref_polarization, ref_wavelengths can be specified"
            )

        # define type of reflection interface
        if ref_ratio != None and ref_ratio != 1:
            self.type = "sampler"
            self.ref_ratio = ref_ratio
        elif ref_polarization != None:
            self.type = "polarizing"
            self.ref_polarization = ref_polarization
        elif ref_wavelengths != None:
            self.type = "dichroic"
            self.ref_wavelengths = ref_wavelengths
        else:
            self.type = "mirror"

        self.refractive_index_ratio = refractive_index_ratio

    def get_output_beams(self, incident_beam: BeamSegment) -> list[BeamSegment]:
        """
        Get the output beams from an incident beam interacting with the interface

        Args:
            incident_beam (Beam): Incident beam object

        Returns:
            output_beams (list): List of output Beam objects
        """

        global_normal = self.get_global_normal()
        beam_direction = incident_beam.get_global_direction()
        intercept = self.get_intercept(incident_beam)

        if intercept is None:
            return []

        incident_jones = _normalize_jones_vector(incident_beam.polarization_jones)

        # calculate ratio of transmitted to reflected power for different interface types
        if self.type == "mirror":
            transmit_ratio = 0
            transmit_jones = incident_jones
            reflect_jones = incident_jones
        if self.type == "sampler":
            transmit_ratio = 1 - self.ref_ratio
            transmit_jones = incident_jones
            reflect_jones = incident_jones
        if self.type == "polarizing":
            reflect_axis = _normalize_jones_vector(
                linear_polarization(self.ref_polarization)
            )
            transmit_axis = _normalize_jones_vector(
                linear_polarization(self.ref_polarization + 90)
            )

            reflect_component = np.vdot(reflect_axis, incident_jones) * reflect_axis
            transmit_component = np.vdot(transmit_axis, incident_jones) * transmit_axis

            reflect_ratio = float(
                np.real(np.vdot(reflect_component, reflect_component))
            )
            transmit_ratio = float(
                np.real(np.vdot(transmit_component, transmit_component))
            )
            total_ratio = reflect_ratio + transmit_ratio
            if total_ratio > 1e-9:
                reflect_ratio /= total_ratio
                transmit_ratio /= total_ratio

            if reflect_ratio > 1e-9:
                reflect_jones = _normalize_jones_vector(reflect_component)
            else:
                reflect_jones = reflect_axis
            if transmit_ratio > 1e-9:
                transmit_jones = _normalize_jones_vector(transmit_component)
            else:
                transmit_jones = transmit_axis
        if self.type == "dichroic":
            transmit_ratio = 1
            transmit_jones = incident_jones
            reflect_jones = incident_jones
            # check if wavelength within the reflection ranges
            for lmin, lmax in self.ref_wavelengths:
                if lmin == None:
                    lmin = -np.inf
                if lmax == None:
                    lmax = np.inf
                if lmin <= incident_beam.wavelength <= lmax:
                    transmit_ratio = 0
                    break
        reflect_ratio = 1 - transmit_ratio

        local_origin = incident_beam.get_relative_position(intercept)
        waist_position, rayleigh_range = self.apply_abcd(incident_beam)

        output_beams = []

        # generate transmitted beam
        if not np.isclose(transmit_ratio, 0):
            if reflect_ratio > 0:
                index = incident_beam.index << 1  # handle beam splitting
            else:
                index = incident_beam.index

            # adjust for beam hitting the backside of interface
            incident_angle = np.arccos(
                np.clip(np.dot(global_normal, -beam_direction), -1, 1)
            )
            if incident_angle > np.pi / 2:
                global_normal = -global_normal
                refractive_index_ratio = 1 / self.refractive_index_ratio
            else:
                refractive_index_ratio = self.refractive_index_ratio

            # calculate refraction
            refraction_angle = 1 - refractive_index_ratio**2 * (
                1 - np.dot(global_normal, beam_direction) ** 2
            )
            if refraction_angle < 0:
                # TODO: handle total internal reflection
                print(
                    "Warning: Total internal reflection occurred, but not implemented. Expect inaccurate results."
                )
            else:
                direction = (
                    refractive_index_ratio * beam_direction
                    - global_normal * np.sqrt(refraction_angle)
                    - refractive_index_ratio
                    * global_normal
                    * np.dot(global_normal, beam_direction)
                )
                local_direction = incident_beam.get_relative_direction(direction)
                transmitted_beam = BeamSegment(
                    index=index,
                    direction=local_direction,
                    wavelength=incident_beam.wavelength,
                    polarization=transmit_jones,
                    power=incident_beam.power * transmit_ratio,
                    waist_position=waist_position,
                    rayleigh_range=rayleigh_range,
                )
                incident_beam.add(transmitted_beam, origin=local_origin)
                output_beams.append(transmitted_beam)

        # generate reflected beam
        if not np.isclose(reflect_ratio, 0):
            if transmit_ratio > 0:
                index = (incident_beam.index << 1) + 1  # handle beam splitting
            else:
                index = incident_beam.index

            # calculate reflected direction
            direction = (
                beam_direction
                - 2 * np.dot(beam_direction, global_normal) * global_normal
            )
            local_direction = incident_beam.get_relative_direction(direction)
            reflect_beam = BeamSegment(
                index=index,
                direction=local_direction,
                wavelength=incident_beam.wavelength,
                polarization=reflect_jones,
                power=incident_beam.power * reflect_ratio,
                waist_position=waist_position,
                rayleigh_range=rayleigh_range,
            )
            incident_beam.add(reflect_beam, origin=local_origin)
            output_beams.append(reflect_beam)

        return output_beams


class Lens(Interface):
    """
    Base class for lens interface
    Supports spherical lenses using thin lens approximation

    Args:
        position (tuple): (x, y, z) coordinates
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        focal_length (float): Focal length of the lens
        diameter (float): Diameter for circular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        focal_length: dim,
        diameter: dim = None,
        max_angle: float = 90,
    ):

        super().__init__(
            position=position,
            rotation=rotation,
            diameter=diameter,
            max_angle=max_angle,
            single_sided=False,
        )

        self.focal_length = focal_length

        self.abcd_matrix = [1, 0, -1 / focal_length, 1]

    def get_output_beams(self, incident_beam: BeamSegment) -> list[BeamSegment]:
        """
        Get the output beams from an incident beam interacting with the interface

        Args:
            incident_beam (Beam): Incident beam object

        Returns:
            output_beams (list): List of output Beam objects
        """

        global_normal = self.get_global_normal()
        beam_direction = incident_beam.get_global_direction()
        intercept = self.get_intercept(incident_beam)

        if intercept is None:
            return []

        local_origin = incident_beam.get_relative_position(intercept)
        waist_position, rayleigh_range = self.apply_abcd(incident_beam)

        # handle off-center interactions
        radial_vector = intercept - self.get_global_position()
        if np.isclose(np.linalg.norm(radial_vector), 0):
            direction = beam_direction  # on-axis beam, no change in direction
        else:
            # calculate new beam direction using thin lens approximation
            normal_component = np.dot(beam_direction, global_normal)
            radial_direction = radial_vector / np.linalg.norm(radial_vector)
            tangent_direction = np.cross(radial_direction, global_normal)
            tangent_component = np.dot(beam_direction, tangent_direction)
            tangent_slope = tangent_component / normal_component
            radial_slope = np.dot(beam_direction, radial_direction) / normal_component
            radial_slope -= (
                np.linalg.norm(radial_vector)
                / self.focal_length
                * np.sign(normal_component)
            )
            # construct new direction vector
            direction = global_normal * normal_component
            direction += tangent_direction * tangent_slope * normal_component
            direction += radial_direction * radial_slope * normal_component
            direction /= np.linalg.norm(direction)

        local_direction = incident_beam.get_relative_direction(direction)

        # generate output beam
        output_beam = BeamSegment(
            index=incident_beam.index,
            direction=local_direction,
            wavelength=incident_beam.wavelength,
            polarization=incident_beam.polarization_jones,
            power=incident_beam.power,
            waist_position=waist_position,
            rayleigh_range=rayleigh_range,
        )
        incident_beam.add(output_beam, origin=local_origin)

        return [output_beam]


class Waveplate(Interface):
    """
    Base class for waveplate interface
    Supports quarter and half waveplates

    Args:
        position (tuple): (x, y, z)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        retardance (float): The phase delay in waves (0.25 quarter-wave, 0.5 half-wave)
        fast_axis_angle (float): The angle of the fast axis in degrees
        diameter (float): Diameter for circular interface
        width (float): x-distance for rectangular interface
        height (float): y-distance for rectangular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        retardance: float,
        fast_axis_angle: float,
        diameter: dim = None,
        width: dim = None,
        height: dim = None,
        max_angle: float = 90,
    ):

        super().__init__(
            position=position,
            rotation=rotation,
            diameter=diameter,
            width=width,
            height=height,
            max_angle=max_angle,
            single_sided=False,
        )
        self.retardance = retardance
        self.fast_axis_angle = fast_axis_angle

    def get_output_beams(self, incident_beam: BeamSegment) -> list[BeamSegment]:
        """
        Get the output beams from an incident beam interacting with the interface

        Args:
            incident_beam (Beam): Incident beam object

        Returns:
            output_beams (list): List of output Beam objects
        """

        global_normal = self.get_global_normal()
        beam_direction = incident_beam.get_global_direction()
        intercept = self.get_intercept(incident_beam)

        if intercept is None:
            return []

        local_origin = incident_beam.get_relative_position(intercept)
        # Apply ideal waveplate Jones transform (retardance is specified in waves).
        theta = np.radians(self.fast_axis_angle)
        delta = 2 * np.pi * self.retardance
        rotation = np.array(
            [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]],
            dtype=complex,
        )
        phase_delay = np.array([[1, 0], [0, np.exp(1j * delta)]], dtype=complex)
        transform = rotation @ phase_delay @ rotation.T
        output_jones = _normalize_jones_vector(
            transform @ _normalize_jones_vector(incident_beam.polarization_jones)
        )

        # generate output beam (no change in direction or other properties)
        output_beam = BeamSegment(
            index=incident_beam.index,
            direction=incident_beam.get_relative_direction(beam_direction),
            wavelength=incident_beam.wavelength,
            polarization=output_jones,
            power=incident_beam.power,
            waist_position=incident_beam.waist_position,
            rayleigh_range=incident_beam.rayleigh_range,
        )
        incident_beam.add(output_beam, origin=local_origin)

        return [output_beam]


class Diffraction(Interface):
    """
    Base class for basic diffraction interfaces
    Only supports single diffraction line
    # TODO multi line support
    # (idea: if 3 lines, have the transmitted beam index be 1000 and diffracted beams be 11, 101, and 1001)

    Args:
        position (tuple): (x, y, z) coordinates
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        diffracted_angle (float): Diffraction angle for the generated order
        diffracted_ratio (float): Relative power in the diffracted order
        radius (float): Radius for circular interface
        width (float): Width for rectangular interface
        height (float): Height for rectangular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        diffracted_angle: float,
        diffracted_ratio: float,
        radius: dim = None,
        width: dim = None,
        height: dim = None,
        max_angle: float = 90,
    ):

        # TODO finish this
        super().__init__(
            position=position,
            rotation=rotation,
            radius=radius,
            width=width,
            height=height,
            max_angle=max_angle,
            single_sided=False,
        )


class AcoustoOptic(Interface):
    """
    Implement acousto-optic diffraction

    Args:
        position (tuple): (x, y, z) coordinates
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        rf_frequencies (list[float]): list of rf tones to apply
        sound_velocity (float): velocity of sound in the AO material in m/s - defaults to longitudinal TeO2
        orders (list[int]): list of orders to generate - defaults to 0th and +1st
        order_powers (list[float]): relative power in each of the above orders
        diameter (float): Diameter for circular interface
        width (float): Width for rectangular interface
        height (float): Height for rectangular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        rf_frequencies: float | list[float],
        sound_velocity: float = 4200,  # TeO2
        orders: list[int] = [0, 1],
        order_powers: list[float] = None,
        diameter: dim = None,
        width: dim = None,
        height: dim = None,
        max_angle: float = 90,
    ):

        super().__init__(
            position=position,
            rotation=rotation,
            diameter=diameter,
            width=width,
            height=height,
            max_angle=max_angle,
            single_sided=False,
        )
        self.sound_velocity = sound_velocity
        self.rf_frequencies = rf_frequencies
        if len(orders) != len(order_powers):
            raise ValueError(
                "The number of specified powers must match the number of orders"
            )
        self.orders = orders
        self.order_powers = order_powers

    def get_output_beams(self, incident_beam: BeamSegment) -> list[BeamSegment]:
        """
        Get the output beams from an incident beam interacting with the interface

        Args:
            incident_beam (Beam): Incident beam object

        Returns:
            output_beams (list): List of output Beam objects
        """
        output_beams = []
        beam_direction = incident_beam.get_global_direction()
        intercept = self.get_intercept(incident_beam)

        if intercept is None:
            return []
        local_origin = incident_beam.get_relative_position(intercept)
        waist_position, rayleigh_range = self.apply_abcd(incident_beam)

        # figure out how many bits will be needed to count the beams
        num_beams = len(self.orders) * len(self.rf_frequencies)
        num_bits = int(np.ceil(np.log2(num_beams)))
        i = 0

        # loop over all generated beams
        for freq in self.rf_frequencies:
            for k, order in enumerate(self.orders):

                photon_k = 2 * np.pi / (incident_beam.wavelength * 1e-9)
                phonon_k = 2 * np.pi * freq / self.sound_velocity

                direction = (
                    beam_direction * photon_k
                    + self.get_global_transverse() * phonon_k * order
                )
                direction /= np.linalg.norm(direction)

                local_direction = incident_beam.get_relative_direction(direction)

                # generate output beam
                # not changing polarization for now (reasonable for longitudinal mode AOMs)
                # powers can be specified for each order

                if self.order_powers is not None:
                    power = self.order_powers[k] * incident_beam.power
                else:
                    power = incident_beam.power

                output_beam = BeamSegment(
                    index=(incident_beam.index << num_bits) + i,
                    direction=local_direction,
                    wavelength=incident_beam.wavelength,
                    polarization=incident_beam.polarization_jones,
                    power=power,
                    waist_position=waist_position,
                    rayleigh_range=rayleigh_range,
                )
                incident_beam.add(output_beam, origin=local_origin)
                output_beams.append(output_beam)
                i += 1

        return output_beams
