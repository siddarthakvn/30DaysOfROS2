#!/usr/bin/env python3
"""
Day 04 Investigation B — Long-running Service (intentional anti-pattern).

Exposes std_srvs/Trigger on ~/long_rotate. When called, blocks in the
service callback while publishing /turtle1/cmd_vel for duration_sec, then
returns a single response. No feedback. No cancel API.

Official Humble guidance: never use services for longer-running / preemptable
work — prefer an Action. This node exists to make that failure mode visible.

Usage:
  python3 long_rotate_server.py --ros-args -p duration_sec:=5.0
"""

from __future__ import annotations

import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import Trigger


class LongRotateServer(Node):
    def __init__(self) -> None:
        super().__init__("long_rotate_server")

        self.declare_parameter("cmd_vel_topic", "/turtle1/cmd_vel")
        self.declare_parameter("duration_sec", 5.0)
        self.declare_parameter("angular_z", 1.0)
        self.declare_parameter("publish_hz", 20.0)
        self.declare_parameter("send_zero_when_done", True)

        self._topic = str(self.get_parameter("cmd_vel_topic").value)
        self._duration = float(self.get_parameter("duration_sec").value)
        self._angular_z = float(self.get_parameter("angular_z").value)
        self._hz = float(self.get_parameter("publish_hz").value)
        self._send_zero = bool(self.get_parameter("send_zero_when_done").value)

        if self._duration <= 0.0:
            raise ValueError(f"duration_sec must be > 0, got {self._duration}")
        if self._hz <= 0.0:
            raise ValueError(f"publish_hz must be > 0, got {self._hz}")

        self._pub = self.create_publisher(Twist, self._topic, 10)
        self._busy = False
        self._srv = self.create_service(Trigger, "long_rotate", self._on_long_rotate)

        self.get_logger().info(
            f"Service ready: ~/long_rotate (std_srvs/Trigger) | "
            f"duration_sec={self._duration:.1f} angular_z={self._angular_z:.2f} "
            f"on {self._topic} — ANTI-PATTERN for long preemptable work"
        )

    def _on_long_rotate(
        self, _request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        if self._busy:
            response.success = False
            response.message = "rejected: already rotating (no queue / no cancel)"
            self.get_logger().warn(response.message)
            return response

        self._busy = True
        period = 1.0 / self._hz
        n = 0
        t0 = time.monotonic()
        self.get_logger().info(
            f"SERVICE START duration={self._duration:.1f}s "
            f"(blocking callback — no feedback, no cancel)"
        )

        try:
            while (time.monotonic() - t0) < self._duration:
                msg = Twist()
                msg.angular.z = self._angular_z
                self._pub.publish(msg)
                n += 1
                elapsed = time.monotonic() - t0
                if n == 1 or n % int(max(1, self._hz)) == 0:
                    self.get_logger().info(
                        f"SPIN n={n} elapsed={elapsed:.2f}s "
                        f"(client still waiting for ONE response)"
                    )
                time.sleep(period)

            if self._send_zero:
                self._pub.publish(Twist())

            elapsed = time.monotonic() - t0
            response.success = True
            response.message = (
                f"finished after {elapsed:.2f}s published={n} (single response only)"
            )
            self.get_logger().info(f"SERVICE DONE {response.message}")
            return response
        finally:
            self._busy = False


def main() -> None:
    rclpy.init()
    node = LongRotateServer()
    try:
        rclpy.spin(node)
    except ExternalShutdownException:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
