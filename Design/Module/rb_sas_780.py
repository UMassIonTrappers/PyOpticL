import numpy as np
from PyOpticL import layout, optomech

# baseplate constants
base_dx = 10 * layout.inch
base_dy = 4   * layout.inch 
base_dz = layout.inch
gap = layout.inch / 8

# x-y coordinates of mount holes (in inches)
mount_holes = [
    (0, 0),
    (0, base_dy / layout.inch - 1),
    (base_dx / layout.inch - 1, 0),
    (base_dx / layout.inch - 1, base_dy / layout.inch - 1 ),
]


# input beam coordinates
input_x = base_dx - 3.0 * layout.inch
input_y = gap
input_dir = layout.cardinal["up"]


# Begin baseplate design
def Rb_SAS(x=0, y=0, angle=0):

    # define and place baseplate object
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, z=0, angle=angle, gap=gap, mount_holes=mount_holes, optics_dz=layout.inch/2 + 1)

    # add beam
    beam = baseplate.add_beam_path(x=input_x, y=input_y, angle=input_dir, z=0, color=(1.0, 0.0, 0.0), width=0.1)

    # add input fiberport, defined at the same coordinates as beam
    baseplate.place_element("Input Fiberport", obj_class=optomech.fixed_mount_smr1, x=input_x, y=input_y+10, angle=input_dir)

    # add half waveplate
    baseplate.place_element_along_beam(
        "PBS Waveplate",
        optomech.waveplate,
        beam,
        beam_index=0b1,
        distance=30,
        angle=-90,
        mount_type=optomech.rotation_stage_rsp05,
    )

    # add PBS
    baseplate.place_element_along_beam(
        "PBS",
        optomech.cube_splitter,
        beam,
        beam_index=0b1,
        y=base_dy/2,
        angle=-90,
        mount_type=optomech.skate_mount,
    )

    # Rubidium Cell
    baseplate.place_element_along_beam(
        name="Rb gas cell",
        obj_class=optomech.rb_cell_vbc2,
        beam_obj=beam,
        beam_index=0b11,
        distance= 75/2+1*layout.inch,
        angle=layout.cardinal["right"],
        tube_diameter=19,
        tube_length=75,
    )

    # quarter waveplate
    baseplate.place_element_along_beam(
        name="quarter waveplate 1",
        obj_class=optomech.waveplate,
        beam_obj=beam,
        beam_index=0b11,
        distance=75/2+20,
        mount_type=optomech.rotation_stage_rsp05,
        angle=0,
    )

    baseplate.place_element_along_beam(
        name="ND filter",
        obj_class=optomech.waveplate,
        beam_obj=beam,
        beam_index=0b11,
        distance=19,
        mount_type=optomech.fixed_mount_smr05,
        angle=0,
        mount_args={"adapter":True}
    )

    # retroreflection mirror
    baseplate.place_element_along_beam(
        name="mirror 1",
        obj_class=optomech.circular_mirror,
        beam_obj=beam,
        beam_index=0b11,
        distance=16,
        #x=gap + 0.75 * layout.inch,
        angle=0,
        mount_type=optomech.mirror_mount_km05,
        mount_args=dict(thumbscrews=False),
    )

    # ND filter
    # ndfilter = baseplate.place_element_along_beam(
    #     "ND filter",
    #     optomech.circular_lens,
    #     beam,
    #     beam_index=0b11,
    #     distance=10,
    #     angle=180 - 10,
    #     mount_type=optomech.lens_holder_l05g,
    # )


    # readout photodiode
    baseplate.place_element_along_beam(
        name="Photodiode",
        obj_class=optomech.photodetector_pda10a2,
        beam_obj=beam,
        beam_index=0b110,
        angle=180,
        x=base_dx - gap - 1.5 * layout.inch,
        tube_args=dict(lens_tube_footprint=8)
    )


# this allows the file to be run as a macro or imported into other files
if __name__ == "__main__":
    Rb_SAS()
    layout.redraw()
