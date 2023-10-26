## Auto-Generated Optomech Library Documentation  
### example_component
  
    An example component class for reference on importing new components  
    creates a simple cube which mounts using a single bolt  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        side_length (float) : The side length of the cube  
    
### baseplate_mount
  
    Mount holes for attaching to an optical table  
    Uses 14_20 bolts with washers  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        bore_depth (float) : The depth for the counterbore of the mount hole  
    
### surface_adapter
  
    Surface adapter for post-mounted parts  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        mount_hole_dy (float) : The spacing between the two mount holes of the adapter  
        adapter_height (float) : The height of the suface adapter  
        outer_thickness (float) : The thickness of the walls around the bolt holes  
    
### skate_mount
  
    Skate mount for splitter cubes  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        cube_size (float) : The side length of the splitter cube  
        mount_hole_dy (float) : The spacing between the two mount holes of the adapter  
        cube_depth (float) : The depth of the recess for the cube  
        outer_thickness (float) : The thickness of the walls around the bolt holes  
        cube_tol (float) : The tolerance for size of the recess in the skate mount  
    
### slide_mount
  
    Slide mount adapter for post-mounted parts  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        slot_length (float) : The length of the slot used for mounting to the baseplate  
        drill_offset (float) : The distance to offset the drill hole along the slot  
        adapter_height (float) : The height of the suface adapter  
        post_thickness (float) : The thickness of the post that mounts to the element  
        outer_thickness (float) : The thickness of the walls around the bolt holes  
    
### mount_for_km100pm
  
    Adapter for mounting isomet AOMs to km100pm kinematic mount  
  
    Args:  
        mount_offset (float[3]) : The offset position of where the adapter mounts to the component  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        slot_length (float) : The length of the slots used for mounting to the km100pm  
        countersink (bool) : Whether to drill a countersink instead of a counterbore for the AOM mount holes  
        counter_depth (float) : The depth of the countersink/bores for the AOM mount holes  
        arm_thickness (float) : The thickness of the arm the mounts to the km100PM  
        arm_clearance (float) : The distance between the bottom of the adapter arm and the bottom of the km100pm  
        stage_thickness (float) : The thickness of the stage that mounts to the AOM  
        stage_length (float) : The length of the stage that mounts to the AOM  
    
### fiberport_holder
  
    Part for mounting an HCA3 fiberport coupler to the side of a baseplate  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
    
### pbs_on_skate_mount
  
    Beam-splitter cube  
  
    Args:  
        invert (bool) : Invert pick-off direction, false is left, true is right  
        cube_size (float) : The side length of the splitter cube  
        cube_part_num (string) : The Thorlabs part number of the splitter cube being used  
    
### rotation_stage_rsp05
  
    Rotation stage, model RSP05  
  
    Args:  
        invert (bool) : Whether the mount should be offset 90 degrees from the component  
        mount_hole_dy (float) : The spacing between the two mount holes of it's adapter  
        wave_plate_part_num (string) : The Thorlabs part number of the wave plate being used  
  
    Sub-Parts:  
        surface_adapter (adapter_args)  
    
### mirror_mount_k05s2
  
    Mirror mount, model K05S2  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        mirror (bool) : Whether to add a mirror component to the mount  
  
    Sub-Parts:  
        circular_mirror (mirror_args)  
    
### mirror_mount_k05s1
  
    Mirror mount, model K05S1  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        mirror (bool) : Whether to add a mirror component to the mount  
  
    Sub-Parts:  
        circular_mirror (mirror_args)  
    
### splitter_mount_b05g
  
    Splitter mount, model B05G  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        splitter (bool) : Whether to add a splitter plate component to the mount  
  
    Sub-Parts:  
        circular_splitter (mirror_args)  
    
### mirror_mount_c05g
  
    Mirror mount, model C05G  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        mirror (bool) : Whether to add a mirror component to the mount  
  
    Sub-Parts:  
        circular_mirror (mirror_args)  
    
### mirror_mount_km05
  
    Mirror mount, model KM05  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        mirror (bool) : Whether to add a mirror component to the mount  
        bolt_length (float) : The length of the bolt used for mounting  
  
    Sub-Parts:  
        circular_mirror (mirror_args)  
    
