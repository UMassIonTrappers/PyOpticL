from __future__ import annotations

import FreeCAD as App
import numpy as np
import Part

from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout
from PyOpticL.utils import collect_children, wavelength_to_rgb

beam_icon = """
        /* XPM */
        static char *_0ddddfe6a2d42f3d616a62ec3bb0f7c8Jp52mHVQRFtBmFY[] = {
        /* columns rows colors chars-per-pixel */
        "16 16 6 1 ",
        "  c #ED1C24",
        ". c #ED5C5E",
        "X c #ED9092",
        "o c #EDBDBD",
        "O c #EDDFDF",
        "+ c None",
        /* pixels */
        "+++++++++..XooOO",
        "++++++..+..XXooO",
        "++++++++++. XXoo",
        "+++++++.++  .XXo",
        "++++++.++  .  XX",
        "++++++++  .  ..X",
        "+++++++  .  ++..",
        "++++++  .  +++++",
        "+++++  .  ++.+.+",
        "++++  .  ++.++.+",
        "+++  .  ++++++++",
        "++  .  +++++++++",
        "+  .  ++++++++++",
        "  .  +++++++++++",
        " .  ++++++++++++",
        ".  +++++++++++++"
        };
        """


class Beam_Segment(Layout):
    """
    Class representing a beam segment

    Args:
    position (tuple): (x, y, z) coordinates
    direction (tuple): (x, y, z) normalized direction vector
    waist (float): Beam waist
    wavelength (float): Wavelength of the beam
    polarization (string): Polarization angle of the beam in radians
    power (float): Power of the beam
    focal_rate (float): Focal rate of beam (waist / focal length)
    """

    def __init__(
        self,
        index: int,
        direction: tuple[float],
        waist: float,
        wavelength: float,
        polarization: float,
        power: float,
        focal_rate: float,
    ):

        super().__init__(
            label=f"Beam {bin(index)}",
        )

        self.index = index
        self.direction = tuple(direction)
        self.waist = waist
        self.wavelength = wavelength
        self.polarization = polarization
        self.power = power
        self.focal_rate = focal_rate
        self.distance = 0  # to be set during path calculation

        # add properties for displaying beam parameters in FreeCAD
        self.make_property("BeamWaist", "App::PropertyLength", visible=True)
        self.make_property("FocalLength", "App::PropertyDistance", visible=True)
        self.make_property("Wavelength", "App::PropertyLength", visible=True)
        self.make_property("PolarizationAngle", "App::PropertyAngle", visible=True)
        self.make_property("Power", "App::PropertyPower", visible=True)
        self.make_property("Distance", "App::PropertyLength", visible=True)

        self.make_property("ChildObject", "App::PropertyLinkHidden")
        self.make_property("BoundParent", "App::PropertyLinkHidden")

    def set_parent(self, parent):
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
        distance: float = None,
        x_position: float = None,
        y_position: float = None,
        z_position: float = None,
    ) -> np.ndarray[float]:
        """
        Get the position of the beam at a specified distance or coordinate

        Args:
        distance (float): Distance along the beam direction from origin
        x_position (float): x-coordinate of the beam position
        y_position (float): y-coordinate of the beam position
        z_position (float): z-coordinate of the beam position

        Returns:
        position (np.ndarray): (x, y, z) coordinates of the beam position
        """

        obj = self.get_object()

        if (distance != None) + (x_position != None) + (y_position != None) + (
            z_position != None
        ) != 1:
            raise ValueError(
                "Exactly one of distance, x_position, y_position, or z_position must be specified"
            )

        # get placement relative to bound parent
        bound_placement = obj.BoundParent.Placement
        placement = obj.Placement * bound_placement.inverse()

        # get origin and direction from object placement
        position = np.array(placement.Base)
        direction = np.array(placement.Rotation.multVec(App.Vector(*self.direction)))

        # calculate position based on specified constraint
        if distance != None:
            output = position + distance * direction
        if x_position != None:
            t = (x_position - position[0]) / direction[0]
            output = position + t * direction
        if y_position != None:
            t = (y_position - position[1]) / direction[1]
            output = position + t * direction
        if z_position != None:
            t = (z_position - position[2]) / direction[2]
            output = position + t * direction

        # return global output
        return output + np.array(bound_placement.Base)

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
        position = obj.Placement.Base
        return global_position - np.array(position)

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

    def calculate(self):
        """
        Calculate the beam segment properties
        """
        super().calculate()

        obj = self.get_object()
        if obj.Parent != None and isinstance(obj.Parent.Proxy, Beam_Segment):
            self.relative_power = (
                self.power / obj.Parent.Proxy.power
            ) * obj.Parent.Proxy.relative_power
        else:
            self.relative_power = 1.0

        # generate segment shape
        if np.isclose(self.focal_rate, 0):
            focal_length = 0
            shape = Part.makeCylinder(
                self.waist / 2,
                self.distance,
                App.Vector(0, 0, 0),
                App.Vector(*self.direction),
            )
        else:
            # use conical sections to represent focusing/defocusing beams
            start_diameter = self.waist
            end_diameter = self.waist - self.distance * self.focal_rate
            focal_length = self.waist / self.focal_rate
            if self.distance > focal_length > 0:
                distance = focal_length
            else:
                distance = self.distance
            shape = Part.makeCone(
                start_diameter / 2,
                max(end_diameter / 2, 0),
                distance,
                App.Vector(0, 0, 0),
                App.Vector(*self.direction),
            )
            # add cone for remaining distance if focal point is within segment
            if end_diameter < 0 and not np.isclose(end_diameter, 0):
                shape = shape.fuse(
                    Part.makeCone(
                        0,
                        -end_diameter / 2,
                        self.distance - focal_length,
                        distance * App.Vector(*self.direction),
                        App.Vector(*self.direction),
                    )
                )

        # apply placement and set shape
        shape.Placement = obj.Placement
        obj.Shape = shape
        obj.ViewObject.ShapeColor = wavelength_to_rgb(self.wavelength)
        obj.ViewObject.Transparency = int(100 * (1 - self.relative_power))

        # set property values for display
        obj.BeamWaist = self.waist
        obj.Wavelength = App.Units.Quantity(f"{self.wavelength} nm")
        obj.PolarizationAngle = App.Units.Quantity(f"{self.polarization} rad")
        obj.Power = App.Units.Quantity(f"{self.power} W")
        obj.Distance = self.distance
        obj.FocalLength = focal_length


