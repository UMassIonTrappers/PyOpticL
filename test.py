from PyOpticL import laser, layout, optomech
from datetime import datetime
from examples import ECDL
import numpy as np

name = "Test Module"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " +  date_time

dx = 10*layout.inch
dy = 10*layout.inch
dz = layout.inch

def main():
    layout.redraw()

if __name__ == "__main__":
    main()