"""
Modular `BagMesh` (Tas) slot builders for Male & Female Abeto characters:
- `build_bag_red_backpack()`: Default Male crimson-red backpack (#A83A3E) with chamfered
  bottom-back corner, bold 3D off-white "Hi" + two horizontal bars graphic logo (#DCE0D8),
  and thick padded red shoulder straps.
- `build_bag_yellow_crossbody()`: Default Female golden-yellow crossbody sling bag (#E9A82B)
  with smooth non-cyclic lofted elliptical strap (zero normal-crease hatching!) and prominent
  front-left rounded trapezoidal hip pouch.
"""

import math
import bpy
from mesh_utils import (
    join_parts_into_slot_mesh,
    make_box_plate,
    make_loft_from_rings,
    make_toon_source_material,
)


def build_bag_red_backpack():
    """Builds the default Male crimson-red backpack + straps + 3D "Hi" logo as `BagMesh`."""
    mat_red = make_toon_source_material("MatBackpackRed", 0xA83A3E)
    mat_logo = make_toon_source_material("MatBackpackLogo", 0xDCE0D8)
    parts = []

    pack_stations = [
        (0.858, 0.115, -0.102, -0.210),
        (0.882, 0.136, -0.100, -0.242),
        (0.920, 0.146, -0.098, -0.276),
        (1.000, 0.148, -0.096, -0.278),
        (1.095, 0.146, -0.096, -0.275),
        (1.180, 0.140, -0.096, -0.268),
        (1.232, 0.126, -0.094, -0.244),
        (1.255, 0.098, -0.092, -0.192),
    ]
    n_pseg = 28
    pack_rings = []
    for z, hw, yf, yb in pack_stations:
        ring = []
        yc = 0.5 * (yf + yb)
        hy = 0.5 * (yf - yb)
        for s in range(n_pseg):
            ang = (2.0 * math.pi * s) / n_pseg
            ca, sa = math.cos(ang), math.sin(ang)
            sx = math.copysign(abs(ca) ** 0.58, ca) * hw
            sy = yc + math.copysign(abs(sa) ** 0.56, sa) * hy
            ring.append((sx, sy, z))
        pack_rings.append(ring)

    parts.append(
        make_loft_from_rings("BackpackBody", pack_rings, mat_red, cap_start=True, cap_end=True)
    )

    y_in, y_out = -0.268, -0.282
    logo_boxes = [
        ("Logo_H_Top", -0.072, 0.040, y_out, y_in, 1.125, 1.160),
        ("Logo_H_Mid", -0.038, 0.012, y_out, y_in, 1.078, 1.127),
        ("Logo_H_Bot", -0.072, 0.014, y_out, y_in, 1.044, 1.080),
        ("Logo_Dot", 0.026, 0.070, y_out, y_in, 1.042, 1.080),
        ("Logo_Bar1", -0.072, 0.070, y_out, y_in, 0.986, 1.020),
        ("Logo_Bar2", -0.072, 0.070, y_out, y_in, 0.926, 0.960),
    ]
    for bname, x0, x1, y0, y1, z0, z1 in logo_boxes:
        parts.append(make_box_plate(bname, x0, x1, y0, y1, z0, z1, mat_logo))

    strap_path = [
        (0.095, -0.130, 1.225, 0.026, 0.020),
        (0.138, -0.098, 1.248, 0.030, 0.024),
        (0.160, -0.035, 1.254, 0.030, 0.025),
        (0.164, 0.032, 1.238, 0.027, 0.022),
        (0.158, 0.088, 1.192, 0.023, 0.017),
        (0.150, 0.102, 1.125, 0.020, 0.014),
        (0.150, 0.068, 1.050, 0.018, 0.013),
        (0.148, -0.012, 1.000, 0.018, 0.013),
        (0.125, -0.120, 0.980, 0.018, 0.013),
    ]
    n_st_seg = 12
    for side in (-1.0, 1.0):
        st_rings = []
        for cx, cy, cz, hw, ht in strap_path:
            ring = []
            for s in range(n_st_seg):
                ang = (2.0 * math.pi * s) / n_st_seg
                ca, sa = math.cos(ang), math.sin(ang)
                ring.append((side * cx + ca * hw, cy + sa * ht * 0.85, cz + sa * ht * 0.90))
            st_rings.append(ring)

        parts.append(
            make_loft_from_rings(
                f"BackpackStrap_{'L' if side < 0 else 'R'}",
                st_rings,
                mat_red,
                cap_start=True,
                cap_end=True,
            )
        )

    return join_parts_into_slot_mesh(parts, "BagMesh")


