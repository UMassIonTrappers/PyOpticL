measurement_system = "imperial"
minimum_thread_engagement = 8
default_extra_drill_depth = 10
hidden_object_groups = ["hardware"]
enable_beam_transparency = False


def set_measurement_system(system: str):
    """
    Set the global measurement system preference. This will affect hardware sizes and grid spacing..

    Args:
        system (str): The measurement system to use, either 'metric' or 'imperial'
    """

    global measurement_system
    if system.lower() in ["metric", "imperial"]:
        measurement_system = system.lower()
    else:
        raise ValueError("Invalid system preference. Use 'metric' or 'imperial'.")


def get_measurement_system():
    """
    Get the current global measurement system preference.

    Returns:
        str: The current measurement system preference, either 'metric' or 'imperial'
    """

    return measurement_system


def set_minimum_thread_engagement(length: float):
    """
    Set the global minimum thread engagement length for all bolts. This is used to calculate default bolt lengths when not specified.

    Args:
        length (float): The minimum thread engagement length.
    """

    global minimum_thread_engagement
    minimum_thread_engagement = length


def get_minimum_thread_engagement():
    """
    Get the current global minimum thread engagement length for all bolts.

    Returns:
        float: The current minimum thread engagement length.
    """

    return minimum_thread_engagement


def set_default_extra_drill_depth(length: float):
    """
    Set the global default for clearance at the bottom of the drill holes. This is used to calculate default drill depths when not specified.

    Args:
        length (float): The default extra clearance at the bottom of the drill holes.
    """

    global default_extra_drill_depth
    default_extra_drill_depth = length


def get_default_extra_drill_depth():
    """
    Get the current global default for clearance at the bottom of the drill holes.

    Returns:
        float: The current default extra clearance at the bottom of the drill holes.
    """

    return default_extra_drill_depth


def set_hidden_object_groups(groups: list[str]):
    """
    Set the global list of hidden object groups. Objects in these groups will be hidden by default in the 3D view.

    Args:
        groups (list[str]): A list of object group names to hide by default.
    """

    global hidden_object_groups
    hidden_object_groups = groups


def get_hidden_object_groups():
    """
    Get the current global list of hidden object groups.

    Returns:
        list[str]: The current list of object group names that are hidden by default.
    """

    return hidden_object_groups


def set_enable_beam_transparency(enabled: bool):
    """
    Set the global preference for enabling beam transparency in the 3D view. When enabled, beams will be rendered with some transparency to allow seeing components behind them.

    Args:
        enabled (bool): Whether to enable beam transparency.
    """

    global enable_beam_transparency
    enable_beam_transparency = enabled


def get_enable_beam_transparency():
    """
    Get the current global preference for enabling beam transparency in the 3D view.

    Returns:
        bool: Whether beam transparency is currently enabled.
    """

    return enable_beam_transparency
