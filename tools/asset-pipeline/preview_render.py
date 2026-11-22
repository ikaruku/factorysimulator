"""Shared Blender helper to render 5-angle turnaround preview PNGs for any 3D asset."""

import os
import bpy
from mathutils import Vector


def _point_camera_at(cam_obj, target_vec):
    direction = target_vec - cam_obj.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = rot_quat.to_euler()


def render_turnaround_previews(preview_dir, target_z=0.86, distance=2.65, resolution=512):
    """Renders front, right, back, left, and head close-up PNGs using Blender Workbench."""
    os.makedirs(preview_dir, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE"
    if hasattr(scene.display.shading, "show_specular_highlight"):
        scene.display.shading.show_specular_highlight = False
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    if hasattr(scene.display.shading, "cavity_ridge_factor"):
        scene.display.shading.cavity_ridge_factor = 0.90
        scene.display.shading.cavity_valley_factor = 1.60
    scene.display.shading.show_object_outline = True
    scene.display.shading.object_outline_color = (0.10, 0.12, 0.16)

    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("PreviewWorld")
    scene.world.color = (0.54, 0.89, 0.87)

    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("PreviewCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Blender +Y maps to glTF -Z (front); +X is character right, -X is character left.
    views = {
        "front": ((0.0, distance, target_z + 0.06), (0.0, 0.0, target_z)),
        "right": ((distance, 0.0, target_z + 0.06), (0.0, 0.0, target_z)),
        "back": ((0.0, -distance, target_z + 0.06), (0.0, 0.0, target_z)),
        "left": ((-distance, 0.0, target_z + 0.06), (0.0, 0.0, target_z)),
        "three_quarter": (
            (distance * 0.62, distance * 0.78, target_z + 0.10),
            (0.0, 0.0, target_z),
        ),
        "head_closeup": ((0.18, 0.92, 1.50), (0.0, 0.0, 1.48)),
    }

    rendered = []
    for name, (loc, tgt) in views.items():
        cam_obj.location = Vector(loc)
        _point_camera_at(cam_obj, Vector(tgt))
        out_path = os.path.join(preview_dir, f"{name}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        rendered.append(out_path)

    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)
    return rendered
