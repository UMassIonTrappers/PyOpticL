from warnings import warn

import Draft
import FreeCAD as App
import Mesh
import numpy as np
import Part

from .layout import optomech


class Beam:
    """
    Defines a beam object

    Args:
        name (string): Beam's name
        position (App.Vector): Beam origin's vector position
        direction (App.Vector): Vector defining the beam's direction
    """

    def __init__(self, name, position, direction):
        self.obj = App.ActiveDocument.addObject("Part::FeaturePython", name)

        self.obj.Proxy = self
        ViewProvider(self.obj.ViewObject)

        self.obj.addProperty("App::PropertyVectorList", "Origins").Origins += [position]
        self.obj.addProperty("App::PropertyVectorList", "Offsets").Offsets += [
            direction
        ]
        self.obj.addProperty("App::PropertyFloatList", "Distances")

    def placeAlong(self, obj, distance, normal=None, beam_index=1):
        """
        Places an object along the beam path

        Args:
            obj: The object to place
            distance (float): The distance along the beam to place the object
            normal (App.Vector): The normal vector of the object (will override obj's normal if it exists)
            beam_index (int): The binary tree index of the beam object
        """

        obj.obj.addProperty("App::PropertyFloat", "Distance").Distance = distance
        if normal != None:
            obj.obj.Vec2 = normal.normalize()
        obj.obj.Position = App.Vector(0, 0, 0)

        obj.obj.addProperty("App::PropertyInteger", "BeamIndex").BeamIndex = beam_index

        obj.obj.addProperty("App::PropertyBool", "Unplaced").Unplaced = True

        obj.obj.addProperty("App::PropertyLink", "Parent").Parent = self.obj

        if not hasattr(self.obj, "InlineComponents"):
            self.obj.addProperty("App::PropertyLinkList", "InlineComponents")
        self.obj.InlineComponents += [obj.obj]

    def execute(self, obj):
        shapes = []
        for i in range(len(self.obj.Origins)):
            temp = Part.makeCylinder(
                0.5, self.obj.Distances[i], self.obj.Origins[i], self.obj.Offsets[i], 0
            )
            shapes.append(temp)
        comp = Part.Compound(shapes)
        obj.Shape = comp

    def calculate(
        self, parent_placement=App.Placement(App.Matrix()), depth=0, beam_index=1
    ):
        if depth > 250:
            return

        # do something and create a list of possible components and inline_components

        for i in range(len(self.obj.Origins)):
            self.obj.Origins[i] = parent_placement * self.obj.Origins[i]
            self.obj.Offsets[i] = parent_placement.Rotation * self.obj.Offsets[i]

        optical_components = []

        for i in App.ActiveDocument.Objects:
            if hasattr(i, "OpticalType"):
                if hasattr(i, "Parent"):
                    if i.Parent == self.obj or i.Unplaced:
                        continue
                optical_components.append(i)

        inline_components = []

        for i in self.obj.InlineComponents:
            if i.BeamIndex == beam_index:
                inline_components.append(i)

        inline_index = 0
        dist_since_last_inline = 0
        count = 0
        last_hit = None

        while True:
            count += 1
            if count > 1000:
                print("hit interaction limit")
                break

            origin = self.obj.Origins[-1]
            offset = self.obj.Offsets[-1]
            hit = None
            for (
                check_comp
            ) in optical_components:  # check all optical components w/ known positions
                print(check_comp, last_hit)
                if (
                    last_hit != None and check_comp == last_hit
                ):  # can't hit same component twice
                    continue
                if (
                    type(check_comp.Proxy) is optomech.CylindricalOptic
                    and check_comp.Vec2.dot(offset) != 0
                ):
                    t = (
                        check_comp.Vec2.dot(check_comp.Position.add(origin.negative()))
                    ) / (check_comp.Vec2.dot(offset))
                    if (
                        (
                            origin.add(t * offset).add(check_comp.Position.negative())
                        ).Length
                    ) <= check_comp.Radius:
                        if (
                            (not hasattr(self.obj, "InlineComponents"))
                            or t
                            < (
                                inline_components[inline_index].Distance
                                - dist_since_last_inline
                            )
                            and (
                                hit == None or t < hit[1]
                            )  # take the component if it hits it before the next inline component gets placed
                        ):
                            # if check_comp.OpticalType == "mirror":
                            hit = check_comp, t
            print(hit)
            if hit != None:
                dist_since_last_inline += hit[1]
                self.obj.Distances += [hit[1]]
                self.obj.Origins += [origin.add(hit[1] * offset)]

                last_hit = hit[0]

                if hit[0].OpticalType == "mirror":
                    self.obj.Offsets += [
                        App.Rotation(offset.negative(), hit[0].Vec2)
                        * App.Rotation(offset.negative(), hit[0].Vec2)
                        * offset.negative()
                    ]  # TODO: check for max_angle
                elif hit[0].OpticalType == "splitter":
                    self.obj.Offsets += [offset]  # transmitted beam
                    self.calculate(parent_placement, depth, beam_index=beam_index<<1)

                    self.obj.Offsets += [
                        App.Rotation(offset.negative(), hit[0].Vec2)
                        * App.Rotation(offset.negative(), hit[0].Vec2)
                        * offset.negative()
                    ]  # reflected beam TODO: check for max_angle
                    self.calculate(parent_placement, depth, beam_index=(beam_index<<1)+1)
            elif (
                hasattr(self.obj, "InlineComponents")
                and len(inline_components) > inline_index
            ):
                hit = (
                    inline_components[inline_index],
                    inline_components[inline_index].Distance,
                )
                dist_since_last_inline = 0
                self.obj.Distances += [hit[1]]
                self.obj.Origins += [origin.add(hit[1] * offset)]

                last_hit = hit[0]

                hit[0].Position = origin.add(hit[1] * offset)
                hit[0].Proxy.calculate(depth=depth + 1)
                hit[0].Unplaced = False

                if hit[0].OpticalType == "mirror":
                    self.obj.Offsets += [
                        App.Rotation(offset.negative(), hit[0].Vec2)
                        * App.Rotation(offset.negative(), hit[0].Vec2)
                        * offset.negative()
                    ]  # TODO: check for max_angle
                elif hit[0].OpticalType == "splitter":
                    self.obj.Offsets += [offset]  # transmitted beam
                    self.calculate(parent_placement, depth, beam_index=beam_index<<1)

                    self.obj.Origins += [origin.add(hit[1] * offset)]
                    self.obj.Offsets += [
                        App.Rotation(offset.negative(), hit[0].Vec2)
                        * App.Rotation(offset.negative(), hit[0].Vec2)
                        * offset.negative()
                    ]  # reflected beam TODO: check for max_angle
                    self.calculate(parent_placement, depth, beam_index=(beam_index<<1)+1)

                inline_index += 1
            else:
                self.obj.Distances += [50]
                warn("Uncapped beam detected")
                break


class ViewProvider:
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        return

    def getDefaultDisplayMode(self):
        return "Shaded"

    # def updateData(self, base_obj, prop):
    #     if prop in "Children":
    #
    #
    #     for obj in App.ActiveDocument.Objects:
    #         if hasattr(obj, "BasePlacement") and obj.Baseplate != None:
    #             obj.Placement.Base = (
    #                 obj.BasePlacement.Base + obj.Baseplate.Placement.Base
    #             )
    #             obj.Placement = App.Placement(
    #                 obj.Placement.Base,
    #                 obj.Baseplate.Placement.Rotation,
    #                 -obj.BasePlacement.Base,
    #             )
    #             obj.Placement.Rotation = obj.Placement.Rotation.multiply(
    #                 obj.BasePlacement.Rotation
    #             )

    # def onDelete(self, feature, subelements):
    # # delete all elements when baseplate is deleted
    # for i in App.ActiveDocument.Objects:
    #     if i != feature.Object:
    #         App.ActiveDocument.removeObject(i.Name)
    # return True

    def claimChildren(self):
        if hasattr(self.Object, "ChildObjects"):
            return self.Object.ChildObjects
        else:
            return []

    def getIcon(self):
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
