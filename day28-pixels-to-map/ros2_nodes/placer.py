#!/usr/bin/env python3
"""Place the camera point into the map. origin skips TF. map uses it."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PointStamped, PoseStamped
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time
from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, TransformListener

from geom import distance
from qos import latched


class Placer(Node):
    def __init__(self) -> None:
        super().__init__("placer")
        self.declare_parameter("mode", "map")
        self._mode = str(self.get_parameter("mode").value)
        if self._mode not in ("origin", "map"):
            raise ValueError(f"unknown mode: {self._mode}")
        self._camera = None
        self._survey = None
        self._done = False
        self._buffer = Buffer()
        self._listener = TransformListener(self._buffer, self)
        self._point_pub = self.create_publisher(PointStamped, "/point_map", latched())
        self._goal_pub = self.create_publisher(PoseStamped, "/goal", latched())
        self.create_subscription(PointStamped, "/point_camera", self._on_camera, latched())
        self.create_subscription(PointStamped, "/survey_map", self._on_survey, latched())
        self.create_timer(0.1, self._try_place)

    def _on_camera(self, msg: PointStamped) -> None:
        self._camera = msg

    def _on_survey(self, msg: PointStamped) -> None:
        self._survey = msg

    def _try_place(self) -> None:
        if self._done or self._camera is None or self._survey is None:
            return
        cam = (self._camera.point.x, self._camera.point.y, self._camera.point.z)
        stamp = self._camera.header.stamp
        if self._mode == "origin":
            placed = PointStamped()
            placed.header.frame_id = "map"
            placed.point.x, placed.point.y, placed.point.z = cam
            used_tf = 0
            cam_in_map = (0.0, 0.0, 0.0)
        else:
            if not self._buffer.can_transform(
                "map", self._camera.header.frame_id, Time(), timeout=Duration(seconds=0.0)
            ):
                return
            tf = self._buffer.lookup_transform("map", self._camera.header.frame_id, Time())
            placed = do_transform_point(self._camera, tf)
            placed.header.frame_id = "map"
            used_tf = 1
            cam_in_map = (
                tf.transform.translation.x,
                tf.transform.translation.y,
                tf.transform.translation.z,
            )
        placed.header.stamp = stamp
        goal = PoseStamped()
        goal.header.stamp = stamp
        goal.header.frame_id = "map"
        goal.pose.position.x = placed.point.x
        goal.pose.position.y = placed.point.y
        goal.pose.position.z = placed.point.z
        goal.pose.orientation.w = 1.0
        self._point_pub.publish(placed)
        self._goal_pub.publish(goal)
        self._done = True
        survey = (self._survey.point.x, self._survey.point.y, self._survey.point.z)
        here = (placed.point.x, placed.point.y, placed.point.z)
        print(
            "SUMMARY "
            f"node=placer mode={self._mode} used_tf={used_tf} frame={placed.header.frame_id} "
            f"x={here[0]:.6f} y={here[1]:.6f} z={here[2]:.6f} "
            f"target_x={survey[0]:.6f} target_y={survey[1]:.6f} target_z={survey[2]:.6f} "
            f"error_m={distance(here, survey):.6f} "
            f"cam_in_map_x={cam_in_map[0]:.6f} cam_in_map_y={cam_in_map[1]:.6f} "
            f"cam_in_map_z={cam_in_map[2]:.6f} goal=1",
            flush=True,
        )
        print(f"READY node=placer mode={self._mode}", flush=True)


def main() -> None:
    rclpy.init()
    node = Placer()
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
