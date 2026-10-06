#!/usr/bin/env python3
"""Publish one nav_msgs/Odometry pose from wheel rates, and print the result."""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSProfile

from kinematics import integrate


def yaw_to_quat(yaw: float) -> Quaternion:
    q = Quaternion()
    q.z = math.sin(yaw * 0.5)
    q.w = math.cos(yaw * 0.5)
    return q


class WheelOdom(Node):
    def __init__(self) -> None:
        super().__init__("wheel_odom")
        self.declare_parameter("omega_left", 5.0)
        self.declare_parameter("omega_right", 5.0)
        self.declare_parameter("radius", 0.1)
        self.declare_parameter("track_width", 0.4)
        self.declare_parameter("seconds", 2.0)
        self.declare_parameter("x0", 0.0)
        self.declare_parameter("y0", 0.0)
        self.declare_parameter("yaw0", 0.0)

        pose = integrate(
            omega_left=float(self.get_parameter("omega_left").value),
            omega_right=float(self.get_parameter("omega_right").value),
            radius=float(self.get_parameter("radius").value),
            track_width=float(self.get_parameter("track_width").value),
            seconds=float(self.get_parameter("seconds").value),
            x=float(self.get_parameter("x0").value),
            y=float(self.get_parameter("y0").value),
            yaw=float(self.get_parameter("yaw0").value),
        )
        self._pose = pose
        qos = QoSProfile(depth=1)
        self._pub = self.create_publisher(Odometry, "/odom", qos)
        self._msg = Odometry()
        self._msg.header.frame_id = "odom"
        self._msg.child_frame_id = "base_link"
        self._msg.pose.pose.position.x = pose["x"]
        self._msg.pose.pose.position.y = pose["y"]
        self._msg.pose.pose.orientation = yaw_to_quat(pose["yaw"])
        self._msg.twist.twist.linear.x = pose["v"]
        self._msg.twist.twist.linear.y = pose["body_vy"]
        self._msg.twist.twist.angular.z = pose["w"]
        self.create_timer(0.2, self._on_timer)
        self._ticks = 0

    def _on_timer(self) -> None:
        self._msg.header.stamp = self.get_clock().now().to_msg()
        self._pub.publish(self._msg)
        self._ticks += 1
        if self._ticks == 1:
            yaw_deg = math.degrees(self._pose["yaw"])
            print(
                "SUMMARY "
                f"x={self._pose['x']:.4f} "
                f"y={self._pose['y']:.4f} "
                f"yaw_deg={yaw_deg:.2f} "
                f"body_vx={self._pose['v']:.4f} "
                f"body_vy={self._pose['body_vy']:.4f} "
                f"frame={self._msg.header.frame_id} "
                f"child={self._msg.child_frame_id}"
            )
        if self._ticks >= 3:
            raise SystemExit(0)


def main() -> None:
    rclpy.init()
    node = WheelOdom()
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
