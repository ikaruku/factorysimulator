"""
Stage 1B-K4: Canonical 22-bone Humanoid Armature & Slot-Aware Analytical Smooth Skinning.

Shared identically across Male, Female, and all future modular character presets so
`BodyMesh`, `HairMesh`, `TopMesh`, `BottomMesh`, `ShoesMesh`, and `BagMesh` can be
interchanged freely at runtime with identical bone names and smooth joint deformation.

Coordinate convention in Blender:
  +X = character right, -X = character left, +Y = front, +Z = up, feet grounded at z = 0.
"""

import math
import bpy
from mathutils import Vector

# Canonical 22-bone humanoid rig definition: (name, parent_name, head_xyz, tail_xyz)
HUMANOID_BONES = (
    ("Hips", None, (0.0, 0.000, 0.780), (0.0, 0.002, 0.900)),
    ("Spine", "Hips", (0.0, 0.002, 0.900), (0.0, 0.005, 1.070)),
    ("Chest", "Spine", (0.0, 0.005, 1.070), (0.0, 0.008, 1.275)),
    ("Neck", "Chest", (0.0, 0.008, 1.275), (0.0, 0.020, 1.380)),
    ("Head", "Neck", (0.0, 0.020, 1.380), (0.0, 0.024, 1.605)),
    ("BagRoot", "Chest", (0.0, -0.080, 1.040), (0.0, -0.220, 1.040)),
    # Left Arm (-X)
    ("Shoulder.L", "Chest", (-0.045, 0.000, 1.235), (-0.135, -0.006, 1.225)),
    ("UpperArm.L", "Shoulder.L", (-0.135, -0.006, 1.225), (-0.192, -0.022, 0.985)),
    ("LowerArm.L", "UpperArm.L", (-0.192, -0.022, 0.985), (-0.196, 0.044, 0.768)),
    ("Hand.L", "LowerArm.L", (-0.196, 0.044, 0.768), (-0.196, 0.052, 0.665)),
    # Right Arm (+X)
    ("Shoulder.R", "Chest", (0.045, 0.000, 1.235), (0.135, -0.006, 1.225)),
    ("UpperArm.R", "Shoulder.R", (0.135, -0.006, 1.225), (0.192, -0.022, 0.985)),
    ("LowerArm.R", "UpperArm.R", (0.192, -0.022, 0.985), (0.196, 0.044, 0.768)),
    ("Hand.R", "LowerArm.R", (0.196, 0.044, 0.768), (0.196, 0.052, 0.665)),
    # Left Leg (-X)
    ("Thigh.L", "Hips", (-0.081, 0.002, 0.765), (-0.081, 0.006, 0.450)),
    ("Shin.L", "Thigh.L", (-0.081, 0.006, 0.450), (-0.081, -0.002, 0.120)),
    ("Foot.L", "Shin.L", (-0.081, -0.002, 0.120), (-0.083, 0.075, 0.032)),
    ("Toe.L", "Foot.L", (-0.083, 0.075, 0.032), (-0.085, 0.145, 0.028)),
    # Right Leg (+X)
    ("Thigh.R", "Hips", (0.081, 0.002, 0.765), (0.081, 0.006, 0.450)),
    ("Shin.R", "Thigh.R", (0.081, 0.006, 0.450), (0.081, -0.002, 0.120)),
    ("Foot.R", "Shin.R", (0.081, -0.002, 0.120), (0.083, 0.075, 0.032)),
    ("Toe.R", "Foot.R", (0.083, 0.075, 0.032), (0.085, 0.145, 0.028)),
)

BONE_NAMES = tuple(b[0] for b in HUMANOID_BONES)


def _smoothstep(edge0, edge1, x):
    if edge1 <= edge0:
        return 1.0 if x >= edge1 else 0.0
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def _add_normalized_weights(vg_map, v_idx, raw_weights):
    """Normalizes vertex weights (max 4 strongest influences for WebGL2/glTF compliance)."""
    filtered = [(name, w) for name, w in raw_weights.items() if w > 1e-4]
    if not filtered:
        vg_map["Hips"].add([v_idx], 1.0, "REPLACE")
        return
    filtered.sort(key=lambda item: item[1], reverse=True)
    top4 = filtered[:4]
    total = sum(w for _, w in top4)
    for name, w in top4:
        vg_map[name].add([v_idx], w / total, "REPLACE")


def _spine_chain_weights(z):
    """Smooth vertical weight distribution along Hips -> Spine -> Chest -> Neck -> Head."""
    if z <= 0.84:
        return {"Hips": 1.0}
    if z < 0.96:
        t = _smoothstep(0.84, 0.96, z)
        return {"Hips": 1.0 - t, "Spine": t}
    if z < 1.03:
        return {"Spine": 1.0}
    if z < 1.15:
        t = _smoothstep(1.03, 1.15, z)
        return {"Spine": 1.0 - t, "Chest": t}
    if z < 1.25:
        return {"Chest": 1.0}
    if z < 1.32:
        t = _smoothstep(1.25, 1.32, z)
        return {"Chest": 1.0 - t, "Neck": t}
    if z < 1.39:
        t = _smoothstep(1.32, 1.39, z)
        return {"Neck": 1.0 - t, "Head": t}
    return {"Head": 1.0}


