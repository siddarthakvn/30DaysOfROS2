#!/usr/bin/env python3
"""Publish JointState for Day 11 Investigations B/C."""
from __future__ import annotations

import math
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class JointDemo(Node):
    def __init__(self) -> None:
        super().__init__("joint_demo")
        self.declare_parameter("mode", "pose")  # zero | pose | sweep
        self.declare_parameter("joints", "r_shoulder,r_elbow")
        self.declare_parameter("positions", "0.0,0.0")
        self.declare_parameter("hz", 30.0)
        self.declare_parameter("run_sec", 8.0)

        self.mode = str(self.get_parameter("mode").value)
        joints_raw = self.get_parameter("joints").value
        positions_raw = self.get_parameter("positions").value
        if isinstance(joints_raw, (list, tuple)):
            joints = [str(j).strip() for j in joints_raw]
        else:
            joints = [j.strip() for j in str(joints_raw).split(",") if j.strip()]
        if isinstance(positions_raw, (list, tuple)):
            positions = [float(p) for p in positions_raw]
        else:
            positions = [float(p) for p in str(positions_raw).split(",") if p.strip()]
        self.joints = list(joints)
        self.positions = [float(p) for p in positions]
        if len(self.positions) < len(self.joints):
            self.positions += [0.0] * (len(self.joints) - len(self.positions))
        self.hz = float(self.get_parameter("hz").value)
        self.run_sec = float(self.get_parameter("run_sec").value)

        self.pub = self.create_publisher(JointState, "joint_states", 10)
        self.t0 = time.monotonic()
        self.timer = self.create_timer(1.0 / max(self.hz, 1.0), self.tick)
        self.get_logger().info(
            f"joint_demo mode={self.mode} joints={self.joints} "
            f"positions={self.positions[: len(self.joints)]} run_sec={self.run_sec}"
        )

    def tick(self) -> None:
        elapsed = time.monotonic() - self.t0
        if elapsed > self.run_sec:
            self.get_logger().info("joint_demo complete - exiting")
            raise SystemExit(0)

        if self.mode == "zero":
            pos = [0.0] * len(self.joints)
        elif self.mode == "sweep":
            pos = []
            for i, _name in enumerate(self.joints):
                pos.append(0.5 * math.sin(elapsed + i))
        else:  # pose
            pos = list(self.positions[: len(self.joints)])

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self.joints)
        msg.position = [float(p) for p in pos]
        msg.velocity = []
        msg.effort = []
        self.pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = JointDemo()
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
