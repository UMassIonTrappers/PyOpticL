from __future__ import annotations

import FreeCAD as App

from PyOpticL.utils import collect_children


class Dimension(float):
    """
    Class to handle dimensions with units
    value is stored internally as mm

    Args:
        value (float) : numerical value of the dimension
        unit (str) : unit of the dimension, options are 'um', 'mm', 'cm', 'm', 'in', 'ft'
    """

    conversion_factors = {
        "um": 0.001,
        "mm": 1,
        "cm": 10,
        "m": 1000,
        "in": 25.4,
        "ft": 304.8,
    }

    def __new__(self, value: float, unit: str = "mm") -> Dimension:
        if unit not in self.conversion_factors:
            raise ValueError(f"Unsupported unit: {unit}")
        instance = super().__new__(self, value * self.conversion_factors[unit])
        instance.unit = unit
        return instance

    def to_unit(self, unit: str) -> float:
        if unit in self.conversion_factors:
            return self.value / self.conversion_factors[unit]
        else:
            raise ValueError(f"Unsupported unit: {unit}")


class Layout:
    """
    Abstracted proxy for a FreeCAD object representing a layout

    Args:
        label (string): Name of the object
        recompute_priority (int): Priority for recompute order
    """

    object_type = "Part"  # FreeCAD object type (must be Part or Mesh)
    object_group = "layout"  # group name for management
    object_icon = ""  # icon for the object in the tree view

    def __init__(
        self,
        label: str,
        recompute_priority: int = 0,
    ):

        # create or get document
        if App.ActiveDocument != None:
            document = App.ActiveDocument
        else:
            document = App.newDocument(label)

        # initialize FeaturePython object
        obj = document.addObject(f"{self.object_type}::FeaturePython", label, self)
        obj.Label = label
        obj.setEditorMode("Label", 1)  # make label read-only
        self.document_id = document.Name
        self.object_id = obj.Name
        ViewProvider(obj.ViewObject, icon=self.object_icon)

        # setup placement properties
        self.make_property("Placement", "App::PropertyPlacement")
        self.make_property("BasePlacement", "App::PropertyPlacement", visible=True)

        # initialize parent and children properties
        self.make_property("Parent", "App::PropertyLinkHidden")
        obj.Parent = None
        self.make_property("Children", "App::PropertyLinkList")
        obj.Children = []

        self.recompute_priority = recompute_priority

    def get_object(self) -> App.DocumentObject:
        """
        Get the FreeCAD object associated with this proxy

        Returns:
            App.DocumentObject: The FreeCAD document object
        """
        document = App.getDocument(self.document_id)
        return document.getObject(self.object_id)

    def make_property(self, name: str, type: str, visible: bool = False):
        """
        Create a property on the FreeCAD object if it does not already exist

        Args:
            name (string): Name of the property
            type (string): Type of the property
            visible (bool): Whether the property is visible in the property editor
        """
        obj = self.get_object()
        if not hasattr(obj, name):
            obj.addProperty(type, name)
        if visible:
            obj.setEditorMode(name, 1)  # read-only
        else:
            obj.setEditorMode(name, 2)  # hidden

    def set_parent(self, parent: Layout):
        """
        Set the parent object of this component

        Args:
            parent (Layout): Parent object to set
        """

        obj = self.get_object()
        parent_obj = parent.get_object()
        obj.Parent = parent_obj

    def add(
        self,
        child: Layout,
        position: tuple,
        rotation: tuple,
    ) -> Layout:
        """Add a child object to this component

        Args:
            child (Layout): Child object to add
            position (tuple): (x, y, z) relative coordinates of child
            rotation (tuple): (angle_x, angle_y, angle_z) relative rotation of child

        Returns:
            child (Layout): The added child layout
        """

        obj = self.get_object()
        child_obj = child.get_object()

        if child_obj.Parent != None:
            raise RuntimeError("Child object already has a parent assigned")

        obj.Children += [child_obj]
        child.set_parent(self)

        child_obj.BasePlacement = App.Placement(
            App.Vector(*position), App.Rotation("XYZ", *rotation)
        )

        return child

    def compute_placement(self):
        """Calculate global placement of object"""

        obj = self.get_object()

        # calculate final placement
        obj.Placement = obj.BasePlacement
        if obj.Parent != None:
            obj.Placement = obj.Parent.Placement * obj.Placement

        obj.purgeTouched()  # prevent triggering recompute

    def recompute(self):
        """Recursively recompute all children of this object"""

        obj = self.get_object()
        self.compute_placement()

        compute_list = obj.Children
        # sort by recompute priority
        compute_list.sort(
            key=lambda child_obj: child_obj.Proxy.recompute_priority, reverse=True
        )
        for child_obj in compute_list:
            child_obj.Proxy.recompute()

    # link built-in FreeCAD execute to internal recompute
    def execute(self, obj):
        """Execute method called by FreeCAD to recompute the object"""

        print(f"Recomputing {obj.Name}...")
        self.recompute()


