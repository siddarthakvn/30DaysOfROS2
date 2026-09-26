#!/usr/bin/env python3
"""
Day 12 — Fake odometry: publishes continuous odom → base_link.

Simulates a robot driving forward with a slow yaw drift (dead reckoning that
quietly wanders). Guarantees continuity: no discrete jumps.
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


class OdomBroadcaster(Node):
    def __init__(self) -> None:
        super().__init__("odom_broadcaster")
        self.declare_parameter("vx", 0.25)  # m/s forward in body
        self.declare_parameter("yaw_rate_bias", 0.03)  # rad/s drift
        self.declare_parameter("hz", 50.0)
        self.declare_parameter("run_sec", 8.0)
        self.declare_parameter("odom_frame", "odom")
        self.declare_parameter("base_frame", "base_link")

        self.vx = float(self.get_parameter("vx").value)
        self.yaw_bias = float(self.get_parameter("yaw_rate_bias").value)
        self.hz = float(self.get_parameter("hz").value)
        self.run_sec = float(self.get_parameter("run_sec").value)
        self.odom_frame = str(self.get_parameter("odom_frame").value)
        self.base_frame = str(self.get_parameter("base_frame").value)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.t = 0.0
        self.dt = 1.0 / max(self.hz, 1.0)

        self.br = TransformBroadcaster(self)
        self.timer = self.create_timer(self.dt, self.tick)
        self.get_logger().info(
            f"odom→base continuous drive vx={self.vx} yaw_bias={self.yaw_bias} "
            f"run_sec={self.run_sec}"
        )

    def tick(self) -> None:
        if self.t >= self.run_sec:
            self.get_logger().info(
                f"ODOM_DONE x={self.x:+.3f} y={self.y:+.3f} yaw={self.yaw:+.3f}"
            )
            raise SystemExit(0)

        # Body-frame forward + constant yaw bias → smooth but drifting path.
        self.yaw += self.yaw_bias * self.dt
        self.x += self.vx * math.cos(self.yaw) * self.dt
        self.y += self.vx * math.sin(self.yaw) * self.dt
        self.t += self.dt

        qx, qy, qz, qw = yaw_to_quat(self.yaw)
        msg = TransformStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.odom_frame
        msg.child_frame_id = self.base_frame
        msg.transform.translation.x = self.x
        msg.transform.translation.y = self.y
        msg.transform.translation.z = 0.0
        msg.transform.rotation.x = qx
        msg.transform.rotation.y = qy
        msg.transform.rotation.z = qz
        msg.transform.rotation.w = qw
        self.br.sendTransform(msg)

        if int(self.t * 2) != int((self.t - self.dt) * 2):
            self.get_logger().info(
                f"ODOM t={self.t:4.1f}s  base_in_odom=({self.x:+.3f},{self.y:+.3f}) "
                f"yaw={self.yaw:+.3f}"
            )


def main() -> None:
    rclpy.init()
    node = OdomBroadcaster()
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
