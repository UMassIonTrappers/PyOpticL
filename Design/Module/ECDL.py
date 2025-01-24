from PyOpticL import layout, optomech

def ECDL(x = 0,y = 0, angle = 0):
    layout.place_element_on_table("ecdl",  optomech.ECDL, x = 30 + x, y = 0 + y, angle= angle)#, x_ = 0, y_=0,z_=0)

## This code will generate the ECDL with cover. If you want to change anything to the cover or the ECDL design then it has to be #
# done in laser_mount_km100pm part of the optomech file 

if __name__ == "__main__":
    ECDL()
    layout.redraw()