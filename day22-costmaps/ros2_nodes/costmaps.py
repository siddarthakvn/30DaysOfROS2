#!/usr/bin/env python3
"""Publish the global costmap, the local costmap, and the path around a phantom.

live      the current scan of the empty room. The old cell is free.
stale     the obstacle layer still holds that cell. Inflation is off.
inflated  the same cell, plus the inflation layer. This is the swerve.
"""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_msgs.msg import Costmap, CostmapMetaData
from nav_msgs.msg import Path
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from layers import RES, ascii_scene, local_grid, run, summary_line


def _grid_to_costmap(node: Node, grid: list[list[int]], frame: str, layer: str, origin_xy: tuple[float, float]) -> Costmap:
    msg = Costmap()
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.header.frame_id = frame
    meta = CostmapMetaData()
    meta.map_load_time = msg.header.stamp
    meta.update_time = msg.header.stamp
    meta.layer = layer
    meta.resolution = RES
    meta.size_x = len(grid[0])
    meta.size_y = len(grid)
    meta.origin.position.x = origin_xy[0]
    meta.origin.position.y = origin_xy[1]
    meta.origin.orientation.w = 1.0
    msg.metadata = meta
    data = []
    for row in grid:
        data.extend(row)
    msg.data = bytes(data)
    return msg


class CostmapDemo(Node):
    def __init__(self) -> None:
        super().__init__("costmap_demo")
        self.declare_parameter("mode", "inflated")
        mode = str(self.get_parameter("mode").value)
        latched = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._global_pub = self.create_publisher(Costmap, "/global_costmap/costmap", latched)
        self._local_pub = self.create_publisher(Costmap, "/local_costmap/costmap", latched)
        self._path_pub = self.create_publisher(Path, "/plan", latched)
        result = run(mode)
        self._publish(result)
        print(summary_line_safe(result), flush=True)
        print("MAP", flush=True)
        print(ascii_scene(result), flush=True)
        print("MAP_END", flush=True)
        print(f"READY mode={mode}", flush=True)

    def _publish(self, result: dict) -> None:
        global_msg = _grid_to_costmap(self, result["grid"], "map", "master", (0.0, 0.0))
        self._global_pub.publish(global_msg)

        local, origin_x, origin_y, _ = local_grid()
        local_msg = _grid_to_costmap(self, local, "odom", "master", (origin_x, origin_y))
        self._local_pub.publish(local_msg)

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


def summary_line_safe(result: dict) -> str:
    return summary_line(result)


def main() -> None:
    rclpy.init()
    node = CostmapDemo()
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
