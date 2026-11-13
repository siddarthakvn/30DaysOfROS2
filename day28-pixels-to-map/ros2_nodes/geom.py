"""Camera, robot pose, and the surveyed box. The pixel is computed from these."""

from __future__ import annotations

import math

from sensor_msgs.msg import CameraInfo

WIDTH = 640
HEIGHT = 480
FX = 500.0
FY = 500.0
CX = 320.0
CY = 240.0

# map -> base_link. The robot faces +x.
BASE_XYZ = (1.00, 2.00, 0.00)
BASE_YAW = 0.0

# base_link -> camera_link. The lens is ahead of the base and above the floor.
CAM_XYZ = (0.20, 0.00, 0.30)
CAM_RPY = (0.0, 0.0, 0.0)

# camera_link -> camera_optical_frame. Optical axes match the image: x right, y down, z forward.
OPTICAL_RPY = (-math.pi / 2.0, 0.0, -math.pi / 2.0)

# Surveyed box center, meters, in the map.
TARGET = (3.50, 2.20, 0.25)


def quaternion_from_euler(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    """Roll, pitch, yaw about fixed axes x, y, z. Same convention as tf_transformations sxyz."""
    half_roll = roll * 0.5
    half_pitch = pitch * 0.5
    half_yaw = yaw * 0.5
    cr, sr = math.cos(half_roll), math.sin(half_roll)
    cp, sp = math.cos(half_pitch), math.sin(half_pitch)
    cy, sy = math.cos(half_yaw), math.sin(half_yaw)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def camera_info() -> CameraInfo:
    msg = CameraInfo()
    msg.width = WIDTH
    msg.height = HEIGHT
    msg.distortion_model = "plumb_bob"
    msg.d = [0.0, 0.0, 0.0, 0.0, 0.0]
    msg.k = [FX, 0.0, CX, 0.0, FY, CY, 0.0, 0.0, 1.0]
    msg.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    msg.p = [FX, 0.0, CX, 0.0, 0.0, FY, CY, 0.0, 0.0, 0.0, 1.0, 0.0]
    msg.header.frame_id = "camera_optical_frame"
    return msg


def backproject(model, u: float, v: float, depth_z: float) -> tuple[float, float, float]:
    """Optical-frame point. depth_z is Z along the optical axis, not the range."""
    ray = model.projectPixelTo3dRay((u, v))
    scale = depth_z / ray[2]
    return (ray[0] * scale, ray[1] * scale, ray[2] * scale)


def distance(a, b) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
