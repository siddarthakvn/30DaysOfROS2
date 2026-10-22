#!/usr/bin/env python3
"""Why a planner swerves across an empty floor.

The simulator room has walls and no cushion. The global costmap is a different
picture. An earlier scan marked one cell while the cushion was still there.
The robot is now farther away than raytrace_max_range, so the obstacle layer
never clears that cell. The inflation layer then grows it by the robot radius.

Numbers below are the Humble nav2_bringup defaults, copied from
/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml.
"""

from __future__ import annotations

import heapq
import math

RES = 0.05
WIDTH = 6.0
HEIGHT = 4.0
NX = int(round(WIDTH / RES))
NY = int(round(HEIGHT / RES))

FREE = 0
INSCRIBED = 253
LETHAL = 254
UNKNOWN = 255

# nav2_bringup global_costmap / local_costmap defaults.
ROBOT_RADIUS = 0.22
INFLATION_RADIUS = 0.55
COST_SCALING = 3.0
OBSTACLE_MAX = 2.5
RAYTRACE_MAX = 3.0
LOCAL_WIDTH = 3.0
LOCAL_HEIGHT = 3.0

# NavFn translates a traversable cost as COST_NEUTRAL + COST_FACTOR * cost.
COST_NEUTRAL = 50.0
COST_FACTOR = 0.8

START = (0.80, 2.00)
GOAL = (5.20, 2.00)
# World point of the old return. The cell that contains it is the phantom.
CUSHION_POINT = (4.00, 2.00)
# Where the robot was when the return was inside obstacle_max_range.
MARK_POSE = (1.70, 2.00)


def cell_of(x: float, y: float) -> tuple[int, int]:
    return int(x / RES), int(y / RES)


def center(ix: int, iy: int) -> tuple[float, float]:
    return (ix + 0.5) * RES, (iy + 0.5) * RES


CUSHION = cell_of(*CUSHION_POINT)


def empty() -> list[list[int]]:
    return [[FREE for _ in range(NX)] for _ in range(NY)]


def is_wall(ix: int, iy: int) -> bool:
    return ix <= 0 or iy <= 0 or ix >= NX - 1 or iy >= NY - 1


def static_layer() -> list[list[int]]:
    grid = empty()
    for iy in range(NY):
        for ix in range(NX):
            if is_wall(ix, iy):
                grid[iy][ix] = LETHAL
    return grid


def in_map(ix: int, iy: int) -> bool:
    return 0 <= ix < NX and 0 <= iy < NY


def cast_scan(
    obstacle: list[list[int]],
    pose: tuple[float, float],
    cushion_present: bool,
) -> None:
    """Mark hits inside obstacle_max_range. Clear cells out to raytrace_max_range.

    A hit stops the ray, so the endpoint stays lethal. Past raytrace_max_range
    the old value is left alone. That is how a cell marked up close survives
    once the robot has backed away.
    """
    ox, oy = pose
    step = RES * 0.5
    for deg in range(360):
        ang = math.radians(deg)
        dist = 0.0
        while True:
            dist += step
            if dist > RAYTRACE_MAX:
                break
            x = ox + math.cos(ang) * dist
            y = oy + math.sin(ang) * dist
            ix, iy = cell_of(x, y)
            if not in_map(ix, iy):
                break
            hit = is_wall(ix, iy) or (cushion_present and (ix, iy) == CUSHION)
            if hit:
                if dist <= OBSTACLE_MAX:
                    obstacle[iy][ix] = LETHAL
                break
            obstacle[iy][ix] = FREE


def remember_cushion() -> list[list[int]]:
    """Obstacle layer after the cushion is gone and the robot is back at the start."""
    obstacle = empty()
    cast_scan(obstacle, MARK_POSE, cushion_present=True)
    cast_scan(obstacle, START, cushion_present=False)
    return obstacle


def live_obstacle() -> list[list[int]]:
    obstacle = empty()
    cast_scan(obstacle, START, cushion_present=False)
    return obstacle


def inflation_cost(distance_m: float) -> int:
    """nav2_costmap_2d::InflationLayer::computeCost, distance already in meters."""
    if distance_m == 0.0:
        return LETHAL
    if distance_m <= ROBOT_RADIUS:
        return INSCRIBED
    factor = math.exp(-1.0 * COST_SCALING * (distance_m - ROBOT_RADIUS))
    return int((INSCRIBED - 1) * factor)


