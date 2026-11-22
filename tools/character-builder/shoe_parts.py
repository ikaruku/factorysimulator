"""
Modular `ShoesMesh` (Sepatu) slot builders for Male & Female Abeto characters:
- `build_shoes_high_top_sneakers()`: Default Male chunky dark high-top skate sneakers (#1E2228)
  with flat dark sole (#171B20), padded ankle collar, tall tongue, and twin white stripes.
- `build_shoes_white_strap_sneakers()`: Default Female chunky off-white high-top strap sneakers
  matching the 4 female reference views (Back, Front, Left, Right):
  * Thick dark charcoal platform sole (#1E2228) grounded flat at z = 0
  * Rounded off-white shoe upper (#E2E6DE)
  * Wide sage-grey velcro mid-foot strap (#C2CEC6) across the front instep
  * Chunky folded off-white ankle collar cuff (#DCE0D8) with rear heel seam
  * Prominent tall rounded off-white tongue (#E2E6DE) rising in front of the ankle cuff.
"""

import math
import bpy
from mesh_utils import join_parts_into_slot_mesh, make_loft_from_rings, make_toon_source_material


def build_shoes_high_top_sneakers():
    """Builds the default Male chunky dark high-top sneakers as `ShoesMesh`."""
    mat_shoe = make_toon_source_material("MatSneakerDark", 0x1E2228)
    mat_sole = make_toon_source_material("MatSneakerSole", 0x171B20)
    mat_white = make_toon_source_material("MatSneakerWhite", 0xE2E6DE)
    parts = []

    for side in (-1.0, 1.0):
        sx = side * 0.084

        sole_stations = [
            (0.000, 0.056, 0.118, 0.042),
            (0.032, 0.058, 0.120, 0.042),
            (0.036, 0.052, 0.112, 0.042),
        ]
        upper_stations = [
            (0.032, 0.055, 0.116, 0.042),
            (0.062, 0.056, 0.118, 0.042),
            (0.092, 0.050, 0.102, 0.036),
            (0.108, 0.036, 0.068, 0.018),
        ]
        n_sh_seg = 24

        for part_name, st_list, p_mat, c_start, c_end in (
            (f"SneakerSole_{'L' if side < 0 else 'R'}", sole_stations, mat_sole, True, True),
            (f"SneakerUpper_{'L' if side < 0 else 'R'}", upper_stations, mat_shoe, False, True),
        ):
            sh_rings = []
            for z, rx, ry, cy in st_list:
                ring = []
                for s in range(n_sh_seg):
                    ang = (2.0 * math.pi * s) / n_sh_seg
                    ca, sa = math.cos(ang), math.sin(ang)
                    bx = math.copysign(abs(ca) ** 0.72, ca) * rx
                    by = cy + math.copysign(abs(sa) ** 0.75, sa) * ry
                    ring.append((sx + bx, by, z))
                sh_rings.append(ring)
            parts.append(make_loft_from_rings(part_name, sh_rings, p_mat, c_start, c_end))

        collar_stations = [
            (0.090, 0.052, 0.060, 0.002),
            (0.128, 0.058, 0.066, 0.006),
            (0.168, 0.056, 0.064, 0.010),
            (0.174, 0.045, 0.050, 0.010),
        ]
        collar_rings = []
        for z, crx, cry, cy_shift in collar_stations:
            cring = []
            for s in range(18):
                ang = (2.0 * math.pi * s) / 18
                ca, sa = math.cos(ang), math.sin(ang)
                z_dip = -0.010 * max(0.0, -sa) if z > 0.14 else 0.0
                cring.append((sx + ca * crx, cy_shift + sa * cry, z + z_dip))
            collar_rings.append(cring)
        parts.append(
            make_loft_from_rings(
                f"SneakerCollar_{'L' if side < 0 else 'R'}",
                collar_rings,
                mat_shoe,
                cap_start=True,
                cap_end=True,
            )
        )

        bpy.ops.mesh.primitive_cube_add(size=0.090, location=(0.0, 0.0, 0.0))
        tongue = bpy.context.active_object
        tongue.name = f"SneakerTongue_{'L' if side < 0 else 'R'}"
        sub_t = tongue.modifiers.new("Subsurf", "SUBSURF")
        sub_t.levels = 2
        sub_t.render_levels = 2
        bpy.ops.object.modifier_apply(modifier="Subsurf")
        tongue.scale = (0.80, 0.44, 1.16)
        tongue.rotation_euler = (-0.22, 0.0, 0.0)
        tongue.location = (sx, 0.060, 0.134)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        tongue.data.materials.append(mat_shoe)
        tongue.select_set(False)
        parts.append(tongue)

        for idx_s, sy in enumerate((0.036, 0.068)):
            bpy.ops.mesh.primitive_cube_add(size=0.016, location=(0.0, 0.0, 0.0))
            stripe = bpy.context.active_object
            stripe.name = f"SneakerSideStripe_{'L' if side < 0 else 'R'}_{idx_s}"
            stripe.scale = (0.55, 0.82, 2.35)
            stripe.rotation_euler = (-0.20, 0.0, 0.0)
            stripe.location = (sx + side * 0.054, sy, 0.064)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            stripe.data.materials.append(mat_white)
            stripe.select_set(False)
            parts.append(stripe)

        for idx_f, (fy, fz) in enumerate(((0.100, 0.082), (0.122, 0.068))):
            bpy.ops.mesh.primitive_cube_add(size=0.015, location=(sx + side * 0.008, fy, fz))
            bar = bpy.context.active_object
            bar.name = f"SneakerFrontBar_{'L' if side < 0 else 'R'}_{idx_f}"
            bar.scale = (1.75, 0.45, 0.52)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bar.data.materials.append(mat_white)
            bar.select_set(False)
            parts.append(bar)

    return join_parts_into_slot_mesh(parts, "ShoesMesh")


