#!/usr/bin/env python3
"""
Day 12 — Fake odometry: publishes continuous odom → base_link.

Simulates a robot driving forward with a tiny yaw bias (drift seed).
Never jumps. That is the REP-105 odom contract.
"""
from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


def yaw_to_quat(yaw: float) -> tuple[float, float, float, float]:
    half = 0.5 * yaw
    return (0.0, 0.0, math.sin(half), math.cos(half))


class OdomDriver(Node):
    def __init__(self) -> None:
        super().__init__("odom_driver")
        self.declare_parameter("vx", 0.25)  # m/s forward in odom
        self.declare_parameter("yaw_rate_bias", 0.02)  # rad/s — quiet drift
        self.declare_parameter("hz", 30.0)
        self.declare_parameter("run_sec", 12.0)
        self.declare_parameter("parent", "odom")
        self.declare_parameter("child", "base_link")

        self.vx = float(self.get_parameter("vx").value)
        self.yaw_bias = float(self.get_parameter("yaw_rate_bias").value)
        self.hz = float(self.get_parameter("hz").value)
        self.run_sec = float(self.get_parameter("run_sec").value)
        self.parent = str(self.get_parameter("parent").value)
        self.child = str(self.get_parameter("child").value)

        self.br = TransformBroadcaster(self)
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.t0 = self.get_clock().now()
        self.timer = self.create_timer(1.0 / max(self.hz, 1.0), self.tick)
        self.get_logger().info(
            f"odom_driver {self.parent}->{self.child} vx={self.vx} "
            f"yaw_bias={self.yaw_bias} run_sec={self.run_sec}"
        )

    def tick(self) -> None:
        now = self.get_clock().now()
        elapsed = (now - self.t0).nanoseconds * 1e-9
        if elapsed > self.run_sec:
            self.get_logger().info("odom_driver complete - exiting")
            raise SystemExit(0)

        dt = 1.0 / max(self.hz, 1.0)
        self.yaw += self.yaw_bias * dt
        self.x += self.vx * math.cos(self.yaw) * dt
        self.y += self.vx * math.sin(self.yaw) * dt

        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = self.parent
        t.child_frame_id = self.child
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        qx, qy, qz, qw = yaw_to_quat(self.yaw)
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.br.sendTransform(t)

        if int(elapsed * 2) != int((elapsed - dt) * 2):
            self.get_logger().info(
                f"ODOM pose x={self.x:+.3f} y={self.y:+.3f} yaw={self.yaw:+.3f}"
            )


def main() -> None:
    rclpy.init()
    node = OdomDriver()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
