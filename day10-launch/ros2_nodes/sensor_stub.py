#!/usr/bin/env python3
"""Day 10 — tiny sensor stub. Publishes a heartbeat Int32 on a relative topic."""

from __future__ import annotations

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Int32


class SensorStub(Node):
    def __init__(self) -> None:
        super().__init__("sensor_stub")
        self.declare_parameter("topic", "sensor")
        self.declare_parameter("rate_hz", 5.0)
        self.declare_parameter("label", "sensor")

        topic = str(self.get_parameter("topic").value)
        rate = float(self.get_parameter("rate_hz").value)
        self._label = str(self.get_parameter("label").value)
        self._n = 0
        self._pub = self.create_publisher(Int32, topic, 10)
        self.create_timer(1.0 / max(rate, 0.1), self._tick)
        self.get_logger().info(f"{self._label} publishing on relative topic '{topic}' @ {rate} Hz")

    def _tick(self) -> None:
        self._n += 1
        msg = Int32()
        msg.data = self._n
        self._pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = SensorStub()
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
