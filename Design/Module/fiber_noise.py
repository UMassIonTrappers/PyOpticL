from PyOpticL import layout, optomech
from datetime import datetime


# Fiber noise cancellation baseplate
# This baseplate sends light from an input fiberport through two steering mirrors,
# a waveplate, and a beam splitter. One branch is sent through the AOM and then
# to a noisy output fiberport. The other is sent to the next subsystem.
def fnc(x=0, y=0, angle=0, mirror=optomech.mirror_mount_km05, x_split=False, thumbscrews=True):

    # Adding name and date to keep track of updates
    name = "FNC"
    date_time = datetime.now().strftime("%m/%d/%Y")
    label = ""  # name + " " + date_time

    # Dimension of the baseplate
    base_dx = 15.5 * layout.inch
    base_dy = 5.5 * layout.inch
    base_dz = layout.inch
    gap = layout.inch / 8

    # Beam input location

    input_x = 13.5 * layout.inch

    mount_holes = []
    extra_mount_holes = []

    # Defining the baseplate
    baseplate = layout.baseplate(
        base_dx, base_dy, base_dz,
        x=x, y=y, angle=angle,
        gap=gap,
        mount_holes=mount_holes + extra_mount_holes,
        name=name, label=label
    )

    # Adding the beam to the baseplate
    beam = baseplate.add_beam_path(input_x, gap, layout.cardinal['up'])

    # Adding input fiberport to send the beam into the baseplate
    baseplate.place_element(
        "Input Fiberport", optomech.fiberport_mount_hca3,
        x=266.7 + 3 * layout.inch, y=2.6,
        angle=layout.cardinal['up']
    )

    # Adding two mirrors to give the beam enough degree of freedom
    baseplate.place_element_along_beam(
        "Input Mirror 1", optomech.circular_mirror, beam,
        beam_index=0b1, distance=18, angle=layout.turn['up-right'],
        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)
    )

    baseplate.place_element_along_beam(
        "Input Mirror 2", optomech.circular_mirror, beam,
        beam_index=0b1, distance=layout.inch, angle=layout.turn['right-up'],
        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)
    )

    # Adding a half waveplate to control the polarization
    baseplate.place_element_along_beam(
        "Half Waveplate", optomech.waveplate, beam,
        beam_index=0b1, distance=22, angle=layout.cardinal['up'],
        mount_type=optomech.rotation_stage_rsp05
    )

    # Adding beam splitter to divide the beam
    # One branch stays on the baseplate and another is routed to the next subsystem
    baseplate.place_element_along_beam(
        "Beam Splitter", optomech.cube_splitter, beam,
        beam_index=0b1, distance=27.5, angle=layout.cardinal['up'],
        mount_type=optomech.skate_mount
    )

    # Adding first lens before the AOM section
    lens = baseplate.place_element_along_beam(
        "Lens 1", optomech.circular_lens, beam,
        beam_index=0b11, distance=102.7, angle=layout.cardinal['right'],
        focal_length=100, part_number='LA1213-AB',
        mount_type=optomech.lens_holder_l05g
    )

    # Adding AOM
    aom = baseplate.place_element_relative(
        "AOM", optomech.isomet_1205c_on_km100pm, lens,
        x_off=-100, angle=layout.cardinal['left'],
        forward_direction=1, backward_direction=1, diffraction_angle=.7
    )

    # Adding second lens after the AOM
    baseplate.place_element_relative(
        "Lens 2", optomech.circular_lens, aom,
        x_off=-100, angle=layout.cardinal['left'],
        focal_length=100, part_number='LA1213-AB',
        mount_type=optomech.lens_holder_l05g
    )

    # Output branch
    baseplate.place_element_along_beam(
        "Output Mirror 1", optomech.d_mirror, beam,
        beam_index=0b111, distance=4 * layout.inch + 17,
        angle=45,
        mount_type=optomech.mirror_mount_km05dr,
        mount_args=dict(thumbscrews=thumbscrews), flip=True
    )

    baseplate.place_element_along_beam(
        "Output Mirror 2", optomech.circular_mirror, beam,
        beam_index=0b111, distance=1.9 * layout.inch, angle=225,
        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)
    )

    # Output fiberport goes to the fiber whos noise we want to cancel
    baseplate.place_element_along_beam(
        "Output Fiberport", optomech.fiberport_mount_hca3, beam,
        beam_index=0b111, distance=50.18,
        angle=layout.cardinal['right']
    )

    # Retroreflection branch
    baseplate.place_element_along_beam(
        "Retro Mirror 1", optomech.circular_mirror, beam,
        beam_index=0b110, distance=5.25 * layout.inch + 10, angle=-45,
        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)
    )

    baseplate.place_element_along_beam(
        "ND Filter", optomech.circular_lens, beam,
        beam_index=0b110, distance=0.5 * layout.inch + 12.5,
        angle=layout.cardinal['up'],
        mount_type=optomech.lens_holder_l05g
    )

    baseplate.place_element_along_beam(
        "Retro Mirror 2", optomech.circular_mirror, beam,
        beam_index=0b110, distance=0.6 * layout.inch + 7.5, angle=90,
        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)
    )

    # Photodetector branch
    baseplate.place_element_along_beam(
        "PD Mirror 1", optomech.d_mirror, beam,
        beam_index=0b1101, distance=4.4 * layout.inch + 7,
        angle=225,
        mount_type=optomech.mirror_mount_km05dr,
        mount_args=dict(thumbscrews=thumbscrews), flip=True
    )

    baseplate.place_element_along_beam(
        "PD Mirror 2", optomech.circular_mirror, beam,
        beam_index=0b1101, distance=1.2 * layout.inch, angle=135,
        mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews)
    )

    baseplate.place_element_along_beam(
        "Iris", optomech.pinhole_ida12, beam,
        beam_index=0b1101, distance=4.95 * layout.inch + 10,
        angle=layout.cardinal['left']
    )

    baseplate.place_element_along_beam(
        "Photodetector", optomech.photodetector_pda10a2, beam,
        beam_index=0b1101, distance=1.35 * layout.inch ,
        angle=layout.cardinal['right']
    )

    # baseplate.add_cover(dz=45)


if __name__ == "__main__":
    fnc()
    layout.redraw()