class Beam_Path(Layout):
    """
    Class representing a beam path layout object

    Args:
    label (str): Label for the beam path
    position (tuple): (x, y, z) coordinates
    rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
    bound_parent (Layout): parent whose children this beam path should interact with
    """

    object_type = "Part"  # FreeCAD object type
    object_group = "beam_path"  # group name for management
    object_icon = beam_icon  # icon for tree view

    def __init__(
        self,
        label: str,
        waist: dim = dim(1, "mm"),
        wavelength: float = 635,
        polarization: float = 0,
        power: float = 1,
        focal_length: dim = None,
        bound_parent: Layout = None,
    ):
        super().__init__(
            label=label,
            recompute_priority=-1,
        )

        obj = self.get_object()

        self.make_property("BoundParent", "App::PropertyLinkHidden")
        obj.BoundParent = bound_parent

        self.make_property("BeamChildren", "App::PropertyLinkListHidden")
        self.make_property("BeamSegments", "App::PropertyLinkListHidden")

        self.waist = waist
        self.wavelength = wavelength
        self.polarization = polarization
        self.power = power
        self.focal_length = focal_length

    def set_parent(self, parent: Layout):
        """Set the parent object of this component"""

        super().set_parent(parent)
        obj = self.get_object()
        parent_obj = parent.get_object()
        if obj.BoundParent is None:
            obj.BoundParent = parent_obj

    def add(
        self,
        child: Layout,
        beam_index: int,
        rotation: tuple,
        distance: dim = None,
        x_position: dim = None,
        y_position: dim = None,
        z_position: dim = None,
        offset: tuple[dim] = (0, 0),
        interface_index: int = 0,
    ):
        """
        Add a child layout to the beam path and assign beam index

        Args:
            child (Layout): Child layout to add
            beam_index (int): Index of the beam this child interacts with
            distance (float): Distance along the beam from the last component
            x_position (float): x-coordinate of the beam position
            y_position (float): y-coordinate of the beam position
            z_position (float): z-coordinate of the beam position
            rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
            offset (tuple): (y, z) offset from the center of the interface
            interface_index (int): Index of the interface on the child object to interact with
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
        child.distance = distance
        child.x_position = x_position
        child.y_position = y_position
        child.z_position = z_position
        child.offset = offset
        child.interface_index = interface_index
        child.placed = False

        return child

    def calculate(self):
        """
        Calculate the beam path through the layout
        """

        super().calculate()

        obj = self.get_object()

        # reset rotation so that child placements are correct
        if obj.Parent != None:
            obj.Placement.Rotation = obj.Parent.Placement.Rotation
        else:
            obj.Placement.Rotation = App.Rotation("XYZ", 0, 0, 0)

        if len(obj.BeamSegments) == 0:
            direction = obj.BasePlacement.Rotation.multVec(App.Vector(1, 0, 0))
            if self.focal_length != None:
                focal_rate = self.waist / self.focal_length
            else:
                focal_rate = 0
            input_beam = Beam_Segment(
                index=1,
                direction=direction,
                waist=self.waist,
                wavelength=self.wavelength,
                polarization=self.polarization,
                power=self.power,
                focal_rate=focal_rate,
            )
            super().add(input_beam, position=(0, 0, 0), rotation=(0, 0, 0))
            obj.BeamSegments += [input_beam.get_object()]

        # check for loose ends and start simulation from there
        for beam in obj.BeamSegments:
            Layout.calculate(beam.Proxy)
            if len(beam.Children) == 0:
                self.step(beam.Proxy)
                beam.Proxy.recompute()

    def recompute(self):
        """
        Recompute the beam path layout
        """
        self.calculate()
        obj = self.get_object()
        obj.purgeTouched()

    def get_next_global(self, input_beam: Beam_Segment):
        """
        Get the next global object the beam will interact with
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
            if not hasattr(proxy, "get_interfaces") or (
                child in obj.BeamChildren and not proxy.placed
            ):
                continue
            # check all interfaces of the object
            for interface in proxy.get_interfaces():
                intercept = interface.get_intercept(input_beam)
                if intercept is not None:
                    distance = np.linalg.norm(intercept - input_beam_obj.Placement.Base)
                    # find closest intercept
                    if distance < min_distance:
                        min_distance = distance
                        next_object = child
                        next_interface = interface

        return next_object, next_interface, min_distance

    def get_next_child(self, input_beam: Beam_Segment):
        """
        Get the next beam child object for placement
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
            if not hasattr(next_object.Proxy, "get_interfaces"):
                raise RuntimeError(
                    f"Beam child {next_object.Label} does not have any interfaces"
                )

            proxy = next_object.Proxy
            next_position = input_beam.get_constraint_position(
                proxy.distance,
                proxy.x_position,
                proxy.y_position,
                proxy.z_position,
            )

            # sum previous global interaction distances
            previous_distance = 0
            for beam_obj in reversed(obj.BeamSegments[:-1]):
                beam = beam_obj.Proxy
                index_diff = input_beam.index.bit_length() - beam.index.bit_length()
                root_index = beam.index >> index_diff
                if (
                    beam_obj.ChildObject not in obj.BeamChildren
                    and root_index == input_beam.index
                ):
                    previous_distance += beam.distance
                else:
                    break

            # get total constraint distance to next child
            next_distance = (
                np.linalg.norm(next_position - input_beam_obj.Placement.Base)
                - previous_distance
            )

            # gather all interfaces associated with the object
            object_children = []
            collect_children(next_object, object_children)
            interfaces = proxy.get_interfaces()
            for child in object_children:
                proxy = child.Proxy
                if hasattr(proxy, "get_interfaces"):
                    interfaces.extend(proxy.get_interfaces())
            # get specified interface
            next_interface = interfaces[proxy.interface_index]

        return next_object, next_interface, next_distance

    def step(self, input_beam: Beam_Segment):
        """
        Perform a single calculation step for the beam path
        """

        obj = self.get_object()
        beam_obj = input_beam.get_object()

        # get next global object
        next_global = self.get_next_global(input_beam)
        # get next beam child object
        next_child = self.get_next_child(input_beam)

        global_distance, child_distance = next_global[2], next_child[2]

        if global_distance == np.inf and child_distance == np.inf:
            # no more interactions, set beam distance to large value
            input_beam.distance = 50
            return

        if global_distance < child_distance:
            next_object, next_interface, next_distance = next_global
        else:
            next_object, next_interface, next_distance = next_child

            # get object placement
            intercept = input_beam.get_constraint_position(distance=next_distance)
            intercept -= obj.Placement.Base  # convert to local coordinates
            Layout.calculate(next_object.Proxy)  # update placement
            object_rotation = next_object.Placement.Rotation
            offset = object_rotation.multVec(App.Vector(0, *next_object.Proxy.offset))
            object_position = intercept - next_interface.position + offset
            # apply placement
            next_object.BasePlacement.Base = App.Vector(*object_position)
            next_object.Proxy.placed = True
            next_object.Proxy.recompute()

        # get output beams from interaction
        input_beam.distance = next_distance
        beam_obj.ChildObject = next_object
        output_beams = next_interface.get_output_beams(input_beam)
        for beam in output_beams:
            new_beam_obj = beam.get_object()
            obj.BeamSegments += [new_beam_obj]
            Layout.calculate(beam)
            self.step(beam)


class Interface:
    """
    Base class for optical interface elements

    Args:
        position (tuple): (x, y, z) coordinates (relative to parent)
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees (relative to parent)
        diameter (float): Diameter for circular interface
        dx (float): x-dimension for rectangular interface
        dy (float): y-dimension for rectangular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
        single_sided (bool): Whether the interface only interacts with beams from one side
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        diameter: dim = None,
        dx: dim = None,
        dy: dim = None,
        max_angle: float = 90,
        single_sided: bool = False,
    ):
        self.position = np.array(position)

        # calculate normal vector from rotation
        rotation_obj = App.Rotation("XYZ", *rotation)
        self.normal = np.array(rotation_obj.multVec(App.Vector(1, 0, 0)))

        # define bound type
        if diameter != None:
            self.shape = "circular"
            self.diameter = diameter
        elif dx != None and dy != None:
            self.shape = "rectangular"
            self.dx = dx
            self.dy = dy
        else:
            raise ValueError("Either radius or dx and dy must be specified")

        self.max_angle = max_angle
        self.single_sided = single_sided
        self.parent = None  # to be set when initialized in parent object

    def get_global_position(self) -> np.ndarray[float]:
        """
        Get the global position of the interface

        Returns:
            position (np.ndarray): (x, y, z) coordinates of the interface
        """

        parent_obj = self.parent.get_object()
        position = parent_obj.Placement.Base
        global_position = np.array(position) + self.position
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

    def get_intercept(self, incident_beam: Beam_Segment) -> np.ndarray[float] | None:
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

        print(f"Checking intercept with interface at {global_position}")

        # check if beam is within max angle
        incident_angle = abs(
            np.arccos(np.clip(np.dot(global_normal, -beam_direction), -1, 1))
        )
        if not self.single_sided and incident_angle > np.pi / 2:
            incident_angle -= np.pi
        if incident_angle > np.deg2rad(self.max_angle):
            print("Beam exceeds max angle for interface")
            return None

        denom = np.dot(global_normal, beam_direction)
        # check if beam is parallel to interface
        if np.abs(denom) < 1e-6:
            print("Beam is parallel to interface")
            return None

        distance = np.dot(global_normal, global_position - beam_position) / denom
        # check if intercept is behind beam origin
        if distance < 0:
            print("Intercept is behind beam origin")
            return None
        # check if intercept is too close to origin
        if -1e-6 < distance < 1e-6:
            print("Intercept is too close to origin")
            return None

        intercept = beam_position + distance * beam_direction

        # Check if intercept is within the interface bounds
        offset_vec = intercept - global_position
        if self.shape == "circular":
            if np.linalg.norm(offset_vec) > self.diameter / 2:
                return None
        elif self.shape == "rectangular":
            if abs(offset_vec[0]) > self.dx / 2 or abs(offset_vec[1]) > self.dy / 2:
                return None

        return intercept


