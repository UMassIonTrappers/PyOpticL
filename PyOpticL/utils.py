import FreeCAD as App


def collect_children(parent: App.DocumentObject, output_list: list):
    """
    Recursively collect all children of a given FreeCAD document object.

    Args:
        parent (App.DocumentObject): The parent FreeCAD object.
        output_list (list): List to append the collected children to.
    """
    if hasattr(parent, "Children"):
        for child in parent.Children:
            output_list.append(child)
            collect_children(child, output_list)


def wavelength_to_rgb(wl: float) -> tuple:
    """
    Convert a wavelength in nm to an RGB color tuple.

    Args:
        wl (float): Wavelength in nanometers.
    """

    # clip input to visible range
    wl = max(380, min(780, wl))

    gamma = 0.8
    max_intensity = 1.0

    # basic values
    r = g = b = 0.0
    if 380 <= wl <= 439:
        r = -(wl - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= wl <= 489:
        r = 0.0
        g = (wl - 440) / (490 - 440)
        b = 1.0
    elif 490 <= wl <= 509:
        r = 0.0
        g = 1.0
        b = -(wl - 510) / (510 - 490)
    elif 510 <= wl <= 579:
        r = (wl - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= wl <= 644:
        r = 1.0
        g = -(wl - 645) / (645 - 580)
        b = 0.0
    elif 645 <= wl <= 780:
        r = 1.0
        g = 0.0
        b = 0.0

    # gamma correction factor
    if 380 <= wl <= 419:
        factor = 0.3 + 0.7 * (wl - 380) / (420 - 380)
    elif 420 <= wl <= 700:
        factor = 1.0
    elif 701 <= wl <= 780:
        factor = 0.3 + 0.7 * (780 - wl) / (780 - 700)
    else:
        factor = 0.0

    def scale(channel: float) -> float:
        if channel > 0:
            return float(max_intensity * ((channel * factor) ** gamma))
        return 0.0

    return (scale(r), scale(g), scale(b))
