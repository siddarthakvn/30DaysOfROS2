#!/usr/bin/env python3
"""Build one occupancy grid three ways and publish /scan and /map.

Modes
  truth  paint each scan at the real pose
  drift  paint each scan at wheel odometry (a growing offset)
  match  slide the new scan onto the previous one, then paint

The room is a 4 m square. The robot drives from x=1.0 m to x=1.90 m
along y=1.5 m. Odometry adds 0.03 m of extra x every step.
"""

from __future__ import annotations

import math

import rclpy
from nav_msgs.msg import OccupancyGrid
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan

WALLS = (
    ((0.0, 0.0), (4.0, 0.0)),
    ((4.0, 0.0), (4.0, 4.0)),
    ((4.0, 4.0), (0.0, 4.0)),
    ((0.0, 4.0), (0.0, 0.0)),
)

STEPS = 16
STEP_X = 0.06
BIAS_X = 0.03
BEAMS = 120
MAX_RANGE = 6.0
RES = 0.05
ORIGIN = -0.5
CELLS = 100


def true_pose(i: int) -> tuple[float, float, float]:
    return (1.0 + STEP_X * i, 1.5, 0.0)


def odom_pose(i: int) -> tuple[float, float, float]:
    x, y, yaw = true_pose(i)
    return (x + BIAS_X * i, y, yaw)


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


def endpoints(pose: tuple[float, float, float], ranges: list[float]) -> list[tuple[float, float]]:
    x, y, yaw = pose
    pts = []
    for r, a in zip(ranges, angles()):
        if r >= MAX_RANGE - 1e-6:
            continue
        pts.append((x + r * math.cos(yaw + a), y + r * math.sin(yaw + a)))
    return pts


