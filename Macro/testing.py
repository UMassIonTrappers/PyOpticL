from freecadOptics import layout, optomech

base_dx = 5*layout.inch
base_dy = 5*layout.inch
base_dz = layout.inch
gap = layout.inch/8

def example_baseplate(x, y):

    baseplate = layout.baseplate(base_dx, base_dy, base_dz, gap=gap, x=x, y=y)

    beam = baseplate.add_beam_path(0, 50, layout.cardinal['right'])

    baseplate.place_element_along_beam("Rotation Stage", optomech.rotation_stage_rsp05, beam, 0b1, layout.cardinal['right'], 30)
    baseplate.place_element_along_beam("Splitter", optomech.splitter_mount_b05g, beam, 0b1, layout.turn['right-up'], 30)

if __name__ == "__main__":
    example_baseplate(0, 0)
    layout.redraw()