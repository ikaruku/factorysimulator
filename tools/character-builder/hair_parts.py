"""
Modular `HairMesh` slot builders for Male & Female Abeto character presets:
- `build_hair_shaggy_male()`: continuous sculpted slate-teal shaggy mop hair (#25323A) with
  jagged V-notched bangs, sideburns, ear arches, and wavy nape tufts.
- `build_hair_twin_buns_female()`: precision sculpted dark bob hair (#1F242B) matching the
  4 Female reference images (Back, Front, Left, Right):
  * Smooth swept front bangs with asymmetric brow notches (Image 2)
  * Curved comma-shaped sideburn lock in front of each ear (Images 2, 3, 4)
  * Full ear-arch cutout so both rounded ears project clearly in Front, Back, Left, and Right
  * Compact squared-off lower nape bob (`x = +-0.088` in Front/Back, bulging backward in Side views)
  * Coaxially-oriented upper-back twin buns with golden-yellow hair ties (#E5A530) showing the
    exact diagonal golden band at the base of each bun in Front (Image 2) and Back (Image 1).
"""

import math
import bpy
from mathutils import Vector
from mesh_utils import join_parts_into_slot_mesh, make_loft_from_rings, make_toon_source_material
from rig_builder import assign_part_weights


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
    assign_part_weights(hair_obj, "hair")

    return join_parts_into_slot_mesh([hair_obj], "HairMesh")


def build_hair_twin_buns_female():
    """
    Builds the default Female dark bob hair with swept bangs, curved sideburns, exposed ears,
    compact squared-off nape bob, and coaxially-tied upper-back twin buns as `HairMesh`.
    """
    mat_hair = make_toon_source_material("MatHairDarkBob", 0x1F242B)
    mat_tie = make_toon_source_material("MatHairTieYellow", 0xE5A530)
    parts = []

    n_seg = 60
    n_rings = 16
    head_cy = 0.024
    head_cz = 1.452
    skull_rx = 0.121
    skull_ry_front = 0.129
    skull_ry_back = 0.144
    z_crown = 1.598

    rings = []
    for r_idx in range(n_rings):
        v_t = r_idx / (n_rings - 1)
        ring = []
        for s in range(n_seg):
            ang = (2.0 * math.pi * s) / n_seg
            ca, sa = math.cos(ang), math.sin(ang)

            b_swell = 0.0
            if sa > 0.44:
                # Swept central bangs staying cleanly ABOVE both eyebrows (z = 1.464..1.484, Image 2!)
                n1 = math.exp(-(((ca - 0.44) / 0.13) ** 2))
                n2 = math.exp(-(((ca + 0.48) / 0.14) ** 2))
                z_hem = 1.464 + 0.018 * n1 + 0.015 * n2
            elif sa > 0.12:
                # Distinct curved comma-shaped sideburn lock in front of each ear (Images 2, 3, 4!)
                sb_t = (sa - 0.12) / 0.32
                comma_drop = math.sin(sb_t * math.pi)
                z_hem = 1.440 - 0.026 * comma_drop + 0.026 * (sb_t**1.5)
            elif sa > -0.34:
                # High ear cutout arch so the entire rounded ear projects out clearly in Front & Back!
                ear_arch = math.sin(((sa + 0.34) / 0.46) * math.pi)
                z_hem = 1.382 + 0.086 * (ear_arch**0.66)
            else:
                # Squared-off compact nape bob hemline at z = 1.356 (Images 1, 3, 4!)
                z_hem = 1.356
                # Angular 3-facet bob bulge backward in Side views (Images 3 & 4)
                b_swell = 0.028 * math.sin(min(1.0, v_t / 0.46) * math.pi) * (max(0.0, -sa) ** 0.75)

            z = z_hem + (z_crown - z_hem) * (v_t**0.88)

            nz = (z - head_cz) / (z_crown - head_cz)
            if nz >= 0.0:
                ellipsoid_r = math.sqrt(max(0.002, 1.0 - (min(0.999, nz) ** 2.05)))
            else:
                ellipsoid_r = 1.0 - 0.28 * (abs(nz) ** 1.35)

            ry_base = skull_ry_front if sa >= 0.0 else skull_ry_back
            # Tuck the lower back bob laterally (`x`) below the ears so in Front view (Image 2)
            # NO wide bob curtain sticks out below the ears, and in Back view (Image 1) the
            # compact squared-off bob is narrower than the projecting ears!
            lower_bob_narrow = 0.045 * max(0.0, -nz) * (max(0.0, -sa) ** 0.65) if nz < 0.0 else 0.0
            rx = (skull_rx - lower_bob_narrow) * ellipsoid_r + b_swell * 0.18
            ry = ry_base * ellipsoid_r + b_swell

            # Forward hook on the tip of the comma sideburn in Side views (Images 3 & 4)
            if 0.12 < sa <= 0.44 and v_t < 0.25:
                ry += 0.010 * (1.0 - v_t / 0.25)

            ring.append((ca * rx, head_cy + sa * ry, z))
        rings.append(ring)

    bob_obj = make_loft_from_rings("BobHairFemale", rings, mat_hair, cap_end=True, smooth=True)
    bpy.context.view_layer.objects.active = bob_obj
    bob_obj.select_set(True)
    solid = bob_obj.modifiers.new("Solidify", "SOLIDIFY")
    solid.thickness = 0.011
    solid.offset = 1.0
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.shade_smooth()
    bob_obj.select_set(False)
    parts.append(bob_obj)

    # Coaxially-oriented upper-back twin buns + golden-yellow hair ties (Images 1, 2, 3, 4!)
    # Measured directly from the skull ellipsoid center (0, 0.024, 1.452) so the golden hair tie
    # sits right on the outer hair dome surface (r = 0.124 m) around the bun neck and is 100%
    # visible in Front (Image 2), Back (Image 1), Left (Image 3), and Right (Image 4)!
    skull_center = Vector((0.0, 0.024, 1.452))
    for side in (-1.0, 1.0):
        bun_center = Vector((side * 0.122, -0.022, 1.556))
        axis = (bun_center - skull_center).normalized()
        rot_quat = axis.to_track_quat("Z", "Y")
        rot_euler = rot_quat.to_euler()

        # Slightly flattened chignon bun aligned with `axis`
        bpy.ops.mesh.primitive_cube_add(size=0.136, location=(0.0, 0.0, 0.0))
        bun = bpy.context.active_object
        bun.name = f"HairBun_{'L' if side < 0 else 'R'}"
        bsub = bun.modifiers.new("Subsurf", "SUBSURF")
        bsub.levels = 2
        bsub.render_levels = 2
        bpy.ops.object.modifier_apply(modifier="Subsurf")
        bun.scale = (1.00, 1.00, 0.82)
        bun.rotation_euler = rot_euler
        bun.location = bun_center
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        bun.data.materials.append(mat_hair)
        bun.select_set(False)
        parts.append(bun)

        tie_center = skull_center.lerp(bun_center, 0.74)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.062,
            minor_radius=0.0135,
            major_segments=24,
            minor_segments=10,
            location=tie_center,
            rotation=rot_euler,
        )
        tie = bpy.context.active_object
        tie.name = f"HairTie_{'L' if side < 0 else 'R'}"
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        tie.data.materials.append(mat_tie)
        tie.select_set(False)
        parts.append(tie)

    for part in parts:
        assign_part_weights(part, "hair")
    return join_parts_into_slot_mesh(parts, "HairMesh")
