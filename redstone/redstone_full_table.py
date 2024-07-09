from datetime import datetime

import numpy as np

from PyOpticL import layout, optomech

name = "OQC_grid_optics"  ##optical quantum computer
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " + date_time


# def grid_beam_splitter_along_beam(
#     beam_obj,
#     beam_index,
#     angle,
#     distance,
#     baseplate,
#     parity=1,
#     Row_numnber=6,
#     Column_number=6,
# ):
#     origin = baseplate.place_element_along_beam(
#         "beam_splitter_origin",
#         optomech.circular_mirror,
#         beam_obj,
#         beam_index,
#         angle,
#         distance,
#     )

#     for i in range(Row_numnber):
#         for j in range(Column_number):
#             if i == j == 0:
#                 continue
#             # baseplate.place_element_relative("beam_splitter_" + str(i) + str(j),
#             #                                  optomech.circular_mirror, origin, angle,
#             #                                  x_off=(-1 * parity *
#             #                                         np.sin(np.radians(angle)) * (i) * 2 * layout.inch),
#             #                                  y_off=(parity * np.cos(np.radians(angle))
#             #                                                         * (i) * 2 * layout.inch),
#             #                                  z_off=(2 * layout.inch * j))
#             baseplate.place_element_relative(
#                 "beam_splitter_" + str(i) + str(j),
#                 optomech.circular_mirror,
#                 origin,
#                 angle,
#                 x_off=(
#                     -1
#                     * parity
#                     * np.sign(np.sin(np.radians(angle)))
#                     * (i)
#                     * 2
#                     * layout.inch
#                 ),
#                 y_off=(
#                     parity * np.sign(np.cos(np.radians(angle))) * (i) * 2 * layout.inch
#                 ),
#                 z_off=(2 * layout.inch * j),
#             )
#             print(angle, np.sin(np.radians(angle)), np.cos(np.radians(angle)))
#             print(-1 * parity * np.sin(np.radians(angle)) * (i + 1) * 2 * layout.inch)
#             print(parity * np.cos(np.radians(angle) * (i + 1) * 2 * layout.inch))


def grid_along_beam_new(
    name,
    grid_obj,
    beam_obj,
    beam_index,
    obj_angle,
    beam_angle,
    grid_angle,
    distance,
    baseplate,
    parity=1,
    optional=False,
    Row_numnber=6,
    Column_number=6,
):
    origin = baseplate.place_element_along_beam(
        name + "_origin", grid_obj, beam_obj, beam_index, obj_angle, distance=distance, optional=optional
    )

    for i in range(Row_numnber):
        for j in range(Column_number):
            if i == j == 0:
                continue
            baseplate.place_element_relative(
                name + "_" + str(i) + str(j),
                grid_obj,
                origin,
                obj_angle,
                x_off=(
                    -1
                    * parity
                    * np.sin(np.radians(grid_angle))
                    * (i)
                    * 2
                    * layout.inch
                    / np.abs(np.cos(np.radians(beam_angle - grid_angle)))
                ),
                y_off=(
                    parity
                    * np.cos((np.radians(grid_angle)))
                    * (i)
                    * 2
                    * layout.inch
                    / np.abs(np.cos(np.radians(beam_angle - grid_angle)))
                ),
                z_off=(2 * layout.inch * j),
            )
            # print(angle, np.sin(np.radians(angle)), np.cos(np.radians(angle)))
            # print(-1 * parity * np.sin(np.radians(angle)) * (i + 1) * 2 * layout.inch)
            # print(parity * np.cos(np.radians(angle) * (i + 1) * 2 * layout.inch))


# def test_redstone():
#     baseplate = layout.baseplate(36 * layout.inch, 36 * layout.inch, 1 * layout.inch)

#     beam = baseplate.add_beam_path(
#         25 * layout.inch, 50 * layout.inch, layout.cardinal["left"] + 45
#     )

#     grid_beam_splitter_along_beam(
#         beam_obj=beam,
#         beam_index=0b1,
#         angle=layout.turn["right-up"],
#         distance=15 * layout.inch,
#         baseplate=baseplate,
#     )

#     grid_along_beam(
#         "beam_splitter",
#         optomech.cube_splitter,
#         beam,
#         0b1,
#         layout.cardinal["right"],
#         layout.turn["up-right"],
#         18 * layout.inch,
#         baseplate=baseplate,
#         parity=-1,
#     )

#     grid_along_beam(
#         "mirror1",
#         optomech.circular_mirror,
#         beam,
#         0b10,
#         layout.turn["up-right"],
#         layout.turn["up-right"],
#         18 * layout.inch,
#         baseplate=baseplate,
#         parity=-1,
#     )

#     grid_along_beam(
#         "mirror2",
#         optomech.circular_mirror,
#         beam,
#         0b11,
#         layout.turn["right-down"],
#         layout.turn["right-down"],
#         18 * layout.inch,
#         baseplate=baseplate,
#         parity=1,
#     )


def full_table():
    baseplate = layout.baseplate(136 * layout.inch, 136 * layout.inch, 1 * layout.inch)

    beam = baseplate.add_beam_path(
        120 * layout.inch, 100 * layout.inch, layout.cardinal["sw"]
    )

    # baseplate.place_element_along_beam(
    #     "mirror1",
    #     optomech.lens_holder_l05g,
    #     beam,
    #     0b1,
    #     layout.cardinal["sw"],
    #     2 * layout.inch,
    # )
    #
    # baseplate.place_element_along_beam(
    #     "mirror2",
    #     optomech.lens_holder_l05g,
    #     beam,
    #     0b1,
    #     layout.cardinal["sw"],
    #     2 * layout.inch,
    # )

    grid_along_beam_new("waveplate1",
                        optomech.rotation_stage_rsp05,
                        beam,
                        0b1,
                        layout.cardinal['ne'],
                        layout.cardinal['sw'],
                        layout.cardinal['ne'],
                        10 * layout.inch,
                        baseplate,
                        parity=1,
                        optional=True
                        )

    grid_along_beam_new("beamsplitter1",
                        optomech.cube_splitter,
                        beam,
                        0b1,
                        layout.cardinal['nw'],
                        layout.cardinal['sw'],
                        layout.cardinal['up'],
                        20 * layout.inch,
                        baseplate,
                        parity=1,
                        )

    grid_along_beam_new("mirror2",
                        optomech.square_mirror,
                        beam,
                        0b101,
                        layout.cardinal['right'],
                        layout.cardinal['nw'],
                        layout.cardinal['right'],
                        24 * layout.inch,
                        baseplate,
                        parity=-1,
                        )

    grid_along_beam_new("mirror1",
                        optomech.square_mirror,
                        beam,
                        0b100,
                        layout.cardinal['right'],
                        layout.cardinal['sw'],
                        layout.cardinal['right'],
                        24 * layout.inch,
                        baseplate,
                        parity=1,
                        )

    # grid_along_beam(
    #     "waveplate1",
    #     optomech.rotation_stage_rsp05,
    #     beam,
    #     0b1,
    #     layout.cardinal["right"] + 45,
    #     layout.cardinal["right"] + 45,
    #     10 * layout.inch,
    #     baseplate=baseplate,
    #     parity=1,
    # )
    #
    # grid_along_beam(
    #     "beamsplitter1",
    #     optomech.cube_splitter,
    #     beam,
    #     0b1,
    #     layout.cardinal["right"] + 135,
    #     layout.cardinal["down"],
    #     10 * layout.inch,
    #     baseplate=baseplate,
    #     parity=1,
    # )


if __name__ == "__main__":
    full_table()
    layout.redraw()
