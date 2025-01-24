from PyOpticL import layout, optomech

# baseplate constants - Dimension of the baseplate
base_dx = 3*layout.inch
base_dy = 3*layout.inch
base_dz = layout.inch
gap = layout.inch/8

#Adding the mount holes to bolt the baseplate to the optical table
mount_holes = [(0, 0), (0, 2), (2, 0), (2, 2)]

def telescope(x=0, y=0, angle=0):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes)
    
    # Adding the beam to the baseplate
    beam = baseplate.add_beam_path(x=0, y=1.5*layout.inch, angle=layout.cardinal['right'])

    offset = (2*layout.inch - 45)/2. + 0.5*layout.inch

    # We need to lens to make telescope. Make sure you are using the right distance.  
    lens_1 = baseplate.place_element_along_beam("Lens 1", optomech.circular_lens, beam,
                                       beam_index=0b1, distance=offset, angle=180,
                                       mount_type=optomech.lens_holder_l05g)
    
    lens_2 = baseplate.place_element_along_beam("Lens 1", optomech.circular_lens, beam,
                                       beam_index=0b1, distance=45.0, angle=0,
                                       mount_type=optomech.lens_holder_l05g)
    
if __name__ == "__main__":
    telescope()
    layout.redraw()