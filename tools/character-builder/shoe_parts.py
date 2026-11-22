"""
Modular `ShoesMesh` (Sepatu) slot builder for Male & Female Abeto characters:
- `build_shoes_high_top_sneakers()`: Chunky dark high-top skate sneakers (#1E2228) with
  solid vertical-walled flat skate sole (#171B20) grounded at z = 0, padded high-top ankle
  collar, tall rounded tongue, and twin off-white stripes (#E2E6DE) on the outer side &
  front-outer instep.
"""

import math
import bpy
from mesh_utils import join_parts_into_slot_mesh, make_loft_from_rings, make_toon_source_material


def build_shoes_high_top_sneakers():
    """Builds the default chunky high-top dark sneakers as `ShoesMesh`."""
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