def point_seg_dist(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    vx, vy = x2 - x1, y2 - y1
    l2 = vx * vx + vy * vy
    t = 0.0 if l2 == 0.0 else max(0.0, min(1.0, ((px - x1) * vx + (py - y1) * vy) / l2))
    return math.hypot(px - (x1 + t * vx), py - (y1 + t * vy))


def mean_wall_error(pts: list[tuple[float, float]]) -> float:
    if not pts:
        return float("nan")
    total = 0.0
    for px, py in pts:
        total += min(point_seg_dist(px, py, *a, *b) for a, b in WALLS)
    return total / len(pts)


def _buckets(pts: list[tuple[float, float]]) -> dict[tuple[int, int], list[tuple[float, float]]]:
    out: dict[tuple[int, int], list[tuple[float, float]]] = {}
    for px, py in pts:
        key = (int(math.floor(px / 0.1)), int(math.floor(py / 0.1)))
        out.setdefault(key, []).append((px, py))
    return out


def _nn(buckets: dict, x: float, y: float) -> float:
    ix, iy = int(math.floor(x / 0.1)), int(math.floor(y / 0.1))
    best = 0.75
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for px, py in buckets.get((ix + dx, iy + dy), ()):
                best = min(best, math.hypot(x - px, y - py))
    return best


def match_pose(
    predicted: tuple[float, float, float],
    ranges: list[float],
    grid: "Grid",
) -> tuple[float, float, float]:
    """Slide the scan in x and y until its hits sit on cells already marked occupied."""
    occupied: list[tuple[float, float]] = []
    for idx, value in enumerate(grid.odds):
        if value <= 0.6:
            continue
        ix = idx % CELLS
        iy = idx // CELLS
        occupied.append((ORIGIN + (ix + 0.5) * RES, ORIGIN + (iy + 0.5) * RES))
    buckets = _buckets(occupied)
    px, py, yaw = predicted
    best_score = 1e9
    best = predicted
    for kx in range(-10, 11):
        x = px + kx * 0.01
        for ky in range(-4, 5):
            y = py + ky * 0.01
            score = 0.0
            count = 0
            for r, a in zip(ranges, angles()):
                if r >= MAX_RANGE - 1e-6:
                    continue
                hx = x + r * math.cos(yaw + a)
                hy = y + r * math.sin(yaw + a)
                score += _nn(buckets, hx, hy)
                count += 1
            score /= max(count, 1)
            if score < best_score:
                best_score = score
                best = (x, y, yaw)
    return best


class Grid:
    def __init__(self) -> None:
        self.odds = [0.0] * (CELLS * CELLS)

    def _idx(self, x: float, y: float) -> int | None:
        ix = int((x - ORIGIN) / RES)
        iy = int((y - ORIGIN) / RES)
        if ix < 0 or iy < 0 or ix >= CELLS or iy >= CELLS:
            return None
        return iy * CELLS + ix

    def paint(self, pose: tuple[float, float, float], ranges: list[float]) -> None:
        x, y, yaw = pose
        for r, a in zip(ranges, angles()):
            if r >= MAX_RANGE - 1e-6:
                continue
            hitx = x + r * math.cos(yaw + a)
            hity = y + r * math.sin(yaw + a)
            steps = max(int(r / RES), 1)
            for i in range(steps):
                frac = i / steps
                cell = self._idx(x + (hitx - x) * frac, y + (hity - y) * frac)
                if cell is not None:
                    self.odds[cell] = max(-4.0, self.odds[cell] - 0.35)
            cell = self._idx(hitx, hity)
            if cell is not None:
                self.odds[cell] = min(4.0, self.odds[cell] + 1.4)

    def occupancy(self) -> list[int]:
        out = []
        for value in self.odds:
            if value > 0.6:
                out.append(100)
            elif value < -0.4:
                out.append(0)
            else:
                out.append(-1)
        return out

    def ascii(self) -> str:
        step = 4
        rows = []
        for y0 in range(CELLS - step, -1, -step):
            chars = []
            for x0 in range(0, CELLS, step):
                occupied = False
                free = False
                for iy in range(y0, y0 + step):
                    for ix in range(x0, x0 + step):
                        value = self.odds[iy * CELLS + ix]
                        if value > 0.6:
                            occupied = True
                        elif value < -0.4:
                            free = True
                if occupied:
                    chars.append("#")
                elif free:
                    chars.append(".")
                else:
                    chars.append(" ")
            rows.append("".join(chars))
        return "\n".join(rows)

    def right_wall_spread(self) -> float:
        xs = []
        for idx, value in enumerate(self.odds):
            if value <= 0.6:
                continue
            ix = idx % CELLS
            x = ORIGIN + (ix + 0.5) * RES
            # The east wall sits on x = 4. Ignore the north and south walls.
            if x >= 3.90:
                xs.append(x)
        if len(xs) < 2:
            return float("nan")
        mean = sum(xs) / len(xs)
        var = sum((x - mean) ** 2 for x in xs) / len(xs)
        return math.sqrt(var)


class MapBuilder(Node):
    def __init__(self) -> None:
        super().__init__("map_builder")
        self.declare_parameter("mode", "truth")
        self._mode = str(self.get_parameter("mode").value)
        scan_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        map_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._scan_pub = self.create_publisher(LaserScan, "/scan", scan_qos)
        self._map_pub = self.create_publisher(OccupancyGrid, "/map", map_qos)
        self._grid = Grid()
        self._pose_err = 0.0
        self._wall_err = 0.0
        self._samples = 0
        self._final_err = 0.0
        self._est = true_pose(0)
        self.create_timer(0.1, self._run_once)
        self._ran = False

    def _pose_for(self, i: int, ranges: list[float]) -> tuple[float, float, float]:
        if self._mode == "truth":
            return true_pose(i)
        if self._mode == "drift":
            return odom_pose(i)
        if i == 0:
            return true_pose(0)
        ox, oy, oyaw = odom_pose(i)
        px, py, pyaw = odom_pose(i - 1)
        ex, ey, eyaw = self._est
        predicted = (ex + (ox - px), ey + (oy - py), eyaw + (oyaw - pyaw))
        return match_pose(predicted, ranges, self._grid)

    def _run_once(self) -> None:
        if self._ran:
            self._map_pub.publish(self._map_msg())
            return
        self._ran = True
        beam_angles = angles()
        for i in range(STEPS):
            truth = true_pose(i)
            ranges = scan_at(truth)
            pose = self._pose_for(i, ranges)
            self._est = pose
            self._grid.paint(pose, ranges)
            pts = endpoints(pose, ranges)
            self._pose_err += math.hypot(pose[0] - truth[0], pose[1] - truth[1])
            self._wall_err += mean_wall_error(pts)
            self._samples += 1
            self._final_err = math.hypot(pose[0] - truth[0], pose[1] - truth[1])
            self._scan_pub.publish(self._scan_msg(ranges, beam_angles))
        self._map_pub.publish(self._map_msg())
        mean_pose = self._pose_err / self._samples
        mean_wall = self._wall_err / self._samples
        occupied = sum(1 for v in self._grid.occupancy() if v == 100)
        spread = self._grid.right_wall_spread()
        print(
            f"SUMMARY mode={self._mode} scans={STEPS} "
            f"mean_pose_error_m={mean_pose:.4f} "
            f"final_pose_error_m={self._final_err:.4f} "
            f"mean_wall_error_m={mean_wall:.4f} "
            f"right_wall_spread_m={spread:.4f} "
            f"occupied_cells={occupied}",
            flush=True,
        )
        print("MAP", flush=True)
        print(self._grid.ascii(), flush=True)
        print("MAP_END", flush=True)

    def _scan_msg(self, ranges: list[float], beam_angles: list[float]) -> LaserScan:
        msg = LaserScan()
        msg.header.frame_id = "base_scan"
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.angle_min = beam_angles[0]
        msg.angle_max = beam_angles[-1]
        msg.angle_increment = beam_angles[1] - beam_angles[0]
        msg.range_min = 0.05
        msg.range_max = MAX_RANGE
        msg.ranges = ranges
        msg.scan_time = 0.1
        msg.time_increment = 0.0
        return msg

    def _map_msg(self) -> OccupancyGrid:
        msg = OccupancyGrid()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.info.resolution = RES
        msg.info.width = CELLS
        msg.info.height = CELLS
        msg.info.origin.position.x = ORIGIN
        msg.info.origin.position.y = ORIGIN
        msg.info.origin.orientation.w = 1.0
        msg.data = self._grid.occupancy()
        return msg


def main() -> None:
    rclpy.init()
    node = MapBuilder()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
