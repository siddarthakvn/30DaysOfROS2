#!/usr/bin/env python3
"""
Day 03 — Camera / sensor firehose stand-in.

Publishes monotonically increasing frame ids on /perception/frames.
Does not wait for subscribers. Rate is commanded by publish_hz.

Usage:
  python3 frame_camera_pub.py --ros-args \\
    -p publish_hz:=30.0 -p depth:=10 -p reliability:=reliable
"""

from __future__ import annotations

import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Int32

from qos_utils import build_qos


class FrameCameraPub(Node):
    def __init__(self) -> None:
        super().__init__("frame_camera")

        self.declare_parameter("publish_hz", 30.0)
        self.declare_parameter("depth", 10)
        self.declare_parameter("reliability", "reliable")
        self.declare_parameter("topic", "/perception/frames")

        publish_hz = float(self.get_parameter("publish_hz").value)
        depth = int(self.get_parameter("depth").value)
        reliability = str(self.get_parameter("reliability").value)
        topic = str(self.get_parameter("topic").value)

        if publish_hz <= 0.0:
            raise ValueError(f"publish_hz must be > 0, got {publish_hz}")

        qos = build_qos(depth, reliability)
        self._pub = self.create_publisher(Int32, topic, qos)
        self._frame_id = 0
        self._period_s = 1.0 / publish_hz
        self._window_start = time.monotonic()
        self._window_count = 0

        self.create_timer(self._period_s, self._on_timer)

        self.get_logger().info(
            f"Publishing on {topic} at {publish_hz:.1f} Hz | "
            f"KEEP_LAST depth={depth} reliability={reliability}"
        )

    def _on_timer(self) -> None:
        self._frame_id += 1
        msg = Int32()
        msg.data = self._frame_id
        self._pub.publish(msg)

        self._window_count += 1
        now = time.monotonic()
        elapsed = now - self._window_start
        if elapsed >= 1.0:
            rate = self._window_count / elapsed
            self.get_logger().info(
                f"PUB frame={self._frame_id}  measured_hz={rate:.1f}"
            )
            self._window_start = now
            self._window_count = 0


def main() -> None:
    rclpy.init()
    node = FrameCameraPub()
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
