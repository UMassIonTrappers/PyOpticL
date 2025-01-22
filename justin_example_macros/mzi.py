from PyOpticL import layout, optomech

# define baseplate constants, calculate parameters, etc.

# define the baseplate as a function so it can be imported into other files
def mzi_baseplate(x=0, y=0, angle=0):
    baseplate = layout.baseplate(4 * layout.inch, 4 * layout.inch, layout.inch,
                                 x=x, y=y, angle=angle)

    beam = baseplate.add_beam_path(x = 20, y = 20, angle = layout.cardinal['right'])

    baseplate.place_element_along_beam("PBS1", optomech.cube_splitter, beam, beam_index=0b1, distance=10, angle=layout.cardinal['right'])

    baseplate.place_element_along_beam("mirror1", optomech.mirror_mount_k05s1, beam, beam_index=0b10, distance = 40, angle = layout.turn['right-up'], optional=false)
    baseplate.place_element_along_beam("mirror2", optomech.mirror_mount_k05s1, beam, beam_index=0b11, distance = 40, angle = layout.turn['up-right'])

    
    # define baseplate and beam
    # add components

# draw the baseplate if the file is run as a macro
if __name__ == "__main__":
    mzi_baseplate()
    layout.redraw()