class Reflection(Interface):
    """
    Base class for reflection interfaces
    Supports mirrors, samplers, polarizing beamsplitters, and dichroic mirrors
    To use type other than basic mirror, use the appropriate ref_* parameter.

    Args:
        position (tuple): (x, y, z) coordinates
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        ref_ratio (float): Ratio of reflected to transmitted power
        ref_polarization (string): Polarization angle of reflected light in radians
        ref_wavelengths (list): List of tuples specifying (min, max) wavelength ranges
                                for reflection in nm. Use None to indicate an open range
        diameter (float): Diameter for circular interface
        dx (float): x-distance for rectangular interface
        dy (float): y-distance for rectangular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
        single_sided (bool): Whether the interface only interacts with beams from one side
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        ref_ratio: float = None,
        ref_polarization: float = None,
        ref_wavelengths: list = None,
        diameter: dim = None,
        dx: dim = None,
        dy: dim = None,
        max_angle: float = 90,
        single_sided: bool = False,
    ):

        super().__init__(
            position=position,
            rotation=rotation,
            diameter=diameter,
            dx=dx,
            dy=dy,
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

    def get_output_beams(self, incident_beam: Beam_Segment) -> list[Beam_Segment]:
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

        # calculate ratio of transmitted to reflected power for different interface types
        if self.type == "mirror":
            transmit_ratio = 0
        if self.type == "sampler":
            transmit_ratio = 1 - self.ref_ratio
        if self.type == "polarizing":
            transmit_polarization = self.ref_polarization + np.pi / 2
            reflect_polarization = self.ref_polarization
            angle_diff = incident_beam.polarization - transmit_polarization
            transmit_ratio = np.cos(angle_diff) ** 2
        if self.type == "dichroic":
            transmit_ratio = 1
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

        if self.type != "polarizing":
            # TODO handle polarization change caused by other reflection
            transmit_polarization = incident_beam.polarization
            reflect_polarization = incident_beam.polarization

        local_origin = incident_beam.get_relative_position(intercept)
        waist = incident_beam.waist - incident_beam.distance * incident_beam.focal_rate
        focal_rate = incident_beam.focal_rate * np.sign(waist)
        waist = abs(waist)

        output_beams = []

        # generate transmitted beam
        if transmit_ratio > 0:
            if reflect_ratio > 0:
                index = incident_beam.index << 1  # handle beam splitting
            else:
                index = incident_beam.index
            direction = incident_beam.get_relative_direction(beam_direction)
            transmitted_beam = Beam_Segment(
                index=index,
                direction=direction,
                waist=waist,
                wavelength=incident_beam.wavelength,
                polarization=transmit_polarization,
                power=incident_beam.power * transmit_ratio,
                focal_rate=focal_rate,
            )
            incident_beam.add(transmitted_beam, origin=local_origin)
            output_beams.append(transmitted_beam)

        # generate reflected beam
        if reflect_ratio > 0:
            if transmit_ratio > 0:
                index = (incident_beam.index << 1) + 1  # handle beam splitting
            else:
                index = incident_beam.index

            direction = (
                beam_direction
                - 2 * np.dot(beam_direction, global_normal) * global_normal
            )
            local_direction = incident_beam.get_relative_direction(direction)
            reflect_beam = Beam_Segment(
                index=index,
                direction=local_direction,
                waist=waist,
                wavelength=incident_beam.wavelength,
                polarization=reflect_polarization,
                power=incident_beam.power * reflect_ratio,
                focal_rate=focal_rate,
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
        single_sided (bool): Whether the interface is single-sided
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        focal_length: float,
        diameter: dim = None,
        max_angle: float = 90,
        single_sided: bool = False,
    ):

        super().__init__(
            position=position,
            rotation=rotation,
            diameter=diameter,
            max_angle=max_angle,
            single_sided=single_sided,
        )

        self.focal_length = focal_length

    def get_output_beams(self, incident_beam: Beam_Segment) -> list[Beam_Segment]:

        global_normal = self.get_global_normal()
        beam_direction = incident_beam.get_global_direction()
        intercept = self.get_intercept(incident_beam)

        if intercept is None:
            return []

        local_origin = incident_beam.get_relative_position(intercept)
        waist = incident_beam.waist - incident_beam.distance * incident_beam.focal_rate
        if np.isclose(incident_beam.focal_rate, 0):
            focal_rate = waist / self.focal_length
        else:
            incident_focal_length = incident_beam.waist / incident_beam.focal_rate
            denom = incident_focal_length + self.focal_length - incident_beam.distance
            if np.isclose(denom, 0):
                focal_rate = 0
            else:
                focal_length = (
                    incident_focal_length
                    * self.focal_length
                    / (
                        incident_focal_length
                        + self.focal_length
                        - incident_beam.distance
                    )
                )
                focal_rate = waist / focal_length
        waist = abs(waist)

        # calculate beam rotation using thin lens approximation
        radial_vector = intercept - self.get_global_position()
        if np.isclose(np.linalg.norm(radial_vector), 0):
            direction = beam_direction
        else:
            normal_component = np.dot(beam_direction, global_normal)
            radial_direction = radial_vector / np.linalg.norm(radial_vector)
            tangent_direction = np.cross(radial_direction, global_normal)
            tangent_component = np.dot(beam_direction, tangent_direction)
            tangent_slope = tangent_component / normal_component
            radial_slope = np.dot(beam_direction, radial_direction) / normal_component
            radial_slope -= np.linalg.norm(radial_vector) / self.focal_length

            direction = global_normal * normal_component
            direction += tangent_direction * tangent_slope * normal_component
            direction += radial_direction * radial_slope * normal_component
            direction /= np.linalg.norm(direction)

        local_direction = incident_beam.get_relative_direction(direction)

        output_beam = Beam_Segment(
            index=incident_beam.index,
            direction=local_direction,
            waist=waist,
            wavelength=incident_beam.wavelength,
            polarization=incident_beam.polarization,
            power=incident_beam.power,
            focal_rate=focal_rate,
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
        diff_angle (float): Diffraction angle
        diameter (float): Diameter for circular interface
        dx (float): x-distance for rectangular interface
        dy (float): y-distance for rectangular interface
        max_angle (float): Maximum angle between incident beam and interface normal in degrees
    """

    def __init__(
        self,
        position: tuple,
        rotation: tuple,
        diffracted_angle: float,
        diffracted_ratio: float,
        radius: dim = None,
        dx: dim = None,
        dy: dim = None,
        max_angle: float = 90,
    ):

        # TODO finish this
        super().__init__(
            position=position,
            rotation=rotation,
            radius=radius,
            dx=dx,
            dy=dy,
            max_angle=max_angle,
            single_sided=False,
        )
