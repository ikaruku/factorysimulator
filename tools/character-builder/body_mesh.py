"""
Stage 1B-K2/K3: Modular `BodyMesh` builder for Male & Female Abeto characters.

Produces the `BodyMesh` slot object containing:
- Slender ~5.8-head human body with full forearms (compatible with both long-sleeve hoodies
  and short-sleeve T-shirts), stylized anime hands (distinct thumb + curled finger block),
  and bare lower calves (`z = 0.24..0.31`).
- Sculpted 3D anime head with V-oval front jawline, horizontal under-jaw plane, upturned nose
  tip, exposed sculpted ears, and cylindrical 1024x1024 face UV mapping.
"""

import math
import bmesh
import bpy
from mesh_utils import join_parts_into_slot_mesh, make_toon_source_material
from textures import create_face_material


def _build_skin_body_mesh(mat_skin):
    """Creates the slender anime base body (neck, core, full forearms, hands, lower legs)."""
    mesh = bpy.data.meshes.new("HumanBodySkinData")
    obj = bpy.data.objects.new("HumanBodySkin", mesh)
    bpy.context.scene.collection.objects.link(obj)

    nodes = [
        # Slender spine + short natural forward-inclined neck (0..5)
        (0.0, 0.0, 0.80, 0.092, 0.072),  # 0: pelvis
        (0.0, 0.004, 0.95, 0.090, 0.070),  # 1: waist
        (0.0, 0.006, 1.12, 0.098, 0.074),  # 2: chest
        (0.0, 0.006, 1.245, 0.088, 0.068),  # 3: upper chest
        (0.0, 0.015, 1.320, 0.043, 0.044),  # 4: neck mid
        (0.0, 0.024, 1.400, 0.043, 0.044),  # 5: neck inside skull base
        # Right arm chain (6..10) - fits cleanly inside long hoodie sleeves AND looks great in short sleeves!
        (0.135, -0.006, 1.225, 0.040, 0.040),  # 6: shoulder
        (0.172, -0.016, 1.105, 0.036, 0.036),  # 7: upper arm
        (0.192, -0.022, 0.985, 0.034, 0.034),  # 8: elbow
        (0.196, 0.012, 0.865, 0.031, 0.031),  # 9: forearm
        (0.194, 0.044, 0.768, 0.026, 0.025),  # 10: wrist
        # Right leg chain (11..18) - natural slender stance at x = 0.082
        (0.078, 0.0, 0.765, 0.060, 0.060),  # 11: hip
        (0.081, 0.004, 0.600, 0.054, 0.054),  # 12: thigh
        (0.082, 0.006, 0.435, 0.045, 0.045),  # 13: knee
        (0.082, -0.002, 0.275, 0.042, 0.043),  # 14: exposed bare lower calf (z=0.24..0.31)
        (0.082, -0.002, 0.120, 0.036, 0.037),  # 15: ankle
        (0.082, -0.018, 0.040, 0.035, 0.035),  # 16: heel
        (0.084, 0.048, 0.040, 0.037, 0.035),  # 17: midfoot
        (0.086, 0.108, 0.040, 0.034, 0.028),  # 18: toes
    ]

    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
        (3, 6),
        (6, 7),
        (7, 8),
        (8, 9),
        (9, 10),
        (0, 11),
        (11, 12),
        (12, 13),
        (13, 14),
        (14, 15),
        (15, 16),
        (15, 17),
        (17, 18),
    ]

    bm = bmesh.new()
    verts = [bm.verts.new((n[0], n[1], n[2])) for n in nodes]
    for a, b in edges:
        bm.edges.new((verts[a], verts[b]))
    bm.to_mesh(mesh)
    bm.free()

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    mirror = obj.modifiers.new("Mirror", "MIRROR")
    mirror.use_axis[0] = True
    mirror.use_clip = True
    mirror.merge_threshold = 0.005

    skin = obj.modifiers.new("Skin", "SKIN")
    skin.use_smooth_shade = True
    skin.branch_smoothing = 0.35

    skin_verts = obj.data.skin_vertices[0].data
    for idx, node in enumerate(nodes):
        sv = skin_verts[idx]
        sv.radius = (node[3], node[4])
        sv.use_root = idx == 0

    subsurf = obj.modifiers.new("Subsurf", "SUBSURF")
    subsurf.levels = 2
    subsurf.render_levels = 2

    for mod_name in ("Mirror", "Skin", "Subsurf"):
        bpy.ops.object.modifier_apply(modifier=mod_name)

    min_z = min(v.co.z for v in obj.data.vertices)
    for v in obj.data.vertices:
        v.co.z -= min_z
        if v.co.z < 0.016:
            v.co.z = 0.0

    obj.data.update()
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat_skin)
    obj.select_set(False)
    return obj


