from math import *
import numpy as np

vec = [0,0,0]

def rotate(rot):
    global vec
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

    vec = np.dot(rotx, vec)
    vec = np.dot(roty, vec)
    vec = np.dot(rotz, vec)

def translate(tran):
    global vec
    vec = np.add(vec, tran)

translate([-13.3, -19 + 0.6 + 12.7, -28])
rotate([90, 0, 90])
translate([0, 0, -12.7])
translate([0, 0, 0])

print(list(np.round(vec,2)))