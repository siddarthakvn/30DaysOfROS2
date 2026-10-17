#!/usr/bin/env python3
"""A frozen house map and a tiny particle filter.

The map is the floor plan. Guesses are poses dropped on its free space.
Wheels move every guess. The laser scores each guess. Resampling keeps the
ones that fit.
"""

from __future__ import annotations

import math
import random

# Outer rectangle 8 m by 5 m. Kitchen is the left room.
# A doorway in the wall at x = 3 faces the hall. The bedroom sits at the
# top-right, so a scan in each room looks different.
WALLS = (
    ((0.0, 0.0), (8.0, 0.0)),
    ((8.0, 0.0), (8.0, 5.0)),
    ((8.0, 5.0), (0.0, 5.0)),
    ((0.0, 5.0), (0.0, 0.0)),
    ((3.0, 0.0), (3.0, 1.3)),
    ((3.0, 2.7), (3.0, 5.0)),
    ((5.4, 2.4), (5.4, 5.0)),
    ((5.4, 2.4), (8.0, 2.4)),
)

# True walk stays in the kitchen. The view changes: wall, then doorway, then
# the far kitchen wall.
# Kitchen start, facing +x. The walk turns and drives inside the kitchen.
# The same body steps, applied to a bedroom guess, stay in the bedroom.
TRUE_POSES = (
    (1.4, 1.1, 0.0),
    (1.4, 1.1, math.pi / 2),
    (1.4, 2.1, math.pi / 2),
    (1.4, 3.0, math.pi / 2),
    (1.4, 3.0, 0.0),
    (1.9, 3.0, 0.0),
)

BEDROOM_GUESS = (6.5, 2.6, 0.0)
BEAMS = 90
MAX_RANGE = 8.0
PARTICLES = 400
MOTION_XY = 0.02
MOTION_YAW = math.radians(1.0)
SENSOR_SIGMA = 0.18


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def angles() -> list[float]:
    return [-math.pi + (2.0 * math.pi) * k / BEAMS for k in range(BEAMS)]


def ray_hit(ox: float, oy: float, theta: float) -> float:
    dx, dy = math.cos(theta), math.sin(theta)
    best = MAX_RANGE
    for (x1, y1), (x2, y2) in WALLS:
        sx, sy = x2 - x1, y2 - y1
        den = dx * sy - dy * sx
        if abs(den) < 1e-9:
            continue
        t = ((x1 - ox) * sy - (y1 - oy) * sx) / den
        u = ((x1 - ox) * dy - (y1 - oy) * dx) / den
        if t >= 0.0 and 0.0 <= u <= 1.0:
            best = min(best, t)
    return best


def scan_at(pose: tuple[float, float, float]) -> list[float]:
    x, y, yaw = pose
    return [ray_hit(x, y, yaw + a) for a in angles()]


