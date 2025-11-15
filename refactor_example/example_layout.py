from PyOpticL import optomech
from PyOpticL.layout import Component
from PyOpticL.layout import Dimension as dim
from PyOpticL.layout import Layout

example_component = optomech.example_component(
    side_length=dim(20, "mm"),
    height=dim(15, "mm"),
    drill_depth=dim(10, "mm"),
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