class Component(Layout):
    """
    Abstracted proxy for a FreeCAD object representing a component
    Inherits from Layout

    Args:
        label (string): Name of the object
        definition (Component_Definition): Template defining component properties
        recompute_priority (int): Priority for recompute order
    """

    object_group = "component"  # group name for management
    object_color = (0.5, 0.5, 0.5)  # color for the object model
    object_transparency = 0  # transparency for the object model

    def __init__(
        self,
        label: str,
        definition: object,
        recompute_priority: int = 0,
    ):

        # Define attributes to override using the component definition
        override_attributes = (
            "object_color",
            "object_icon",
            "object_group",
            "object_transparency",
        )

        # inherit methods from component template
        class Component_Wrapper(Component):
            def __getattr__(self, name):
                if hasattr(definition, name):
                    return getattr(definition, name)
                raise AttributeError(name)

            for attr in override_attributes:
                if hasattr(definition, attr):
                    setattr(self, attr, getattr(definition, attr))

            if hasattr(definition, "mesh"):
                object_type = "Mesh"

            # wrap interfaces to set parent
            if hasattr(definition, "interfaces"):

                def interfaces(self):
                    interfaces = definition.interfaces()
                    for interface in interfaces:
                        interface.parent = self
                    return interfaces

        self.__class__ = Component_Wrapper

        super().__init__(
            label=label,
            recompute_priority=recompute_priority,
        )

        # set object color
        obj = self.get_object()
        obj.ViewObject.ShapeColor = self.object_color
        obj.ViewObject.Transparency = self.object_transparency

        # add any sub-components defined in the template
        if hasattr(definition, "subcomponents"):
            for subcomponent in definition.subcomponents():
                self.add(
                    child=subcomponent.component,
                    position=subcomponent.position,
                    rotation=subcomponent.rotation,
                )

    def compute_shape(self):
        """Calculate and set the shape of the object"""

        obj = self.get_object()

        # update object shape
        if self.object_type == "Part" and hasattr(self, "shape"):
            shape = self.shape()

            # gather peer objects
            drill_objs = []
            if obj.Parent != None:
                for child in obj.Parent.Children:
                    if child != obj:
                        drill_objs.append(child)

            # gather child objects recursively
            collect_children(obj, drill_objs)

            # apply drilling
            for drill_obj in drill_objs:
                if hasattr(drill_obj.Proxy, "drill"):
                    drill_obj.Proxy.compute_placement()
                    drill_shape = drill_obj.Proxy.drill()
                    drill_shape.Placement = (
                        obj.Placement.inverse() * drill_obj.Placement
                    )
                    shape = shape.cut(drill_shape)

            # apply placement and set final shape
            shape.Placement = obj.Placement
            obj.Shape = shape

        elif self.object_type == "Mesh" and hasattr(self, "mesh"):
            mesh = self.mesh
            mesh.Placement = obj.Placement
            obj.Mesh = mesh

        obj.purgeTouched()  # prevent triggering recompute

    def recompute(self):
        """Recursively recompute all children of this object"""

        super().recompute()
        self.compute_shape()


# ViewProvider handles how the object is handled in the FreeCAD GUI
class ViewProvider:
    def __init__(self, obj, icon=None):
        obj.Proxy = self
        self.icon = icon
        proxy = obj.Object.Proxy
        self.document_id = proxy.document_id
        self.object_id = proxy.object_id

    def get_object(self) -> App.DocumentObject:
        document = App.getDocument(self.document_id)
        return document.getObject(self.object_id)

    def getIcon(self):
        return self.icon

    def getDefaultDisplayMode(self):
        return "Shaded"

    def claimChildren(self):
        obj = self.get_object()
        return obj.Children

    def onDelete(self, feature, subelements):
        obj = self.get_object()
        document = App.getDocument(self.document_id)

        # remove all children recursively
        children = []
        collect_children(obj, children)
        for child in reversed(children):
            document.removeObject(child.Name)

        return True
