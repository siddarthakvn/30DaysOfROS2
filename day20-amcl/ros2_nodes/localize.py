#!/usr/bin/env python3
"""Place guesses on a frozen house map and publish the cloud.

Modes
  one_guess    one dot, dropped in the bedroom
  wheels_only  dots everywhere, moved by the wheels, never scored
  laser_vote   dots everywhere, scored by the laser, copies kept
"""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import Pose, PoseArray, PoseWithCovarianceStamped
from nav_msgs.msg import OccupancyGrid
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from house_filter import (
    WALLS,
    ascii_map,
    in_house,
    near_wall,
    run,
)


def _yaw_to_quat(yaw: float) -> tuple[float, float, float, float]:
    return 0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0)


class Localizer(Node):
    def __init__(self) -> None:
        super().__init__("localizer")
        self.declare_parameter("mode", "laser_vote")
        self._mode = str(self.get_parameter("mode").value)
        map_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        pose_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self._map_pub = self.create_publisher(OccupancyGrid, "/map", map_qos)
        self._cloud_pub = self.create_publisher(PoseArray, "/particle_cloud", pose_qos)
        self._pose_pub = self.create_publisher(PoseWithCovarianceStamped, "/amcl_pose", pose_qos)
        self._result = run(self._mode)
        self._map = self._map_msg()
        self._report()
        self.create_timer(0.5, self._publish)

    def _report(self) -> None:
        result = self._result
        print(
            f"SUMMARY mode={result['mode']} particles={len(result['particles'])} "
            f"final_error_m={result['final_error_m']:.3f} "
            f"final_spread_m={result['final_spread_m']:.3f} "
            f"kitchen_fraction={result['kitchen_fraction']:.3f}",
            flush=True,
        )
        for row in result["history"]:
            print(
                f"step={row['step']} error_m={row['error']:.3f} "
                f"spread_m={row['spread']:.3f} kitchen_fraction={row['kitchen']:.3f}",
                flush=True,
            )
        print("MAP", flush=True)
        print(ascii_map(result["particles"], result["truth"], result["estimate"]), flush=True)
        print("MAP_END", flush=True)

    def _publish(self) -> None:
        stamp = self.get_clock().now().to_msg()
        self._map.header.stamp = stamp
        self._map_pub.publish(self._map)
        cloud = PoseArray()
        cloud.header.stamp = stamp
        cloud.header.frame_id = "map"
        for x, y, yaw in self._result["particles"]:
            pose = Pose()
            cloud.poses.append(pose)
            pose.position.x = x
            pose.position.y = y
            qx, qy, qz, qw = _yaw_to_quat(yaw)
            pose.orientation.x = qx
            pose.orientation.y = qy
            pose.orientation.z = qz
            pose.orientation.w = qw
        self._cloud_pub.publish(cloud)
        estimate = PoseWithCovarianceStamped()
        estimate.header.stamp = stamp
        estimate.header.frame_id = "map"
        ex, ey, eyaw = self._result["estimate"]
        estimate.pose.pose.position.x = ex
        estimate.pose.pose.position.y = ey
        qx, qy, qz, qw = _yaw_to_quat(eyaw)
        estimate.pose.pose.orientation.z = qz
        estimate.pose.pose.orientation.w = qw
        self._pose_pub.publish(estimate)

    def _map_msg(self) -> OccupancyGrid:
        res = 0.05
        width = int(8.0 / res)
        height = int(5.0 / res)
        data = [-1] * (width * height)
        for iy in range(height):
            y = (iy + 0.5) * res
            for ix in range(width):
                x = (ix + 0.5) * res
                if near_wall(x, y, 0.08):
                    value = 100
                elif in_house(x, y):
                    value = 0
                else:
                    continue
                data[iy * width + ix] = value
        # Draw every wall segment, including the bits in_house skips.
        for (x1, y1), (x2, y2) in WALLS:
            length = max(int(math.hypot(x2 - x1, y2 - y1) / res), 1)
            for i in range(length + 1):
                t = i / length
                ix = int((x1 + (x2 - x1) * t) / res)
                iy = int((y1 + (y2 - y1) * t) / res)
                if 0 <= ix < width and 0 <= iy < height:
                    data[iy * width + ix] = 100
        msg = OccupancyGrid()
        msg.header.frame_id = "map"
        msg.info.resolution = res
        msg.info.width = width
        msg.info.height = height
        msg.info.origin.orientation.w = 1.0
        msg.data = data
        return msg


def main() -> None:
    rclpy.init()
    node = Localizer()
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
