#!/usr/bin/env python3
"""Publish the camera, the pixel, the depth, and the surveyed box. No map goal."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PointStamped, TransformStamped
from image_geometry import PinholeCameraModel
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import Float64
from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, StaticTransformBroadcaster, TransformListener

from geom import (
    BASE_XYZ,
    BASE_YAW,
    CAM_RPY,
    CAM_XYZ,
    OPTICAL_RPY,
    TARGET,
    camera_info,
    quaternion_from_euler,
)
from qos import latched


def _transform(parent: str, child: str, xyz, rpy, stamp) -> TransformStamped:
    msg = TransformStamped()
    msg.header.stamp = stamp
    msg.header.frame_id = parent
    msg.child_frame_id = child
    msg.transform.translation.x = float(xyz[0])
    msg.transform.translation.y = float(xyz[1])
    msg.transform.translation.z = float(xyz[2])
    qx, qy, qz, qw = quaternion_from_euler(*rpy)
    msg.transform.rotation.x = qx
    msg.transform.rotation.y = qy
    msg.transform.rotation.z = qz
    msg.transform.rotation.w = qw
    return msg


class Scene(Node):
    def __init__(self) -> None:
        super().__init__("scene")
        stamp = self.get_clock().now().to_msg()
        self._broadcaster = StaticTransformBroadcaster(self)
        self._broadcaster.sendTransform([
            _transform("map", "base_link", BASE_XYZ, (0.0, 0.0, BASE_YAW), stamp),
            _transform("base_link", "camera_link", CAM_XYZ, CAM_RPY, stamp),
            _transform("camera_link", "camera_optical_frame", (0.0, 0.0, 0.0), OPTICAL_RPY, stamp),
        ])
        self._buffer = Buffer()
        self._listener = TransformListener(self._buffer, self)
        self._info = camera_info()
        self._info.header.stamp = stamp
        self._model = PinholeCameraModel()
        self._model.fromCameraInfo(self._info)
        self._info_pub = self.create_publisher(CameraInfo, "/camera_info", latched())
        self._pixel_pub = self.create_publisher(PointStamped, "/pixel", latched())
        self._depth_pub = self.create_publisher(Float64, "/depth", latched())
        self._survey_pub = self.create_publisher(PointStamped, "/survey_map", latched())
        self._done = False
        self.create_timer(0.1, self._try_project)

    def _try_project(self) -> None:
        if self._done:
            return
        if not self._buffer.can_transform(
            "camera_optical_frame", "map", Time(), timeout=Duration(seconds=0.0)
        ):
            return
        survey = PointStamped()
        survey.header.frame_id = "map"
        survey.header.stamp = Time().to_msg()
        survey.point.x, survey.point.y, survey.point.z = TARGET
        optical_tf = self._buffer.lookup_transform("camera_optical_frame", "map", Time())
        optical = do_transform_point(survey, optical_tf)
        u, v = self._model.project3dToPixel((optical.point.x, optical.point.y, optical.point.z))
        pixel = PointStamped()
        pixel.header.stamp = self._info.header.stamp
        pixel.header.frame_id = "camera_optical_frame"
        pixel.point.x = float(u)
        pixel.point.y = float(v)
        pixel.point.z = 0.0
        depth = Float64()
        depth.data = float(optical.point.z)
        survey.header.stamp = self._info.header.stamp
        self._info_pub.publish(self._info)
        self._pixel_pub.publish(pixel)
        self._depth_pub.publish(depth)
        self._survey_pub.publish(survey)
        self._done = True
        print(
            "SUMMARY "
            f"node=scene u={u:.3f} v={v:.3f} depth_m={optical.point.z:.6f} "
            f"cam_x={optical.point.x:.6f} cam_y={optical.point.y:.6f} cam_z={optical.point.z:.6f} "
            f"target_x={TARGET[0]:.3f} target_y={TARGET[1]:.3f} target_z={TARGET[2]:.3f} "
            f"fx={self._model.fx():.1f} fy={self._model.fy():.1f} "
            f"cx={self._model.cx():.1f} cy={self._model.cy():.1f} "
            f"base_x={BASE_XYZ[0]:.2f} base_y={BASE_XYZ[1]:.2f} base_z={BASE_XYZ[2]:.2f} "
            f"cam_dx={CAM_XYZ[0]:.2f} cam_dz={CAM_XYZ[2]:.2f} map_goal=0",
            flush=True,
        )
        print("READY node=scene", flush=True)


def main() -> None:
    rclpy.init()
    node = Scene()
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
