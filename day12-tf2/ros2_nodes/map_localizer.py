#!/usr/bin/env python3
"""
Day 12 — Fake localization: publishes map → odom.

Starts as identity (aligned), then applies a discrete JUMP — the REP-105
map contract. Corrects global pose without touching odom → base_link.
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


class MapLocalizer(Node):
    def __init__(self) -> None:
        super().__init__("map_localizer")
        self.declare_parameter("jump_at_sec", 5.0)
        self.declare_parameter("jump_x", 1.50)  # meters in map
        self.declare_parameter("jump_y", 0.80)
        self.declare_parameter("jump_yaw", 0.35)  # rad
        self.declare_parameter("hz", 20.0)
        self.declare_parameter("run_sec", 12.0)
        self.declare_parameter("parent", "map")
        self.declare_parameter("child", "odom")

        self.jump_at = float(self.get_parameter("jump_at_sec").value)
        self.jump_x = float(self.get_parameter("jump_x").value)
        self.jump_y = float(self.get_parameter("jump_y").value)
        self.jump_yaw = float(self.get_parameter("jump_yaw").value)
        self.hz = float(self.get_parameter("hz").value)
        self.run_sec = float(self.get_parameter("run_sec").value)
        self.parent = str(self.get_parameter("parent").value)
        self.child = str(self.get_parameter("child").value)

        self.br = TransformBroadcaster(self)
        self.jumped = False
        self.ox = 0.0
        self.oy = 0.0
        self.oyaw = 0.0
        self.t0 = self.get_clock().now()
        self.timer = self.create_timer(1.0 / max(self.hz, 1.0), self.tick)
        self.get_logger().info(
            f"map_localizer {self.parent}->{self.child} "
            f"jump_at={self.jump_at}s Δ=({self.jump_x},{self.jump_y},{self.jump_yaw})"
        )

    def tick(self) -> None:
        now = self.get_clock().now()
        elapsed = (now - self.t0).nanoseconds * 1e-9
        if elapsed > self.run_sec:
            self.get_logger().info("map_localizer complete - exiting")
            raise SystemExit(0)

        if (not self.jumped) and elapsed >= self.jump_at:
            self.ox = self.jump_x
            self.oy = self.jump_y
            self.oyaw = self.jump_yaw
            self.jumped = True
            self.get_logger().warn(
                f"MAP JUMP applied map->odom  "
                f"x={self.ox:+.3f} y={self.oy:+.3f} yaw={self.oyaw:+.3f}"
            )

        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = self.parent
        t.child_frame_id = self.child
        t.transform.translation.x = self.ox
        t.transform.translation.y = self.oy
        t.transform.translation.z = 0.0
        qx, qy, qz, qw = yaw_to_quat(self.oyaw)
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.br.sendTransform(t)


def main() -> None:
    rclpy.init()
    node = MapLocalizer()
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