### fiberport_mount_km05
  
    Mirror mount, model KM05, adapted to use as fiberport mount  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
  
    Sub-Parts:  
        mirror_mount_km05 (mount_args)  
    
### km05_50mm_laser
  
    Mirror mount, model KM05, adapted to use as laser mount  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        tec_thickness (float) : The thickness of the TEC used  
  
    Sub-Parts:  
        mirror_mount_km05 (mount_args)  
        km05_tec_upper_plate (upper_plate_args)  
        km05_tec_lower_plate (lower_plate_args)  
    
### mirror_mount_mk05
  
    Mirror mount, model MK05  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
  
    Sub-Parts:  
        circular_mirror (mirror_args)  
    
### mount_mk05pm
  
    Mount, model MK05  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
    
### grating_mount_on_mk05pm
  
    Grating and Parallel Mirror Mounted on MK05PM  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        littrow_angle (float) : The angle of the grating and parallel mirror  
  
    Sub_Parts:  
        mount_mk05pm (mount_args)  
        square_grating (grating_args)  
        square_mirror (mirror_args)  
    
### lens_holder_l05g
  
    Lens Holder, Model L05G  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
  
    Sub-Parts:  
        circular_lens (lens_args)  
    
### pinhole_ida12
  
    Pinhole Iris, Model IDA12  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
  
    Sub-Parts:  
        slide_mount (adapter_args)  
    
### prism_mount_km100pm
  
    Kinematic Prism Mount, Model KM100PM  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
    
### isomet_1205c_on_km100pm
  
    Isomet 1205C AOM on KM100PM Mount  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        diffraction_angle (float) : The diffraction angle (in radians) of the AOM  
        forward_direction (integer) : The direction of diffraction on forward pass (1=right, -1=left)  
        backward_direction (integer) : The direction of diffraction on backward pass (1=right, -1=left)  
  
    Sub-Parts:  
        prism_mount_km100pm (mount_args)  
        mount_for_km100pm (adapter_args)  
    
### isolator_670
  
    Isolator Optimized for 670nm, Model IOT-5-670-VLP  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
  
    Sub-Parts:  
        surface_adapter (adapter_args)  
    
### isolator_405
  
    Isolator Optimized for 405nm, Model IOT-5-670-VLP  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
  
    Sub-Parts:  
        surface_adapter  
    
### square_grating
  
    Square Grating  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        thickness (float) : The thickness of the grating  
        width (float) : The width of the grating  
        height (float) : The height of the grating  
        part_number (string) : The part number of the grating being used  
    
### circular_splitter
  
    Circular Beam Splitter Plate  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        thickness (float) : The edge thickness of the plate  
        diameter (float) : The width of the plate  
        part_number (string) : The part number of the plate being used  
    
### circular_lens
  
    Circular Lens  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        focal_length (float) : The focal length of the lens  
        thickness (float) : The edge thickness of the lens  
        diameter (float) : The width of the lens  
        part_number (string) : The part number of the lens being used  
    
### circular_mirror
  
    Circular Mirror  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        thickness (float) : The thickness of the mirror  
        diameter (float) : The width of the mirror  
        part_number (string) : The part number of the mirror being used  
    
### square_mirror
  
    Square Mirror  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        thickness (float) : The thickness of the mirror  
        width (float) : The width of the mirror  
        height (float) : The height of the mirror  
        part_number (string) : The part number of the mirror being used  
    
### rb_cell
  
    Rubidium Cell Holder  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
    
### periscope
  
    Custom periscope mount  
  
    Args:  
        drill (bool) : Whether baseplate mounting for this part should be drilled  
        lower_dz (float) : Distance from the bottom of the mount to the center of the lower mirror  
        upper_dz (float) : Distance from the bottom of the mount to the center of the upper mirror  
        mirror_type (obj class) : Object class of mirrors to be used  
        table_mount (bool) : Whether the periscope is meant to be mounted directly to the optical table  
  
    Sub-Parts:  
        mirror_type x2  
    
