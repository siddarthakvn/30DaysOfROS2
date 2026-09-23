#!/usr/bin/env python3
"""Day 10 — control stub. Publishes Twist on relative cmd_vel (remap-friendly)."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class ControlStub(Node):
    def __init__(self) -> None:
        super().__init__("control_stub")
        self.declare_parameter("speed", 0.2)
        self.declare_parameter("rate_hz", 2.0)
        speed = float(self.get_parameter("speed").value)
        rate = float(self.get_parameter("rate_hz").value)
        self._speed = speed
        self._pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.create_timer(1.0 / max(rate, 0.1), self._tick)
        self.get_logger().info(f"control publishing on relative 'cmd_vel' speed={speed}")

    def _tick(self) -> None:
        msg = Twist()
        msg.linear.x = self._speed
        self._pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = ControlStub()
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