def build_bag_yellow_crossbody():
    """
    Builds the default Female golden-yellow crossbody sling bag (#E9A82B) as `BagMesh`.
    Uses an explicit lofted elliptical quad-tube whose two ends terminate cleanly inside the
    front-left hip pouch so there is ZERO cyclic NURBS seam or black hatching!
    """
    mat_bag = make_toon_source_material("MatYellowBag", 0xE9A82B)
    parts = []

    # Non-cyclic path starting inside front-top of pouch -> across front chest -> over right
    # shoulder -> diagonally down back -> wrapping left waist -> ending inside back of pouch!
    strap_waypoints = [
        (-0.160, 0.108, 0.785),  # anchored inside front-top of pouch
        (-0.146, 0.126, 0.855),  # front-left waist above pouch
        (-0.086, 0.132, 0.955),  # lower front chest
        (-0.018, 0.128, 1.065),  # mid front chest
        (0.046, 0.116, 1.162),  # upper front chest
        (0.092, 0.088, 1.236),  # right collarbone (hugs tee collar snugly!)
        (0.112, 0.032, 1.260),  # front-top right shoulder (zero air gap!)
        (0.114, -0.025, 1.262),  # back-top right shoulder crest
        (0.092, -0.084, 1.232),  # upper back right
        (0.030, -0.114, 1.150),  # upper-mid back
        (-0.042, -0.122, 1.045),  # mid back
        (-0.114, -0.122, 0.935),  # lower back left
        (-0.156, -0.068, 0.842),  # left hip wrap behind pouch (snug against tee!)
        (-0.172, 0.015, 0.788),  # outer-back edge of pouch
        (-0.168, 0.072, 0.765),  # anchored inside back of pouch
    ]

    n_seg = 12
    rx, ry = 0.017, 0.009
    st_rings = []
    for i, (cx, cy, cz) in enumerate(strap_waypoints):
        # Compute local outward surface normal roughly pointing away from torso axis (0, 0, cz)
        nx, ny = cx, cy
        n_len = max(1e-6, math.sqrt(nx * nx + ny * ny))
        nx, ny = nx / n_len, ny / n_len
        # Tangent vector along strap
        if i == 0:
            tx = strap_waypoints[1][0] - cx
            ty = strap_waypoints[1][1] - cy
            tz = strap_waypoints[1][2] - cz
        else:
            tx = cx - strap_waypoints[i - 1][0]
            ty = cy - strap_waypoints[i - 1][1]
            tz = cz - strap_waypoints[i - 1][2]
        t_len = max(1e-6, math.sqrt(tx * tx + ty * ty + tz * tz))
        tx, ty, tz = tx / t_len, ty / t_len, tz / t_len

        # Binormal = tangent x normal (lies flat along torso surface)
        bx = ty * 0.0 - tz * ny
        by = tz * nx - tx * 0.0
        bz = tx * ny - ty * nx
        b_len = max(1e-6, math.sqrt(bx * bx + by * by + bz * bz))
        bx, by, bz = bx / b_len, by / b_len, bz / b_len

        ring = []
        for s in range(n_seg):
            ang = (2.0 * math.pi * s) / n_seg
            ca, sa = math.cos(ang), math.sin(ang)
            u = ca * rx
            v = sa * ry
            ring.append((cx + bx * u + nx * v, cy + by * u + ny * v, cz + bz * u))
        st_rings.append(ring)

    parts.append(
        make_loft_from_rings(
            "CrossbodyStrap",
            st_rings,
            mat_bag,
            cap_start=True,
            cap_end=True,
            smooth=True,
        )
    )

    # Prominent rounded pear/trapezoid pouch at front-left hip
    bpy.ops.mesh.primitive_cube_add(size=0.185, location=(0.0, 0.0, 0.0))
    pouch = bpy.context.active_object
    pouch.name = "CrossbodyPouch"
    sub = pouch.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    for v in pouch.data.vertices:
        z_t = (v.co.z + 0.0925) / 0.185
        v.co.x *= 0.54 * (1.10 - 0.24 * z_t)
        v.co.y *= 1.00 * (1.14 - 0.26 * z_t)
        v.co.z *= 1.20
    pouch.data.update()

    pouch.rotation_euler = (0.06, -0.10, 0.42)
    pouch.location = (-0.168, 0.092, 0.742)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    pouch.data.materials.append(mat_bag)
    pouch.select_set(False)
    parts.append(pouch)

    return join_parts_into_slot_mesh(parts, "BagMesh")
