#!/usr/bin/env python3
"""Publish one pose estimate and print how far it sits from the straight-line truth."""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSProfile

import ekf


def yaw_to_quat(yaw: float) -> Quaternion:
    q = Quaternion()
    q.z = math.sin(yaw * 0.5)
    q.w = math.cos(yaw * 0.5)
    return q


class FusePose(Node):
    def __init__(self) -> None:
        super().__init__("fuse_pose")
        self.declare_parameter("case", "ekf")
        case = str(self.get_parameter("case").value)
        truth_x = ekf.TRUE_V * ekf.SECONDS

        if case == "wheels":
            rates = ekf.wheel_yaw_rates()
            x, y, yaw = ekf.integrate_wheels(rates)
            extra = ""
        elif case == "gyro":
            x, y, yaw = ekf.integrate_gyro()
            extra = ""
        elif case == "ekf":
            fused = ekf.fuse(ekf.wheel_yaw_rates())
            x, y, yaw = fused["x"], fused["y"], fused["yaw"]
            extra = f" bias={fused['bias']:.4f} yaw_var={fused['yaw_var']:.4f}"
        elif case == "fight":
            snapped = ekf.fight()
            x, y, yaw = 0.0, 0.0, snapped["yaw"]
            self._line = (
                "SUMMARY "
                f"case=fight yaw_deg={math.degrees(yaw):.2f} "
                f"jumps={int(snapped['jumps'])} "
                f"span_deg={math.degrees(snapped['span']):.2f} "
                f"yaw_var={snapped['yaw_var']:.3e} "
                "frame=odom child=base_link"
            )
            self._publish(x, y, yaw)
            return
        else:
            raise ValueError(f"unknown case {case}")

        self._line = (
            "SUMMARY "
            f"case={case} "
            f"x={x:.4f} y={y:.4f} yaw_deg={math.degrees(yaw):.2f} "
            f"err_x={x - truth_x:.4f} err_y={y - 0.0:.4f} "
            f"err_yaw_deg={math.degrees(yaw):.2f}"
            f"{extra} frame=odom child=base_link"
        )
        self._publish(x, y, yaw)

    def _publish(self, x: float, y: float, yaw: float) -> None:

        qos = QoSProfile(depth=1)
        self._pub = self.create_publisher(Odometry, "/odometry/filtered", qos)
        self._msg = Odometry()
        self._msg.header.frame_id = "odom"
        self._msg.child_frame_id = "base_link"
        self._msg.pose.pose.position.x = x
        self._msg.pose.pose.position.y = y
        self._msg.pose.pose.orientation = yaw_to_quat(yaw)
        self._ticks = 0
        self.create_timer(0.2, self._on_timer)

    def _on_timer(self) -> None:
        self._msg.header.stamp = self.get_clock().now().to_msg()
        self._pub.publish(self._msg)
        self._ticks += 1
        if self._ticks == 1:
            print(self._line, flush=True)
        if self._ticks >= 3:
            raise SystemExit(0)


def main() -> None:
    rclpy.init()
    node = FusePose()
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
