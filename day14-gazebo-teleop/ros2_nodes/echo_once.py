#!/usr/bin/env python3
"""Print one Twist and exit. Used so smoke does not hang on ros2 topic echo."""
from __future__ import annotations

import sys

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


def main() -> None:
    topic = sys.argv[1] if len(sys.argv) > 1 else "/model/vehicle_blue/cmd_vel"
    rclpy.init()
    node = Node("echo_once")
    got = {"msg": None}

    def cb(msg: Twist) -> None:
        got["msg"] = msg

    node.create_subscription(Twist, topic, cb, 10)
    end = node.get_clock().now().nanoseconds + int(3e9)
    while rclpy.ok() and got["msg"] is None and node.get_clock().now().nanoseconds < end:
        rclpy.spin_once(node, timeout_sec=0.2)
    msg = got["msg"]
    if msg is None:
        print("ECHO timeout")
    else:
        print(
            f"ECHO linear.x={msg.linear.x:.3f} linear.y={msg.linear.y:.3f} "
            f"angular.z={msg.angular.z:.3f}"
        )
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
