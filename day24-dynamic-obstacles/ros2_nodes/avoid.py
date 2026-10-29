#!/usr/bin/env python3
"""What happens when a box appears on a path the robot is already following.

The global plan is drawn first, on an empty floor: a straight line from
start to goal. Then the box is there.

blind    the controller follows that line and stops at the box.
local    the same line stays published. A short-range steer goes around
         the box, because a bypass still fits inside the local reach.
replan   the box is wider than that reach. The local steer reports no
         passage, one global search draws a new line, and the controller
         follows the new line.
"""

from __future__ import annotations

import heapq
import math

DT = 0.05
SPEED = 0.40
LOOKAHEAD = 0.55
GOAL_TOLERANCE = 0.20
RADIUS = 0.22
MARGIN = 0.28
LOCAL_REACH = 1.05
APPEAR_Y = 2.20

START = (3.0, 1.0, math.pi / 2.0)
GOAL = (3.0, 7.0)
X_MIN, X_MAX = 0.40, 5.60
Y_MIN, Y_MAX = 0.40, 7.60

# xmin, xmax, ymin, ymax
SMALL = (2.55, 3.45, 3.55, 4.45)
WIDE = (1.55, 5.55, 3.55, 4.45)

RES = 0.10


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def box_for(mode: str) -> tuple[float, float, float, float]:
    return WIDE if mode == "replan" else SMALL


def clearance(x: float, y: float, box: tuple[float, float, float, float]) -> float:
    """Distance from the robot center to the box, minus the body radius."""
    cx = min(max(x, box[0]), box[1])
    cy = min(max(y, box[2]), box[3])
    return math.hypot(x - cx, y - cy) - RADIUS


def in_room(x: float, y: float) -> bool:
    return X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX


def straight_path() -> list[tuple[float, float]]:
    path = []
    y = START[1]
    while y < GOAL[1] - 1e-9:
        path.append((START[0], y))
        y += RES
    path.append((GOAL[0], GOAL[1]))
    return path