def _arm_chain_weights(x, z, side_suffix):
    """Smooth axial weight distribution along Chest -> Shoulder -> UpperArm -> LowerArm -> Hand."""
    abs_x = abs(x)
    sh_name = f"Shoulder.{side_suffix}"
    ua_name = f"UpperArm.{side_suffix}"
    la_name = f"LowerArm.{side_suffix}"
    hd_name = f"Hand.{side_suffix}"

    # Shoulder cap blending from torso Chest -> Shoulder -> UpperArm
    if z >= 1.14 and abs_x < 0.165:
        chest_to_sh = _smoothstep(0.088, 0.128, abs_x)
        sh_to_ua = _smoothstep(0.122, 0.162, abs_x)
        w_chest = 1.0 - chest_to_sh
        w_ua = chest_to_sh * sh_to_ua
        w_sh = chest_to_sh * (1.0 - sh_to_ua)
        return {"Chest": w_chest, sh_name: w_sh, ua_name: w_ua}

    # Elbow smooth blend (joint at z = 0.985, wider blend band 0.925..1.045 for rounder bends)
    if z > 1.045:
        sh_blend = _smoothstep(1.16, 1.24, z) * (1.0 - _smoothstep(0.145, 0.180, abs_x))
        return {ua_name: 1.0 - sh_blend, sh_name: sh_blend}
    if z >= 0.925:
        t = _smoothstep(0.925, 1.045, z)
        return {la_name: 1.0 - t, ua_name: t}

    # Wrist smooth blend (joint at z = 0.768, blend band 0.745..0.790)
    if z > 0.790:
        return {la_name: 1.0}
    if z >= 0.745:
        t = _smoothstep(0.745, 0.790, z)
        return {hd_name: 1.0 - t, la_name: t}
    return {hd_name: 1.0}


def _leg_chain_weights(x, y, z, side_suffix, is_garment=False):
    """Smooth axial weight distribution along Hips -> Thigh -> Shin -> Foot -> Toe."""
    th_name = f"Thigh.{side_suffix}"
    sh_name = f"Shin.{side_suffix}"
    ft_name = f"Foot.{side_suffix}"
    to_name = f"Toe.{side_suffix}"

    # Upper hip / pelvis union band (prevents crotch/waist tearing when legs stride wide!)
    hip_low = 0.62 if is_garment else 0.67
    hip_high = 0.77 if is_garment else 0.79
    if z >= hip_high:
        return {"Hips": 1.0}
    if z > hip_low:
        t_hips = _smoothstep(hip_low, hip_high, z)
        # Keep midline crotch seam anchored gently toward Hips
        mid_anchor = (1.0 - _smoothstep(0.008, 0.048, abs(x))) * _smoothstep(0.55, 0.66, z)
        w_hips = max(t_hips, mid_anchor * 0.85)
        return {"Hips": w_hips, th_name: 1.0 - w_hips}

    # Knee smooth blend (joint at z = 0.450, blend band 0.400..0.500)
    if z > 0.500:
        return {th_name: 1.0}
    if z >= 0.400:
        t = _smoothstep(0.400, 0.500, z)
        return {sh_name: 1.0 - t, th_name: t}

    # Ankle smooth blend (joint at z = 0.120, blend band 0.090..0.155)
    if z > 0.155:
        return {sh_name: 1.0}
    if z >= 0.090:
        t = _smoothstep(0.090, 0.155, z)
        return {ft_name: 1.0 - t, sh_name: t}

    # Toe flex blend along foot length (ball of foot at y = 0.075)
    t_toe = _smoothstep(0.062, 0.095, y)
    return {ft_name: 1.0 - t_toe, to_name: t_toe}


