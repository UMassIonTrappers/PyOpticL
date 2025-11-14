baseplate = layout.baseplate(...)
    # add beam
beam = baseplate.add_beam_path(...)
# add input fiberport, defined at the same coordinates as beam
baseplate.place_element("Input Fiberport", optomech.fiberport_mount_hca3, ...)
# add splitter component along beam, 40 mm from beam input
baseplate.place_element_along_beam("Beam Splitter Cube", optomech.cube_splitter, beam,
                                    beam_index=0b1, distance=40, ...)
# add waveplate along the transmitted beam, 35 mm from the splitter cube, mounted in a rotation stage
baseplate.place_element_along_beam("Rotation Stage", optomech.waveplate, beam,
                                    beam_index=0b10, distance=25, ...)
# add mirror along the reflected beam, 1 inch from the splitter cube, mounted in a polaris mount
baseplate.place_element_along_beam("Mirror", optomech.circular_mirror, beam,
                                    beam_index=0b11, distance=layout.inch, ...)
# add output fiberport along the beam, defined by settings it's x position to the edge of the baseplate
baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_mount_hca3, beam,
                                    beam_index=0b11, x=base_dx-gap, ...)

baseplate = Component(
    label="Baseplate Layout",
    definition=optomech.baseplate(
        dimensions=(dim(100, "mm"), dim(100, "mm"), dim(1, "in"))
    ))

beam_path = baseplate.add(Beam_Path(
    label="Beam Path",
    position=(dim(10, "mm"), dim(50, "mm"), dim(0, "mm")),
    rotation=(0, 0, 0),
    waist=dim(2, "mm"),
    wavelength=350,
))

baseplate.add(Component(
    label="Input Fiberport",
    definition=optomech.fiberport_mount_hca3(),
    position=(dim(10, "mm"), dim(50, "mm"), dim(0, "mm")),
    rotation=(0, 0, 0),
))

beam_path.add(Component(
    label="Beam Splitter Cube",
    definition=optomech.cube_splitter(),
    rotation=(0, 0, 0),
), beam_index=0b1, distance=dim(40, "mm"))

beam_path.add(Component(
    label="Rotation Stage",
    definition=optomech.waveplate(),
    rotation=(0, 0, 0),
), beam_index=0b10, distance=dim(25, "mm"))

beam_path.add(Component(
    label="Mirror",
    definition=optomech.circular_mirror(),
    rotation=(0, 0, 0),
), beam_index=0b11, distance=dim(1, "in"))

beam_path.add(Component(
    label="Output Fiberport",
    definition=optomech.fiberport_mount_hca3(),
    rotation=(0, 0, 0),
), beam_index=0b11, x=baseplate.dimensions[0])