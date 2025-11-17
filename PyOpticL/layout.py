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
        position (tuple): (x, y, z) coordinates
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
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
        """Get the FreeCAD object associated with this proxy"""
        document = App.getDocument(self.document_id)
        return document.getObject(self.object_id)

    def make_property(self, name, type, visible=False):
        obj = self.get_object()
        if not hasattr(obj, name):
            obj.addProperty(type, name)
        if not visible:
            obj.setEditorMode(name, 2)

    def set_parent(self, parent: Layout):
        """Set the parent object of this component"""

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
            position (tuple): (x, y, z) coordinates of child (overrides initial position)
            rotation (tuple): (angle_x, angle_y, angle_z) rotation of child (overrides initial rotation)
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

    def calculate(self):
        """Calculate global placement of object"""

        obj = self.get_object()

        # calculate final placement
        obj.Placement = obj.BasePlacement
        if obj.Parent != None:
            obj.Placement = obj.Parent.Placement * obj.Placement

        obj.purgeTouched()  # prevent multiple recomputes

    def recompute(self):
        """Recursively recompute all children of this object"""

        obj = self.get_object()
        self.calculate()

        compute_list = obj.Children
        # sort by recompute priority
        compute_list.sort(
            key=lambda child_obj: child_obj.Proxy.recompute_priority, reverse=True
        )
        for child_obj in compute_list:
            child_obj.Proxy.recompute()
            child_obj.purgeTouched()  # prevent multiple recomputes

        # prevent multiple recomputes
        obj.purgeTouched()
        if obj.Parent != None:
            obj.Parent.purgeTouched()

    # link built-in FreeCAD execute to internal recompute
    def execute(self, obj):
        print(f"Recomputing {obj.Name}...")
        self.recompute()


class Component(Layout):
    """
    Abstracted proxy for a FreeCAD object representing a component
    Inherits from Layout

    Args:
        label (string): Name of the object
        definition (Component_Definition): Template defining component properties
        position (tuple): (x, y, z) coordinates
        rotation (tuple): (angle_x, angle_y, angle_z) rotation in degrees
        recompute_priority (int): Priority for recompute order
    """

    object_type = "Part"  # FreeCAD object type
    object_group = "component"  # group name for management
    object_icon = ""  # icon for the object in the tree view
    object_color = (0.5, 0.5, 0.5)  # color for the object model
    object_transparency = 0  # transparency for the object model

    def __init__(
        self,
        label: str,
        definition: object,
        recompute_priority: int = 0,
    ):

        super().__init__(
            label=label,
            recompute_priority=recompute_priority,
        )

        # Define attributes to override using the component definition
        override_attributes = (
            "object_color",
            "object_icon",
            "object_type",
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

            # wrap get_interfaces to set parent
            if hasattr(definition, "get_interfaces"):

                def get_interfaces(self):
                    interfaces = definition.get_interfaces()
                    for interface in interfaces:
                        interface.parent = self
                    return interfaces

        self.__class__ = Component_Wrapper

        # set object color
        obj = self.get_object()
        obj.ViewObject.ShapeColor = self.object_color
        obj.ViewObject.Transparency = self.object_transparency

        # add any sub-components defined in the template
        if hasattr(definition, "get_components"):
            for comp, placement in definition.get_components():
                self.add(comp, **placement)

    def calculate(self):
        """Calculate global placement of object and update shape"""

        super().calculate()
        obj = self.get_object()

        # update object shape
        if hasattr(self, "get_shape"):
            shape = self.get_shape()

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
                if hasattr(drill_obj.Proxy, "get_drill"):
                    drill_shape = drill_obj.Proxy.get_drill()
                    shape = shape.cut(drill_shape)

            # apply placement and set final shape
            shape.Placement = obj.Placement
            if self.object_type == "Part":
                obj.Shape = shape
            elif self.object_type == "Mesh":
                obj.Mesh = shape


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

    def onChanged(self, vp, prop):
        # propagate visibility changes to all children recursively
        if prop == "Visibility":
            try:
                visible = bool(vp.Visibility)
            except Exception:
                return

            obj = self.get_object()

            children = []
            collect_children(obj, children)
            for child in children:
                child.ViewObject.Visibility = visible
