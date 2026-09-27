#!/usr/bin/env python3
"""Publish /joint_states only. This node never broadcasts TF.

Stands in for joint_state_publisher when that package is not installed:
angles in, frames out of robot_state_publisher.
"""
from __future__ import annotations

import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class JointAngles(Node):
    def __init__(self) -> None:
        super().__init__("joint_angles")
        self.declare_parameter("shoulder", 0.0)
        self.declare_parameter("elbow", 0.0)
        self.declare_parameter("hz", 20.0)
        self.declare_parameter("run_sec", 8.0)

        self.shoulder = float(self.get_parameter("shoulder").value)
        self.elbow = float(self.get_parameter("elbow").value)
        self.hz = float(self.get_parameter("hz").value)
        self.run_sec = float(self.get_parameter("run_sec").value)

        self.pub = self.create_publisher(JointState, "joint_states", 10)
        self.t0 = time.monotonic()
        self.timer = self.create_timer(1.0 / max(self.hz, 1.0), self.tick)
        self.get_logger().info(
            f"joint_angles shoulder={self.shoulder} elbow={self.elbow} "
            "(publishes /joint_states only)"
        )

    def tick(self) -> None:
        if time.monotonic() - self.t0 > self.run_sec:
            self.get_logger().info("joint_angles complete - exiting")
            raise SystemExit(0)
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ["shoulder", "elbow"]
        msg.position = [self.shoulder, self.elbow]
        self.pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = JointAngles()
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
