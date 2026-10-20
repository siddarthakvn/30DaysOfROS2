#!/usr/bin/env python3
"""Goal, path, and speed are three different steps.

A wall sits between the start and the goal. The straight command would hit it.
The planner draws a line around the wall. The controller turns that line into
Twist. The goal itself never becomes a wheel speed.
"""

from __future__ import annotations

import math

# Wall blocks the direct hallway. Inflate it so the path leaves a gap.
WALL = (2.3, 3.5, 0.0, 2.35)
START = (0.6, 0.6, 0.0)
GOAL = (5.2, 0.6, 0.0)
RES = 0.2
X_MAX = 6.0
Y_MAX = 4.0
LOOKAHEAD = 0.45
SPEED = 0.45
GOAL_TOLERANCE = 0.15


def blocked(x: float, y: float) -> bool:
    return WALL[0] <= x <= WALL[1] and WALL[2] <= y <= WALL[3]


def in_bounds(x: float, y: float) -> bool:
    return 0.15 <= x <= X_MAX - 0.15 and 0.15 <= y <= Y_MAX - 0.15 and not blocked(x, y)


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def plan(start: tuple[float, float], goal: tuple[float, float]) -> list[tuple[float, float]]:
    def cell(x: float, y: float) -> tuple[int, int]:
        return int(x / RES), int(y / RES)

    start_c = cell(*start)
    goal_c = cell(*goal)
    if blocked(*start) or blocked(*goal):
        return []

    open_set = {start_c}
    came: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {start_c: 0.0}
    f_score = {start_c: math.hypot(goal[0] - start[0], goal[1] - start[1])}

    def neighbors(c: tuple[int, int]) -> list[tuple[int, int]]:
        found = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nxt = (c[0] + dx, c[1] + dy)
                x, y = (nxt[0] + 0.5) * RES, (nxt[1] + 0.5) * RES
                if in_bounds(x, y):
                    found.append(nxt)
        return found

    while open_set:
        current = min(open_set, key=lambda c: f_score.get(c, 1e9))
        if current == goal_c:
            path = [current]
            while path[-1] in came:
                path.append(came[path[-1]])
            path.reverse()
            return [((c[0] + 0.5) * RES, (c[1] + 0.5) * RES) for c in path]
        open_set.remove(current)
        for nxt in neighbors(current):
            step = math.hypot(nxt[0] - current[0], nxt[1] - current[1]) * RES
            tentative = g_score[current] + step
            if tentative < g_score.get(nxt, 1e9):
                came[nxt] = current
                g_score[nxt] = tentative
                x, y = (nxt[0] + 0.5) * RES, (nxt[1] + 0.5) * RES
                f_score[nxt] = tentative + math.hypot(goal[0] - x, goal[1] - y)
                open_set.add(nxt)
    return []


def path_length(path: list[tuple[float, float]]) -> float:
    total = 0.0
    for a, b in zip(path, path[1:]):
        total += math.hypot(b[0] - a[0], b[1] - a[1])
    return total


def max_y(path: list[tuple[float, float]]) -> float:
    return max((p[1] for p in path), default=0.0)


def _nearest(path: list[tuple[float, float]], pose: tuple[float, float, float]) -> int:
    return min(range(len(path)), key=lambda i: math.hypot(path[i][0] - pose[0], path[i][1] - pose[1]))


def lookahead_point(path: list[tuple[float, float]], pose: tuple[float, float, float]) -> tuple[float, float]:
    index = _nearest(path, pose)
    travelled = 0.0
    point = path[index]
    for a, b in zip(path[index:], path[index + 1 :]):
        travelled += math.hypot(b[0] - a[0], b[1] - a[1])
        point = b
        if travelled >= LOOKAHEAD:
            break
    return point


def control(pose: tuple[float, float, float], path: list[tuple[float, float]]) -> tuple[float, float]:
    gx, gy = path[-1]
    distance = math.hypot(gx - pose[0], gy - pose[1])
    if distance < GOAL_TOLERANCE:
        return 0.0, 0.0
    tx, ty = lookahead_point(path, pose)
    heading = math.atan2(ty - pose[1], tx - pose[0])
    error = wrap(heading - pose[2])
    linear = SPEED * max(0.0, math.cos(error))
    angular = 1.8 * error
    return linear, max(-1.2, min(1.2, angular))


def integrate(pose: tuple[float, float, float], linear: float, angular: float, dt: float) -> tuple[float, float, float]:
    x, y, yaw = pose
    return (
        x + linear * math.cos(yaw) * dt,
        y + linear * math.sin(yaw) * dt,
        wrap(yaw + angular * dt),
    )


