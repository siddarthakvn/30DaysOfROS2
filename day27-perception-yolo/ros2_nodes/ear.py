#!/usr/bin/env python3
"""Hear /detections. Say SEEN only for a person at or above the score line."""

from __future__ import annotations

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String
from vision_msgs.msg import Detection2DArray

from qos import latched
from yolo import SEEN_SCORE


class MissionEar(Node):
    def __init__(self) -> None:
        super().__init__("mission_ear")
        self.declare_parameter("scene", "street")
        self._scene = str(self.get_parameter("scene").value)
        self._done = False
        self._pub = self.create_publisher(String, "/mission_event", latched())
        self.create_subscription(Detection2DArray, "/detections", self._on_detections, latched())

    def _on_detections(self, msg: Detection2DArray) -> None:
        if self._done:
            return
        self._done = True
        best_name = "-"
        best_score = 0.0
        for det in msg.detections:
            if not det.results:
                continue
            hyp = det.results[0].hypothesis
            if hyp.class_id == "person" and hyp.score > best_score:
                best_name = hyp.class_id
                best_score = float(hyp.score)
        seen = best_name == "person" and best_score >= SEEN_SCORE
        if seen:
            event = String()
            event.data = "SEEN"
            self._pub.publish(event)
        print(
            "SUMMARY "
            f"node=ear scene={self._scene} seen={int(seen)} "
            f"best_person={best_score:.3f} class_id={best_name} "
            f"threshold={SEEN_SCORE:.2f} detections={len(msg.detections)} "
            f"frame={msg.header.frame_id} stamp_sec={msg.header.stamp.sec} "
            f"stamp_nsec={msg.header.stamp.nanosec}",
            flush=True,
        )
        print(f"READY node=ear scene={self._scene}", flush=True)


def main() -> None:
    rclpy.init()
    node = MissionEar()
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
