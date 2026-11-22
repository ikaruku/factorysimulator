"""
Stage 1B-K5: Looping Abeto Gameplay Skeletal Animations (`Idle`, `Walk`, `Run`).

All clips target the canonical 22-bone `CharacterRig` armature from `rig_builder.py`
whose local `+X` axis is strictly aligned to world `+X`:
  - Upward spine bones (`Hips`, `Spine`, `Chest`, `Neck`, `Head`):
      `-rx` = lean FORWARD (+Y),  `+rx` = lean BACKWARD (-Y)
      `+ry` = twist LEFT,         `-ry` = twist RIGHT
  - Downward limb bones (`Thigh`, `Shin`, `UpperArm`, `LowerArm`, `Hand`):
      `+rx` = swing/bend FORWARD (+Y)  (e.g. forward thigh raise, forward elbow bend)
      `-rx` = swing/bend BACKWARD (-Y) (e.g. backward leg kick, natural backward knee bend)
  - Forward horizontal bones (`Foot`, `Toe`):
      `+rx` = toes pitch UP (dorsiflexion), `-rx` = toes pitch DOWN (plantarflexion)
  - Backward horizontal bone (`BagRoot`):
      `-rx` = backpack lifts/floats upward slightly, `+rx` = backpack settles downward.
"""

import math
import bpy
from rig_builder import BONE_NAMES


def _set_bone_rot(arm_obj, bone_name, rx_deg=0.0, ry_deg=0.0, rz_deg=0.0, frame=1):
    pb = arm_obj.pose.bones[bone_name]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg))
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)


def _set_bone_loc(arm_obj, bone_name, dx=0.0, dy=0.0, dz=0.0, frame=1):
    pb = arm_obj.pose.bones[bone_name]
    pb.location = (dx, dy, dz)
    pb.keyframe_insert(data_path="location", frame=frame)


def _reset_all_pose_bones(arm_obj):
    for pb in arm_obj.pose.bones:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.location = (0.0, 0.0, 0.0)


def _keyframe_pose(arm_obj, pose_rot_deg, frame, hips_loc=(0.0, 0.0, 0.0)):
    _set_bone_loc(arm_obj, "Hips", *hips_loc, frame=frame)
    for bname in BONE_NAMES:
        rx, ry, rz = pose_rot_deg.get(bname, (0.0, 0.0, 0.0))
        _set_bone_rot(arm_obj, bname, rx, ry, rz, frame=frame)


def _mirror_pose(pose_rot_deg):
    """Mirrors a pose dictionary left <-> right (swaps .L/.R and negates ry, rz)."""
    mirrored = {}
    for bname, (rx, ry, rz) in pose_rot_deg.items():
        if bname.endswith(".L"):
            target = bname[:-2] + ".R"
        elif bname.endswith(".R"):
            target = bname[:-2] + ".L"
        else:
            target = bname
        mirrored[target] = (rx, -ry, -rz)
    return mirrored


def _make_cyclic(action):
    """Applies smooth cyclic Bezier extrapolation so glTF baked sampling loops seamlessly."""
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"
        fc.modifiers.new(type="CYCLES")


def _build_idle_action(arm_obj):
    """Calm 2.0 s (48 frames @ 24 fps) Abeto breathing & relaxed poise idle cycle."""
    act = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data.action = act
    _reset_all_pose_bones(arm_obj)

    inhale_low = {
        "Hips": (0.0, 0.6, 0.0),
        "Spine": (-0.6, -0.4, 0.0),
        "Chest": (-0.6, -0.4, 0.0),
        "Neck": (0.4, 0.2, 0.0),
        "Head": (0.6, 0.2, 0.0),
        "BagRoot": (0.4, 0.0, 0.0),
        "UpperArm.L": (2.2, 0.0, 2.2),
        "UpperArm.R": (2.2, 0.0, -2.2),
        "LowerArm.L": (6.0, 0.0, 0.0),
        "LowerArm.R": (6.0, 0.0, 0.0),
        "Thigh.L": (1.0, 0.0, 0.8),
        "Thigh.R": (1.0, 0.0, -0.8),
        "Shin.L": (-2.0, 0.0, 0.0),
        "Shin.R": (-2.0, 0.0, 0.0),
        "Foot.L": (1.0, 0.0, 0.0),
        "Foot.R": (1.0, 0.0, 0.0),
    }
    inhale_high = {
        "Hips": (0.0, -0.6, 0.0),
        "Spine": (-1.2, 0.4, 0.0),
        "Chest": (-2.4, 0.5, 0.0),
        "Neck": (0.8, -0.2, 0.0),
        "Head": (1.8, -0.3, 0.0),
        "BagRoot": (-1.6, 0.0, 0.0),
        "Shoulder.L": (0.0, 0.0, 1.2),
        "Shoulder.R": (0.0, 0.0, -1.2),
        "UpperArm.L": (3.8, 0.0, 3.4),
        "UpperArm.R": (3.8, 0.0, -3.4),
        "LowerArm.L": (9.0, 0.0, 0.0),
        "LowerArm.R": (9.0, 0.0, 0.0),
        "Thigh.L": (0.4, 0.0, 0.8),
        "Thigh.R": (0.4, 0.0, -0.8),
        "Shin.L": (-0.8, 0.0, 0.0),
        "Shin.R": (-0.8, 0.0, 0.0),
        "Foot.L": (0.4, 0.0, 0.0),
        "Foot.R": (0.4, 0.0, 0.0),
    }

    _keyframe_pose(arm_obj, inhale_low, frame=1, hips_loc=(0.0, 0.0, -0.004))
    _keyframe_pose(arm_obj, inhale_high, frame=25, hips_loc=(0.0, 0.0, 0.008))
    _keyframe_pose(arm_obj, inhale_low, frame=49, hips_loc=(0.0, 0.0, -0.004))
    _make_cyclic(act)
    return act


