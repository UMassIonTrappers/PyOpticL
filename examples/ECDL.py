from PyOpticL import layout, optomech

layout.place_element_on_table("test", optomech.laser_mount_km100pm, 0, 0, 0)

## This code will generate the ECDL with cover. If you want to change anything to the cover or the ECDL design then it has to be #
# done in laser_mount_km100pm part of the optomech file 