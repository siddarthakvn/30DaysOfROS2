#!/usr/bin/env python3
"""How a planner picks a path from A to B.

The straight line crosses a wall. Dijkstra floods outward by travel cost
alone. A* adds the straight-line distance still left, so it opens fewer
cells. With that guess never larger than the real distance left, both
searches return a shortest path.
"""

from __future__ import annotations

import heapq
import math

RES = 0.1
WIDTH = 8.0
HEIGHT = 6.0
NX = int(round(WIDTH / RES))
NY = int(round(HEIGHT / RES))

START = (1.0, 1.2)
GOAL = (7.0, 4.8)
# Two vertical bars. The straight line from A to B crosses the upper one.
WALLS = (
    (3.2, 3.6, 2.4, 5.6),
    (4.6, 5.0, 0.4, 3.2),
)


def cell_of(x: float, y: float) -> tuple[int, int]:
    return int(x / RES), int(y / RES)


def center(ix: int, iy: int) -> tuple[float, float]:
    return (ix + 0.5) * RES, (iy + 0.5) * RES


def in_map(ix: int, iy: int) -> bool:
    return 0 <= ix < NX and 0 <= iy < NY


def is_wall(ix: int, iy: int) -> bool:
    x, y = center(ix, iy)
    if ix <= 0 or iy <= 0 or ix >= NX - 1 or iy >= NY - 1:
        return True
    for x0, x1, y0, y1 in WALLS:
        if x0 <= x <= x1 and y0 <= y <= y1:
            return True
    return False


def straight_hits() -> int:
    """How many samples of the A-to-B line sit on a wall."""
    hits = 0
    steps = int(math.hypot(GOAL[0] - START[0], GOAL[1] - START[1]) / (RES * 0.5))
    for i in range(steps + 1):
        t = i / steps
        x = START[0] + (GOAL[0] - START[0]) * t
        y = START[1] + (GOAL[1] - START[1]) * t
        ix, iy = cell_of(x, y)
        if in_map(ix, iy) and is_wall(ix, iy):
            hits += 1
    return hits


def search(kind: str) -> dict:
    """kind is 'line', 'dijkstra', or 'astar'."""
    start = cell_of(*START)
    goal = cell_of(*GOAL)
    straight = math.hypot(GOAL[0] - START[0], GOAL[1] - START[1])
    hits = straight_hits()
    if kind == "line":
        return {
            "mode": kind,
            "path": [],
            "expanded": 0,
            "straight_m": straight,
            "path_length_m": 0.0,
            "path_poses": 0,
            "line_wall_hits": hits,
            "reached": 0,
            "visited": set(),
        }

    heuristic = 1.0 if kind == "astar" else 0.0
    gx, gy = center(*goal)

    def h(ix: int, iy: int) -> float:
        x, y = center(ix, iy)
        return heuristic * math.hypot(gx - x, gy - y)

    open_heap: list[tuple[float, int, tuple[int, int]]] = []
    heapq.heappush(open_heap, (h(*start), 0, start))
    came: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {start: 0.0}
    closed: set[tuple[int, int]] = set()
    order = 0

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        if current == goal:
            chain = [current]
            while chain[-1] in came:
                chain.append(came[chain[-1]])
            chain.reverse()
            path = [center(ix, iy) for ix, iy in chain]
            return {
                "mode": kind,
                "path": path,
                "expanded": len(closed),
                "straight_m": straight,
                "path_length_m": _length(path),
                "path_poses": len(path),
                "line_wall_hits": hits,
                "reached": 1,
                "visited": closed,
            }
        cx, cy = current
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nxt = (cx + dx, cy + dy)
                nx, ny = nxt
                if not in_map(nx, ny) or is_wall(nx, ny) or nxt in closed:
                    continue
                if dx != 0 and dy != 0 and (is_wall(cx + dx, cy) or is_wall(cx, cy + dy)):
                    continue
                dist = math.hypot(dx, dy) * RES
                tentative = g_score[current] + dist
                if tentative < g_score.get(nxt, 1e18):
                    came[nxt] = current
                    g_score[nxt] = tentative
                    order += 1
                    heapq.heappush(open_heap, (tentative + h(nx, ny), order, nxt))
    return {
        "mode": kind,
        "path": [],
        "expanded": len(closed),
        "straight_m": straight,
        "path_length_m": 0.0,
        "path_poses": 0,
        "line_wall_hits": hits,
        "reached": 0,
        "visited": closed,
    }


def _length(path: list[tuple[float, float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))


def ascii_scene(result: dict) -> str:
    path_cells = {cell_of(x, y) for x, y in result["path"]}
    visited = result["visited"]
    lines = []
    for iy in range(NY - 1, -1, -1):
        row = []
        for ix in range(NX):
            if (ix, iy) == cell_of(*START):
                row.append("A")
            elif (ix, iy) == cell_of(*GOAL):
                row.append("B")
            elif is_wall(ix, iy):
                row.append("#")
            elif (ix, iy) in path_cells:
                row.append(".")
            elif (ix, iy) in visited:
                row.append("+")
            else:
                row.append(" ")
        lines.append("".join(row))
    return "\n".join(lines)


def free_count() -> int:
    return sum(1 for iy in range(NY) for ix in range(NX) if not is_wall(ix, iy))


def summary_line(result: dict) -> str:
    return (
        f"SUMMARY mode={result['mode']} "
        f"reached={result['reached']} "
        f"expanded={result['expanded']} "
        f"free_cells={free_count()} "
        f"path_poses={result['path_poses']} "
        f"path_length_m={result['path_length_m']:.2f} "
        f"straight_m={result['straight_m']:.2f} "
        f"line_wall_hits={result['line_wall_hits']}"
    )


if __name__ == "__main__":
    for name in ("line", "dijkstra", "astar"):
        result = search(name)
        print(summary_line(result), flush=True)
        print("MAP", flush=True)
        print(ascii_scene(result), flush=True)
        print("MAP_END", flush=True)
