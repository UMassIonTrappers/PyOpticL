from freecadOptics import layout, optomech

layout.create_baseplate(200, 100, layout.INCH)

beam = layout.add_beam_path(0, 30, 0)
layout.add_beam_path(0, 33, 0)
layout.add_beam_path(0, 27, 0)
layout.place_element_along_beam("Lens1_F50", optomech.lens_holder_l05g, beam, 0b1, layout.cardinal['right'], 50, foc_len=50)
layout.place_element_along_beam("Lens2_F50", optomech.lens_holder_l05g, beam, 0b1, layout.cardinal['left'], 100, foc_len=50)

beam2 = layout.add_beam_path(0, 70, 0)
layout.add_beam_path(0, 73, 0)
layout.add_beam_path(0, 67, 0)
layout.place_element_along_beam("Lens3_F100", optomech.lens_holder_l05g, beam2, 0b1, layout.cardinal['right'], 25, foc_len=100)
layout.place_element_along_beam("Lens4_F25", optomech.lens_holder_l05g, beam2, 0b1, layout.cardinal['left'], 125, foc_len=25)

layout.redraw()