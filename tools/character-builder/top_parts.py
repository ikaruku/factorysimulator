"""
Modular `TopMesh` (Pakaian Atas) slot builders for Male & Female Abeto characters:
- `build_top_orange_hoodie()`: Default Male oversized orange pullover hoodie (#DE6F45) with
  plump folded hood, V-collar, dark-grey drawstrings + white eyelets, and long sculpted sleeves
  with elbow & forearm cloth creases.
- `build_top_cyan_colorblock_tee()`: Default Female crisp A-line oversized short-sleeve T-shirt
  with 1024x1024 cyan (#2FA6CC) / off-white (#E4E8E0) color-blocking, sculpted torso drape,
  and wide flared short sleeves.
"""

import math
import bpy
from mesh_utils import join_parts_into_slot_mesh, make_loft_from_rings, make_toon_source_material
from textures import create_colorblock_shirt_material


def build_top_orange_hoodie():
    """Builds the default Male oversized orange pullover hoodie as `TopMesh`."""
    mat_hoodie = make_toon_source_material("MatHoodieOrange", 0xDE6F45)
    mat_string = make_toon_source_material("MatDrawstringGrey", 0x4A4D54)
    mat_eyelet = make_toon_source_material("MatEyeletWhite", 0xDCE0D8)
    parts = []

    # 1. Sculpted Hoodie Torso (z = 0.775 to 1.292)
    torso_stations = [
        (0.775, 0.132, 0.092, 0.104, 0.008, 0.000),
        (0.785, 0.160, 0.120, 0.136, 0.008, 0.004),
        (0.835, 0.164, 0.126, 0.138, 0.012, 0.008),
        (0.905, 0.158, 0.118, 0.120, 0.010, 0.008),
        (0.985, 0.154, 0.112, 0.112, 0.008, 0.005),
        (1.065, 0.150, 0.106, 0.106, 0.006, 0.004),
        (1.145, 0.148, 0.102, 0.102, 0.005, 0.002),
        (1.215, 0.146, 0.096, 0.096, 0.005, 0.000),
        (1.260, 0.122, 0.084, 0.086, 0.006, 0.000),
        (1.292, 0.070, 0.064, 0.068, 0.012, 0.000),
    ]
    n_seg = 36
    torso_rings = []
    for z, rx, ry_f, ry_b, cy, f_amp in torso_stations:
        ring = []
        for s in range(n_seg):
            ang = (2.0 * math.pi * s) / n_seg
            ca, sa = math.cos(ang), math.sin(ang)
            ry = ry_f if sa >= 0.0 else ry_b
            x = ca * rx
            y = sa * ry + cy
            if f_amp > 0.0 and sa > 0.15:
                diag = math.sin(ca * 2.6 + (z - 0.84) * 11.0)
                y += f_amp * 0.70 * diag * (sa**1.2)
            z_local = z
            if z < 0.85:
                z_local += 0.010 * (abs(ca) ** 1.6) * (1.0 - (z - 0.775) / 0.075)
            ring.append((x, y, z_local))
        torso_rings.append(ring)

    parts.append(make_loft_from_rings("HoodieTorso", torso_rings, mat_hoodie, cap_start=True))

    # 2. Plump Smooth Folded Hood & Cozy V-Neck Front Collar
    hood_stations = [
        (1.248, 0.092, 0.108, 0.088, -0.145),
        (1.275, 0.104, 0.122, 0.104, -0.188),
        (1.305, 0.106, 0.124, 0.098, -0.202),
        (1.334, 0.098, 0.114, 0.084, -0.188),
        (1.352, 0.082, 0.096, 0.068, -0.152),
        (1.335, 0.062, 0.072, 0.052, -0.088),
    ]
    n_hseg = 32
    hood_rings = []
    for z, rxf, rxb, yf, yb in hood_stations:
        ring = []
        y_center = 0.5 * (yf + yb)
        ry_half = 0.5 * (yf - yb)
        for s in range(n_hseg):
            ang = (2.0 * math.pi * s) / n_hseg
            ca, sa = math.cos(ang), math.sin(ang)
            t_fb = 0.5 * (sa + 1.0)
            rx = rxb + (rxf - rxb) * t_fb
            x = ca * rx
            y = y_center + sa * ry_half
            z_local = z
            if sa > 0.35:
                v_notch = math.exp(-((ca / 0.32) ** 2))
                z_local -= 0.024 * v_notch * ((sa - 0.35) / 0.65)
                z_local += 0.008 * max(0.0, ca) * ((sa - 0.35) / 0.65)
                y += 0.005 * ca * v_notch
            elif sa < -0.25 and 1.29 < z < 1.32:
                fold = math.exp(-(((z - 1.305 + ca * 0.012) / 0.012) ** 2))
                y += 0.006 * fold
            ring.append((x, y, z_local))
        hood_rings.append(ring)

    parts.append(make_loft_from_rings("HoodieHood", hood_rings, mat_hoodie))

    # 3. Two Grey Drawstrings & Off-White Collar Eyelets
    for side, len_drop, x_end_shift in ((-1.0, 0.112, -0.002), (1.0, 0.124, 0.004)):
        ex = side * 0.019
        ey = 0.102
        ez = 1.260
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.0050,
            minor_radius=0.0020,
            major_segments=14,
            minor_segments=8,
            location=(ex, ey, ez),
            rotation=(math.radians(78), 0.0, 0.0),
        )
        eyelet = bpy.context.active_object
        eyelet.name = f"HoodieEyelet_{'L' if side < 0 else 'R'}"
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        eyelet.data.materials.append(mat_eyelet)
        eyelet.select_set(False)
        parts.append(eyelet)

        cord_stations = 7
        cord_rings = []
        for k in range(cord_stations):
            t = k / (cord_stations - 1)
            cx = ex + x_end_shift * t + side * 0.0015 * math.sin(t * math.pi)
            cy = ey + 0.010 * math.sin(t * math.pi * 0.65) + 0.005 * t
            cz = ez - len_drop * t
            r_cord = 0.0050 * (1.0 - 0.10 * t)
            c_ring = []
            for s in range(10):
                a = (2.0 * math.pi * s) / 10
                c_ring.append((cx + math.cos(a) * r_cord, cy + math.sin(a) * r_cord, cz))
            cord_rings.append(c_ring)
        parts.append(
            make_loft_from_rings(
                f"HoodieDrawstring_{'L' if side < 0 else 'R'}",
                cord_rings,
                mat_string,
                cap_start=True,
                cap_end=True,
            )
        )

    # 4. Sculpted Long Hoodie Sleeves with Elbow & Forearm Crease Bands
    sleeve_stations = [
        (0.095, -0.002, 1.248, 0.056, 0.058, 0.000, 0.000),
        (0.138, -0.008, 1.222, 0.062, 0.064, 0.000, 0.000),
        (0.162, -0.015, 1.162, 0.062, 0.064, 0.000, 0.000),
        (0.178, -0.022, 1.088, 0.063, 0.066, 0.003, 0.002),
        (0.190, -0.028, 1.025, 0.064, 0.068, 0.005, 0.006),
        (0.198, -0.030, 0.980, 0.066, 0.070, 0.009, 0.008),
        (0.196, -0.012, 0.935, 0.062, 0.065, 0.002, 0.006),
        (0.198, 0.010, 0.880, 0.061, 0.064, 0.003, 0.000),
        (0.198, 0.028, 0.825, 0.060, 0.063, 0.005, 0.004),
        (0.195, 0.040, 0.798, 0.052, 0.054, 0.000, 0.003),
        (0.194, 0.046, 0.760, 0.048, 0.050, 0.000, 0.000),
        (0.194, 0.046, 0.768, 0.034, 0.034, 0.000, 0.000),
    ]
    n_sseg = 24
    for side in (-1.0, 1.0):
        slv_rings = []
        for cx, cy, cz, rx, ry, elb_corner, in_crease in sleeve_stations:
            ring = []
            for s in range(n_sseg):
                ang = (2.0 * math.pi * s) / n_sseg
                ca, sa = math.cos(ang), math.sin(ang)
                outer_lat = max(0.0, ca * side)
                back_dir = max(0.0, -sa)
                inner_front = max(0.0, -ca * side * 0.4 + sa * 0.9)

                lx = ca * rx
                ly = sa * ry
                if elb_corner > 0.0:
                    lx += side * elb_corner * (outer_lat**1.5)
                    ly -= elb_corner * 0.75 * (back_dir**1.5)
                if in_crease > 0.0:
                    ly -= in_crease * (inner_front**1.6)
                ring.append((side * cx + lx, cy + ly, cz))
            slv_rings.append(ring)

        parts.append(
            make_loft_from_rings(
                f"HoodieSleeve_{'L' if side < 0 else 'R'}",
                slv_rings,
                mat_hoodie,
                cap_start=True,
                cap_end=True,
                sharp_ring_indices=(5, 8),
            )
        )

    return join_parts_into_slot_mesh(parts, "TopMesh")


