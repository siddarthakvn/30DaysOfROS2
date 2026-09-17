#!/usr/bin/env python3
"""
Day 04 Investigation A — Topic-driven motion.

Publishes geometry_msgs/Twist on /turtle1/cmd_vel for a burst, then exits.
By default does NOT publish a zero Twist on exit — so "stop publishing"
is not the same as an Action cancel with cleanup.

Usage:
  # Full 5 s burst
  python3 cmd_vel_burst.py --ros-args -p duration_sec:=5.0

  # Interrupt style: publish ~2 s then exit (no zero cmd)
  python3 cmd_vel_burst.py --ros-args \\
    -p duration_sec:=5.0 -p stop_after_sec:=2.0 -p send_zero_on_exit:=false
"""

from __future__ import annotations

import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class CmdVelBurst(Node):
    def __init__(self) -> None:
        super().__init__("cmd_vel_burst")

        self.declare_parameter("topic", "/turtle1/cmd_vel")
        self.declare_parameter("publish_hz", 20.0)
        self.declare_parameter("angular_z", 1.0)
        self.declare_parameter("linear_x", 0.0)
        self.declare_parameter("duration_sec", 5.0)
        self.declare_parameter("stop_after_sec", -1.0)  # <0 => use duration_sec
        self.declare_parameter("send_zero_on_exit", False)

        self._topic = str(self.get_parameter("topic").value)
        self._hz = float(self.get_parameter("publish_hz").value)
        self._angular_z = float(self.get_parameter("angular_z").value)
        self._linear_x = float(self.get_parameter("linear_x").value)
        self._duration = float(self.get_parameter("duration_sec").value)
        stop_after = float(self.get_parameter("stop_after_sec").value)
        self._send_zero = bool(self.get_parameter("send_zero_on_exit").value)

        if self._hz <= 0.0:
            raise ValueError(f"publish_hz must be > 0, got {self._hz}")
        if self._duration <= 0.0:
            raise ValueError(f"duration_sec must be > 0, got {self._duration}")

        self._active_for = self._duration if stop_after < 0.0 else stop_after
        if self._active_for <= 0.0:
            raise ValueError(f"stop_after_sec must be > 0 when set, got {stop_after}")

        self._pub = self.create_publisher(Twist, self._topic, 10)
        self._period = 1.0 / self._hz
        self._t0 = time.monotonic()
        self._count = 0
        self._done = False

        self.create_timer(self._period, self._on_timer)
        self.get_logger().info(
            f"Topic burst on {self._topic} | hz={self._hz:.1f} "
            f"angular_z={self._angular_z:.2f} active_for={self._active_for:.2f}s "
            f"(planned_duration={self._duration:.2f}s) "
            f"send_zero_on_exit={self._send_zero}"
        )

    def _on_timer(self) -> None:
        if self._done:
            return

        elapsed = time.monotonic() - self._t0
        if elapsed >= self._active_for:
            self._done = True
            if self._send_zero:
                self._pub.publish(Twist())
                self.get_logger().info("Published zero Twist on exit")
            else:
                self.get_logger().warn(
                    "Exiting WITHOUT zero Twist — stop publishing ≠ Action cancel"
                )
            self.get_logger().info(
                f"DONE published={self._count} elapsed={elapsed:.2f}s"
            )
            raise SystemExit(0)

        msg = Twist()
        msg.linear.x = self._linear_x
        msg.angular.z = self._angular_z
        self._pub.publish(msg)
        self._count += 1
        if self._count == 1 or self._count % int(max(1, self._hz)) == 0:
            self.get_logger().info(
                f"PUB n={self._count} elapsed={elapsed:.2f}s "
                f"angular_z={self._angular_z:.2f}"
            )


def main() -> None:
    rclpy.init()
    node = CmdVelBurst()
    try:
        rclpy.spin(node)
    except (ExternalShutdownException, SystemExit):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
