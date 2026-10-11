"""Planar predict-then-correct filter for one scripted straight drive.

Truth is 1.0 m/s straight for 10 s, so the pose ends at x=10, y=0, yaw=0.
The wheel speed is 10% high. The gyro reports 0.02 rad/s while the robot
is not turning. Wheel yaw rate is noisy and unbiased.
"""

from __future__ import annotations

import math
import random

DT = 0.01
SECONDS = 10.0
TRUE_V = 1.0
WHEEL_V = 1.10
GYRO_RATE = 0.02
WHEEL_YAW_SIGMA = 0.05
SEED = 18


def wrap(angle: float) -> float:
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def _steps() -> int:
    return int(round(SECONDS / DT))


def wheel_yaw_rates() -> list[float]:
    rng = random.Random(SEED)
    return [rng.gauss(0.0, WHEEL_YAW_SIGMA) for _ in range(_steps())]


def integrate_wheels(rates: list[float]) -> tuple[float, float, float]:
    x = y = yaw = 0.0
    for z in rates:
        yaw = wrap(yaw + z * DT)
        x += WHEEL_V * math.cos(yaw) * DT
        y += WHEEL_V * math.sin(yaw) * DT
    return x, y, yaw


def integrate_gyro() -> tuple[float, float, float]:
    x = y = yaw = 0.0
    for _ in range(_steps()):
        yaw = wrap(yaw + GYRO_RATE * DT)
        x += TRUE_V * math.cos(yaw) * DT
        y += TRUE_V * math.sin(yaw) * DT
    return x, y, yaw


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    rows = len(a)
    cols = len(b[0])
    inner = len(b)
    return [
        [sum(a[i][k] * b[k][j] for k in range(inner)) for j in range(cols)]
        for i in range(rows)
    ]


def _add(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [
        [a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))
    ]


def _transpose(a: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*a)]


def fuse(rates: list[float]) -> dict[str, float]:
    """Predict with wheel speed and gyro. Correct the gyro bias from wheel yaw rate."""
    x = y = yaw = bias = 0.0
    p = [[0.0] * 4 for _ in range(4)]
    p[0][0] = 1e-4
    p[1][1] = 1e-4
    p[2][2] = 0.05
    p[3][3] = 0.01
    q_diag = (1e-8, 1e-8, 1e-8, 1e-10)
    r = WHEEL_YAW_SIGMA ** 2

    for z in rates:
        f = [
            [1.0, 0.0, -WHEEL_V * math.sin(yaw) * DT, 0.0],
            [0.0, 1.0, WHEEL_V * math.cos(yaw) * DT, 0.0],
            [0.0, 0.0, 1.0, -DT],
            [0.0, 0.0, 0.0, 1.0],
        ]
        x = x + WHEEL_V * math.cos(yaw) * DT
        y = y + WHEEL_V * math.sin(yaw) * DT
        yaw = wrap(yaw + (GYRO_RATE - bias) * DT)
        q = [[q_diag[r_i] if r_i == c else 0.0 for c in range(4)] for r_i in range(4)]
        p = _add(_matmul(_matmul(f, p), _transpose(f)), q)

        predicted_rate = GYRO_RATE - bias
        innovation = z - predicted_rate
        s = p[3][3] + r
        k = [p[row][3] * (-1.0) / s for row in range(4)]
        x += k[0] * innovation
        y += k[1] * innovation
        yaw = wrap(yaw + k[2] * innovation)
        bias += k[3] * innovation
        h = (0.0, 0.0, 0.0, -1.0)
        i_kh = [
            [(1.0 if row == col else 0.0) - k[row] * h[col] for col in range(4)]
            for row in range(4)
        ]
        p = _matmul(i_kh, p)

    return {
        "x": x,
        "y": y,
        "yaw": yaw,
        "bias": bias,
        "yaw_var": p[2][2],
    }


def fight(steps: int = 20) -> dict[str, float]:
    """Two yaw readings, 0 and 0.20 rad, both with tiny variance. The guess snaps."""
    yaw = 0.0
    variance = 0.05
    jumps = 0
    previous = yaw
    low = high = yaw
    measurement_var = 1e-6
    for i in range(steps):
        variance += 0.02
        measured = 0.0 if i % 2 == 0 else 0.20
        gain = variance / (variance + measurement_var)
        yaw = yaw + gain * (measured - yaw)
        variance = (1.0 - gain) * variance
        low = min(low, yaw)
        high = max(high, yaw)
        if abs(yaw - previous) > math.radians(5.0):
            jumps += 1
        previous = yaw
    return {
        "yaw": yaw,
        "jumps": float(jumps),
        "span": high - low,
        "yaw_var": variance,
    }
