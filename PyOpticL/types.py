import numpy as np

cardinal_angle = {
    "right": 0,
    "left": 180,
    "up": 90,
    "down": -90,
    "ne": 45,
    "se": -45,
    "sw": -135,
    "nw": 135,
}
turn_angle = {
    "up-right": -45,
    "right-up": 135,
    "up-left": -135,
    "left-up": 45,
    "down-right": 45,
    "right-down": -135,
    "down-left": 135,
    "left-down": -45,
}


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

    def __new__(self, value: float, unit: str = "mm"):
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
