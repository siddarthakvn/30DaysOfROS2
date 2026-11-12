#!/usr/bin/env python3
"""Publish one map point from a YOLO-style pixel, and print the result."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from rclpy.qos import QoSProfile

import geometry


class PixelToMap(Node):
    def __init__(self) -> None:
        super().__init__("pixel_to_map")
        self.declare_parameter("case", "full")
        case = str(self.get_parameter("case").value)
        result = geometry.run_case(case)

        self._line = (
            "SUMMARY "
            f"case={result['case']} "
            f"u={result['u']:.2f} v={result['v']:.2f} "
            f"depth={result['depth']:.4f} "
            f"map_x={result['map_x']:.4f} map_y={result['map_y']:.4f} "
            f"map_z={result['map_z']:.4f} "
            f"err_xy={result['err_xy']:.4f} "
            f"frame={result['frame']}"
        )

        qos = QoSProfile(depth=1)
        self._pub = self.create_publisher(PointStamped, "/detection/map_point", qos)
        self._msg = PointStamped()
        self._msg.header.frame_id = str(result["frame"])
        self._msg.point.x = float(result["map_x"])
        self._msg.point.y = float(result["map_y"])
        self._msg.point.z = float(result["map_z"])
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
    node = PixelToMap()
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
