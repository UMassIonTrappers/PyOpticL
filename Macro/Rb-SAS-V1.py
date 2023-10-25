# Ryland Yurow 10/20/23

from freecadOptics import layout, optomech
from datetime import datetime

INCH = layout.INCH
grid_offset = 0.4
base_x = 5
base_y = 4.8
# in inches

name = "Rb SAS - Simple"
date_time = datetime.now().strftime("%m/%d/%Y")
label = name + " " + date_time

baseplate = layout.create_baseplate(((base_x)+(2*grid_offset))*INCH, ((base_y)+(2*grid_offset))*INCH, 1*INCH, x=(-grid_offset*INCH), y=(-grid_offset*INCH), name=name, label=label)
# Initializing the baseplate with negative coordinates allows the first grid hole to occur at the origin

#mirror = optomech.mirror_mount_km05
#fiberport = optomech.fiberport_holder
#splitter = optomech.splitter_mount_c05g
#fiberport = optomech.fiberport_holder
#mirror2 = optomech.mirror_mount_c05g

beam_422 = layout.add_beam_path(4.5*INCH, -1*INCH, 90)
mirror_mounts = optomech.mirror_mount_km05
layout.place_element_along_beam("422in-alignment-mirror1", mirror_mounts, beam_422, 0b1, layout.turn['up-right'], 1.5*INCH)
layout.place_element_along_beam("422in-alignment-mirror2", mirror_mounts, beam_422, 0b1, layout.turn['right-up'], 1*INCH)

















'''
layout.place_element_along_beam("461in-alignment-mirror1", mirror_mounts, beam_461, 0b1, layout.turn['up-right'], 1.5*INCH)
layout.place_element_along_beam("461in-alignment-mirror2", mirror_mounts, beam_461, 0b1, layout.turn['right-up'], 1*INCH)

beam_405 = layout.add_beam_path(5.5*INCH, 3*INCH, 180)
layout.place_element_along_beam("405in-alignment-mirror1", mirror_mounts, beam_405, 0b1, layout.turn['left-down'], 1*INCH)
layout.place_element_along_beam("405in-alignment-mirror2", mirror_mounts, beam_405, 0b1, layout.turn['down-left'], 1*INCH)
layout.place_element_along_beam("dichroic-mirror", optomech.splitter_mount_c05g, beam_405, 0b1, layout.turn['left-up'], 2.5*INCH)
layout.place_element_along_beam("out-alignment-mirror1", mirror_mounts, beam_405, 0b11, layout.turn['up-left'], 1*INCH)
layout.place_element_along_beam("out-alignment-mirror2", mirror_mounts, beam_405, 0b11, layout.turn['left-up'], 1*INCH)
layout.place_element("fiberport-out", optomech.fiberport_holder, 1*INCH, (base_y+grid_offset)*INCH, layout.cardinal['down'])

#layout.place_element("461in-fiberport", optomech.fiberport_holder, 1*INCH, (-grid_offset*INCH), layout.cardinal['up'])
#layout.place_element("405in-fiberport", optomech.fiberport_holder, (base_x+grid_offset)*INCH, (3*INCH), layout.cardinal['left'])

# layout.place_element("461in-fiberport-alt", optomech.mirror_mount_km05, 1*INCH, (-grid_offset*INCH), layout.cardinal['up'])
#layout.place_element_along_beam("out-fiberport-alt", optomech.mirror_mount_km05, beam_405, 0b11, y=(base_y-0.3)*INCH, angle=layout.cardinal['down'])
#layout.place_element("405in-fiberport-alt", optomech.mirror_mount_km05, (base_x+grid_offset)*INCH, 3*INCH, layout.cardinal['left'])
'''

#for i in [[0, 0], [base_x, 0], [0, 4], [base_x, 4]]:
    #layout.place_element("mounthole%s"%(str(i)), optomech.baseplate_mount, (i[0])*INCH, (i[1])*INCH, 0)

#layout.redraw()