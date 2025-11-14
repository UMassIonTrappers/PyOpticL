from ...layout import Origin
from .baseplate import Baseplate
from .optomech import *
import FreeCAD as App

NORMALS = {
    "up-right": (1, -1, 0),
    "up-left": (-1, -1, 0),
    "right-down": (-1, -1, 0),
    "right-up": (-1, 1, 0),
    "down-left": (-1, 1, 0),
    "down-right": (1, 1, 0),
    "left-up": (1, 1, 0),
    "left-down": (1, -1, 0),
}
