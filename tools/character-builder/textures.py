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


def _point_in_poly(u, v, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        ui, vi = poly[i]
        uj, vj = poly[j]
        if (vi > v) != (vj > v) and u < (uj - ui) * (v - vi) / (vj - vi + 1e-12) + ui:
            inside = not inside
        j = i
    return inside


def _draw_polygon(pixels, w, h, poly, color):
    us = [p[0] for p in poly]
    vs = [p[1] for p in poly]
    min_x = max(0, int((min(us) - 0.01) * w))
    max_x = min(w - 1, int((max(us) + 0.01) * w))
    min_y = max(0, int((min(vs) - 0.01) * h))
    max_y = min(h - 1, int((max(vs) + 0.01) * h))
    for py in range(min_y, max_y + 1):
        v = (py + 0.5) / h
        for px in range(min_x, max_x + 1):
            u = (px + 0.5) / w
            if _point_in_poly(u, v, poly):
                idx = (py * w + px) * 4
                pixels[idx : idx + 4] = color


def _cubic_bezier(p0, p1, p2, p3, t):
    mt = 1.0 - t
    c0 = mt * mt * mt
    c1 = 3.0 * mt * mt * t
    c2 = 3.0 * mt * t * t
    c3 = t * t * t
    return (
        c0 * p0[0] + c1 * p1[0] + c2 * p2[0] + c3 * p3[0],
        c0 * p0[1] + c1 * p1[1] + c2 * p2[1] + c3 * p3[1],
    )


def create_nike_backpack_logo_material():
    """
    Creates a razor-sharp 1024x1024 coral-crimson (#D24442) backpack upper-panel texture
    with the crisp white (#F2F4EE) Futura-Condensed-Italic 'NIKE' + Swoosh logo.
    """
    w, h = 1024, 1024
    red_bg = _hex_to_rgba(0xD24442)
    white_logo = _hex_to_rgba(0xF2F4EE)

    img, pixels = _create_image("NikeBackpackLogoTex", w, h, red_bg)

    # 1. Iconic Bold Condensed Oblique "NIKE" letters (slanted right by slant_k = 0.22)
    slant_k = 0.22
    v_ref = 0.42

    def sl(u0, v0):
        return (u0 + slant_k * (v0 - v_ref), v0)

    letter_polys = [
        # 'N' (left stem, diagonal, right stem)
        [sl(0.320, 0.435), sl(0.354, 0.435), sl(0.354, 0.755), sl(0.320, 0.755)],
        [sl(0.334, 0.755), sl(0.364, 0.755), sl(0.412, 0.435), sl(0.382, 0.435)],
        [sl(0.384, 0.435), sl(0.418, 0.435), sl(0.418, 0.755), sl(0.384, 0.755)],
        # 'I'
        [sl(0.432, 0.435), sl(0.468, 0.435), sl(0.468, 0.755), sl(0.432, 0.755)],
        # 'K' (left stem, upper arm, lower leg)
        [sl(0.482, 0.435), sl(0.518, 0.435), sl(0.518, 0.755), sl(0.482, 0.755)],
        [sl(0.506, 0.565), sl(0.548, 0.755), sl(0.586, 0.755), sl(0.530, 0.540)],
        [sl(0.518, 0.615), sl(0.546, 0.615), sl(0.586, 0.435), sl(0.546, 0.435)],
        # 'E' (left stem, top bar, mid bar, bottom bar)
        [sl(0.594, 0.435), sl(0.630, 0.435), sl(0.630, 0.755), sl(0.594, 0.755)],
        [sl(0.594, 0.688), sl(0.678, 0.688), sl(0.678, 0.755), sl(0.594, 0.755)],
        [sl(0.594, 0.562), sl(0.668, 0.562), sl(0.668, 0.626), sl(0.594, 0.626)],
        [sl(0.594, 0.435), sl(0.674, 0.435), sl(0.674, 0.500), sl(0.594, 0.500)],
    ]
    for lpoly in letter_polys:
        _draw_polygon(pixels, w, h, lpoly, white_logo)

    # 2. Iconic Curved Nike Swoosh sweeping underneath and through the lower right of "NIKE"
    p_hook = (0.334, 0.545)
    p_tip = (0.785, 0.535)

    # Outer (lower) boundary: hook -> left belly -> bottom belly -> sharp right wingtip
    outer_seg1 = [
        _cubic_bezier(p_hook, (0.242, 0.375), (0.240, 0.195), (0.345, 0.195), i / 40.0)
        for i in range(41)
    ]
    outer_seg2 = [
        _cubic_bezier((0.345, 0.195), (0.445, 0.195), (0.615, 0.375), p_tip, i / 50.0)
        for i in range(1, 51)
    ]
    # Inner (upper) boundary: sharp right wingtip -> inner trough -> hook
    inner_seg1 = [
        _cubic_bezier(p_tip, (0.600, 0.415), (0.445, 0.295), (0.365, 0.312), i / 50.0)
        for i in range(1, 51)
    ]
    inner_seg2 = [
        _cubic_bezier((0.365, 0.312), (0.305, 0.325), (0.296, 0.425), p_hook, i / 35.0)
        for i in range(1, 35)
    ]

    swoosh_poly = outer_seg1 + outer_seg2 + inner_seg1 + inner_seg2
    _draw_polygon(pixels, w, h, swoosh_poly, white_logo)

    img.pixels.foreach_set(pixels)
    img.pack()
    # Linear filtering + mipmaps keep oblique 3/4 views of italic "NIKE" & Swoosh razor-smooth
    return _make_textured_material("MatNikeBackpackLogo", img, closest=False)


def create_nike_backpack_side_material():
    """
    Creates a clean 512x512 coral-red (#D24442) side-panel texture with subtle darker crimson
    (#B23232) main zipper seam and side-pocket horizontal seam lines — zero intersecting
    geometry so the Abeto outline shader produces zero black speckles on the backpack sides.
    """
    w, h = 512, 512
    red_bg = _hex_to_rgba(0xD24442)
    seam_col = _hex_to_rgba(0xAE3030)

    img, pixels = _create_image("NikeBackpackSideTex", w, h, red_bg)

    # Vertical main zipper track seam along u ~ 0.58 from mid-side (v=0.33) curving over upper arch
    _draw_capsule(pixels, w, h, 0.58, 0.34, 0.58, 0.72, 0.011, seam_col)
    _draw_capsule(pixels, w, h, 0.58, 0.72, 0.52, 0.88, 0.011, seam_col)
    # Horizontal side-pocket top hem seam from back (u=0.04) forward to zipper track (u=0.58)
    _draw_capsule(pixels, w, h, 0.04, 0.34, 0.58, 0.34, 0.009, seam_col)

    img.pixels.foreach_set(pixels)
    img.pack()
    return _make_textured_material("MatNikeBackpackSide", img, closest=False)


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
