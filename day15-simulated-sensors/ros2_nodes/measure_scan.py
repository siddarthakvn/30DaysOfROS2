#!/usr/bin/env python3
"""Collect a few LaserScan messages and report repeatability and rate."""

from __future__ import annotations

import math
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan


def finite(values):
    return [v for v in values if math.isfinite(v)]


class Measure(Node):
    def __init__(self) -> None:
        super().__init__("measure_scan")
        self.declare_parameter("listen_sec", 3.0)
        self.declare_parameter("topic", "/lidar")
        self._listen_sec = float(self.get_parameter("listen_sec").value)
        topic = str(self.get_parameter("topic").value)
        # Gazebo's lidar bridge is often best-effort. Match it.
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self._scans: list[list[float]] = []
        self._t0 = time.monotonic()
        self.create_subscription(LaserScan, topic, self._on_scan, qos)
        self.create_timer(0.2, self._tick)
        self._done = False

    def _on_scan(self, msg: LaserScan) -> None:
        self._scans.append(list(msg.ranges))

    def _tick(self) -> None:
        if time.monotonic() - self._t0 < self._listen_sec:
            return
        if self._done:
            return
        self._done = True
        self._report()
        raise SystemExit(0)

    def _report(self) -> None:
        n = len(self._scans)
        elapsed = max(time.monotonic() - self._t0, 1e-6)
        hz = n / elapsed
        max_diff = 0.0
        center_vals = []
        for a, b in zip(self._scans, self._scans[1:]):
            width = min(len(a), len(b))
            for i in range(width):
                if math.isfinite(a[i]) and math.isfinite(b[i]):
                    max_diff = max(max_diff, abs(a[i] - b[i]))
        if self._scans:
            mid = len(self._scans[0]) // 2
            center_vals = finite(scan[mid] for scan in self._scans if mid < len(scan))
        center = sum(center_vals) / len(center_vals) if center_vals else float("nan")
        print(
            f"SUMMARY scans={n} hz={hz:.2f} "
            f"max_abs_diff_m={max_diff:.6f} center_mean_m={center:.4f}"
        )


def main() -> None:
    rclpy.init()
    node = Measure()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException, SystemExit):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
