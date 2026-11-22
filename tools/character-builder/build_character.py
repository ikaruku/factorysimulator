"""
Stage 1B-K5: Modular Abeto Character Builder with 22-Bone Armature & Looping Gameplay Animations.

Builds a complete character preset (`--gender male` or `--gender female`) keeping the 6
standardized modular mesh slots SEPARATE inside the exported `.glb` hierarchy:
- `BodyMesh`   (base human body, sculpted anime head, cylindrical 1024x1024 face UV, hands, legs)
- `HairMesh`   (male: shaggy slate-teal hair; female: dark bob with twin buns & yellow ties)
- `TopMesh`    (upper garment — male: orange pullover hoodie; female: cyan/off-white color-blocked tee)
- `BottomMesh` (lower garment — male: cropped charcoal joggers; female: charcoal shorts)
- `ShoesMesh`  (footwear — male: chunky dark high-top sneakers; female: off-white strap high-tops)
- `BagMesh`    (bag — male: Nike Red Backpack; female: golden-yellow crossbody sling bag)

All 6 slot meshes carry normalized slot-aware smooth weights bound to the canonical 22-bone
`CharacterRig` armature, exporting seamless looping `Idle`, `Walk`, and `Run` NLA strips and
rendering 6-angle turnaround previews plus `Walk` and `Run` pose verification previews.
"""

import argparse
import os
import sys
import bpy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "asset-pipeline"))
for extra_dir in (SCRIPT_DIR, PIPELINE_DIR):
    if extra_dir not in sys.path:
        sys.path.insert(0, extra_dir)

from anim_clips import author_k5_gameplay_clips  # noqa: E402
from bag_parts import build_bag_red_backpack, build_bag_yellow_crossbody  # noqa: E402
from body_mesh import build_body_slot_mesh  # noqa: E402
from bottom_parts import (  # noqa: E402
    build_bottom_charcoal_joggers,
    build_bottom_charcoal_shorts,
)
from hair_parts import build_hair_shaggy_male, build_hair_twin_buns_female  # noqa: E402
from preview_render import (  # noqa: E402
    render_pose_check_previews,
    render_turnaround_previews,
)
from rig_builder import (  # noqa: E402
    bind_slots_to_armature,
    create_humanoid_armature,
)
from shoe_parts import (  # noqa: E402
    build_shoes_high_top_sneakers,
    build_shoes_white_strap_sneakers,
)
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
    parser.add_argument("--parts-dir", default="")
    return parser.parse_args(argv)


PART_EXPORT_SPEC_BY_GENDER = {
    "male": (
        ("top", "orange-hoodie", "TopMesh"),
        ("bottom", "charcoal-joggers", "BottomMesh"),
        ("shoes", "high-top-sneakers", "ShoesMesh"),
        ("bag", "red-backpack", "BagMesh"),
    ),
    "female": (
        ("top", "cyan-colorblock-tee", "TopMesh"),
        ("bottom", "charcoal-shorts", "BottomMesh"),
        ("shoes", "white-strap-sneakers", "ShoesMesh"),
        ("bag", "yellow-crossbody", "BagMesh"),
    ),
}


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build_modular_character_slots(gender):
    """Builds the 6 standardized modular slot meshes with K4 humanoid skin weights."""
    body_mesh = build_body_slot_mesh(gender=gender)

    if gender == "female":
        hair_mesh = build_hair_twin_buns_female()
        top_mesh = build_top_cyan_colorblock_tee()
        bottom_mesh = build_bottom_charcoal_shorts()
        shoes_mesh = build_shoes_white_strap_sneakers()
        bag_mesh = build_bag_yellow_crossbody()
    else:
        hair_mesh = build_hair_shaggy_male()
        top_mesh = build_top_orange_hoodie()
        bottom_mesh = build_bottom_charcoal_joggers()
        shoes_mesh = build_shoes_high_top_sneakers()
        bag_mesh = build_bag_red_backpack()

    slot_meshes = [body_mesh, hair_mesh, top_mesh, bottom_mesh, shoes_mesh, bag_mesh]

    # Ensure the lowest vertex across all slots rests exactly on z = 0
    global_min_z = min(min(v.co.z for v in obj.data.vertices) for obj in slot_meshes)
    if abs(global_min_z) > 1e-5:
        for obj in slot_meshes:
            for v in obj.data.vertices:
                v.co.z -= global_min_z
            obj.data.update()

    return slot_meshes


def export_glb(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_animations=True,
        export_nla_strips=True,
        export_force_sampling=True,
        export_materials="EXPORT",
    )


def export_standalone_part_glbs(gender, arm_obj, slot_meshes, parts_dir):
    """
    Exports each modular outfit slot (`top`, `bottom`, `shoes`, `bag`) into its own standalone
    skinned `.glb` file (`content/characters/parts/<slot>/<id>.glb`) bound to `CharacterRig`.
    """
    if not parts_dir:
        return
    mesh_by_name = {obj.name: obj for obj in slot_meshes}
    for slot_folder, part_id, node_name in PART_EXPORT_SPEC_BY_GENDER[gender]:
        mesh_obj = mesh_by_name.get(node_name)
        if mesh_obj is None:
            continue
        part_path = os.path.join(parts_dir, slot_folder, f"{part_id}.glb")
        os.makedirs(os.path.dirname(part_path), exist_ok=True)
        bpy.ops.object.select_all(action="DESELECT")
        arm_obj.select_set(True)
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.export_scene.gltf(
            filepath=part_path,
            export_format="GLB",
            use_selection=True,
            export_yup=True,
            export_apply=False,
            export_animations=False,
            export_materials="EXPORT",
        )
    bpy.ops.object.select_all(action="DESELECT")


def main():
    args = parse_args()
    clear_scene()
    slot_meshes = build_modular_character_slots(args.gender)
    arm_obj = create_humanoid_armature()
    bind_slots_to_armature(slot_meshes, arm_obj)

    # Export standalone modular outfit part GLBs in clean rest pose before authoring NLA clips
    export_standalone_part_glbs(args.gender, arm_obj, slot_meshes, args.parts_dir)

    idle_action, walk_action, run_action = author_k5_gameplay_clips(arm_obj)

    # Render standard 6-angle rest/idle turnaround previews
    arm_obj.animation_data.action = idle_action
    bpy.context.scene.frame_set(1)
    render_turnaround_previews(args.preview_dir, target_z=0.84, distance=2.75)

    # Render K5 Walk contact-phase previews (frame 1 of Walk)
    arm_obj.animation_data.action = walk_action
    bpy.context.scene.frame_set(1)
    render_pose_check_previews(args.preview_dir, target_z=0.84, distance=2.75, prefix="pose_walk")

    # Render K5 Run flight/stride previews (frame 7 of Run)
    arm_obj.animation_data.action = run_action
    bpy.context.scene.frame_set(7)
    render_pose_check_previews(args.preview_dir, target_z=0.84, distance=2.75, prefix="pose_run")

    # Restore Idle frame 1 before exporting GLB
    arm_obj.animation_data.action = idle_action
    bpy.context.scene.frame_set(1)
    export_glb(args.output)


if __name__ == "__main__":
    main()
