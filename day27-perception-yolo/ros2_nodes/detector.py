#!/usr/bin/env python3
"""Turn one image message into a Detection2DArray. The header is copied, not invented."""

from __future__ import annotations

import rclpy
from cv_bridge import CvBridge
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose

from qos import latched
from yolo import best_person, detect, load_net


class YoloDetector(Node):
    def __init__(self) -> None:
        super().__init__("yolo_detector")
        self.declare_parameter("scene", "street")
        self._scene = str(self.get_parameter("scene").value)
        self._bridge = CvBridge()
        self._net = load_net()
        self._done = False
        self._pub = self.create_publisher(Detection2DArray, "/detections", latched())
        self.create_subscription(Image, "/front/image_raw", self._on_image, latched())

    def _on_image(self, msg: Image) -> None:
        if self._done:
            return
        self._done = True
        image = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        rows = detect(image, self._net)
        out = Detection2DArray()
        out.header.stamp = msg.header.stamp
        out.header.frame_id = msg.header.frame_id
        for index, row in enumerate(rows):
            det = Detection2D()
            det.header.stamp = msg.header.stamp
            det.header.frame_id = msg.header.frame_id
            det.id = f"{row['name']}-{index}"
            hyp = ObjectHypothesisWithPose()
            hyp.hypothesis.class_id = row["name"]
            hyp.hypothesis.score = float(row["score"])
            det.results.append(hyp)
            det.bbox.center.position.x = float(row["cx"])
            det.bbox.center.position.y = float(row["cy"])
            det.bbox.center.theta = 0.0
            det.bbox.size_x = float(row["sx"])
            det.bbox.size_y = float(row["sy"])
            out.detections.append(det)
        self._pub.publish(out)
        person = best_person(rows)
        score = 0.0 if person is None else person["score"]
        if person is None:
            box = "cx=0.0 cy=0.0 sx=0.0 sy=0.0"
        else:
            box = (
                f"cx={person['cx']:.1f} cy={person['cy']:.1f} "
                f"sx={person['sx']:.1f} sy={person['sy']:.1f}"
            )
        names = ",".join(row["name"] for row in rows) if rows else "-"
        same = (
            out.header.stamp.sec == msg.header.stamp.sec
            and out.header.stamp.nanosec == msg.header.stamp.nanosec
            and out.header.frame_id == msg.header.frame_id
        )
        print(
            "SUMMARY "
            f"node=detector scene={self._scene} width={image.shape[1]} height={image.shape[0]} "
            f"detections={len(rows)} persons={sum(1 for row in rows if row['name'] == 'person')} "
            f"best_person={score:.3f} {box} classes={names} "
            f"frame={out.header.frame_id} stamp_sec={out.header.stamp.sec} "
            f"stamp_nsec={out.header.stamp.nanosec} stamp_match={int(same)}",
            flush=True,
        )
        print(f"READY node=detector scene={self._scene}", flush=True)


def main() -> None:
    rclpy.init()
    node = YoloDetector()
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
