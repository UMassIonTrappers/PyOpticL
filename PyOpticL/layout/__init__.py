from .origin import Origin
from .baseplate import Baseplate
from .optomech import *
import FreeCAD as App

NORMALS = {
        'up-right': App.Vector(1, -1, 0).normalize(),
        'up-left': App.Vector(-1, -1, 0).normalize(),
        'right-down': App.Vector(-1, -1, 0).normalize(),
        'right-up': App.Vector(-1, 1, 0).normalize(),
        'down-left': App.Vector(-1, 1, 0).normalize(),
        'down-right': App.Vector(1, 1, 0).normalize(),
        'left-up': App.Vector(1, 1, 0).normalize(),
        'left-down': App.Vector(1, -1, 0).normalize(),
        }