def _build_walk_action(arm_obj):
    """Natural 1.0 s (24 frames @ 24 fps) 8-phase Abeto walking cycle."""
    act = bpy.data.actions.new(name="Walk")
    arm_obj.animation_data.action = act
    _reset_all_pose_bones(arm_obj)

    # Phase 1: Left Contact (left heel strike forward, right toe push-off back)
    p_contact = {
        "Hips": (-2.0, -5.0, 1.2),
        "Spine": (-2.0, 2.5, -0.6),
        "Chest": (-2.0, 5.5, -0.8),
        "Neck": (2.0, -1.5, 0.0),
        "Head": (3.5, -2.5, 0.0),
        "BagRoot": (-0.8, 0.0, 0.0),
        "Thigh.L": (28.0, 0.0, 0.5),
        "Shin.L": (-6.0, 0.0, 0.0),
        "Foot.L": (10.0, 0.0, 0.0),
        "Toe.L": (4.0, 0.0, 0.0),
        "Thigh.R": (-24.0, 0.0, -0.5),
        "Shin.R": (-16.0, 0.0, 0.0),
        "Foot.R": (-14.0, 0.0, 0.0),
        "Toe.R": (18.0, 0.0, 0.0),
        "UpperArm.R": (24.0, 0.0, -3.5),
        "LowerArm.R": (20.0, 0.0, 0.0),
        "UpperArm.L": (-22.0, 0.0, 3.5),
        "LowerArm.L": (12.0, 0.0, 0.0),
    }

    # Phase 2: Left Down (weight catch, lowest hip height, widest arm swing)
    p_down = {
        "Hips": (-3.0, -3.5, 2.0),
        "Spine": (-2.5, 2.0, -1.0),
        "Chest": (-2.5, 4.0, -1.2),
        "Neck": (2.5, -1.0, 0.0),
        "Head": (4.5, -1.5, 0.0),
        "BagRoot": (1.8, 0.0, 0.0),
        "Thigh.L": (16.0, 0.0, 0.5),
        "Shin.L": (-20.0, 0.0, 0.0),
        "Foot.L": (4.0, 0.0, 0.0),
        "Toe.L": (0.0, 0.0, 0.0),
        "Thigh.R": (-18.0, 0.0, -0.5),
        "Shin.R": (-42.0, 0.0, 0.0),
        "Foot.R": (-18.0, 0.0, 0.0),
        "Toe.R": (8.0, 0.0, 0.0),
        "UpperArm.R": (28.0, 0.0, -4.0),
        "LowerArm.R": (26.0, 0.0, 0.0),
        "UpperArm.L": (-26.0, 0.0, 4.0),
        "LowerArm.L": (10.0, 0.0, 0.0),
    }

    # Phase 3: Left Passing (left leg vertical supporting weight, right knee bent passing through)
    p_passing = {
        "Hips": (-2.0, 0.0, 0.8),
        "Spine": (-2.0, 0.0, -0.4),
        "Chest": (-2.0, 0.0, -0.4),
        "Neck": (2.0, 0.0, 0.0),
        "Head": (3.0, 0.0, 0.0),
        "BagRoot": (-0.6, 0.0, 0.0),
        "Thigh.L": (2.0, 0.0, 0.5),
        "Shin.L": (-8.0, 0.0, 0.0),
        "Foot.L": (2.0, 0.0, 0.0),
        "Toe.L": (0.0, 0.0, 0.0),
        "Thigh.R": (10.0, 0.0, -0.5),
        "Shin.R": (-52.0, 0.0, 0.0),
        "Foot.R": (-8.0, 0.0, 0.0),
        "Toe.R": (0.0, 0.0, 0.0),
        "UpperArm.R": (4.0, 0.0, -3.0),
        "LowerArm.R": (16.0, 0.0, 0.0),
        "UpperArm.L": (-4.0, 0.0, 3.0),
        "LowerArm.L": (14.0, 0.0, 0.0),
    }

    # Phase 4: Left High Point (push-off lift, highest hip height, right leg reaching forward)
    p_up = {
        "Hips": (-2.0, 3.5, -0.8),
        "Spine": (-1.5, -2.0, 0.4),
        "Chest": (-1.5, -4.0, 0.5),
        "Neck": (1.5, 1.0, 0.0),
        "Head": (2.5, 1.5, 0.0),
        "BagRoot": (-2.2, 0.0, 0.0),
        "Thigh.L": (-14.0, 0.0, 0.5),
        "Shin.L": (-8.0, 0.0, 0.0),
        "Foot.L": (-10.0, 0.0, 0.0),
        "Toe.L": (14.0, 0.0, 0.0),
        "Thigh.R": (26.0, 0.0, -0.5),
        "Shin.R": (-18.0, 0.0, 0.0),
        "Foot.R": (4.0, 0.0, 0.0),
        "Toe.R": (2.0, 0.0, 0.0),
        "UpperArm.R": (-14.0, 0.0, -3.2),
        "LowerArm.R": (12.0, 0.0, 0.0),
        "UpperArm.L": (16.0, 0.0, 3.2),
        "LowerArm.L": (18.0, 0.0, 0.0),
    }

    phases = [
        (1, p_contact, (0.0, 0.0, -0.012)),
        (4, p_down, (0.0, 0.0, -0.028)),
        (7, p_passing, (0.0, 0.0, 0.008)),
        (10, p_up, (0.0, 0.0, 0.020)),
        (13, _mirror_pose(p_contact), (0.0, 0.0, -0.012)),
        (16, _mirror_pose(p_down), (0.0, 0.0, -0.028)),
        (19, _mirror_pose(p_passing), (0.0, 0.0, 0.008)),
        (22, _mirror_pose(p_up), (0.0, 0.0, 0.020)),
        (25, p_contact, (0.0, 0.0, -0.012)),
    ]
    for frame, pose, hloc in phases:
        _keyframe_pose(arm_obj, pose, frame=frame, hips_loc=hloc)

    _make_cyclic(act)
    return act


