from PyOpticL import layout, optomech
from datetime import datetime

inch = 25.4
mm = 1/inch

def doublepass_metric_f50(x=0, y=0, angle=0, mirror = optomech.mirror_mount_k05s2, x_split = False, thumbscrews=True):
    
    name = "doublepass"
    date_time = datetime.now().strftime("%d/%m/%Y")
    label = "" #name + " " +  date_time

    base_dx = 250
    base_dy = 150
    base_dz = 25
    gap = 2

    input_x = 175 # integer multiple of grid

    mount_holes = [(0,0),(0, 125*mm), (225*mm,0), (225*mm, 125*mm)]
    
    extra_mount_holes = []
    # extra_mount_holes = [(0, 62.5*mm),(132.5*mm,0),(275*mm,62.5*mm),(125*mm,125*mm)]
    
    baseplate = layout.baseplate(base_dx, base_dy, base_dz, x=x, y=y, angle=angle,
                                 gap=gap, mount_holes=mount_holes+extra_mount_holes,
                                 name=name, label=label, x_splits=[0*25]*x_split)
    
    beam = baseplate.add_beam_path(input_x, gap, layout.cardinal["up"])

    baseplate.place_element("Input Fiberport", optomech.fiberport_mount_hca3,
                                       x=input_x, y=gap, angle=layout.cardinal["up"])

    baseplate.place_element_along_beam("Input Mirror 1", optomech.circular_mirror, beam, 
                                       beam_index=0b1, distance=35, angle=layout.turn["up-right"],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    baseplate.place_element_along_beam("Input Mirror 2", optomech.circular_mirror, beam, 
                                       beam_index=0b1, distance=25, angle=layout.turn["right-up"],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    baseplate.place_element_along_beam("Half waveplate", optomech.waveplate, beam,
                                       beam_index=0b1, distance=55, angle=layout.cardinal["up"],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    baseplate.place_element_along_beam("Beam Splitter", optomech.cube_splitter, beam,
                                       beam_index=0b1, distance=28, angle=layout.cardinal["up"],
                                       mount_type=optomech.skate_mount)
    
    baseplate.place_element_along_beam("AOM", optomech.isomet_1205c_on_km100pm, beam,
                                       beam_index=0b11, distance=55, angle=layout.cardinal["left"],
                                       forward_direction=-1, backward_direction=1)
    
    lens = baseplate.place_element_along_beam("Lens f50mm AB coat", optomech.circular_lens, beam,
                                              beam_index=0b110, distance=50, angle=layout.cardinal["right"],
                                              focal_length=50, part_number="LA1213-AB", mount_type=optomech.lens_holder_l05g)
    
    baseplate.place_element_along_beam("Quarter waveplate", optomech.waveplate, beam,
                                       beam_index=0b110, distance=24, angle=layout.cardinal["left"],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    baseplate.place_element_along_beam("Iris", optomech.pinhole_ida12, beam,
                                       beam_index=0b111, distance=17.5, angle=layout.cardinal["right"],
                                       pre_refs=2, adapter_args=dict(drill_offset=-2))

    baseplate.place_element_relative("Retro Mirror", optomech.circular_mirror, lens,
                                       x_off=-50, angle=layout.cardinal["right"],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    
    baseplate.place_element_along_beam("Output Mirror 1", optomech.circular_mirror, beam,
                                       beam_index=0b11110, distance=30, angle=layout.turn['right-down'],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    baseplate.place_element_along_beam("Output Mirror 2", optomech.circular_mirror, beam,
                                       beam_index=0b11110, distance=40, angle=layout.turn["right-up"],
                                       mount_type=mirror, mount_args=dict(thumbscrews=thumbscrews))
    
    baseplate.place_element_along_beam("Half Waveplate Out", optomech.waveplate, beam,
                                       beam_index=0b11110, distance=110, angle=layout.cardinal["left"],
                                       mount_type=optomech.rotation_stage_rsp05)
    
    baseplate.place_element_along_beam("Iris Out", optomech.pinhole_ida12, beam,
                                       beam_index=0b11110, distance=40, angle=layout.cardinal["right"])
    
    baseplate.place_element_along_beam("Output Fiberport", optomech.fiberport_mount_hca3, beam, 
                                       beam_index=0b11110,x=gap-1,angle=layout.cardinal["right"])

    

if __name__ == "__main__":
    doublepass_metric_f50()
    layout.redraw()