def inflate(master: list[list[int]]) -> None:
    lethal = [
        (ix, iy)
        for iy in range(NY)
        for ix in range(NX)
        if master[iy][ix] == LETHAL
    ]
    reach = int(math.ceil(INFLATION_RADIUS / RES))
    for sx, sy in lethal:
        for iy in range(max(0, sy - reach), min(NY, sy + reach + 1)):
            for ix in range(max(0, sx - reach), min(NX, sx + reach + 1)):
                dist = math.hypot(ix - sx, iy - sy) * RES
                if dist > INFLATION_RADIUS:
                    continue
                cost = inflation_cost(dist)
                if cost > master[iy][ix]:
                    master[iy][ix] = cost


def master_grid(obstacle: list[list[int]], use_inflation: bool) -> list[list[int]]:
    static = static_layer()
    grid = empty()
    for iy in range(NY):
        for ix in range(NX):
            grid[iy][ix] = max(static[iy][ix], obstacle[iy][ix])
    if use_inflation:
        inflate(grid)
    return grid


def local_grid() -> tuple[list[list[int]], float, float, int]:
    """Rolling window around the robot, filled only by the scan from here.

    The cushion cell is outside this window, so the local map cannot be the
    thing that bends the path.
    """
    cells = int(round(LOCAL_WIDTH / RES))
    origin_x = START[0] - LOCAL_WIDTH / 2.0
    origin_y = START[1] - LOCAL_HEIGHT / 2.0
    # Current scan only. The remembered cushion is not in this layer.
    full = master_grid(live_obstacle(), use_inflation=True)
    grid = [[UNKNOWN for _ in range(cells)] for _ in range(cells)]
    cushion_here = 0
    for iy in range(cells):
        for ix in range(cells):
            wx, wy = origin_x + (ix + 0.5) * RES, origin_y + (iy + 0.5) * RES
            gx, gy = cell_of(wx, wy)
            if not in_map(gx, gy):
                continue
            grid[iy][ix] = full[gy][gx]
            if (gx, gy) == CUSHION:
                cushion_here = grid[iy][ix]
    return grid, origin_x, origin_y, cushion_here


def _blocked(cost: int) -> bool:
    return cost >= INSCRIBED


def plan(grid: list[list[int]]) -> list[tuple[float, float]]:
    """8-connected A*. Cells at 253 and 254 are closed, as in NavFn.

    A cheaper cell is preferred by the same scale NavFn publishes:
    step length times (50 + 0.8 * cost) / 50.
    """
    start = cell_of(*START)
    goal = cell_of(*GOAL)
    if _blocked(grid[start[1]][start[0]]) or _blocked(grid[goal[1]][goal[0]]):
        return []

    def penalty(ix: int, iy: int) -> float:
        return (COST_NEUTRAL + COST_FACTOR * grid[iy][ix]) / COST_NEUTRAL

    open_heap: list[tuple[float, tuple[int, int]]] = []
    heapq.heappush(open_heap, (0.0, start))
    came: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {start: 0.0}
    closed: set[tuple[int, int]] = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        if current == goal:
            chain = [current]
            while chain[-1] in came:
                chain.append(came[chain[-1]])
            chain.reverse()
            return [center(ix, iy) for ix, iy in chain]
        cx, cy = current
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nxt = (cx + dx, cy + dy)
                nx, ny = nxt
                if not in_map(nx, ny) or _blocked(grid[ny][nx]):
                    continue
                # Do not squeeze between two blocked cells.
                if dx != 0 and dy != 0:
                    if _blocked(grid[cy][cx + dx]) or _blocked(grid[cy + dy][cx]):
                        continue
                dist = math.hypot(dx, dy) * RES
                tentative = g_score[current] + dist * penalty(nx, ny)
                if tentative < g_score.get(nxt, 1e18):
                    came[nxt] = current
                    g_score[nxt] = tentative
                    hx, hy = center(nx, ny)
                    gx, gy = center(*goal)
                    heapq.heappush(open_heap, (tentative + math.hypot(gx - hx, gy - hy), nxt))
    return []