def _build_run_action(arm_obj):
    """Energetic 0.67 s (16 frames @ 24 fps) 8-phase Abeto athletic run cycle."""
    act = bpy.data.actions.new(name="Run")
    arm_obj.animation_data.action = act
    _reset_all_pose_bones(arm_obj)

    # Phase 1: Left Contact / Strike (lively forward torso lean, eyes level, bent elbows pumping)
    r_contact = {
        "Hips": (-4.5, -7.0, 1.8),
        "Spine": (-5.0, 4.0, -1.0),
        "Chest": (-5.0, 8.0, -1.2),
        "Neck": (4.5, -2.5, 0.0),
        "Head": (8.5, -4.5, 0.0),
        "BagRoot": (-0.6, 0.0, 0.0),
        "Thigh.L": (44.0, 0.0, 0.5),
        "Shin.L": (-24.0, 0.0, 0.0),
        "Foot.L": (6.0, 0.0, 0.0),
        "Toe.L": (4.0, 0.0, 0.0),
        "Thigh.R": (-32.0, 0.0, -0.5),
        "Shin.R": (-68.0, 0.0, 0.0),
        "Foot.R": (-22.0, 0.0, 0.0),
        "Toe.R": (8.0, 0.0, 0.0),
        "UpperArm.R": (42.0, 0.0, -6.0),
        "LowerArm.R": (76.0, 0.0, 0.0),
        "UpperArm.L": (-36.0, 0.0, 6.0),
        "LowerArm.L": (62.0, 0.0, 0.0),
    }

    # Phase 2: Left Drive / Squash (deep athletic knee absorb, backpack settles down)
    r_drive = {
        "Hips": (-5.5, -3.5, 2.4),
        "Spine": (-5.5, 2.0, -1.2),
        "Chest": (-5.5, 4.0, -1.4),
        "Neck": (5.0, -1.5, 0.0),
        "Head": (10.0, -2.5, 0.0),
        "BagRoot": (2.6, 0.0, 0.0),
        "Thigh.L": (18.0, 0.0, 0.5),
        "Shin.L": (-42.0, 0.0, 0.0),
        "Foot.L": (12.0, 0.0, 0.0),
        "Toe.L": (0.0, 0.0, 0.0),
        "Thigh.R": (-4.0, 0.0, -0.5),
        "Shin.R": (-80.0, 0.0, 0.0),
        "Foot.R": (-18.0, 0.0, 0.0),
        "Toe.R": (4.0, 0.0, 0.0),
        "UpperArm.R": (26.0, 0.0, -6.5),
        "LowerArm.R": (78.0, 0.0, 0.0),
        "UpperArm.L": (-22.0, 0.0, 6.5),
        "LowerArm.L": (68.0, 0.0, 0.0),
    }

    # Phase 3: Left Push-Off (explosive leg extension back, opposite knee driving high)
    r_push = {
        "Hips": (-4.5, 2.5, -1.0),
        "Spine": (-4.5, -1.5, 0.5),
        "Chest": (-4.5, -3.0, 0.6),
        "Neck": (4.0, 1.0, 0.0),
        "Head": (8.0, 1.5, 0.0),
        "BagRoot": (-1.2, 0.0, 0.0),
        "Thigh.L": (-22.0, 0.0, 0.5),
        "Shin.L": (-16.0, 0.0, 0.0),
        "Foot.L": (-24.0, 0.0, 0.0),
        "Toe.L": (22.0, 0.0, 0.0),
        "Thigh.R": (36.0, 0.0, -0.5),
        "Shin.R": (-62.0, 0.0, 0.0),
        "Foot.R": (-6.0, 0.0, 0.0),
        "Toe.R": (0.0, 0.0, 0.0),
        "UpperArm.R": (-8.0, 0.0, -5.5),
        "LowerArm.R": (68.0, 0.0, 0.0),
        "UpperArm.L": (10.0, 0.0, 5.5),
        "LowerArm.L": (72.0, 0.0, 0.0),
    }

    # Phase 4: Flight / Airborne Apex (both feet clear ground, backpack floats slightly!)
    r_flight = {
        "Hips": (-4.0, 6.5, -1.6),
        "Spine": (-4.5, -3.5, 0.8),
        "Chest": (-4.5, -7.0, 1.0),
        "Neck": (4.0, 2.0, 0.0),
        "Head": (8.0, 4.0, 0.0),
        "BagRoot": (-4.2, 0.0, 0.0),
        "Thigh.L": (-36.0, 0.0, 0.5),
        "Shin.L": (-58.0, 0.0, 0.0),
        "Foot.L": (-26.0, 0.0, 0.0),
        "Toe.L": (6.0, 0.0, 0.0),
        "Thigh.R": (48.0, 0.0, -0.5),
        "Shin.R": (-34.0, 0.0, 0.0),
        "Foot.R": (-4.0, 0.0, 0.0),
        "Toe.R": (4.0, 0.0, 0.0),
        "UpperArm.R": (-34.0, 0.0, -5.5),
        "LowerArm.R": (62.0, 0.0, 0.0),
        "UpperArm.L": (38.0, 0.0, 5.5),
        "LowerArm.L": (74.0, 0.0, 0.0),
    }

    phases = [
        (1, r_contact, (0.0, 0.0, -0.020)),
        (3, r_drive, (0.0, 0.0, -0.052)),
        (5, r_push, (0.0, 0.0, 0.012)),
        (7, r_flight, (0.0, 0.0, 0.038)),
        (9, _mirror_pose(r_contact), (0.0, 0.0, -0.020)),
        (11, _mirror_pose(r_drive), (0.0, 0.0, -0.052)),
        (13, _mirror_pose(r_push), (0.0, 0.0, 0.012)),
        (15, _mirror_pose(r_flight), (0.0, 0.0, 0.038)),
        (17, r_contact, (0.0, 0.0, -0.020)),
    ]
    for frame, pose, hloc in phases:
        _keyframe_pose(arm_obj, pose, frame=frame, hips_loc=hloc)

    _make_cyclic(act)
    return act


def author_k5_gameplay_clips(arm_obj):
    """
    Authors the 3 looping Stage 1B-K5 skeletal gameplay clips (`Idle`, `Walk`, `Run`)
    and pushes each onto its own NLA track for glTF 2.0 export.
    """
    scene = bpy.context.scene
    scene.render.fps = 24
    arm_obj.animation_data_create()

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")

    idle_action = _build_idle_action(arm_obj)
    walk_action = _build_walk_action(arm_obj)
    run_action = _build_run_action(arm_obj)

    bpy.ops.object.mode_set(mode="OBJECT")

    for track_name, act in (("Idle", idle_action), ("Walk", walk_action), ("Run", run_action)):
        track = arm_obj.animation_data.nla_tracks.new()
        track.name = track_name
        track.strips.new(track_name, 1, act)

    arm_obj.animation_data.action = idle_action
    scene.frame_set(1)
    return idle_action, walk_action, run_action
