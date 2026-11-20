"""Three-robot fleet layout, rescue target, and controller constants."""

from __future__ import annotations

import math

ROBOTS = ("r1", "r2", "r3")

START_POSES: dict[str, tuple[float, float]] = {
    "r1": (1.00, 3.00),
    "r2": (1.00, 1.00),
    "r3": (5.00, 1.00),
}

TARGET_XY = (2.50, 3.00)

DT = 0.05
KP = 2.5
MAX_SPEED = 1.40
GOAL_TOLERANCE = 0.04
WINDOW_SEC = 3.5


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def clamp_vec(vx: float, vy: float, limit: float = MAX_SPEED) -> tuple[float, float]:
    mag = math.hypot(vx, vy)
    if mag <= limit or mag == 0.0:
        return vx, vy
    scale = limit / mag
    return vx * scale, vy * scale
