from example_layout import example_layout

from PyOpticL import optomech
from PyOpticL.layout import Component, Layout
from PyOpticL.utils import Dimension as dim


def nesting_example():

    layout = Layout("Nesting Example")

    layout.add(
        example_layout(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    )

    layout.add(
        example_layout(),
        position=(dim(4, "in"), dim(4, "in"), 0),
        rotation=(0, 0, 90),
    )

    return layout


if __name__ == "__main__":
    layout = nesting_example()
    layout.recompute()
