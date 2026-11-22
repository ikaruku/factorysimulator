"""
Modular `BottomMesh` (Pakaian Bawah) slot builders for Male & Female Abeto characters:
- `build_bottom_charcoal_joggers()`: Default Male baggy cropped dark charcoal joggers (#22262B)
  with sculpted angular outer-calf folds + off-white crew socks (#DCE0D8).
- `build_bottom_charcoal_shorts()`: Separate Female shorts model (`celana pendek`, #22262B)
  with relaxed tailored A-line silhouette, sculpted thigh folds, and cuffed hem above the
  knee (`z = 0.49`), paired with off-white crew socks (#E2E6DE, `z = 0.14..0.24`).
"""

import math
from mesh_utils import join_parts_into_slot_mesh, make_loft_from_rings, make_toon_source_material
from rig_builder import assign_part_weights


def _build_crew_socks(parts, mat_socks, x_offset=0.082):
    """Adds left and right off-white crew socks (`z = 0.140..0.242`) to the parts list."""
    sock_stations = [
        (0.140, 0.041, 0.042),
        (0.195, 0.043, 0.044),
        (0.238, 0.045, 0.046),
        (0.242, 0.039, 0.040),
    ]
    for side in (-1.0, 1.0):
        sock_rings = []
        for z, srx, sry in sock_stations:
            sring = []
            for s in range(18):
                ang = (2.0 * math.pi * s) / 18
                sring.append(
                    (side * x_offset + math.cos(ang) * srx, -0.002 + math.sin(ang) * sry, z)
                )
            sock_rings.append(sring)

        parts.append(
            make_loft_from_rings(
                f"CrewSock_{'L' if side < 0 else 'R'}",
                sock_rings,
                mat_socks,
                cap_start=True,
                cap_end=True,
            )
        )


def build_bottom_charcoal_joggers():
    """Builds the default Male baggy cropped charcoal joggers + crew socks as `BottomMesh`."""
    mat_pants = make_toon_source_material("MatJoggerPants", 0x22262B)
    mat_socks = make_toon_source_material("MatWhiteSocks", 0xDCE0D8)
    parts = []

    leg_stations = [
        (0.308, 0.036, 0.126, 0.046, 0.048, -0.002),
        (0.312, 0.020, 0.142, 0.064, 0.066, -0.002),
        (0.346, 0.018, 0.144, 0.066, 0.068, -0.002),
        (0.362, 0.018, 0.138, 0.063, 0.065, -0.001),
        (0.415, 0.010, 0.172, 0.088, 0.092, 0.002),
        (0.478, 0.008, 0.158, 0.084, 0.088, 0.005),
        (0.540, 0.000, 0.166, 0.092, 0.096, 0.005),
        (0.595, -0.026, 0.168, 0.102, 0.106, 0.004),
        (0.690, -0.030, 0.164, 0.108, 0.112, 0.004),
        (0.795, -0.028, 0.150, 0.100, 0.104, 0.004),
    ]
    n_lseg = 24
    for side in (-1.0, 1.0):
        leg_rings = []
        for z, xi, xo, ryf, ryb, cy_off in leg_stations:
            ring = []
            xc = side * 0.5 * (xi + xo)
            rx = 0.5 * (xo - xi)
            for s in range(n_lseg):
                ang = (2.0 * math.pi * s) / n_lseg
                ca, sa = math.cos(ang), math.sin(ang)
                ry = ryf if sa >= 0.0 else ryb
                inner_med = max(0.0, -ca * side)
                ry_local = ry * (1.0 + 0.12 * inner_med) if z > 0.55 else ry
                ring.append((xc + ca * rx, cy_off + sa * ry_local, z))
            leg_rings.append(ring)

        parts.append(
            make_loft_from_rings(
                f"JoggerLeg_{'L' if side < 0 else 'R'}",
                leg_rings,
                mat_pants,
                cap_start=True,
                cap_end=True,
                sharp_ring_indices=(2, 4),
            )
        )

    _build_crew_socks(parts, mat_socks, x_offset=0.082)
    for part in parts:
        if part.name == "JoggerLeg_L":
            assign_part_weights(part, "leg_L")
        elif part.name == "JoggerLeg_R":
            assign_part_weights(part, "leg_R")
        elif part.name == "CrewSock_L":
            assign_part_weights(part, "sock_L")
        else:
            assign_part_weights(part, "sock_R")
    return join_parts_into_slot_mesh(parts, "BottomMesh")


def build_bottom_charcoal_shorts():
    """
    Builds the separate Female relaxed streetwear shorts (`celana pendek`, #22262B) with
    sculpted thigh folds and cuffed hem above the knee (`z = 0.485`), plus crew socks, as `BottomMesh`.
    """
    mat_shorts = make_toon_source_material("MatCharcoalShorts", 0x22262B)
    mat_socks = make_toon_source_material("MatWhiteSocks", 0xE2E6DE)
    parts = []

    # Tailored wide streetwear shorts from above-knee cuff (z = 0.485) up to waist (z = 0.795)
    shorts_stations = [
        (0.485, 0.028, 0.132, 0.056, 0.058, 0.004),  # inner shorts cuff tuck around bare knee/thigh
        (0.490, 0.008, 0.160, 0.084, 0.088, 0.004),  # crisp shorts bottom cuff rim
        (0.528, 0.006, 0.164, 0.088, 0.092, 0.005),  # top of shorts cuff band
        (0.545, 0.006, 0.158, 0.085, 0.089, 0.005),  # subtle fold crease above shorts cuff
        (0.605, -0.024, 0.168, 0.098, 0.104, 0.004),  # relaxed lower-mid thigh union
        (0.695, -0.030, 0.164, 0.106, 0.110, 0.004),  # hip fullness
        (0.795, -0.028, 0.148, 0.098, 0.102, 0.004),  # waist tucked inside T-shirt hem
    ]
    n_lseg = 24
    for side in (-1.0, 1.0):
        leg_rings = []
        for z, xi, xo, ryf, ryb, cy_off in shorts_stations:
            ring = []
            xc = side * 0.5 * (xi + xo)
            rx = 0.5 * (xo - xi)
            for s in range(n_lseg):
                ang = (2.0 * math.pi * s) / n_lseg
                ca, sa = math.cos(ang), math.sin(ang)
                ry = ryf if sa >= 0.0 else ryb
                inner_med = max(0.0, -ca * side)
                ry_local = ry * (1.0 + 0.12 * inner_med) if z > 0.58 else ry
                ring.append((xc + ca * rx, cy_off + sa * ry_local, z))
            leg_rings.append(ring)

        parts.append(
            make_loft_from_rings(
                f"ShortsLeg_{'L' if side < 0 else 'R'}",
                leg_rings,
                mat_shorts,
                cap_start=True,
                cap_end=True,
                sharp_ring_indices=(2,),
            )
        )

    _build_crew_socks(parts, mat_socks, x_offset=0.080)
    for part in parts:
        if part.name == "ShortsLeg_L":
            assign_part_weights(part, "leg_L")
        elif part.name == "ShortsLeg_R":
            assign_part_weights(part, "leg_R")
        elif part.name == "CrewSock_L":
            assign_part_weights(part, "sock_L")
        else:
            assign_part_weights(part, "sock_R")
    return join_parts_into_slot_mesh(parts, "BottomMesh")
