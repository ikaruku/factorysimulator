"""
Modular `BagMesh` (Tas) slot builders for Male & Female Abeto characters:
- `build_bag_red_backpack()`: Default Male Nike Heritage Coral-Red Backpack (#D24442) with
  arch-top dome silhouette, crisp 1024x1024 white "NIKE" + Swoosh logo, 3D raised zipper welt,
  3D protruding lower front box pocket with overhanging zipper flap hood and vertical pull tab,
  3D top webbing haul loop handle, and curved padded red shoulder straps.
- `build_bag_yellow_crossbody()`: Default Female golden-yellow crossbody sling bag (#E5A530)
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
from rig_builder import assign_part_weights
from textures import (
    create_nike_backpack_logo_material,
    create_nike_backpack_side_material,
)


def _assign_backpack_uvs(pack_obj, mat_red, mat_logo, mat_side):
    """
    Maps `BackpackBody` cleanly to 3 material slots:
      - slot 0 (`mat_red`): base/front/bottom faces
      - slot 1 (`mat_logo`): upper rear dome arch panel (1024x1024 Linear-filtered NIKE + Swoosh)
      - slot 2 (`mat_side`): left/right side walls (clean painted zipper & side-pocket seams,
        zero intersecting thin tubes so the outline pass stays 100% crisp without speckles).
    """
    mesh = pack_obj.data
    mesh.materials.clear()
    mesh.materials.append(mat_red)  # slot 0
    mesh.materials.append(mat_logo)  # slot 1
    mesh.materials.append(mat_side)  # slot 2

    uv_layer = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
    uv_layer.name = "UVMap"

    for poly in mesh.polygons:
        c = poly.center
        n = poly.normal
        # Rear upper dome face above the lower front pocket
        is_logo_panel = n.y < -0.55 and 1.008 < c.z < 1.242 and abs(c.x) < 0.132
        # Left/right side panels (y in [-0.228, -0.090], z in [0.855, 1.245])
        is_side_panel = abs(n.x) > 0.55 and 0.865 < c.z < 1.235

        if is_logo_panel:
            poly.material_index = 1
            for loop_idx in poly.loop_indices:
                v = mesh.vertices[mesh.loops[loop_idx].vertex_index].co
                # Back view (-Y looking to +Y): -X is viewer LEFT (u=0), +X is viewer RIGHT (u=1)
                u = max(0.01, min(0.99, 0.5 + v.x / 0.285))
                nv = max(0.01, min(0.99, (v.z - 1.012) / 0.222))
                uv_layer.data[loop_idx].uv = (u, nv)
        elif is_side_panel:
            poly.material_index = 2
            for loop_idx in poly.loop_indices:
                v = mesh.vertices[mesh.loops[loop_idx].vertex_index].co
                # u=0 against character back (y=-0.090), u=1 at rear face (y=-0.228)
                u = max(0.01, min(0.99, (-0.090 - v.y) / 0.138))
                nv = max(0.01, min(0.99, (v.z - 0.858) / 0.395))
                uv_layer.data[loop_idx].uv = (u, nv)
        else:
            poly.material_index = 0
            for loop_idx in poly.loop_indices:
                uv_layer.data[loop_idx].uv = (0.02, 0.02)


def build_bag_red_backpack():
    """
    Builds the sleek Nike Heritage Coral-Red Backpack (`media_1795350199916_e293d8c5.jpg`) as `BagMesh`:
    - Sleek, tapered arch-top dome daypack silhouette (#D24442) hugging the back cleanly
    - Anti-aliased Linear-filtered 1024x1024 white "NIKE" + Swoosh logo on the upper arch panel
    - Clean side-panel zipper & side-pocket seam texture (zero outline speckle artifacts)
    - Slim, snug lower front box pocket (2.4 cm depth) with flush zipper flap hood & subtle pull tab
    - Smooth top webbing haul loop handle & smooth padded shoulder straps.
    """
    mat_red = make_toon_source_material("MatBackpackRed", 0xD24442)
    mat_trim = make_toon_source_material("MatBackpackTrimRed", 0xBC3838)
    mat_logo = create_nike_backpack_logo_material()
    mat_side = create_nike_backpack_side_material()
    parts = []

    # 1. Sleek Tapered Arch-Top Main Backpack Body (z = 0.858 to 1.254, snug depth 13.6 cm tapering to top)
    pack_stations = [
        (0.858, 0.120, -0.096, -0.205),  # soft chamfered bottom base
        (0.876, 0.138, -0.090, -0.228),  # lower full width & snug depth (13.8 cm)
        (0.985, 0.140, -0.088, -0.226),  # mid body (side pocket seam height)
        (1.072, 0.138, -0.088, -0.221),  # start of dome arch (slight sleek taper)
        (1.132, 0.130, -0.088, -0.214),  # mid-lower dome arch (NIKE logo center)
        (1.182, 0.116, -0.088, -0.203),  # upper dome arch
        (1.220, 0.092, -0.088, -0.187),  # dome shoulder
        (1.244, 0.058, -0.088, -0.166),  # dome crown
        (1.254, 0.026, -0.090, -0.142),  # top arch apex
    ]
    n_pseg = 32
    pack_rings = []
    for z, hw, yf, yb in pack_stations:
        ring = []
        yc = 0.5 * (yf + yb)
        hy = 0.5 * (yf - yb)
        for s in range(n_pseg):
            ang = (2.0 * math.pi * s) / n_pseg
            ca, sa = math.cos(ang), math.sin(ang)
            # Clean rounded sides + gently flat rear panel for crisp logo & snug front pocket
            sx = math.copysign(abs(ca) ** 0.62, ca) * hw
            sy = yc + math.copysign(abs(sa) ** 0.55, sa) * hy
            ring.append((sx, sy, z))
        pack_rings.append(ring)

    pack_body = make_loft_from_rings(
        "BackpackBody",
        pack_rings,
        mat_red,
        cap_start=True,
        cap_end=True,
        smooth=True,
    )
    _assign_backpack_uvs(pack_body, mat_red, mat_logo, mat_side)
    parts.append(pack_body)

    # 2. Slim, Snug Lower Front Box Pocket (only ~2.4 cm projection, neat inset margins!)
    pocket_stations = [
        (0.874, 0.098, -0.218, -0.244),  # slightly beveled lower edge above pack bottom
        (0.884, 0.102, -0.218, -0.248),  # slim full pocket face
        (0.996, 0.102, -0.218, -0.246),  # gentle inward taper toward top flap
        (1.012, 0.099, -0.218, -0.242),  # snug upper bevel into main body
    ]
    n_kseg = 24
    pocket_rings = []
    for z, hw, yf, yb in pocket_stations:
        ring = []
        yc = 0.5 * (yf + yb)
        hy = 0.5 * (yf - yb)
        for s in range(n_kseg):
            ang = (2.0 * math.pi * s) / n_kseg
            ca, sa = math.cos(ang), math.sin(ang)
            sx = math.copysign(abs(ca) ** 0.42, ca) * hw
            sy = yc + math.copysign(abs(sa) ** 0.42, sa) * hy
            ring.append((sx, sy, z))
        pocket_rings.append(ring)
    parts.append(
        make_loft_from_rings(
            "BackpackFrontPocket",
            pocket_rings,
            mat_red,
            cap_start=True,
            cap_end=True,
            smooth=True,
        )
    )

    # Slim flush zipper flap hood across the top of the pocket (only 2.5 mm proud, 1.8 cm tall!)
    parts.append(
        make_box_plate(
            "BackpackPocketFlap",
            -0.102,
            0.102,
            -0.2505,
            -0.222,
            0.995,
            1.013,
            mat_trim,
        )
    )

    # Sleek thin vertical zipper pull tab tucked cleanly under the flap on the left
    parts.append(
        make_box_plate(
            "BackpackZipperTab",
            -0.056,
            -0.046,
            -0.2505,
            -0.2455,
            0.960,
            0.995,
            mat_trim,
        )
    )

    # 3. Smooth Top Webbing Haul Loop Handle at the apex of the dome (z = 1.240..1.284)
    handle_pts = 11
    handle_rings = []
    for i in range(handle_pts):
        t = i / (handle_pts - 1)
        ang = math.pi * (1.0 - t)
        hx = math.cos(ang) * 0.032
        hz = 1.240 + math.sin(ang) * 0.044
        hy = -0.164 - math.sin(ang) * 0.010
        h_ring = [
            (hx - 0.0035, hy - 0.007, hz),
            (hx + 0.0035, hy - 0.007, hz),
            (hx + 0.0035, hy + 0.007, hz),
            (hx - 0.0035, hy + 0.007, hz),
        ]
        handle_rings.append(h_ring)
    parts.append(
        make_loft_from_rings(
            "BackpackHaulHandle",
            handle_rings,
            mat_trim,
            cap_start=True,
            cap_end=True,
            smooth=True,
        )
    )

    # 4. Smooth Tailored Padded Red Shoulder Straps (sleeker profile, sitting cleanly on shoulder)
    strap_path = [
        (0.088, -0.116, 1.228, 0.022, 0.016),
        (0.132, -0.088, 1.254, 0.025, 0.018),
        (0.155, -0.030, 1.259, 0.025, 0.018),
        (0.160, 0.032, 1.244, 0.023, 0.017),
        (0.152, 0.086, 1.196, 0.020, 0.014),
        (0.140, 0.094, 1.130, 0.016, 0.012),
        (0.114, 0.048, 1.070, 0.011, 0.009),
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
                smooth=True,
            )
        )

    for part in parts:
        if part.name == "BackpackStrap_L":
            assign_part_weights(part, "backpack_strap_L")
        elif part.name == "BackpackStrap_R":
            assign_part_weights(part, "backpack_strap_R")
        elif part.name == "CrossbodyStrap":
            assign_part_weights(part, "crossbody_strap")
        elif part.name == "CrossbodyPouch":
            assign_part_weights(part, "crossbody_pouch")
        else:
            assign_part_weights(part, "backpack")
    return join_parts_into_slot_mesh(parts, "BagMesh")


def build_bag_yellow_crossbody():
    """
    Builds the default Female golden-yellow crossbody sling bag (#E5A530) matching
    Images 1 (Back), 2 (Front), 3 (Left), and 4 (Right) as `BagMesh`:
    - Prominent right-shoulder strap loop cap (+X) visible in Front, Back, and Right views
    - Diagonal front strap across chest into the top-front of the front-left hip pouch (Image 2)
    - Back strap sweeping from upper-right shoulder across upper back to the left mid-ribcage
      under the white sleeve cuff, then dropping vertically down the left side into the pouch
      (Images 1 & 3!)
    - Prominent rounded rectangular/trapezoidal yellow pouch sitting in front of the left arm
      at the front-left hip (Images 2, 3, 4).
    """
    mat_bag = make_toon_source_material("MatYellowBag", 0xE5A530)
    parts = []

    strap_waypoints = [
        (-0.148, 0.118, 0.825),  # anchored inside top-front of pouch
        (-0.132, 0.130, 0.885),  # front-left waist above pouch (Image 2)
        (-0.072, 0.130, 0.978),  # lower front chest
        (-0.008, 0.124, 1.078),  # mid front chest
        (0.052, 0.112, 1.172),  # upper front chest
        (0.096, 0.084, 1.240),  # right collarbone
        (0.114, 0.028, 1.258),  # smooth rounded right-shoulder loop front (Images 2 & 4!)
        (0.116, -0.028, 1.258),  # smooth rounded right-shoulder loop back (Images 1 & 4!)
        (0.074, -0.098, 1.228),  # upper back right (Image 1)
        (-0.015, -0.120, 1.155),  # upper-mid back diagonal (Image 1)
        (-0.106, -0.126, 1.068),  # emerging under left white sleeve cuff on back (Image 1!)
        (-0.156, -0.116, 0.985),  # left mid-ribcage corner (Images 1 & 3!)
        (-0.168, -0.070, 0.895),  # vertical drop down left side behind pouch (Images 1 & 3!)
        (-0.164, 0.012, 0.835),  # entering top-back corner of pouch (Images 2 & 3!)
        (-0.156, 0.068, 0.795),  # anchored inside back of pouch
    ]

    n_seg = 12
    rx, ry = 0.018, 0.010
    st_rings = []
    for i, (cx, cy, cz) in enumerate(strap_waypoints):
        nx, ny = cx, cy
        n_len = max(1e-6, math.sqrt(nx * nx + ny * ny))
        nx, ny = nx / n_len, ny / n_len
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

        bx = -tz * ny
        by = tz * nx
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

    # Prominent rounded rectangular/trapezoidal pouch sitting in front of the left arm (Images 2, 3, 4!)
    bpy.ops.mesh.primitive_cube_add(size=0.180, location=(0.0, 0.0, 0.0))
    pouch = bpy.context.active_object
    pouch.name = "CrossbodyPouch"
    sub = pouch.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    for v in pouch.data.vertices:
        z_t = (v.co.z + 0.090) / 0.180
        v.co.x *= 0.56 * (1.10 - 0.22 * z_t)
        v.co.y *= 1.05 * (1.12 - 0.22 * z_t)
        v.co.z *= 1.24
    pouch.data.update()

    pouch.rotation_euler = (0.05, -0.08, 0.36)
    pouch.location = (-0.158, 0.102, 0.772)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    pouch.data.materials.append(mat_bag)
    pouch.select_set(False)
    parts.append(pouch)

    for part in parts:
        if part.name == "BackpackStrap_L":
            assign_part_weights(part, "backpack_strap_L")
        elif part.name == "BackpackStrap_R":
            assign_part_weights(part, "backpack_strap_R")
        elif part.name == "CrossbodyStrap":
            assign_part_weights(part, "crossbody_strap")
        elif part.name == "CrossbodyPouch":
            assign_part_weights(part, "crossbody_pouch")
        else:
            assign_part_weights(part, "backpack")
    return join_parts_into_slot_mesh(parts, "BagMesh")
