#!/usr/bin/env python3
"""Publish the path a global planner chooses from A to B.

line       the straight segment. It crosses a wall, so nothing is planned.
dijkstra   expand by travel cost alone.
astar      expand by travel cost plus the distance still left to B.
"""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from search import ascii_scene, search, summary_line


class GlobalPlanner(Node):
    def __init__(self) -> None:
        super().__init__("global_planner")
        self.declare_parameter("mode", "astar")
        mode = str(self.get_parameter("mode").value)
        latched = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._path_pub = self.create_publisher(Path, "/plan", latched)
        result = search(mode)
        self._publish(result)
        print(summary_line(result), flush=True)
        print("MAP", flush=True)
        print(ascii_scene(result), flush=True)
        print("MAP_END", flush=True)
        print(f"READY mode={mode}", flush=True)

    def _publish(self, result: dict) -> None:
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = "map"
        for x, y in result["path"]:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self._path_pub.publish(path)


def main() -> None:
    rclpy.init()
    node = GlobalPlanner()
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
