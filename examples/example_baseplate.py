from PyOptic import layout, optomech

# baseplate constants
base_dx = 4*layout.inch
base_dy = 4*layout.inch
base_dz = layout.inch
gap = layout.inch/8

# x-y coordinates of mount holes (in inches)
mount_holes = [(0, 0), (0, 3), (3, 0), (3, 3)]

# y coordinate of beam input
input_y = 1.5*layout.inch

# function so baseplate can be added to other layouts
def example_baseplate(x=0, y=0, angle=0):

    # define and place baseplate object
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes)

    # add beam
    beam = baseplate.add_beam_path(x=gap, y=input_y, angle=layout.cardinal['right'])

    # add input fiberport, defined at the same coordinates as beam
    baseplate.place_element("Input Fiberport", optomech.fiberport_holder,
                            x=gap, y=input_y, angle=layout.cardinal['right'])

    # add splitter component along beam, 40 mm from beam input
    baseplate.place_element_along_beam("Beam Splitter Cube", optomech.pbs_on_skate_mount, beam,
                                       beam_index=0b1, distance=40, angle=layout.cardinal['right'])

    # add rotation stage along the transmitted beam, 30 mm from the splitter cube
    baseplate.place_element_along_beam("Rotation Stage", optomech.rotation_stage_rsp05, beam,
                                       beam_index=0b10, distance=30, angle=layout.cardinal['right'])

    # add mirror along the reflected beam, 1 inch from the splitter cube
    baseplate.place_element_along_beam("Mirror", optomech.mirror_mount_k05s2, beam,
                                       beam_index=0b11, distance=layout.inch, angle=layout.turn['up-right'])

    # add output fiberport along the beam, defined by settings it's x position to the edge of the baseplate
    baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_holder, beam,
                                       beam_index=0b11, x=base_dx-gap, angle=layout.cardinal['left'])

# this allows the file to be run as a macro or imported into other files
if __name__ == "__main__":
    example_baseplate()
    layout.redraw()