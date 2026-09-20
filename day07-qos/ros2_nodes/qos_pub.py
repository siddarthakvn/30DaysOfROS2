#!/usr/bin/env python3
"""
Day 07 — QoS publisher.

Publishes increasing Int32 samples on /qos_demo/stream.
QoS is fully selectable so we can prove match vs mismatch.

Usage:
  python3 qos_pub.py --ros-args \\
    -p reliability:=best_effort -p durability:=volatile -p depth:=10
"""

from __future__ import annotations

import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Int32

from qos_utils import build_qos


class QosPub(Node):
    def __init__(self) -> None:
        super().__init__("qos_pub")

        self.declare_parameter("publish_hz", 10.0)
        self.declare_parameter("depth", 10)
        self.declare_parameter("reliability", "reliable")
        self.declare_parameter("durability", "volatile")
        self.declare_parameter("topic", "/qos_demo/stream")

        publish_hz = float(self.get_parameter("publish_hz").value)
        depth = int(self.get_parameter("depth").value)
        reliability = str(self.get_parameter("reliability").value)
        durability = str(self.get_parameter("durability").value)
        topic = str(self.get_parameter("topic").value)

        if publish_hz <= 0.0:
            raise ValueError(f"publish_hz must be > 0, got {publish_hz}")

        qos = build_qos(depth, reliability, durability)
        self._pub = self.create_publisher(Int32, topic, qos)
        self._seq = 0
        self._period_s = 1.0 / publish_hz
        self._window_start = time.monotonic()
        self._window_count = 0

        self.create_timer(self._period_s, self._on_timer)

        self.get_logger().info(
            f"PUB on {topic} @ {publish_hz:.1f} Hz | "
            f"KEEP_LAST depth={depth} reliability={reliability} "
            f"durability={durability}"
        )

    def _on_timer(self) -> None:
        self._seq += 1
        msg = Int32()
        msg.data = self._seq
        self._pub.publish(msg)

        self._window_count += 1
        now = time.monotonic()
        elapsed = now - self._window_start
        if elapsed >= 1.0:
            rate = self._window_count / elapsed
            self.get_logger().info(
                f"PUB seq={self._seq} measured_hz={rate:.1f}"
            )
            self._window_start = now
            self._window_count = 0


def main() -> None:
    rclpy.init()
    node = QosPub()
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
