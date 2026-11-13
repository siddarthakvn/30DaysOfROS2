#!/usr/bin/env python3
"""Turn one pixel, the camera model, and a depth into a point in the camera frame."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PointStamped
from image_geometry import PinholeCameraModel
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import Float64

from geom import backproject
from qos import latched


class Ray(Node):
    def __init__(self) -> None:
        super().__init__("ray")
        self._info = None
        self._pixel = None
        self._depth = None
        self._done = False
        self._pub = self.create_publisher(PointStamped, "/point_camera", latched())
        self.create_subscription(CameraInfo, "/camera_info", self._on_info, latched())
        self.create_subscription(PointStamped, "/pixel", self._on_pixel, latched())
        self.create_subscription(Float64, "/depth", self._on_depth, latched())

    def _on_info(self, msg: CameraInfo) -> None:
        self._info = msg
        self._finish()

    def _on_pixel(self, msg: PointStamped) -> None:
        self._pixel = msg
        self._finish()

    def _on_depth(self, msg: Float64) -> None:
        self._depth = msg
        self._finish()

    def _finish(self) -> None:
        if self._done or self._info is None or self._pixel is None or self._depth is None:
            return
        self._done = True
        model = PinholeCameraModel()
        model.fromCameraInfo(self._info)
        u = float(self._pixel.point.x)
        v = float(self._pixel.point.y)
        depth_z = float(self._depth.data)
        x, y, z = backproject(model, u, v, depth_z)
        point = PointStamped()
        point.header.stamp = self._pixel.header.stamp
        point.header.frame_id = "camera_optical_frame"
        point.point.x = x
        point.point.y = y
        point.point.z = z
        self._pub.publish(point)
        print(
            "SUMMARY "
            f"node=ray u={u:.3f} v={v:.3f} depth_m={depth_z:.6f} "
            f"cam_x={x:.6f} cam_y={y:.6f} cam_z={z:.6f} "
            f"frame={point.header.frame_id}",
            flush=True,
        )
        print("READY node=ray", flush=True)


def main() -> None:
    rclpy.init()
    node = Ray()
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