def point_seg_dist(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    vx, vy = x2 - x1, y2 - y1
    length = vx * vx + vy * vy
    t = 0.0 if length == 0.0 else max(0.0, min(1.0, ((px - x1) * vx + (py - y1) * vy) / length))
    return math.hypot(px - (x1 + t * vx), py - (y1 + t * vy))


def near_wall(x: float, y: float, margin: float = 0.25) -> bool:
    return min(point_seg_dist(x, y, *a, *b) for a, b in WALLS) < margin


def in_house(x: float, y: float) -> bool:
    return 0.15 < x < 7.85 and 0.15 < y < 4.85 and not near_wall(x, y)


def body_delta(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    ax, ay, ayaw = a
    bx, by, byaw = b
    dx, dy = bx - ax, by - ay
    forward = math.cos(ayaw) * dx + math.sin(ayaw) * dy
    left = -math.sin(ayaw) * dx + math.cos(ayaw) * dy
    return forward, left, wrap(byaw - ayaw)


def apply_motion(pose: tuple[float, float, float], delta: tuple[float, float, float], noisy: bool, rng: random.Random) -> tuple[float, float, float]:
    x, y, yaw = pose
    forward, left, dyaw = delta
    if noisy:
        forward += rng.gauss(0.0, MOTION_XY)
        left += rng.gauss(0.0, MOTION_XY * 0.5)
        dyaw += rng.gauss(0.0, MOTION_YAW)
    # Move in the particle's own frame, then turn.
    nx = x + forward * math.cos(yaw) - left * math.sin(yaw)
    ny = y + forward * math.sin(yaw) + left * math.cos(yaw)
    return nx, ny, wrap(yaw + dyaw)


def mean_abs_error(expected: list[float], actual: list[float]) -> float:
    total = 0.0
    for e, a in zip(expected, actual):
        total += abs(e - a)
    return total / max(len(actual), 1)


def weight_of(error: float) -> float:
    return math.exp(-0.5 * (error / SENSOR_SIGMA) ** 2)


def resample_ok(particles: list[tuple[float, float, float]], weights: list[float], rng: random.Random) -> list[tuple[float, float, float]]:
    total = sum(weights)
    if total <= 0.0:
        return [p for p in particles]
    probs = [w / total for w in weights]
    cumulative = []
    running = 0.0
    for p in probs:
        running += p
        cumulative.append(running)
    step = 1.0 / len(particles)
    start = rng.random() * step
    chosen = []
    index = 0
    for i in range(len(particles)):
        target = start + i * step
        while index < len(cumulative) - 1 and cumulative[index] < target:
            index += 1
        chosen.append(particles[index])
    return chosen


def scatter(rng: random.Random, count: int) -> list[tuple[float, float, float]]:
    dots = []
    while len(dots) < count:
        pose = (rng.uniform(0.4, 7.6), rng.uniform(0.4, 4.6), rng.uniform(-math.pi, math.pi))
        if in_house(pose[0], pose[1]):
            dots.append(pose)
    return dots


def pose_error(pose: tuple[float, float, float], truth: tuple[float, float, float]) -> float:
    return math.hypot(pose[0] - truth[0], pose[1] - truth[1])


def spread(particles: list[tuple[float, float, float]]) -> float:
    mx = sum(p[0] for p in particles) / len(particles)
    my = sum(p[1] for p in particles) / len(particles)
    var = sum((p[0] - mx) ** 2 + (p[1] - my) ** 2 for p in particles) / len(particles)
    return math.sqrt(var)


def in_kitchen(pose: tuple[float, float, float]) -> bool:
    return pose[0] < 2.7


def jitter(pose: tuple[float, float, float], rng: random.Random) -> tuple[float, float, float]:
    return (
        pose[0] + rng.gauss(0.0, 0.10),
        pose[1] + rng.gauss(0.0, 0.10),
        wrap(pose[2] + rng.gauss(0.0, math.radians(3.0))),
    )


def cloud_mean(particles: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    n = len(particles)
    return (
        sum(p[0] for p in particles) / n,
        sum(p[1] for p in particles) / n,
        math.atan2(sum(math.sin(p[2]) for p in particles), sum(math.cos(p[2]) for p in particles)),
    )


def run(mode: str, seed: int = 20) -> dict:
    rng = random.Random(seed)
    if mode == "one_guess":
        particles = [BEDROOM_GUESS]
    else:
        particles = scatter(rng, PARTICLES)

    history = []
    actual_scans = [scan_at(pose) for pose in TRUE_POSES]
    # After the walk, the robot stands still and keeps scanning. A still
    # laser can pull a tight cloud onto the pose that matches.
    holds = 4 if mode == "laser_vote" else 0
    schedule = [(i, pose, False) for i, pose in enumerate(TRUE_POSES)]
    schedule += [(len(TRUE_POSES) + h, TRUE_POSES[-1], True) for h in range(holds)]
    for step, truth, held in schedule:
        if step > 0 and not held:
            delta = body_delta(TRUE_POSES[step - 1], truth)
            particles = [apply_motion(p, delta, mode != "one_guess", rng) for p in particles]
        weights = []
        for pose in particles:
            if mode != "laser_vote":
                weights.append(1.0)
                continue
            if not in_house(pose[0], pose[1]):
                weights.append(1e-18)
                continue
            seen = actual_scans[-1] if held else actual_scans[step]
            error = mean_abs_error(scan_at(pose), seen)
            weights.append(weight_of(error))
        if mode == "laser_vote":
            particles = [jitter(p, rng) for p in resample_ok(particles, weights, rng)]
        estimate = particles[0] if mode == "one_guess" else cloud_mean(particles)
        kitchen = sum(1 for p in particles if in_kitchen(p)) / len(particles)
        history.append(
            {
                "step": step,
                "error": pose_error(estimate, truth),
                "spread": spread(particles),
                "kitchen": kitchen,
                "estimate": estimate,
                "truth": truth,
            }
        )
    final = history[-1]
    return {
        "mode": mode,
        "particles": particles,
        "weights_note": mode,
        "final_error_m": final["error"],
        "final_spread_m": final["spread"],
        "kitchen_fraction": final["kitchen"],
        "history": history,
        "estimate": final["estimate"],
        "truth": final["truth"],
    }


def ascii_map(particles: list[tuple[float, float, float]], truth: tuple[float, float, float], estimate: tuple[float, float, float]) -> str:
    cols, rows = 42, 22
    grid = [[" " for _ in range(cols)] for _ in range(rows)]

    def cell(x: float, y: float) -> tuple[int, int] | None:
        ix = int(x / 8.0 * (cols - 1))
        iy = int(y / 5.0 * (rows - 1))
        if ix < 0 or iy < 0 or ix >= cols or iy >= rows:
            return None
        return ix, iy

    for (x1, y1), (x2, y2) in WALLS:
        length = max(int(math.hypot(x2 - x1, y2 - y1) / 0.15), 1)
        for i in range(length + 1):
            t = i / length
            spotted = cell(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
            if spotted:
                grid[rows - 1 - spotted[1]][spotted[0]] = "#"
    for pose in particles:
        spotted = cell(pose[0], pose[1])
        if spotted and grid[rows - 1 - spotted[1]][spotted[0]] == " ":
            grid[rows - 1 - spotted[1]][spotted[0]] = "."
    for pose, mark in ((estimate, "E"), (truth, "T")):
        spotted = cell(pose[0], pose[1])
        if spotted:
            grid[rows - 1 - spotted[1]][spotted[0]] = mark
    return "\n".join("".join(row) for row in grid)


def _demo() -> None:
    for mode in ("one_guess", "wheels_only", "laser_vote"):
        result = run(mode)
        print(
            f"SUMMARY mode={result['mode']} particles={len(result['particles'])} "
            f"final_error_m={result['final_error_m']:.3f} "
            f"final_spread_m={result['final_spread_m']:.3f} "
            f"kitchen_fraction={result['kitchen_fraction']:.3f}"
        )
        for row in result["history"]:
            print(
                f"  step={row['step']} error={row['error']:.3f} "
                f"spread={row['spread']:.3f} kitchen={row['kitchen']:.3f}"
            )
        print(ascii_map(result["particles"], result["truth"], result["estimate"]))
        print()


if __name__ == "__main__":
    _demo()
