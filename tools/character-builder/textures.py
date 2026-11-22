"""
High-resolution (1024x1024) procedural packed PNG textures for Male & Female Abeto characters:
- `create_face_material(gender)`: cylindrical-UV anime face texture (focused angled brows for male;
  calm arched brows & almond eyes for female).
- `create_colorblock_shirt_material()`: razor-sharp 1024x1024 cyan (#2FA6CC) / off-white (#E4E8E0)
  color-blocked T-shirt texture for the female default top (`top_cyan_colorblock_tee`).
"""

import math
import bpy


def _hex_to_rgba(hex_rgb, alpha=1.0):
    r = ((hex_rgb >> 16) & 255) / 255.0
    g = ((hex_rgb >> 8) & 255) / 255.0
    b = (hex_rgb & 255) / 255.0
    return (r, g, b, alpha)


def _create_image(name, width, height, fill_rgba):
    img = bpy.data.images.new(name=name, width=width, height=height, alpha=True)
    pixels = list(fill_rgba) * (width * height)
    return img, pixels


def _draw_ellipse(pixels, w, h, cx, cy, rx, ry, color, tilt=0.0):
    cos_t = math.cos(tilt)
    sin_t = math.sin(tilt)
    min_x = max(0, int((cx - max(rx, ry) - 0.01) * w))
    max_x = min(w - 1, int((cx + max(rx, ry) + 0.01) * w))
    min_y = max(0, int((cy - max(rx, ry) - 0.01) * h))
    max_y = min(h - 1, int((cy + max(rx, ry) + 0.01) * h))
    for py in range(min_y, max_y + 1):
        v = (py + 0.5) / h
        dy = v - cy
        for px in range(min_x, max_x + 1):
            u = (px + 0.5) / w
            dx = u - cx
            lx = dx * cos_t + dy * sin_t
            ly = -dx * sin_t + dy * cos_t
            if (lx / rx) ** 2 + (ly / ry) ** 2 <= 1.0:
                idx = (py * w + px) * 4
                pixels[idx : idx + 4] = color


def _draw_capsule(pixels, w, h, x0, y0, x1, y1, radius, color):
    vx, vy = x1 - x0, y1 - y0
    seg_len_sq = max(vx * vx + vy * vy, 1e-8)
    min_x = max(0, int((min(x0, x1) - radius - 0.01) * w))
    max_x = min(w - 1, int((max(x0, x1) + radius + 0.01) * w))
    min_y = max(0, int((min(y0, y1) - radius - 0.01) * h))
    max_y = min(h - 1, int((max(y0, y1) + radius + 0.01) * h))
    r_sq = radius * radius
    for py in range(min_y, max_y + 1):
        v = (py + 0.5) / h
        for px in range(min_x, max_x + 1):
            u = (px + 0.5) / w
            t = max(0.0, min(1.0, ((u - x0) * vx + (v - y0) * vy) / seg_len_sq))
            dx = u - (x0 + t * vx)
            dy = v - (y0 + t * vy)
            if dx * dx + dy * dy <= r_sq:
                idx = (py * w + px) * 4
                pixels[idx : idx + 4] = color


def _make_textured_material(name, img, closest=True):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex_node = nt.nodes.new("ShaderNodeTexImage")
    tex_node.image = img
    if closest:
        tex_node.interpolation = "Closest"
    if bsdf:
        nt.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.90
    return mat


def create_face_material(gender="male"):
    """Creates a razor-sharp 1024x1024 Abeto face texture for 'male' or 'female'."""
    w, h = 1024, 1024
    skin = _hex_to_rgba(0xCFB6BA)
    ink = _hex_to_rgba(0x14171D)
    mouth_col = _hex_to_rgba(0x3A2C31)

    img, pixels = _create_image(f"CharacterFaceTex_{gender}", w, h, skin)

    for side in (-1.0, 1.0):
        ex = 0.5 + side * 0.282
        ey = 0.495

        if gender == "female":
            # Calm, soft almond eyes & level-arched eyebrows (Abeto female reference)
            _draw_ellipse(pixels, w, h, ex, ey - 0.010, 0.084, 0.044, ink, tilt=side * 0.04)
            _draw_capsule(
                pixels,
                w,
                h,
                ex - side * 0.096,
                ey + 0.014,
                ex + side * 0.106,
                ey + 0.022,
                0.016,
                ink,
            )
            # Smooth gently arched eyebrows
            _draw_capsule(
                pixels,
                w,
                h,
                ex - side * 0.115,
                ey + 0.088,
                ex + side * 0.010,
                ey + 0.098,
                0.016,
                ink,
            )
            _draw_capsule(
                pixels,
                w,
                h,
                ex + side * 0.010,
                ey + 0.098,
                ex + side * 0.115,
                ey + 0.090,
                0.015,
                ink,
            )
        else:
            # Focused boyish anime eyes & confident angled eyebrows (Abeto male reference)
            _draw_ellipse(pixels, w, h, ex, ey - 0.012, 0.088, 0.046, ink, tilt=side * 0.06)
            _draw_capsule(
                pixels,
                w,
                h,
                ex - side * 0.098,
                ey + 0.012,
                ex + side * 0.104,
                ey + 0.028,
                0.017,
                ink,
            )
            _draw_capsule(
                pixels,
                w,
                h,
                ex - side * 0.122,
                ey + 0.072,
                ex + side * 0.018,
                ey + 0.100,
                0.017,
                ink,
            )
            _draw_capsule(
                pixels,
                w,
                h,
                ex + side * 0.018,
                ey + 0.100,
                ex + side * 0.120,
                ey + 0.108,
                0.016,
                ink,
            )

    _draw_capsule(pixels, w, h, 0.428, 0.228, 0.572, 0.228, 0.010, mouth_col)

    img.pixels.foreach_set(pixels)
    img.pack()
    return _make_textured_material(f"MatFace_{gender}", img, closest=True)


def create_colorblock_shirt_material():
    """
    Creates the 1024x1024 cyan + off-white color-blocked T-shirt texture for the female default top:
      u in [0.0, 0.5): FRONT (u=0 -> char right/+X, u=0.5 -> char left/-X)
      u in [0.5, 1.0]: BACK  (u=0.5 -> char left/-X, u=1.0 -> char right/+X)
    """
    w, h = 1024, 1024
    cyan = _hex_to_rgba(0x2FA6CC)
    off_white = _hex_to_rgba(0xE4E8E0)

    img, pixels = _create_image("CharacterColorblockShirtTex", w, h, cyan)

    for py in range(h):
        v = (py + 0.5) / h
        for px in range(w):
            u = (px + 0.5) / w
            col = cyan

            if u < 0.5:
                lu = u / 0.5
                diag_u = 0.52 + 0.42 * (1.0 - v)
                if lu > diag_u and v > 0.18:
                    col = off_white

                tri_center = 0.46
                tri_half_w = 0.26 * max(0.0, 1.0 - v / 0.25)
                if v < 0.25 and abs(lu - tri_center) < tri_half_w:
                    col = off_white

                if abs(lu - 0.54) + abs(v - 0.53) * 1.15 < 0.052:
                    col = off_white
            else:
                lu = (u - 0.5) / 0.5
                diag_u = 0.46 - 0.48 * (1.0 - v)
                if lu < diag_u and v > 0.22:
                    col = off_white

            idx = (py * w + px) * 4
            pixels[idx : idx + 4] = col

    img.pixels.foreach_set(pixels)
    img.pack()
    return _make_textured_material("MatShirtColorblock", img, closest=True)
