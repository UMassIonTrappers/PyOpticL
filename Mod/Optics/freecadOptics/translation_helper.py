from math import *
import numpy as np

INCH = 25.4

translation = np.array([0,0,0])
rotation = np.array([0,0,0], dtype=np.float32)

def rotate(rot):
    global translation
    global rotation
    rotation += rot
    rot = np.deg2rad(rot)
    rotx = [[1, 0, 0],
            [0, cos(rot[0]), -sin(rot[0])],
            [0, sin(rot[0]), cos(rot[0])]]
    roty = [[cos(rot[1]), 0, sin(rot[1])],
            [0, 1, 0],
            [-sin(rot[1]), 0, cos(rot[1])]]
    rotz = [[cos(rot[2]), -sin(rot[2]), 0],
            [sin(rot[2]), cos(rot[2]), 0],
            [0, 0, 1]]

    translation = np.dot(rotx, translation)
    translation = np.dot(roty, translation)
    translation = np.dot(rotz, translation)

def translate(tran):
    global translation
    translation = np.add(translation, tran)

rotate([90, 0, 0])
translate([0, 14.2, 0])
translate([-51.8+25.8, 0, -(32.92-16)-1])
rotate([0, 0, -90])
translate([0, 0, -(6.35 +0.089*INCH/2)])

print(list(np.round(translation,2)))
print(list(np.round(rotation,2)))