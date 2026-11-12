"""Pixel + depth + camera pose → a point in the map frame.

Camera model is a pinhole in the ROS optical frame:
  x right, y down, z forward.

  X = (u - cx) * Z / fx
  Y = (v - cy) * Z / fy
  Z = depth

Then a fixed camera→map transform turns that optical point into meters
on the floor. That transform is what TF2 carries on a real robot.
"""

from __future__ import annotations

import math

# Pinhole intrinsics (pixels).
FX = 500.0
FY = 500.0
CX = 320.0
CY = 240.0

# True box center in map. Robot base_link sits at the map origin.
TRUE_MAP = (2.0, 0.0, 0.15)

# camera_optical origin in base_link / map (same while base is at origin).
CAM_T = (0.25, 0.0, 0.30)

# Columns are optical axes expressed in the map/base frame:
# optical x → -y, optical y → -z, optical z → +x.
CAM_R = (
    (0.0, 0.0, 1.0),
    (-1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0),
)


def _mat_vec(r: tuple[tuple[float, float, float], ...], v: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        r[0][0] * v[0] + r[0][1] * v[1] + r[0][2] * v[2],
        r[1][0] * v[0] + r[1][1] * v[1] + r[1][2] * v[2],
        r[2][0] * v[0] + r[2][1] * v[1] + r[2][2] * v[2],
    )


def _transpose(r: tuple[tuple[float, float, float], ...]) -> tuple[tuple[float, float, float], ...]:
    return (
        (r[0][0], r[1][0], r[2][0]),
        (r[0][1], r[1][1], r[2][1]),
        (r[0][2], r[1][2], r[2][2]),
    )


def _add(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def project_to_pixel(
    map_point: tuple[float, float, float] = TRUE_MAP,
) -> tuple[float, float, float]:
    """Return (u, v, depth) for the true map point, seen by this camera."""
    p_cam = _mat_vec(_transpose(CAM_R), _sub(map_point, CAM_T))
    z = p_cam[2]
    u = FX * p_cam[0] / z + CX
    v = FY * p_cam[1] / z + CY
    return u, v, z


def pixel_to_optical(u: float, v: float, depth: float) -> tuple[float, float, float]:
    x = (u - CX) * depth / FX
    y = (v - CY) * depth / FY
    return (x, y, depth)


def optical_to_map(optical: tuple[float, float, float]) -> tuple[float, float, float]:
    return _add(_mat_vec(CAM_R, optical), CAM_T)


def project_to_pixel_from(
    map_point: tuple[float, float, float],
    cam_t: tuple[float, float, float],
) -> tuple[float, float, float]:
    p_cam = _mat_vec(_transpose(CAM_R), _sub(map_point, cam_t))
    z = p_cam[2]
    u = FX * p_cam[0] / z + CX
    v = FY * p_cam[1] / z + CY
    return u, v, z


def run_case(case: str) -> dict[str, float | str]:
    u, v, true_depth = project_to_pixel()
    if case == "full":
        optical = pixel_to_optical(u, v, true_depth)
        mapped = optical_to_map(optical)
        depth_used = true_depth
        frame = "map"
    elif case == "bad_depth":
        # Same pixel, but depth is guessed as 1.0 m.
        optical = pixel_to_optical(u, v, 1.0)
        mapped = optical_to_map(optical)
        depth_used = 1.0
        frame = "map"
    elif case == "no_tf":
        # Pixel + depth only. The optical point is treated as if it were map.
        mapped = pixel_to_optical(u, v, true_depth)
        depth_used = true_depth
        frame = "camera_optical"
    elif case == "stale_pose":
        # Robot rolled +0.50 m in x. The camera now sees a new pixel, but the
        # code still applies the old camera→map transform.
        cam_t_new = (CAM_T[0] + 0.50, CAM_T[1], CAM_T[2])
        u, v, true_depth = project_to_pixel_from(TRUE_MAP, cam_t_new)
        optical = pixel_to_optical(u, v, true_depth)
        mapped = optical_to_map(optical)  # stale CAM_T
        depth_used = true_depth
        frame = "map"
    else:
        raise ValueError(f"unknown case {case}")

    err = _sub(mapped, TRUE_MAP)
    err_xy = math.hypot(err[0], err[1])
    return {
        "case": case,
        "u": u,
        "v": v,
        "depth": depth_used,
        "map_x": mapped[0],
        "map_y": mapped[1],
        "map_z": mapped[2],
        "err_x": err[0],
        "err_y": err[1],
        "err_z": err[2],
        "err_xy": err_xy,
        "frame": frame,
    }
