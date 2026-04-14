from PyOpticL.types import Dimension as dim

measurement_system = "imperial"
minimum_thread_engagement = dim(0.25, "in")
default_extra_drill_depth = dim(0.25, "in")


def set_hardware_preference(system: str):
    """
    Set the global hardware preference for the measurement system. This will affect what hardware is used by default in the optomechanical components.

    Args:
        system (str): The measurement system to use, either 'metric' or 'imperial'
    """

    global measurement_system
    if system.lower() in ["metric", "imperial"]:
        measurement_system = system.lower()
    else:
        raise ValueError("Invalid system preference. Use 'metric' or 'imperial'.")


def set_minimum_thread_engagement(length: dim):
    """
    Set the global minimum thread engagement length for all bolts. This is used to calculate default bolt lengths when not specified.

    Args:
        length (dim): The minimum thread engagement length.
    """

    global minimum_thread_engagement
    minimum_thread_engagement = length


def set_default_extra_drill_depth(length: dim):
    """
    Set the global default for clearance at the bottom of the drill holes. This is used to calculate default drill depths when not specified.

    Args:
        length (dim): The default extra clearance at the bottom of the drill holes.
    """

    global default_extra_drill_depth
    default_extra_drill_depth = length