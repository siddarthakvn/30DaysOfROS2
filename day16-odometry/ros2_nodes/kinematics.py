#!/usr/bin/env python3
"""Turn left and right wheel rotation into a pose.

Each step:
  v  = (v_r + v_l) / 2
  w  = (v_r - v_l) / track_width
  x += v * cos(yaw) * dt
  y += v * sin(yaw) * dt
  yaw += w * dt

v_l and v_r are wheel contact speeds: angular_rate * radius.
"""

from __future__ import annotations

import math


def integrate(
    omega_left: float,
    omega_right: float,
    radius: float,
    track_width: float,
    seconds: float,
    dt: float = 0.001,
    x: float = 0.0,
    y: float = 0.0,
    yaw: float = 0.0,
) -> dict:
    if radius <= 0.0 or track_width <= 0.0 or dt <= 0.0 or seconds < 0.0:
        raise ValueError("radius, track width, and dt must be > 0")
    v_l = omega_left * radius
    v_r = omega_right * radius
    v = 0.5 * (v_r + v_l)
    w = (v_r - v_l) / track_width
    steps = int(round(seconds / dt))
    for _ in range(steps):
        x += v * math.cos(yaw) * dt
        y += v * math.sin(yaw) * dt
        yaw += w * dt
    return {
        "x": x,
        "y": y,
        "yaw": yaw,
        "v": v,
        "w": w,
        "body_vy": 0.0,
    }
