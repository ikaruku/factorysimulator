"""
Modular `HairMesh` slot builders for Male & Female Abeto character presets:
- `build_hair_shaggy_male()`: continuous sculpted slate-teal shaggy mop hair (#25323A) with
  jagged V-notched bangs, sideburns, ear arches, and wavy nape tufts.
- `build_hair_twin_buns_female()`: continuous sculpted dark bob hair (#1F242B) with swept bangs,
  sideburns, ear arches, chunky rounded nape bob curve, and upper-back twin buns with
  golden-yellow hair ties (#E9A82B).
"""

import math
import bpy
from mesh_utils import join_parts_into_slot_mesh, make_loft_from_rings, make_toon_source_material


def build_hair_shaggy_male():
    """Builds the default Male shaggy slate-teal hair as `HairMesh`."""
    mat_hair = make_toon_source_material("MatHairSlateTeal", 0x25323A)

    n_seg = 56
    n_rings = 16
    head_cy = 0.024
    head_cz = 1.452
    skull_rx = 0.122
    skull_ry_front = 0.130
    skull_ry_back = 0.142
    z_crown = 1.602

    rings = []
    for r_idx in range(n_rings):
        v_t = r_idx / (n_rings - 1)
        ring = []
        for s in range(n_seg):
            ang = (2.0 * math.pi * s) / n_seg
            ca, sa = math.cos(ang), math.sin(ang)

            r_flick = 0.0
            if sa > 0.44:
                bang_notches = abs(math.sin(ca * 8.5 + 0.25)) ** 1.35
                z_hem = 1.448 + 0.024 * bang_notches
                r_flick = 0.003 * (1.0 - bang_notches)
            elif sa > 0.10:
                sb_t = (sa - 0.10) / 0.34
                z_hem = 1.415 + 0.036 * (sb_t**1.5)
                r_flick = 0.002
            elif sa > -0.28:
                ear_arch = math.sin(((sa + 0.28) / 0.38) * math.pi)
                z_hem = 1.404 + 0.058 * (ear_arch**0.72)
                r_flick = 0.002
            else:
                nape_wave = math.cos(ang * 7.0 + 0.35)
                z_hem = 1.344 + 0.016 * nape_wave
                r_flick = 0.022 * (0.45 + 0.55 * (max(0.0, -nape_wave) ** 1.3))

            z = z_hem + (z_crown - z_hem) * (v_t**0.88)

            nz = (z - head_cz) / (z_crown - head_cz)
            if nz >= 0.0:
                ellipsoid_r = math.sqrt(max(0.002, 1.0 - (min(0.999, nz) ** 2.05)))
            else:
                ellipsoid_r = 1.0 - 0.34 * (abs(nz) ** 1.35)

            back_w = max(0.0, -sa)
            side_back_w = max(0.0, -sa * 0.75 + abs(ca) * 0.45) if sa < 0.05 else 0.0
            hem_w = max(0.0, 1.0 - v_t / 0.48)
            tier_wave = (
                0.018
                * (max(0.0, math.sin(v_t * math.pi * 5.2 + ang * 2.0)) ** 1.25)
                * (side_back_w**0.65)
                if v_t < 0.62 and sa < 0.0
                else 0.0
            )
            flick = r_flick * (hem_w**1.4) + tier_wave

            ry_base = skull_ry_front if sa >= 0.0 else skull_ry_back
            rx_tuck = 0.014 * max(0.0, -nz) * (1.0 - 0.55 * back_w) if nz < 0.0 else 0.0
            rx = (skull_rx - rx_tuck) * ellipsoid_r + flick * 0.85
            ry = ry_base * ellipsoid_r + flick

            ring.append((ca * rx, head_cy + sa * ry, z))
        rings.append(ring)

    hair_obj = make_loft_from_rings("ShaggyHairMale", rings, mat_hair, cap_end=True, smooth=True)
    bpy.context.view_layer.objects.active = hair_obj
    hair_obj.select_set(True)
    solid = hair_obj.modifiers.new("Solidify", "SOLIDIFY")
    solid.thickness = 0.012
    solid.offset = 1.0
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.shade_smooth()
    hair_obj.select_set(False)

    return join_parts_into_slot_mesh([hair_obj], "HairMesh")