def follow(path: list[tuple[float, float]], goal: tuple[float, float, float]) -> dict:
    pose = START
    samples = []
    hit_wall = False
    for _ in range(800):
        linear, angular = control(pose, path)
        samples.append((linear, angular))
        pose = integrate(pose, linear, angular, 0.05)
        if blocked(pose[0], pose[1]):
            hit_wall = True
            break
        if math.hypot(pose[0] - goal[0], pose[1] - goal[1]) < GOAL_TOLERANCE:
            break
    nonzero = sum(1 for v, w in samples if abs(v) > 0.01 or abs(w) > 0.01)
    return {
        "pose": pose,
        "error": math.hypot(pose[0] - goal[0], pose[1] - goal[1]),
        "cmd_samples": len(samples),
        "cmd_nonzero": nonzero,
        "max_linear": max((abs(v) for v, _ in samples), default=0.0),
        "max_angular": max((abs(w) for _, w in samples), default=0.0),
        "hit_wall": hit_wall,
        "first_cmd": samples[0] if samples else (0.0, 0.0),
    }


def straight_length() -> float:
    return math.hypot(GOAL[0] - START[0], GOAL[1] - START[1])


def ascii_scene(path: list[tuple[float, float]], pose: tuple[float, float, float]) -> str:
    cols, rows = 32, 16
    grid = [[" " for _ in range(cols)] for _ in range(rows)]

    def cell(x: float, y: float) -> tuple[int, int] | None:
        ix = int(x / X_MAX * (cols - 1))
        iy = int(y / Y_MAX * (rows - 1))
        if ix < 0 or iy < 0 or ix >= cols or iy >= rows:
            return None
        return ix, rows - 1 - iy

    for iy in range(rows):
        for ix in range(cols):
            x = ix / (cols - 1) * X_MAX
            y = (rows - 1 - iy) / (rows - 1) * Y_MAX
            if blocked(x, y):
                grid[iy][ix] = "#"
    for point in path[::2]:
        spotted = cell(*point)
        if spotted and grid[spotted[1]][spotted[0]] == " ":
            grid[spotted[1]][spotted[0]] = "."
    for point, mark in ((START[:2], "S"), (GOAL[:2], "G"), (pose[:2], "R")):
        spotted = cell(*point)
        if spotted:
            grid[spotted[1]][spotted[0]] = mark
    return "\n".join("".join(row) for row in grid)


def run(mode: str, goal: tuple[float, float, float] = GOAL) -> dict:
    """mode: goal_only, planner_only, full."""
    events = ["goal"]
    path: list[tuple[float, float]] = []
    pose = START
    cmd = (0.0, 0.0)
    result = "ABORTED"
    followed = None
    if mode in ("planner_only", "full"):
        path = plan(START[:2], goal[:2])
        events.append("path")
    if mode == "full" and path:
        followed = follow(path, goal)
        pose = followed["pose"]
        cmd = followed["first_cmd"]
        events.append("cmd_vel")
        if followed["error"] < GOAL_TOLERANCE and not followed["hit_wall"]:
            result = "SUCCEEDED"
    error = math.hypot(pose[0] - goal[0], pose[1] - goal[1])
    return {
        "mode": mode,
        "events": ">".join(events),
        "path_poses": len(path),
        "path_length_m": path_length(path),
        "straight_m": straight_length(),
        "path_max_y_m": max_y(path),
        "wall_top_m": WALL[3],
        "final_error_m": error,
        "result": result,
        "cmd_nonzero": 0 if followed is None else followed["cmd_nonzero"],
        "max_linear": 0.0 if followed is None else followed["max_linear"],
        "max_angular": 0.0 if followed is None else followed["max_angular"],
        "hit_wall": False if followed is None else followed["hit_wall"],
        "first_linear": cmd[0],
        "first_angular": cmd[1],
        "pose": pose,
        "path": path,
    }


def _demo() -> None:
    for mode in ("goal_only", "planner_only", "full"):
        result = run(mode)
        print(
            f"SUMMARY mode={result['mode']} events={result['events']} "
            f"result={result['result']} path_poses={result['path_poses']} "
            f"path_length_m={result['path_length_m']:.2f} "
            f"straight_m={result['straight_m']:.2f} "
            f"path_max_y_m={result['path_max_y_m']:.2f} "
            f"final_error_m={result['final_error_m']:.3f} "
            f"cmd_nonzero={result['cmd_nonzero']} "
            f"max_linear={result['max_linear']:.2f} "
            f"hit_wall={int(result['hit_wall'])}"
        )
        print(ascii_scene(result["path"], result["pose"]))
        print()


if __name__ == "__main__":
    _demo()
