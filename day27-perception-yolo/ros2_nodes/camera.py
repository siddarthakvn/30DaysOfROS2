#!/usr/bin/env python3
"""Publish one camera frame. This node does not know what is in the picture."""

from __future__ import annotations

import rclpy
from cv_bridge import CvBridge
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image

from qos import latched
from yolo import load_scene


class FrontCamera(Node):
    def __init__(self) -> None:
        super().__init__("front_camera")
        self.declare_parameter("scene", "street")
        scene = str(self.get_parameter("scene").value)
        image = load_scene(scene)
        bridge = CvBridge()
        msg = bridge.cv2_to_imgmsg(image, encoding="bgr8")
        msg.header.frame_id = "front"
        msg.header.stamp = self.get_clock().now().to_msg()
        self._msg = msg
        self._pub = self.create_publisher(Image, "/front/image_raw", latched())
        self._pub.publish(self._msg)
        self.create_timer(0.5, self._republish)
        print(
            "SUMMARY "
            f"node=camera scene={scene} width={image.shape[1]} height={image.shape[0]} "
            f"encoding={msg.encoding} frame={msg.header.frame_id} "
            f"stamp_sec={msg.header.stamp.sec} stamp_nsec={msg.header.stamp.nanosec}",
            flush=True,
        )
        print(f"READY node=camera scene={scene}", flush=True)

    def _republish(self) -> None:
        self._pub.publish(self._msg)


def main() -> None:
    rclpy.init()
    node = FrontCamera()
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