def _assign_shirt_uvs(shirt_obj, z_min=0.785, z_max=1.292):
    """Maps front faces (y >= 0) to u in [0, 0.5) and back faces (y < 0) to u in [0.5, 1]."""
    mesh = shirt_obj.data
    uv_layer = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
    uv_layer.name = "UVMap"
    ref_x = 0.175

    for poly in mesh.polygons:
        is_front = poly.center.y >= 0.0
        for loop_idx in poly.loop_indices:
            v = mesh.vertices[mesh.loops[loop_idx].vertex_index].co
            nv = max(0.005, min(0.995, (v.z - z_min) / (z_max - z_min)))
            if is_front:
                lu = max(0.005, min(0.995, 0.5 - v.x / (2.0 * ref_x)))
                u = lu * 0.495
            else:
                lu = max(0.005, min(0.995, 0.5 + v.x / (2.0 * ref_x)))
                u = 0.505 + lu * 0.495
            uv_layer.data[loop_idx].uv = (u, nv)


def build_top_cyan_colorblock_tee():
    """
    Builds the default Female A-line oversized cyan/off-white color-blocked T-shirt matching
    Images 1 (Back), 2 (Front), 3 (Left), and 4 (Right) as `TopMesh`.
    """
    mat_torso = create_colorblock_shirt_material()
    mat_cyan = make_toon_source_material("MatShirtCyan", 0x2FA6CC)
    mat_white = make_toon_source_material("MatShirtWhite", 0xE4E8E0)
    parts = []

    # 1. Sculpted A-Line Oversized Tee Torso (z = 0.785 to 1.285)
    # Flared back tail in Side views (Images 3 & 4) and wider relaxed crew neckline in Front (Image 2)
    torso_stations = [
        (0.785, 0.145, 0.095, 0.106, 0.006, 0.000),
        (0.792, 0.172, 0.122, 0.142, 0.004, 0.004),  # wide A-line bottom hem with flared back tail
        (0.865, 0.164, 0.116, 0.132, 0.005, 0.006),
        (0.955, 0.154, 0.110, 0.120, 0.006, 0.005),
        (1.055, 0.145, 0.104, 0.110, 0.006, 0.003),
        (1.155, 0.138, 0.096, 0.100, 0.005, 0.000),
        (1.235, 0.130, 0.088, 0.092, 0.006, 0.000),
        (1.268, 0.100, 0.074, 0.078, 0.008, 0.000),
        (1.282, 0.068, 0.062, 0.062, 0.012, 0.000),  # relaxed crew neckline
        (1.268, 0.058, 0.054, 0.054, 0.012, 0.000),
    ]
    n_seg = 36
    torso_rings = []
    for z, rx, ry_f, ry_b, cy, f_amp in torso_stations:
        ring = []
        for s in range(n_seg):
            ang = (2.0 * math.pi * s) / n_seg
            ca, sa = math.cos(ang), math.sin(ang)
            ry = ry_f if sa >= 0.0 else ry_b
            x = ca * rx
            y = sa * ry + cy
            if f_amp > 0.0 and sa > 0.15:
                y += f_amp * 0.65 * math.sin(ca * 2.8 + (z - 0.82) * 10.0) * (sa**1.2)
            ring.append((x, y, z))
        torso_rings.append(ring)

    torso_obj = make_loft_from_rings("TeeTorso", torso_rings, mat_torso, cap_start=True)
    _assign_shirt_uvs(torso_obj, z_min=0.785, z_max=1.282)
    parts.append(torso_obj)

    # 2. Natural Drop-Shoulder Straight-Flared Short Sleeves (Images 1, 2, 3, 4!)
    # Kept close to the torso (`outer x ~ +-0.228`, NOT wide conical wings!)
    slv_stations = [
        (0.080, -0.002, 1.258, 0.056, 0.058),
        (0.122, -0.006, 1.228, 0.060, 0.062),
        (0.148, -0.010, 1.158, 0.062, 0.065),
        (0.165, -0.014, 1.082, 0.064, 0.067),
        (0.176, -0.016, 1.015, 0.066, 0.069),  # crisp short-sleeve cuff opening at elbow top
        (0.174, -0.016, 1.020, 0.050, 0.052),
    ]
    n_sseg = 24
    for side, s_mat in ((1.0, mat_cyan), (-1.0, mat_white)):
        slv_rings = []
        for cx, cy, cz, rx, ry in slv_stations:
            ring = []
            for s in range(n_sseg):
                ang = (2.0 * math.pi * s) / n_sseg
                ring.append((side * cx + math.cos(ang) * rx, cy + math.sin(ang) * ry, cz))
            slv_rings.append(ring)
        parts.append(
            make_loft_from_rings(
                f"TeeSleeve_{'R' if side > 0 else 'L'}",
                slv_rings,
                s_mat,
                cap_start=True,
                cap_end=True,
            )
        )

    return join_parts_into_slot_mesh(parts, "TopMesh")
