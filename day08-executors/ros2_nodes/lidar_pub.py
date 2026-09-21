#!/usr/bin/env python3
"""
Day 08 — LiDAR stand-in publisher.

Publishes std_msgs/Int32 scan ids on /day08/lidar after a short warmup.
Each message is meant to trigger a long subscription callback on the robot node.

Usage:
  python3 lidar_pub.py --ros-args \\
    -p period_sec:=1.5 -p warmup_sec:=1.0 -p count:=4
"""

from __future__ import annotations

import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Int32


class LidarPub(Node):
    def __init__(self) -> None:
        super().__init__("lidar_pub")

        self.declare_parameter("topic", "/day08/lidar")
        self.declare_parameter("period_sec", 1.5)
        self.declare_parameter("warmup_sec", 1.0)
        self.declare_parameter("count", 4)
        self.declare_parameter("depth", 10)

        topic = str(self.get_parameter("topic").value)
        self._period = float(self.get_parameter("period_sec").value)
        self._warmup = float(self.get_parameter("warmup_sec").value)
        self._count = int(self.get_parameter("count").value)
        depth = int(self.get_parameter("depth").value)

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=depth,
            reliability=ReliabilityPolicy.RELIABLE,
        )
        self._pub = self.create_publisher(Int32, topic, qos)
        self._sent = 0
        self._start = time.monotonic()
        self._next = self._start + self._warmup
        self.create_timer(0.05, self._on_tick)

        self.get_logger().info(
            f"PUB {topic} | warmup={self._warmup:.1f}s period={self._period:.1f}s "
            f"count={self._count}"
        )

    def _on_tick(self) -> None:
        if self._sent >= self._count:
            # Done publishing — leave spin so the process can exit cleanly.
            raise SystemExit(0)
        now = time.monotonic()
        if now < self._next:
            return
        msg = Int32()
        msg.data = self._sent + 1
        self._pub.publish(msg)
        self._sent += 1
        self.get_logger().info(f"PUB lidar_scan={msg.data} sent={self._sent}/{self._count}")
        self._next = now + self._period
        if self._sent >= self._count:
            self.get_logger().info("PUB complete - exiting")
            raise SystemExit(0)


def main() -> None:
    rclpy.init()
    node = LidarPub()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException, SystemExit):
        pass
    finally:
        try:
            node.destroy_node()
        except Exception:
            pass
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
