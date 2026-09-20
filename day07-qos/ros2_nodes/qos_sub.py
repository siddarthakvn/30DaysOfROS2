#!/usr/bin/env python3
"""
Day 07 — QoS subscriber.

Counts received samples. Under QoS mismatch this stays at zero while the
publisher keeps printing PUB lines.

Usage:
  python3 qos_sub.py --ros-args \\
    -p reliability:=reliable -p durability:=volatile -p depth:=10
"""

from __future__ import annotations

import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Int32

from qos_utils import build_qos


class QosSub(Node):
    def __init__(self) -> None:
        super().__init__("qos_sub")

        self.declare_parameter("depth", 10)
        self.declare_parameter("reliability", "reliable")
        self.declare_parameter("durability", "volatile")
        self.declare_parameter("topic", "/qos_demo/stream")
        self.declare_parameter("report_hz", 1.0)

        depth = int(self.get_parameter("depth").value)
        reliability = str(self.get_parameter("reliability").value)
        durability = str(self.get_parameter("durability").value)
        topic = str(self.get_parameter("topic").value)
        report_hz = float(self.get_parameter("report_hz").value)

        qos = build_qos(depth, reliability, durability)
        self._recv = 0
        self._last_seq = None
        self._window_start = time.monotonic()
        self._window_count = 0

        self.create_subscription(Int32, topic, self._on_msg, qos)
        self.create_timer(1.0 / report_hz, self._on_report)

        self.get_logger().info(
            f"SUB on {topic} | KEEP_LAST depth={depth} "
            f"reliability={reliability} durability={durability}"
        )

    def _on_msg(self, msg: Int32) -> None:
        self._recv += 1
        self._last_seq = int(msg.data)
        self._window_count += 1

    def _on_report(self) -> None:
        now = time.monotonic()
        elapsed = max(now - self._window_start, 1e-6)
        rate = self._window_count / elapsed
        last = "none" if self._last_seq is None else str(self._last_seq)
        self.get_logger().info(
            f"SUB recv_total={self._recv} last_seq={last} "
            f"measured_hz={rate:.1f}"
        )
        self._window_start = now
        self._window_count = 0


def main() -> None:
    rclpy.init()
    node = QosSub()
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
