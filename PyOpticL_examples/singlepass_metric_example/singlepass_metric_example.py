from PyOpticL import layout, optomech

inch = 25.4
mm = 1/inch

# Unit in millimeter
# baseplate mounting to using a 25mm grid with M6 bolts
base_dx = 200
base_dy = 200
base_dz = 25
gap = 2

mount_holes = [(0,0), (0,175*mm), (175*mm,0), (175*mm,175*mm)]

# y coordinate of beam input
input_y = 1.5 * 25

def singlepass_metric_baseplate(x=0, y=0, angle=0):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle, gap=gap, mount_holes=mount_holes, metric=True)

    beam = baseplate.add_beam_path(x=gap, y=input_y, angle=layout.cardinal['right'])

    baseplate.place_element("Input Fiberport", optomech.fiberport_mount_hca3, x=gap, y=input_y, angle=layout.cardinal["right"])

    baseplate.place_element_along_beam("Beam Splitter Cube", optomech.cube_splitter, beam, beam_index=0b1, distance=40, angle=layout.cardinal['right'], mount_type=optomech.skate_mount)

    baseplate.place_element_along_beam("Rotation Stage", optomech.waveplate, beam, beam_index=0b10, distance=25, angle=layout.cardinal['right'], mount_type=optomech.rotation_stage_rsp05)

    baseplate.place_element_along_beam("Mirror", optomech.circular_mirror, beam, beam_index=0b11, distance=25, angle=layout.turn['up-right'], mount_type=optomech.mirror_mount_k05s1)

    baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_mount_hca3, beam,
                                       beam_index=0b11, x=base_dx-gap, angle=layout.cardinal['left'])


if __name__ == "__main__":
    singlepass_metric_baseplate()
    layout.redraw()