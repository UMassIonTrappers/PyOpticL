import PyOpticL
from PyOpticL import optomech
from PyOpticL.layout import Component, Layout
from PyOpticL.utils import Dimension as dim

PyOpticL.set_minimum_thread_engagement(dim(0.5, "in"))

example_component = optomech.example_component(
    side_length=dim(1, "in"),
    height=dim(1, "in"),
)


def example_layout():

    layout = Layout("Example Layout")

    sub_layout = layout.add(
        Layout(
            label="Sub-Layout",
        ),
        position=(50, 0, 0),
        rotation=(0, 0, -90),
    )

    layout.add(
        Component(label="Example Component 1", definition=example_component),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    )

    layout.add(
        Component(label="Example Component 2", definition=example_component),
        position=(0, 20, 0),
        rotation=(0, 0, 0),
    )

    sub_layout.add(
        Component(label="Example Component 3", definition=example_component),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    )

    sub_layout.add(
        Component(label="Example Component 4", definition=example_component),
        position=(0, 20, 0),
        rotation=(0, 0, 0),
    )

    return layout


if __name__ == "__main__":
    layout = example_layout()
    layout.recompute()
