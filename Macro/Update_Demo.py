from freecadOptics import layout, optomech

gap = layout.INCH/2
base_dx = 7*layout.INCH-gap
base_dy = 5*layout.INCH-gap
base_dz = layout.INCH

layout.create_baseplate(base_dx, base_dy, base_dz)

input_x = 40
input_y = 30
beam = layout.add_beam_path(input_x, input_y, layout.cardinal['right'])

"""
Add Optical Elements
"""

layout.place_element("Laser diode", optomech.km05_50mm_laser, input_x, input_y, layout.cardinal['right'], upper_plate_args=dict(thickness=layout.INCH/8), lower_plate_args=dict(width=2*layout.INCH, thickness=layout.INCH/8))

layout.place_element_along_beam("Grating", optomech.grating_mount_on_mk05pm, beam, 0b1, layout.cardinal['left'], 40, littrow_angle=45, mirror_args=dict(thickness=6))

layout.place_element_along_beam("Mirror 1", optomech.mirror_mount_km05, beam, 0b1, layout.turn['right-up'], x=base_dx-20, mirror_args=dict(thickness=10))
layout.place_element_along_beam("Mirror 2", optomech.mirror_mount_km05, beam, 0b1, layout.turn['up-left'], 40)

layout.place_element_along_beam("Lens", optomech.lens_holder_l05g, beam, 0b1, layout.cardinal['left'], 30, lens_args=dict(focal_length=50))

layout.place_element_along_beam("Optical Isolator", optomech.isolator_405, beam, 0b1, layout.cardinal['left'], 35, adapter_args=dict(mount_hole_dy=45))

layout.place_element_along_beam("Fiber Coupler", optomech.fiberport_mount_km05, beam, 0b1, layout.cardinal['right'], 55)

layout.redraw()