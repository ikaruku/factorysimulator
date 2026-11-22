"""
Stage 1B-K3: Modular Abeto Character Builder (Male & Female Default Designs + Separated Outfit Slots).

Builds a complete character preset (`--gender male` or `--gender female`) keeping the 6
standardized modular mesh slots SEPARATE inside the exported `.glb` hierarchy:
- `BodyMesh`   (base human body, sculpted anime head, cylindrical 1024x1024 face UV, hands, bare calves)
- `HairMesh`   (male: shaggy slate-teal hair; female: dark bob with twin buns & yellow ties)
- `TopMesh`    (pakaian atas — male: orange pullover hoodie; female: cyan/off-white color-blocked tee)
- `BottomMesh` (pakaian bawah — baggy cropped charcoal joggers + off-white crew socks)
- `ShoesMesh`  (sepatu — chunky dark high-top sneakers with twin white stripes)
- `BagMesh`    (tas — male: crimson-red "Hi" backpack; female: golden-yellow crossbody sling bag)

All 6 slot meshes are parented and skinned to the shared `CharacterRig` armature so any slot
can be toggled or swapped independently at runtime.
"""

import argparse
import math
import os
import sys
import bpy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "asset-pipeline"))
for extra_dir in (SCRIPT_DIR, PIPELINE_DIR):
    if extra_dir not in sys.path:
        sys.path.insert(0, extra_dir)

from bag_parts import build_bag_red_backpack, build_bag_yellow_crossbody  # noqa: E402
from body_mesh import build_body_slot_mesh  # noqa: E402
from bottom_parts import build_bottom_charcoal_joggers  # noqa: E402
from hair_parts import build_hair_shaggy_male, build_hair_twin_buns_female  # noqa: E402
from preview_render import render_turnaround_previews  # noqa: E402
from shoe_parts import build_shoes_high_top_sneakers  # noqa: E402
from top_parts import build_top_cyan_colorblock_tee, build_top_orange_hoodie  # noqa: E402


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--gender", choices=("male", "female"), default="male")
    parser.add_argument("--output", required=True)
    parser.add_argument("--preview-dir", required=True)
    return parser.parse_args(argv)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build_modular_character_slots(gender):
    """Builds the 6 standardized modular slot meshes for the specified gender preset."""
    body_mesh = build_body_slot_mesh(gender=gender)

    if gender == "female":
        hair_mesh = build_hair_twin_buns_female()
        top_mesh = build_top_cyan_colorblock_tee()
        bag_mesh = build_bag_yellow_crossbody()
    else:
        hair_mesh = build_hair_shaggy_male()
        top_mesh = build_top_orange_hoodie()
        bag_mesh = build_bag_red_backpack()

    bottom_mesh = build_bottom_charcoal_joggers()
    shoes_mesh = build_shoes_high_top_sneakers()

    slot_meshes = [body_mesh, hair_mesh, top_mesh, bottom_mesh, shoes_mesh, bag_mesh]

    # Ensure the lowest vertex across all slots rests exactly on z = 0
    global_min_z = min(min(v.co.z for v in obj.data.vertices) for obj in slot_meshes)
    if abs(global_min_z) > 1e-5:
        for obj in slot_meshes:
            for v in obj.data.vertices:
                v.co.z -= global_min_z
            obj.data.update()

    return slot_meshes


def attach_preview_idle_rig(slot_meshes):
    """Binds all 6 modular slot meshes to the shared `CharacterRig` armature."""
    bpy.ops.object.armature_add(enter_editmode=True, location=(0.0, 0.0, 0.0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "CharacterRig"
    eb = arm_obj.data.edit_bones

    hips = eb[0]
    hips.name = "Hips"
    hips.head = (0.0, 0.0, 0.80)
    hips.tail = (0.0, 0.0, 1.02)

    chest = eb.new("Chest")
    chest.head = hips.tail
    chest.tail = (0.0, 0.0, 1.30)
    chest.parent = hips

    head = eb.new("Head")
    head.head = chest.tail
    head.tail = (0.0, 0.0, 1.62)
    head.parent = chest

    bpy.ops.object.mode_set(mode="OBJECT")

    for mesh_obj in slot_meshes:
        bpy.ops.object.select_all(action="DESELECT")
        mesh_obj.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type="ARMATURE_NAME")

        vg_hips = mesh_obj.vertex_groups["Hips"]
        vg_chest = mesh_obj.vertex_groups["Chest"]
        vg_head = mesh_obj.vertex_groups["Head"]
        for v in mesh_obj.data.vertices:
            z = v.co.z
            if z < 0.84:
                vg_hips.add([v.index], 1.0, "REPLACE")
            elif z < 1.02:
                t = (z - 0.84) / 0.18
                vg_hips.add([v.index], 1.0 - t, "REPLACE")
                vg_chest.add([v.index], t, "REPLACE")
            elif z < 1.28:
                vg_chest.add([v.index], 1.0, "REPLACE")
            elif z < 1.36:
                t = (z - 1.28) / 0.08
                vg_chest.add([v.index], 1.0 - t, "REPLACE")
                vg_head.add([v.index], t, "REPLACE")
            else:
                vg_head.add([v.index], 1.0, "REPLACE")

    scene = bpy.context.scene
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 49

    action = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action
    bpy.ops.object.mode_set(mode="POSE")
    chest_pose = arm_obj.pose.bones["Chest"]
    chest_pose.rotation_mode = "XYZ"

    for frame, pitch in [(1, 0.0), (25, math.radians(1.5)), (49, 0.0)]:
        chest_pose.rotation_euler = (pitch, 0.0, 0.0)
        chest_pose.keyframe_insert(data_path="rotation_euler", frame=frame)

    bpy.ops.object.mode_set(mode="OBJECT")
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = "Idle"
    track.strips.new("Idle", 1, action)
    return arm_obj


def export_glb(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_animations=True,
        export_nla_strips=True,
        export_materials="EXPORT",
    )


def main():
    args = parse_args()
    clear_scene()
    slot_meshes = build_modular_character_slots(args.gender)
    attach_preview_idle_rig(slot_meshes)
    render_turnaround_previews(args.preview_dir, target_z=0.84, distance=2.75)
    export_glb(args.output)


if __name__ == "__main__":
    main()