def build_shoes_white_strap_sneakers():
    """
    Builds the default Female chunky off-white high-top velcro-strap sneakers matching
    Images 1 (Back), 2 (Front), 3 (Left), and 4 (Right) as `ShoesMesh`.
    """
    mat_upper = make_toon_source_material("MatWhiteSneakerUpper", 0xE6EAE2)
    mat_cuff = make_toon_source_material("MatWhiteSneakerCuff", 0xDCE0D8)
    mat_strap = make_toon_source_material("MatSageSneakerStrap", 0xA4BAB0)
    mat_sole = make_toon_source_material("MatDarkSneakerSole", 0x1E2228)
    parts = []

    for side in (-1.0, 1.0):
        sx = side * 0.080

        # 1. Thick Dark Charcoal Platform Sole (z = 0.000 to 0.036, slightly raised heel wedge)
        sole_stations = [
            (0.000, 0.058, 0.122, 0.042),
            (0.032, 0.060, 0.124, 0.042),
            (0.036, 0.054, 0.116, 0.042),
        ]
        # 2. Chunky Rounded Off-White Shoe Upper (z = 0.030 to 0.108)
        upper_stations = [
            (0.030, 0.056, 0.118, 0.042),
            (0.062, 0.058, 0.122, 0.044),
            (0.090, 0.052, 0.104, 0.036),
            (0.110, 0.040, 0.068, 0.014),
        ]
        n_sh_seg = 24

        for part_name, st_list, p_mat, c_start, c_end in (
            (f"WhiteSneakerSole_{'L' if side < 0 else 'R'}", sole_stations, mat_sole, True, True),
            (
                f"WhiteSneakerUpper_{'L' if side < 0 else 'R'}",
                upper_stations,
                mat_upper,
                False,
                True,
            ),
        ):
            sh_rings = []
            for z, rx, ry, cy in st_list:
                ring = []
                for s in range(n_sh_seg):
                    ang = (2.0 * math.pi * s) / n_sh_seg
                    ca, sa = math.cos(ang), math.sin(ang)
                    bx = math.copysign(abs(ca) ** 0.68, ca) * rx
                    by = cy + math.copysign(abs(sa) ** 0.72, sa) * ry
                    # Slight heel wedge lift on the dark sole in Back/Side views (Images 1, 3, 4)
                    z_adj = z + (0.005 * max(0.0, -sa) if z > 0.01 else 0.0)
                    ring.append((sx + bx, by, z_adj))
                sh_rings.append(ring)
            parts.append(make_loft_from_rings(part_name, sh_rings, p_mat, c_start, c_end))

        # 3. Wide Chunky Folded Off-White Ankle Cuff Collar (Images 1, 2, 3, 4!)
        # Has a distinct sharp horizontal bottom step at z = 0.095 so the outline shader frames
        # the folded ankle cuff clearly from Back, Front, Left, and Right!
        collar_stations = [
            (0.092, 0.048, 0.054, 0.004),  # inner ankle base
            (0.096, 0.064, 0.070, 0.006),  # sharp outward cuff ledge (framed by outline pass!)
            (0.132, 0.066, 0.072, 0.008),  # thick mid cuff body
            (0.166, 0.062, 0.068, 0.010),  # upper cuff rim
            (0.170, 0.046, 0.052, 0.008),  # inner cuff tuck around sock
        ]
        collar_rings = []
        for z, crx, cry, cy_shift in collar_stations:
            cring = []
            for s in range(20):
                ang = (2.0 * math.pi * s) / 20
                ca, sa = math.cos(ang), math.sin(ang)
                bx = math.copysign(abs(ca) ** 0.74, ca) * crx
                by = cy_shift + math.copysign(abs(sa) ** 0.78, sa) * cry
                cring.append((sx + bx, by, z))
            collar_rings.append(cring)
        parts.append(
            make_loft_from_rings(
                f"WhiteSneakerCuff_{'L' if side < 0 else 'R'}",
                collar_rings,
                mat_cuff,
                cap_start=True,
                cap_end=True,
                sharp_ring_indices=(0, 3),
            )
        )

        # 4. Prominent Tall Rounded Off-White Tongue rising in front of the ankle cuff (Images 2, 3, 4!)
        bpy.ops.mesh.primitive_cube_add(size=0.094, location=(0.0, 0.0, 0.0))
        tongue = bpy.context.active_object
        tongue.name = f"WhiteSneakerTongue_{'L' if side < 0 else 'R'}"
        sub_t = tongue.modifiers.new("Subsurf", "SUBSURF")
        sub_t.levels = 2
        sub_t.render_levels = 2
        bpy.ops.object.modifier_apply(modifier="Subsurf")
        tongue.scale = (0.86, 0.48, 1.24)
        tongue.rotation_euler = (-0.24, 0.0, 0.0)
        tongue.location = (sx, 0.066, 0.142)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        tongue.data.materials.append(mat_upper)
        tongue.select_set(False)
        parts.append(tongue)

        # 5. Wide Sage-Grey Velcro Mid-Foot Strap across the front instep (Images 2, 3, 4!)
        # Built with sharp box-plate edges so the outline shader draws a crisp dark border around the strap!
        bpy.ops.mesh.primitive_cube_add(size=0.088, location=(0.0, 0.0, 0.0))
        strap = bpy.context.active_object
        strap.name = f"WhiteSneakerStrap_{'L' if side < 0 else 'R'}"
        strap.scale = (1.34, 0.52, 0.34)
        strap.rotation_euler = (0.42, 0.0, 0.0)
        strap.location = (sx, 0.084, 0.084)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        strap.data.materials.append(mat_strap)
        strap.select_set(False)
        parts.append(strap)

    return join_parts_into_slot_mesh(parts, "ShoesMesh")
