#!/usr/bin/env python3
"""
Day 12 — Fake localization: publishes map → odom.

Starts near identity, then applies a discrete JUMP (localization correction).
That jump must live on map→odom so odom→base_link can stay continuous.
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


class MapCorrector(Node):
    def __init__(self) -> None:
        super().__init__("map_corrector")
        self.declare_parameter("hz", 20.0)
        self.declare_parameter("run_sec", 8.0)
        self.declare_parameter("jump_at_sec", 3.0)
        self.declare_parameter("jump_x", 1.50)  # meters
        self.declare_parameter("jump_y", -0.80)
        self.declare_parameter("jump_yaw", 0.35)  # rad
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("odom_frame", "odom")

        self.hz = float(self.get_parameter("hz").value)
        self.run_sec = float(self.get_parameter("run_sec").value)
        self.jump_at = float(self.get_parameter("jump_at_sec").value)
        self.jump_x = float(self.get_parameter("jump_x").value)
        self.jump_y = float(self.get_parameter("jump_y").value)
        self.jump_yaw = float(self.get_parameter("jump_yaw").value)
        self.map_frame = str(self.get_parameter("map_frame").value)
        self.odom_frame = str(self.get_parameter("odom_frame").value)

        self.t = 0.0
        self.dt = 1.0 / max(self.hz, 1.0)
        self.jumped = False
        self.ox = 0.0
        self.oy = 0.0
        self.oyaw = 0.0

        self.br = TransformBroadcaster(self)
        self.timer = self.create_timer(self.dt, self.tick)
        self.get_logger().info(
            f"map→odom corrector jump_at={self.jump_at}s "
            f"delta=({self.jump_x},{self.jump_y},{self.jump_yaw})"
        )

    def tick(self) -> None:
        if self.t >= self.run_sec:
            self.get_logger().info("MAP_DONE")
            raise SystemExit(0)

        if (not self.jumped) and self.t >= self.jump_at:
            self.ox = self.jump_x
            self.oy = self.jump_y
            self.oyaw = self.jump_yaw
            self.jumped = True
            self.get_logger().warn(
                f"MAP_JUMP applied map→odom = "
                f"({self.ox:+.3f},{self.oy:+.3f}, yaw={self.oyaw:+.3f})"
            )

        qx, qy, qz, qw = yaw_to_quat(self.oyaw)
        msg = TransformStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.map_frame
        msg.child_frame_id = self.odom_frame
        msg.transform.translation.x = self.ox
        msg.transform.translation.y = self.oy
        msg.transform.translation.z = 0.0
        msg.transform.rotation.x = qx
        msg.transform.rotation.y = qy
        msg.transform.rotation.z = qz
        msg.transform.rotation.w = qw
        self.br.sendTransform(msg)

        self.t += self.dt


def main() -> None:
    rclpy.init()
    node = MapCorrector()
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
