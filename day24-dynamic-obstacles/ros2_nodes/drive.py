#!/usr/bin/env python3
"""Publish the global path and the first speed command after a box appears.

blind    follow the old line. Stop at the box.
local    keep the old line. Steer around the box inside the local reach.
replan   the box is wider than that reach. Draw one new global path.
"""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from avoid import ascii_scene, run, summary_line


class Avoidance(Node):
    def __init__(self) -> None:
        super().__init__("avoidance")
        self.declare_parameter("mode", "replan")
        mode = str(self.get_parameter("mode").value)
        latched = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        live = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self._path_pub = self.create_publisher(Path, "/plan", latched)
        self._cmd_pub = self.create_publisher(Twist, "/cmd_vel", live)
        result = run(mode)
        self._publish(result)
        print(summary_line(result), flush=True)
        print("MAP", flush=True)
        print(ascii_scene(result), flush=True)
        print("MAP_END", flush=True)
        print(f"READY mode={mode}", flush=True)

    def _publish(self, result: dict) -> None:
        stamp = self.get_clock().now().to_msg()
        path = Path()
        path.header.stamp = stamp
        path.header.frame_id = "map"
        for x, y in result["path"]:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self._path_pub.publish(path)
        twist = Twist()
        twist.linear.x = float(result["first_cmd"][0])
        twist.angular.z = float(result["first_cmd"][1])
        self._cmd_pub.publish(twist)


def main() -> None:
    rclpy.init()
    node = Avoidance()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
