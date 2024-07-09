from PyOpticL import layout, optomech
from datetime import datetime
import numpy as np
def grid_beam_splitter_along_beam(beam_obj, beam_index, angle, distance, baseplate, parity=1, Row_number = 6, Column_number = 6):
    origin = baseplate.place_element_along_beam("beam_splitter_origin", optomech.circular_mirror, beam_obj, beam_index, angle, distance, optional = True)

    for i in range(Row_number):
        for j in range(Column_number):
            if (i == j ==0):
                continue
            baseplate.place_element_relative("beam_splitter_" + str(i) + str(j),
                                             optomech.circular_mirror, origin, angle,
                                             x_off=(-1 * parity * 
                                                    np.sign(np.sin(np.radians(angle))) * (i) * 2 * layout.inch),
                                             y_off=(parity * np.sign(np.cos(np.radians(angle)))
                                                                    * (i) * 2 * layout.inch),
                                             z_off=(2 * layout.inch * j))
            print(angle, np.sin(np.radians(angle)), np.cos(np.radians(angle)))
            print(-1 * parity * np.sin(np.radians(angle)) * (i + 1) * 2 * layout.inch)
            print(parity * np.cos(np.radians(angle) * (i + 1) * 2 * layout.inch))

def test_redstone():
    baseplate = layout.baseplate(36 * layout.inch, 36 * layout.inch, 1 * layout.inch,)

    beam = baseplate.add_beam_path(1 * layout.inch, 11 * layout.inch, layout.cardinal['right'])
    origin = baseplate.place_element_along_beam("beam_splitter_origin", optomech.circular_mirror, beam_obj = beam, beam_index = 0b1, angle = 360, distance=15 * layout.inch)
    Row_number = 4.
    Column_number = 4.
    # parity = 1
    angle = 0
    for i in range(int(Row_number * Column_number)):
       
        if (i == 0):
            continue
        if i - Column_number * int(i/Column_number) == 0:
            origin = baseplate.place_element_relative("beam_splitter_" + str(i) ,
                                                optomech.circular_mirror, origin, angle,
                                                x_off = 0 ,
                                                z_off = 2 * layout.inch,
                                                y_off = 0 )#(2 * layout.inch))
        else:
            a = int(np.double(i) / Column_number)
            if a -  2 * int(a / 2) == 0:
                origin = baseplate.place_element_relative("beam_splitter_" + str(i) ,
                                                optomech.circular_mirror, origin, angle,
                                                x_off=0 ,
                                                y_off=-2 * layout.inch,
                                                z_off= 0 )#(2 * layout.inch))
            else:
                origin = baseplate.place_element_relative("beam_splitter_" + str(i) ,
                                                optomech.circular_mirror, origin, angle,
                                                x_off=0 ,
                                                y_off=2 * layout.inch,
                                                z_off= 0 )


    # grid_beam_splitter_along_beam(beam_obj=beam, beam_index=0b1, angle=layout.turn['right-up'], distance=15 * layout.inch, baseplate=baseplate)

    # grid_beam_splitter_along_beam(beam_obj=beam, beam_index=0b1, angle=layout.turn['up-right'], distance=15 * layout.inch, baseplate=baseplate, parity=-1)

if __name__ == "__main__":
    test_redstone()
    layout.redraw()