def assign_part_weights(obj, role):
    """
    Creates the canonical 22 vertex groups on `obj` and assigns smooth, artifact-free
    analytical skin weights according to the sub-part's anatomical/garment `role`.
    """
    vg_map = {}
    for bname in BONE_NAMES:
        vg = obj.vertex_groups.get(bname) or obj.vertex_groups.new(name=bname)
        vg_map[bname] = vg

    for v in obj.data.vertices:
        x, y, z = v.co.x, v.co.y, v.co.z
        w = {}

        if role == "hair":
            w = {"Head": 1.0}

        elif role == "head":
            if z >= 1.385:
                w = {"Head": 1.0}
            else:
                t = _smoothstep(1.345, 1.385, z)
                w = {"Neck": 1.0 - t, "Head": t}

        elif role in ("hand_L", "hand_R"):
            suffix = "L" if role.endswith("_L") else "R"
            if z < 0.750:
                w = {f"Hand.{suffix}": 1.0}
            else:
                t = _smoothstep(0.750, 0.785, z)
                w = {f"Hand.{suffix}": 1.0 - t, f"LowerArm.{suffix}": t}

        elif role == "body_skin":
            if z < 0.775 and abs(x) < 0.155:
                suffix = "L" if x < 0.0 else "R"
                w = _leg_chain_weights(x, y, z, suffix, is_garment=False)
            elif abs(x) >= 0.118 and 0.65 <= z <= 1.275:
                suffix = "L" if x < 0.0 else "R"
                w = _arm_chain_weights(x, z, suffix)
            else:
                w = _spine_chain_weights(z)

        elif role == "torso":
            # Strictly spine chain -> arms NEVER pull the side of the hoodie or T-shirt!
            w = _spine_chain_weights(min(z, 1.32))

        elif role == "hood":
            if z <= 1.295:
                w = {"Chest": 1.0}
            else:
                t = _smoothstep(1.295, 1.355, z)
                w = {"Chest": 1.0 - 0.35 * t, "Neck": 0.35 * t}

        elif role in ("sleeve_L", "sleeve_R"):
            suffix = "L" if role.endswith("_L") else "R"
            w = _arm_chain_weights(x, z, suffix)

        elif role in ("leg_L", "leg_R"):
            suffix = "L" if role.endswith("_L") else "R"
            w = _leg_chain_weights(x, y, z, suffix, is_garment=True)

        elif role in ("sock_L", "sock_R"):
            suffix = "L" if role.endswith("_L") else "R"
            t = _smoothstep(0.115, 0.165, z)
            w = {f"Foot.{suffix}": 1.0 - t, f"Shin.{suffix}": t}

        elif role in ("shoe_L", "shoe_R"):
            suffix = "L" if role.endswith("_L") else "R"
            if z > 0.125:
                t_shin = _smoothstep(0.125, 0.172, z)
                w = {f"Foot.{suffix}": 1.0 - 0.70 * t_shin, f"Shin.{suffix}": 0.70 * t_shin}
            else:
                t_toe = _smoothstep(0.068, 0.105, y)
                w = {f"Foot.{suffix}": 1.0 - t_toe, f"Toe.{suffix}": t_toe}

        elif role == "backpack":
            w = {"BagRoot": 1.0}

        elif role in ("backpack_strap_L", "backpack_strap_R"):
            # Follow the torso spine smoothly at every height and blend into BagRoot only in back!
            base_w = _spine_chain_weights(min(z, 1.30))
            t_back = _smoothstep(-0.08, -0.15, y)
            w = {"BagRoot": t_back}
            for bname, bw in base_w.items():
                w[bname] = w.get(bname, 0.0) + bw * (1.0 - t_back)

        elif role == "crossbody_strap":
            # Follows torso spine cleanly from hip pouch up to right shoulder
            w = _spine_chain_weights(min(z, 1.27))

        elif role == "crossbody_pouch":
            # Anchored mainly to Spine/Hips just above the left hip so thigh swings stay clear
            w = {"Hips": 0.45, "Spine": 0.45, "BagRoot": 0.10}

        else:
            w = _spine_chain_weights(z)

        _add_normalized_weights(vg_map, v.index, w)


def create_humanoid_armature():
    """Creates the canonical 22-bone `CharacterRig` armature in Blender."""
    bpy.ops.object.armature_add(enter_editmode=True, location=(0.0, 0.0, 0.0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "CharacterRig"
    arm_obj.data.name = "CharacterRigData"
    eb = arm_obj.data.edit_bones

    # Remove default starter bone and create canonical bones in exact order
    eb.remove(eb[0])
    created = {}
    for bname, parent_name, head_xyz, tail_xyz in HUMANOID_BONES:
        bone = eb.new(bname)
        bone.head = head_xyz
        bone.tail = tail_xyz
        bone.use_connect = False
        if parent_name is not None:
            bone.parent = created[parent_name]

        # Align every bone's local +X strictly to world +X for 100% deterministic pitch axes!
        dz = tail_xyz[2] - head_xyz[2]
        dy = tail_xyz[1] - head_xyz[1]
        if abs(dz) >= abs(dy) and abs(dz) > 0.02:
            # Upward spine bones: local +Z = -Y; Downward limb bones: local +Z = +Y
            bone.align_roll(Vector((0.0, -1.0, 0.0)) if dz > 0.0 else Vector((0.0, 1.0, 0.0)))
        else:
            # Horizontal bones (Foot, Toe, BagRoot, Shoulder): local +Z = world +Z (up)
            bone.align_roll(Vector((0.0, 0.0, 1.0)))

        created[bname] = bone

    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj


def bind_slots_to_armature(slot_meshes, arm_obj):
    """Parents all 6 modular slot meshes to `arm_obj` preserving their analytical vertex weights."""
    for mesh_obj in slot_meshes:
        # Ensure all 22 bone vertex groups exist in canonical order on every slot mesh
        for bname in BONE_NAMES:
            if mesh_obj.vertex_groups.get(bname) is None:
                mesh_obj.vertex_groups.new(name=bname)

        bpy.ops.object.select_all(action="DESELECT")
        mesh_obj.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type="ARMATURE")
        mesh_obj.select_set(False)
