class ECDL:
    """
    ECDL device
    """

    type = "Part::FeaturePython"

    def __init__(
        self,
        obj,
        drill=True,
        slot_length=0,
        countersink=False,
        counter_depth=3,
        arm_thickness=8,
        arm_clearance=2,
        stage_thickness=6,
        stage_length=20,
        mat_thickness=10,
        littrow_angle=56.6,
    ):
        obj.Proxy = self
        # obj.addProperty("App::PropertyPlacement", "BasePlacement")
        ViewProvider(obj.ViewObject)

        obj.addProperty("App::PropertyBool", "Drill").Drill = drill
        obj.addProperty("App::PropertyLength", "SlotLength").SlotLength = slot_length
        obj.addProperty("App::PropertyBool", "Countersink").Countersink = countersink
        obj.addProperty("App::PropertyLength", "CounterDepth").CounterDepth = (
            counter_depth
        )
        obj.addProperty("App::PropertyLength", "ArmThickness").ArmThickness = (
            arm_thickness
        )
        obj.addProperty("App::PropertyLength", "ArmClearance").ArmClearance = (
            arm_clearance
        )
        obj.addProperty("App::PropertyLength", "StageThickness").StageThickness = (
            stage_thickness
        )
        obj.addProperty("App::PropertyLength", "StageLength").StageLength = stage_length
        obj.addProperty("App::PropertyLength", "MatThickness").MatThickness = (
            mat_thickness
        )
        obj.addProperty("App::PropertyAngle", "LittrowAngle").LittrowAngle = (
            littrow_angle
        )
        obj.addProperty("Part::PropertyPartShape", "DrillPart")

        obj.ViewObject.ShapeColor = adapter_color
        obj.setEditorMode("Placement", 2)

        dx = -5.334 + 2.032
        mount = _add_linked_object(
            obj,
            "Mount KM100PM",
            prism_mount_km100pm,
            pos_offset=(2.032 + 13.96 - 3.8, -25.91 + 16, -18.67),
        )
        _add_linked_object(
            obj, "Diode Adapter", diode_adapter_s05lm56, pos_offset=(0, 0, 0)
        )
        _add_linked_object(
            obj, "Lens Tube", lens_tube_sm05l05, pos_offset=(dx + 1.524 + 3.812, 0, 0)
        )
        _add_linked_object(
            obj, "Lens Adapter", lens_adapter_s05tm09, pos_offset=(dx + 1.524 + 5, 0, 0)
        )
        _add_linked_object(
            obj,
            "Lens",
            mounted_lens_c220tmda,
            pos_offset=(dx + 1.524 + 3.167 + 5, 0, 0),
        )

        _add_linked_object(
            obj,
            "Mount",
            fixed_mount_smr05,
            pos_offset=(2.032, 0, 0),
            rot_offset=(90, 0, 0),
            drill=False,
        )
        _add_linked_object(
            obj,
            "Wire Tube",
            wire_tube,
            pos_offset=(0, 0, -0.5 * inch),
            rot_offset=(0, 0, 0),
            drill=False,
        )
        _add_linked_object(
            obj,
            "Brewster_window",
            brewster_window,
            pos_offset=(0, 20, 1 * inch),
            rot_offset=(0, 0, 0),
            drill=False,
        )

        gap = 22
        lit_angle = radians(90 - obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap / sin(2 * beam_angle)
        ref_x = ref_len * cos(2 * beam_angle)
        dx = ref_x + 12.7 * cos(lit_angle) + (6 + 3.2) * sin(lit_angle)
        extra_x = 20 - dx
        grating_dx = -(6 * sin(lit_angle) + 12.7 / 2 * cos(lit_angle)) - extra_x
        mirror_dx = grating_dx - ref_x

        _add_linked_object(
            obj,
            "Grating",
            square_grating,
            pos_offset=(grating_dx + 47, -2 + 5, -2.7),
            rot_offset=(0, 0, 180 - obj.LittrowAngle.Value),
        )
        _add_linked_object(
            obj,
            "PZT",
            box,
            pos_offset=(grating_dx + 48.6, -7 + 5, -2.7),
            rot_offset=(0, 0, 180 - obj.LittrowAngle.Value),
        )
        _add_linked_object(
            obj,
            "Mirror",
            square_mirror,
            pos_offset=(mirror_dx + 36.5, gap - 3, -2.7),
            rot_offset=(0, 0, -obj.LittrowAngle.Value),
        )

        upper_plate = _add_linked_object(
            obj,
            "Upper Plate",
            km05_tec_upper_plate,
            pos_offset=(2.032 + 13.96 - 3.8 - 13.96, 0, -inch / 4 - 6.3),
            width=1.5 * inch,
            drill_obj=mount,
        )
        _add_linked_object(
            obj,
            "TEC",
            TEC,
            pos_offset=(grating_dx + 20, 0, -33.7),
            rot_offset=(90, 90, 90),
        )
        _add_linked_object(
            obj,
            "Lower Plate",
            km05_tec_lower_plate,
            pos_offset=(2.032 + 13.96 - 3.8 - 13.96, 0, 3.25 * inch),
            width=3 * inch,
        )
        _add_linked_object(
            obj,
            "Box",
            laser_box,
            pos_offset=(0, 0, 0 * inch),
            rot_offset=(0, 0, 0),
            mat_thickness=mat_thickness,
        )

    def execute(self, obj):
        dx = obj.ArmThickness.Value
        dy = 45
        dz = 17
        stage_dx = obj.StageLength.Value
        stage_dz = obj.StageThickness.Value

        part = _custom_box(
            dx=dx,
            dy=dy,
            dz=dz - obj.ArmClearance.Value,
            x=0,
            y=4,
            z=obj.ArmClearance.Value,
        )
        part = part.fuse(
            _custom_box(
                dx=stage_dx,
                dy=dy,
                dz=dz - obj.ArmClearance.Value,
                x=0,
                y=4,
                z=dz,
                dir=(1, 0, -1),
            )
        )
        for ddy in [15.2, 38.1]:
            part = part.cut(
                _custom_box(
                    dx=stage_dx + dx,
                    dy=obj.SlotLength.Value + bolt_4_40["clear_dia"],
                    dz=bolt_4_40["clear_dia"],
                    x=stage_dx,
                    y=25.4 - ddy + 2.5,
                    z=6.4,
                    fillet=bolt_4_40["clear_dia"] / 2,
                    dir=(-1, 0, 0),
                )
            )
            part = part.cut(
                _custom_box(
                    dx=stage_dx + dx - 5 - 4,
                    dy=obj.SlotLength.Value + bolt_4_40["head_dia"],
                    dz=bolt_4_40["head_dia"],
                    x=stage_dx,
                    y=25.4 - ddy + 2.5,
                    z=6.4,
                    fillet=bolt_4_40["head_dia"] / 2,
                    dir=(-1, 0, 0),
                )
            )

        extra_y = 0
        gap = 22
        lit_angle = radians(90 - obj.LittrowAngle.Value)
        beam_angle = radians(obj.LittrowAngle.Value)
        ref_len = gap / sin(2 * beam_angle)
        ref_x = ref_len * cos(2 * beam_angle)
        dx2 = ref_x + 9.7 * cos(lit_angle) + (6 + 3.2) * sin(lit_angle)
        extra_x = 18 - dx2
        dy2 = gap + 9.7 * sin(lit_angle) + (6 + 3.2) * cos(lit_angle)
        dz2 = inch / 2
        cut_x = 18.7 * cos(lit_angle)

        part = part.fuse(
            _custom_box(
                dx=stage_dx + dx / 2,
                dy=dy,
                dz=stage_dz + 12.7,
                x=-dx / 2,
                y=4,
                z=dz + 12.7,
                dir=(1, 0, -1),
            )
        )

        part.translate(App.Vector(dx / 2, 25.4 - 15.2 + obj.SlotLength.Value / 2, -6.4))
        part.translate(App.Vector(2.032 + 13.96 - 3.8, -25.91 + 16, -18.67))
        part = part.fuse(part)

        temp = _custom_box(
            dx=ref_len * cos(beam_angle) + 12.2,
            dy=dy / sin(lit_angle) + 15,
            dz=dz,
            x=-cut_x + 9,
            y=-(dx - cut_x) * cos(lit_angle) - 15,
            z=-6 - 3.07,
            dir=(-1, 1, 1),
        )
        temp.rotate(
            App.Vector(-cut_x, 0, 0), App.Vector(0, 0, 1), -obj.LittrowAngle.Value
        )
        temp.translate(
            App.Vector(
                -extra_x + 36, -20.7 / 2 * sin(lit_angle) - 6 * cos(lit_angle), 0.2
            )
        )

        part = part.cut(temp)
        part.Placement = obj.Placement
        obj.Shape = part

        # part = _bounding_box(obj, 3, 4, z_tol=True, min_offset=(0, 0, 0.668))
        # part.Placement = obj.Placement
        obj.DrillPart = part
