from PyOpticL.layout import Component, Layout, Subcomponent
from PyOpticL.library import optics, thorlabs
from PyOpticL.utils import Dimension as dim
from PyOpticL.utils import box_shape, cardinal_angle, cylinder_shape, translate_shape


class Periscope:
    """
    Custom periscope mount for changing beam height.

    Args:
        lower_dz (float): Height of the lower mirror center above mount base
        upper_dz (float): Height of the upper mirror center above mount base
        invert (bool): Mirror the mount footprint about the vertical axis
        table_mount (bool): Offset for direct optical-table mounting
        mirror_definition (object): Mirror definition class instance
    """

    object_group = "misc"
    object_color = (0.6, 0.9, 0.6)

    def __init__(
        self,
        lower_dz: dim = dim(36.5, "mm"),
        upper_dz: dim = dim(76, "mm"),
        invert: bool = True,
        table_mount: bool = True,
        mirror_definition: object = None,
    ):
        self.lower_dz = lower_dz
        self.upper_dz = upper_dz
        self.invert = invert
        self.table_mount = table_mount
        self.mirror_definition = mirror_definition or optics.Circular_Mirror(
            mount_definition=thorlabs.Mirror_Mount_K05S1(),
        )
        self.z_off = -dim(1.5, "in") if table_mount else dim(0, "mm")

    def subcomponents(self):
        sign = -1 if self.invert else 1
        return [
            Subcomponent(
                component=Component(
                    label="Lower Mirror",
                    definition=self.mirror_definition,
                ),
                position=(0, 0, self.lower_dz + self.z_off),
                rotation=(sign * 90, -45, 0),
            ),
            Subcomponent(
                component=Component(
                    label="Upper Mirror",
                    definition=self.mirror_definition,
                ),
                position=(0, 0, self.upper_dz + self.z_off),
                rotation=(sign * 90, 135, 0),
            ),
        ]

    def shape(self):
        width = dim(2, "in")
        fillet = dim(15, "mm")
        height = self.upper_dz + dim(20, "mm")
        post_clearance = dim(0.26, "in") + dim(0.5, "mm")

        part = box_shape(
            dimensions=(dim(70, "mm"), width, height),
            position=(0, 0, 0),
            center=(0, 0, -1),
        )

        for i in [-1, 1]:
            cut = box_shape(
                dimensions=(fillet * 2 + dim(4, "mm"), width, height),
                position=(i * (dim(35, "mm") + fillet), 0, dim(20, "mm")),
                center=(i, 0, -1),
                fillet=fillet,
                fillet_direction=(0, 1, 0),
            )
            part = part.cut(cut)

            for y in [-dim(0.5, "in") / 2, dim(0.5, "in") / 2]:
                hole = cylinder_shape(
                    diameter=post_clearance,
                    height=dim(1, "in") + dim(5, "mm"),
                    position=(i * dim(1, "in"), y, dim(25, "mm")),
                    rotation=(180, 0, 0),
                )
                part = part.cut(hole)

        y_shift = (-1 if self.invert else 1) * (width / 2 + dim(0.5, "in") / 2)
        part = translate_shape(part, (0, y_shift - 6.35, self.z_off))
        return part


def periscope(
    lower_dz: dim = dim(36.5, "mm"),
    upper_dz: dim = dim(76, "mm"),
    invert: bool = True,
    table_mount: bool = True,
) -> Component:
    return Component(
        label="Periscope",
        definition=Periscope(
            lower_dz=lower_dz,
            upper_dz=upper_dz,
            invert=invert,
            table_mount=table_mount,
        ),
    )


if __name__ == "__main__":
    layout = Layout("Periscope")
    layout.add(
        periscope(),
        position=(dim(2.5, "grid"), dim(4.5, "grid"), 0),
        rotation=cardinal_angle["right"],
    )
    layout.recompute()