def path_length(path: list[tuple[float, float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))


def through_box(path: list[tuple[float, float]], box: tuple[float, float, float, float]) -> bool:
    return any(clearance(x, y, box) < 0.0 for x, y in path)


def max_dev(path: list[tuple[float, float]]) -> float:
    if not path:
        return 0.0
    return max(abs(x - START[0]) for x, _ in path)


def _lookahead(path: list[tuple[float, float]], pose: tuple[float, float, float]) -> tuple[float, float]:
    index = min(range(len(path)), key=lambda i: math.hypot(path[i][0] - pose[0], path[i][1] - pose[1]))
    travelled = 0.0
    point = path[index]
    for a, b in zip(path[index:], path[index + 1 :]):
        travelled += math.hypot(b[0] - a[0], b[1] - a[1])
        point = b
        if travelled >= LOOKAHEAD:
            break
    return point


def pursuit(pose: tuple[float, float, float], target: tuple[float, float]) -> tuple[float, float]:
    heading = math.atan2(target[1] - pose[1], target[0] - pose[0])
    error = wrap(heading - pose[2])
    linear = SPEED * max(0.0, math.cos(error))
    angular = max(-1.2, min(1.2, 1.8 * error))
    return linear, angular


def integrate(pose: tuple[float, float, float], linear: float, angular: float) -> tuple[float, float, float]:
    x, y, yaw = pose
    return (x + linear * math.cos(yaw) * DT, y + linear * math.sin(yaw) * DT, wrap(yaw + angular * DT))


def bypasses(box: tuple[float, float, float, float]) -> list[float]:
    """Side targets the local policy may use. Empty when both sit outside its reach."""
    found = []
    for x in (box[0] - RADIUS - MARGIN, box[1] + RADIUS + MARGIN):
        if X_MIN <= x <= X_MAX and abs(x - START[0]) <= LOCAL_REACH:
            found.append(x)
    return found


def path_ahead_hits(
    pose: tuple[float, float, float],
    path: list[tuple[float, float]],
    box: tuple[float, float, float, float],
) -> bool:
    """True when the next 1.5 m of the global path meets the box."""
    index = min(range(len(path)), key=lambda i: math.hypot(path[i][0] - pose[0], path[i][1] - pose[1]))
    travelled = 0.0
    point = path[index]
    if clearance(point[0], point[1], box) < 0.05:
        return True
    for a, b in zip(path[index:], path[index + 1 :]):
        travelled += math.hypot(b[0] - a[0], b[1] - a[1])
        if clearance(b[0], b[1], box) < 0.05:
            return True
        if travelled >= 1.5:
            break
    return False


def local_target(
    pose: tuple[float, float, float],
    path: list[tuple[float, float]],
    box: tuple[float, float, float, float],
    active: bool,
) -> tuple[tuple[float, float] | None, bool]:
    """Steer target, and whether the box blocks every sidestep inside the local reach.

    A unicycle cannot strafe, so a dodge first turns toward a point beside the
    robot, then drives forward along that offset. The offset has to sit inside
    LOCAL_REACH. A wider box leaves no such point.
    """
    if not active or pose[1] > box[3] + 0.40:
        return _lookahead(path, pose), False
    if not path_ahead_hits(pose, path, box):
        return _lookahead(path, pose), False
    sides = bypasses(box)
    if not sides:
        return None, True
    x = min(sides, key=lambda value: abs(value - pose[0]))
    if abs(pose[0] - x) > 0.12:
        return (x, pose[1]), False
    return (x, box[3] + 0.60), False


def plan_around(
    box: tuple[float, float, float, float],
    origin: tuple[float, float, float],
) -> list[tuple[float, float]]:
    """A* on free cells. The box and the walls are closed. Heuristic is straight-line."""
    nx = int(round(6.0 / RES))
    ny = int(round(8.0 / RES))

    def cell(x: float, y: float) -> tuple[int, int]:
        return int(x / RES), int(y / RES)

    def center(ix: int, iy: int) -> tuple[float, float]:
        return (ix + 0.5) * RES, (iy + 0.5) * RES

    def blocked(ix: int, iy: int) -> bool:
        if ix <= 1 or iy <= 1 or ix >= nx - 2 or iy >= ny - 2:
            return True
        x, y = center(ix, iy)
        return clearance(x, y, box) < 0.05

    start = cell(origin[0], origin[1])
    goal = cell(GOAL[0], GOAL[1])
    open_heap: list[tuple[float, int, tuple[int, int]]] = [(0.0, 0, start)]
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
            return [center(ix, iy) for ix, iy in chain]
        cx, cy = current
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nxt = (cx + dx, cy + dy)
                if not (0 <= nxt[0] < nx and 0 <= nxt[1] < ny) or blocked(*nxt) or nxt in closed:
                    continue
                if dx != 0 and dy != 0 and (blocked(cx + dx, cy) or blocked(cx, cy + dy)):
                    continue
                tentative = g_score[current] + math.hypot(dx, dy) * RES
                if tentative < g_score.get(nxt, 1e18):
                    came[nxt] = current
                    g_score[nxt] = tentative
                    order += 1
                    hx, hy = center(*nxt)
                    heapq.heappush(
                        open_heap,
                        (tentative + math.hypot(GOAL[0] - hx, GOAL[1] - hy), order, nxt),
                    )
    return []


def run(mode: str) -> dict:
    box = box_for(mode)
    path = straight_path()
    pose = START
    trail = [(pose[0], pose[1])]
    replans = 0
    hit = 0
    stuck = 0
    commands = 0
    first_cmd = (0.0, 0.0)
    min_clear = 99.0
    reached = 0

    for _ in range(1200):
        if math.hypot(pose[0] - GOAL[0], pose[1] - GOAL[1]) < GOAL_TOLERANCE:
            reached = 1
            break
        active = pose[1] >= APPEAR_Y
        if mode == "blind":
            target = _lookahead(path, pose)
            blocked_local = False
        else:
            target, blocked_local = local_target(pose, path, box, active)
        if target is None:
            stuck += 1
            if mode == "replan" and replans == 0 and stuck >= 10:
                path = plan_around(box, pose)
                replans = 1
                stuck = 0
                if not path:
                    break
            continue
        linear, angular = pursuit(pose, target)
        if commands == 0:
            first_cmd = (linear, angular)
        commands += 1
        nxt = integrate(pose, linear, angular)
        if active and clearance(nxt[0], nxt[1], box) < 0.0:
            hit = 1
            break
        if not in_room(nxt[0], nxt[1]):
            break
        pose = nxt
        trail.append((pose[0], pose[1]))
        if active:
            min_clear = min(min_clear, clearance(pose[0], pose[1], box))
        else:
            stuck = 0

    if min_clear > 90.0:
        min_clear = 0.0
    straight = math.hypot(GOAL[0] - START[0], GOAL[1] - START[1])
    return {
        "mode": mode,
        "path": path,
        "trail": trail,
        "box": box,
        "reached": reached,
        "hit": hit,
        "replans": replans,
        "plan_poses": len(path),
        "plan_length_m": path_length(path),
        "straight_m": straight,
        "plan_through_box": int(through_box(path, box)),
        "plan_dev_m": max_dev(path),
        "driven_dev_m": max_dev(trail),
        "min_clearance_m": min_clear,
        "final_error_m": math.hypot(pose[0] - GOAL[0], pose[1] - GOAL[1]),
        "commands": commands,
        "first_cmd": first_cmd,
        "pose": pose,
    }


def ascii_scene(result: dict) -> str:
    box = result["box"]
    path_cells = {(round(x / 0.2), round(y / 0.2)) for x, y in result["path"]}
    trail_cells = {(round(x / 0.2), round(y / 0.2)) for x, y in result["trail"]}
    lines = []
    for iy in range(40, -1, -1):
        row = []
        y = iy * 0.2
        for ix in range(30):
            x = ix * 0.2
            if abs(x - START[0]) < 0.15 and abs(y - START[1]) < 0.15:
                row.append("S")
            elif abs(x - GOAL[0]) < 0.15 and abs(y - GOAL[1]) < 0.15:
                row.append("G")
            elif box[0] <= x <= box[1] and box[2] <= y <= box[3]:
                row.append("#")
            elif (ix, iy) in trail_cells:
                row.append("r")
            elif (ix, iy) in path_cells:
                row.append(".")
            else:
                row.append(" ")
        lines.append("".join(row))
    return "\n".join(lines)


def summary_line(result: dict) -> str:
    return (
        f"SUMMARY mode={result['mode']} "
        f"reached={result['reached']} "
        f"hit={result['hit']} "
        f"replans={result['replans']} "
        f"plan_poses={result['plan_poses']} "
        f"plan_length_m={result['plan_length_m']:.2f} "
        f"straight_m={result['straight_m']:.2f} "
        f"plan_through_box={result['plan_through_box']} "
        f"plan_dev_m={result['plan_dev_m']:.2f} "
        f"driven_dev_m={result['driven_dev_m']:.2f} "
        f"min_clearance_m={result['min_clearance_m']:.3f} "
        f"final_error_m={result['final_error_m']:.3f} "
        f"commands={result['commands']}"
    )


if __name__ == "__main__":
    for name in ("blind", "local", "replan"):
        result = run(name)
        print(summary_line(result), flush=True)
        print("MAP", flush=True)
        print(ascii_scene(result), flush=True)
        print("MAP_END", flush=True)