def build_hair_twin_buns_female():
    """
    Builds the default Female dark bob hair with swept bangs, visible ear cutouts, chunky
    rounded nape bob curve, and upper-back twin buns with golden-yellow hair ties as `HairMesh`.
    """
    mat_hair = make_toon_source_material("MatHairDarkBob", 0x1F242B)
    mat_tie = make_toon_source_material("MatHairTieYellow", 0xE9A82B)
    parts = []

    n_seg = 56
    n_rings = 16
    head_cy = 0.024
    head_cz = 1.452
    skull_rx = 0.123
    skull_ry_front = 0.130
    skull_ry_back = 0.144
    z_crown = 1.602

    rings = []
    for r_idx in range(n_rings):
        v_t = r_idx / (n_rings - 1)
        ring = []
        for s in range(n_seg):
            ang = (2.0 * math.pi * s) / n_seg
            ca, sa = math.cos(ang), math.sin(ang)

            b_swell = 0.0
            if sa > 0.44:
                # Swept asymmetric female bangs above eyebrows
                bang_notches = abs(math.sin(ca * 7.2 - 0.45)) ** 1.4
                z_hem = 1.450 + 0.022 * bang_notches
            elif sa > 0.10:
                # Curved sideburn lock in front of ear
                sb_t = (sa - 0.10) / 0.34
                z_hem = 1.416 + 0.036 * (sb_t**1.5)
            elif sa > -0.26:
                # High ear arch so the sculpted ear is clearly visible!
                ear_arch = math.sin(((sa + 0.26) / 0.36) * math.pi)
                z_hem = 1.404 + 0.056 * (ear_arch**0.72)
            else:
                # Chunky rounded bob nape hemline at z = 1.355
                z_hem = 1.356 + 0.006 * math.cos(ang * 2.0)
                # Signature rounded bob cushion fullness at the lower back nape
                b_swell = 0.022 * math.sin(min(1.0, v_t / 0.48) * math.pi) * (max(0.0, -sa) ** 0.8)

            z = z_hem + (z_crown - z_hem) * (v_t**0.88)

            nz = (z - head_cz) / (z_crown - head_cz)
            if nz >= 0.0:
                ellipsoid_r = math.sqrt(max(0.002, 1.0 - (min(0.999, nz) ** 2.05)))
            else:
                ellipsoid_r = 1.0 - 0.22 * (abs(nz) ** 1.4)

            ry_base = skull_ry_front if sa >= 0.0 else skull_ry_back
            rx = skull_rx * ellipsoid_r + b_swell * 0.65
            ry = ry_base * ellipsoid_r + b_swell
            ring.append((ca * rx, head_cy + sa * ry, z))
        rings.append(ring)

    bob_obj = make_loft_from_rings("BobHairFemale", rings, mat_hair, cap_end=True, smooth=True)
    bpy.context.view_layer.objects.active = bob_obj
    bob_obj.select_set(True)
    solid = bob_obj.modifiers.new("Solidify", "SOLIDIFY")
    solid.thickness = 0.012
    solid.offset = 1.0
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.shade_smooth()
    bob_obj.select_set(False)
    parts.append(bob_obj)

    # Large twin buns on the upper-back crown + golden-yellow hair ties
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_cube_add(size=0.148, location=(0.0, 0.0, 0.0))
        bun = bpy.context.active_object
        bun.name = f"HairBun_{'L' if side < 0 else 'R'}"
        bsub = bun.modifiers.new("Subsurf", "SUBSURF")
        bsub.levels = 2
        bsub.render_levels = 2
        bpy.ops.object.modifier_apply(modifier="Subsurf")
        bun.scale = (1.02, 0.96, 0.94)
        bun.location = (side * 0.118, -0.056, 1.568)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        bun.data.materials.append(mat_hair)
        bun.select_set(False)
        parts.append(bun)

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.064,
            minor_radius=0.012,
            major_segments=24,
            minor_segments=10,
            location=(side * 0.102, -0.044, 1.554),
            rotation=(-0.38, side * 0.68, 0.0),
        )
        tie = bpy.context.active_object
        tie.name = f"HairTie_{'L' if side < 0 else 'R'}"
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        tie.data.materials.append(mat_tie)
        tie.select_set(False)
        parts.append(tie)

    return join_parts_into_slot_mesh(parts, "HairMesh")