def path_length(path: list[tuple[float, float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))


def cushion_neighborhood(grid: list[list[int]]) -> tuple[int, int, int]:
    """Lethal, inscribed, and other nonzero cells within the inflation radius."""
    cx, cy = center(*CUSHION)
    lethal = inscribed = other = 0
    reach = INFLATION_RADIUS + RES
    for iy in range(NY):
        for ix in range(NX):
            x, y = center(ix, iy)
            if math.hypot(x - cx, y - cy) > reach:
                continue
            cost = grid[iy][ix]
            if cost == LETHAL and not is_wall(ix, iy):
                lethal += 1
            elif cost == INSCRIBED:
                inscribed += 1
            elif cost > FREE:
                other += 1
    return lethal, inscribed, other


def run(mode: str) -> dict:
    if mode == "live":
        obstacle = live_obstacle()
        grid = master_grid(obstacle, use_inflation=True)
    elif mode == "stale":
        obstacle = remember_cushion()
        grid = master_grid(obstacle, use_inflation=False)
    elif mode == "inflated":
        obstacle = remember_cushion()
        grid = master_grid(obstacle, use_inflation=True)
    else:
        raise ValueError(mode)

    path = plan(grid)
    cx, cy = center(*CUSHION)
    cushion_cost = grid[CUSHION[1]][CUSHION[0]]
    lethal, inscribed, other = cushion_neighborhood(grid)
    local, origin_x, origin_y, local_cushion = local_grid()
    local_has = 0 <= int((cx - origin_x) / RES) < len(local[0]) and 0 <= int((cy - origin_y) / RES) < len(local)
    straight = math.hypot(GOAL[0] - START[0], GOAL[1] - START[1])
    if path:
        min_clear = min(math.hypot(p[0] - cx, p[1] - cy) for p in path)
        dev = max(abs(p[1] - START[1]) for p in path)
        through = any(cell_of(p[0], p[1]) == CUSHION for p in path)
    else:
        min_clear = float("nan")
        dev = float("nan")
        through = False
    mark_range = math.hypot(center(*CUSHION)[0] - MARK_POSE[0], center(*CUSHION)[1] - MARK_POSE[1])
    now_range = math.hypot(cx - START[0], cy - START[1])
    return {
        "mode": mode,
        "grid": grid,
        "path": path,
        "straight_m": straight,
        "path_poses": len(path),
        "path_length_m": path_length(path),
        "path_dev_m": dev,
        "min_clearance_m": min_clear,
        "through_cushion": through,
        "global_cushion": cushion_cost,
        "phantom_lethal": lethal,
        "inscribed_cells": inscribed,
        "gradient_cells": other,
        "local_has_cushion": local_has,
        "local_cushion": local_cushion,
        "local_origin": (origin_x, origin_y),
        "mark_range_m": mark_range,
        "now_range_m": now_range,
        "cushion_xy": (cx, cy),
    }


def ascii_scene(result: dict) -> str:
    grid = result["grid"]
    path_cells = {cell_of(x, y) for x, y in result["path"]}
    lines = []
    # One character per 0.10 m, y downward so the page matches a top-down photo.
    for iy in range(NY - 1, -1, -2):
        row = []
        for ix in range(0, NX, 2):
            if (ix, iy) == cell_of(*START) or (ix + 1, iy) == cell_of(*START):
                row.append("S")
            elif (ix, iy) == cell_of(*GOAL) or (ix + 1, iy) == cell_of(*GOAL):
                row.append("G")
            elif (ix, iy) == CUSHION or (ix + 1, iy) == CUSHION:
                row.append("C")
            elif (ix, iy) in path_cells or (ix + 1, iy) in path_cells or (ix, iy - 1) in path_cells:
                row.append(".")
            else:
                cost = max(grid[iy][ix], grid[min(iy, NY - 1)][min(ix + 1, NX - 1)])
                if cost >= LETHAL:
                    row.append("#")
                elif cost >= INSCRIBED:
                    row.append("O")
                elif cost > FREE:
                    row.append("+")
                else:
                    row.append(" ")
        lines.append("".join(row))
    return "\n".join(lines)


def summary_line(result: dict) -> str:
    local = "outside" if not result["local_has_cushion"] else str(result["local_cushion"])
    return (
        f"SUMMARY mode={result['mode']} "
        f"global_cushion={result['global_cushion']} "
        f"local_cushion={local} "
        f"phantom_lethal={result['phantom_lethal']} "
        f"inscribed_cells={result['inscribed_cells']} "
        f"gradient_cells={result['gradient_cells']} "
        f"path_poses={result['path_poses']} "
        f"path_length_m={result['path_length_m']:.2f} "
        f"straight_m={result['straight_m']:.2f} "
        f"path_dev_m={result['path_dev_m']:.2f} "
        f"min_clearance_m={result['min_clearance_m']:.3f} "
        f"through_cushion={int(result['through_cushion'])} "
        f"mark_range_m={result['mark_range_m']:.3f} "
        f"now_range_m={result['now_range_m']:.3f}"
    )


if __name__ == "__main__":
    for name in ("live", "stale", "inflated"):
        result = run(name)
        print(summary_line(result), flush=True)
        print("MAP", flush=True)
        print(ascii_scene(result), flush=True)
        print("MAP_END", flush=True)
