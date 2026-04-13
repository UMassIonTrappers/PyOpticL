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