def _build_stylized_hands(mat_skin):
    """Builds expressive anime hands with a distinct inner-front thumb and curled finger block."""
    hands = []
    for side in (-1.0, 1.0):
        wx = side * 0.194
        wy = 0.046

        bpy.ops.mesh.primitive_cube_add(size=0.072, location=(0.0, 0.0, 0.0))
        palm = bpy.context.active_object
        palm.name = f"HandPalm_{'L' if side < 0 else 'R'}"
        sub = palm.modifiers.new("Subsurf", "SUBSURF")
        sub.levels = 2
        sub.render_levels = 2
        bpy.ops.object.modifier_apply(modifier="Subsurf")

        for v in palm.data.vertices:
            if v.co.z < 0.0:
                curl = abs(v.co.z) / 0.036
                v.co.x -= side * 0.010 * (curl**1.3)
                v.co.y *= 0.88
            else:
                v.co.x *= 0.78

        palm.scale = (0.72, 0.90, 1.48)
        palm.rotation_euler = (0.14, side * 0.10, side * -0.15)
        palm.location = (wx + side * 0.002, wy + 0.004, 0.724)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        palm.data.materials.append(mat_skin)
        palm.select_set(False)
        hands.append(palm)

        bpy.ops.mesh.primitive_cube_add(size=0.044, location=(0.0, 0.0, 0.0))
        thumb = bpy.context.active_object
        thumb.name = f"HandThumb_{'L' if side < 0 else 'R'}"
        tsub = thumb.modifiers.new("Subsurf", "SUBSURF")
        tsub.levels = 2
        tsub.render_levels = 2
        bpy.ops.object.modifier_apply(modifier="Subsurf")
        thumb.scale = (0.58, 0.74, 1.18)
        thumb.rotation_euler = (0.38, side * -0.32, 0.0)
        thumb.location = (wx - side * 0.018, wy + 0.028, 0.718)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        thumb.data.materials.append(mat_skin)
        thumb.select_set(False)
        hands.append(thumb)

    return hands


def _build_stylized_head(mat_skin, mat_face):
    """Creates the sculpted Abeto anime head centered at (0, 0.024, 1.452) with exposed ears."""
    bpy.ops.mesh.primitive_cube_add(size=0.256, location=(0.0, 0.0, 0.0))
    head = bpy.context.active_object
    head.name = "HumanHead"

    sub = head.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 3
    sub.render_levels = 3
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    ref_r = 0.128
    head_cy = 0.024
    head_cz = 1.452

    for v in head.data.vertices:
        x, y, z = v.co.x, v.co.y, v.co.z
        nx = x / ref_r
        ny = y / ref_r
        nz = z / ref_r

        x *= 0.88
        y *= 0.95
        z *= 1.05

        if nz < 0.08:
            jaw_t = min(1.0, (0.08 - nz) / 0.96)
            corner_hold = 0.06 * math.exp(-(((jaw_t - 0.36) / 0.16) ** 2)) * min(1.0, abs(nx))
            x *= (1.0 - 0.44 * (jaw_t**1.35)) + corner_hold

            if ny > -0.12:
                y *= 1.0 - 0.06 * (jaw_t**1.3)
                chin_x = math.exp(-((nx / 0.38) ** 2))
                chin_z = math.exp(-(((nz + 0.58) / 0.24) ** 2))
                y += 0.022 * chin_x * chin_z

                lip_x = math.exp(-((nx / 0.34) ** 2))
                lip_z = math.exp(-(((nz + 0.32) / 0.12) ** 2))
                y -= 0.006 * lip_x * lip_z
            else:
                y *= 1.0 - 0.28 * (jaw_t**1.2)

        if ny > 0.30:
            if abs(nx) > 0.34 and -0.38 < nz < 0.18:
                y -= 0.007 * (abs(nx) - 0.34)

            nas_x = math.exp(-((nx / 0.20) ** 2))
            nas_z = math.exp(-(((nz - 0.14) / 0.10) ** 2))
            y -= 0.007 * nas_x * nas_z

            nose_x = math.exp(-((nx / 0.14) ** 2))
            nose_z = math.exp(-(((nz + 0.10) / 0.14) ** 2))
            y += 0.025 * nose_x * nose_z

        v.co = (x, y + head_cy, z + head_cz)

    head.data.update()
    bpy.ops.object.shade_smooth()
    head.data.materials.append(mat_skin)

    ears = []
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_cube_add(size=0.062, location=(0.0, 0.0, 0.0))
        ear = bpy.context.active_object
        ear.name = f"Ear_{'L' if side < 0 else 'R'}"
        esub = ear.modifiers.new("Subsurf", "SUBSURF")
        esub.levels = 2
        esub.render_levels = 2
        bpy.ops.object.modifier_apply(modifier="Subsurf")
        ear.scale = (0.46, 0.72, 1.00)
        ear.rotation_euler = (-0.15, side * -0.22, side * 0.26)
        ear.location = (side * 0.102, 0.012, 1.426)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        ear.data.materials.append(mat_skin)
        ears.append(ear)

    bpy.ops.object.select_all(action="DESELECT")
    head.select_set(True)
    for ear in ears:
        ear.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()

    # Cylindrical angular UV projection on front & lateral eye sockets
    mesh = head.data
    mesh.materials.clear()
    mesh.materials.append(mat_skin)
    mesh.materials.append(mat_face)

    uv_layer = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
    uv_layer.name = "UVMap"

    for poly in mesh.polygons:
        c = poly.center
        is_face = c.y > 0.042 and abs(c.x) < 0.090 and 1.360 < c.z < 1.528
        poly.material_index = 1 if is_face else 0
        for loop_idx in poly.loop_indices:
            v = mesh.vertices[mesh.loops[loop_idx].vertex_index].co
            theta = math.atan2(v.x, max(0.01, v.y - head_cy))
            u = max(0.01, min(0.99, 0.5 - theta / 1.44))
            nv = max(0.01, min(0.99, (v.z - 1.362) / 0.165))
            uv_layer.data[loop_idx].uv = (u, nv)

    head.select_set(False)
    return head


def build_body_slot_mesh(gender="male"):
    """Builds and returns the unified `BodyMesh` slot object for the given gender."""
    mat_skin = make_toon_source_material("MatHumanSkin", 0xCFB6BA)
    mat_face = create_face_material(gender=gender)

    body = _build_skin_body_mesh(mat_skin)
    hands = _build_stylized_hands(mat_skin)
    head = _build_stylized_head(mat_skin, mat_face)
    return join_parts_into_slot_mesh([body, *hands, head], "BodyMesh")
