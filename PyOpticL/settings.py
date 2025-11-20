metric_hardware = False


def set_hardware_preference(system: str):
    global metric_hardware
    if system.lower() == "metric":
        metric_hardware = True
    elif system.lower() == "imperial":
        metric_hardware = False
    else:
        raise ValueError("Invalid system preference. Use 'metric' or 'imperial'.")
