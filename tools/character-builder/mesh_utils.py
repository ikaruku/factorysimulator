"""
Shared Blender BMesh lofting, material, and slot-joining utilities for modular character parts.
"""

import bmesh
import bpy


def make_toon_source_material(name, hex_rgb):
    """Creates or reuses a flat matte Principled BSDF material for glTF export."""
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    r = ((hex_rgb >> 16) & 255) / 255.0
    g = ((hex_rgb >> 8) & 255) / 255.0
    b = (hex_rgb & 255) / 255.0
    lin = tuple(pow(c, 2.2) for c in (r, g, b))
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.90
    mat.diffuse_color = (*lin, 1.0)
    return mat


def make_loft_from_rings(
    name,
    rings_verts_xyz,
    mat,
    cap_start=False,
    cap_end=False,
    smooth=True,
    sharp_ring_indices=(),
):
    """Creates a quad mesh by lofting 3D vertex rings, with optional flat-creased fold bands."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()
    bm_rings = []
    for ring_coords in rings_verts_xyz:
        bm_rings.append([bm.verts.new(co) for co in ring_coords])

    sharp_set = set(sharp_ring_indices)
    n_seg = len(bm_rings[0])
    for i in range(len(bm_rings) - 1):
        r0, r1 = bm_rings[i], bm_rings[i + 1]
        is_band_smooth = smooth and (i not in sharp_set)
        for s in range(n_seg):
            sn = (s + 1) % n_seg
            f = bm.faces.new((r0[s], r0[sn], r1[sn], r1[s]))
            f.smooth = is_band_smooth

    if cap_start and bm_rings:
        f0 = bm.faces.new(list(reversed(bm_rings[0])))
        f0.smooth = smooth
    if cap_end and bm_rings:
        f1 = bm.faces.new(bm_rings[-1])
        f1.smooth = smooth

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj.data.materials.append(mat)
    return obj


def make_box_plate(name, x0, x1, y0, y1, z0, z1, mat):
    """Creates an axis-aligned 3D rectangular block with sharp edges for crisp outline borders."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()

    v000 = bm.verts.new((x0, y0, z0))
    v100 = bm.verts.new((x1, y0, z0))
    v110 = bm.verts.new((x1, y1, z0))
    v010 = bm.verts.new((x0, y1, z0))
    v001 = bm.verts.new((x0, y0, z1))
    v101 = bm.verts.new((x1, y0, z1))
    v111 = bm.verts.new((x1, y1, z1))
    v011 = bm.verts.new((x0, y1, z1))

    bm.faces.new((v000, v010, v110, v100))
    bm.faces.new((v001, v101, v111, v011))
    bm.faces.new((v000, v100, v101, v001))
    bm.faces.new((v010, v011, v111, v110))
    bm.faces.new((v000, v001, v011, v010))
    bm.faces.new((v100, v110, v111, v101))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)
    return obj


def join_parts_into_slot_mesh(parts, slot_mesh_name):
    """Joins a list of sub-meshes into a single named modular slot mesh with identity transform."""
    if not parts:
        raise ValueError(f"Cannot create empty slot mesh {slot_mesh_name}")

    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    slot_obj = bpy.context.active_object
    slot_obj.name = slot_mesh_name
    slot_obj.data.name = f"{slot_mesh_name}Data"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    slot_obj.data.validate(clean_customdata=False)
    slot_obj.data.update()
    slot_obj.select_set(False)
    return slot_obj
