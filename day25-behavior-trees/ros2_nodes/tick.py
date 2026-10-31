#!/usr/bin/env python3
"""Publish the tick trace for the knot, the state machine, and the behavior tree.

knot     five boxes, an arrow both ways between each pair.
machine  plan, follow, back up, and the retry edges written by hand.
tree     the same leaves under one recovery node.
"""

from __future__ import annotations

import rclpy
from nav2_msgs.msg import BehaviorTreeLog, BehaviorTreeStatusChange
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from checklist import run, summary_line


class Checklist(Node):
    def __init__(self) -> None:
        super().__init__("checklist")
        self.declare_parameter("mode", "tree")
        mode = str(self.get_parameter("mode").value)
        latched = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._log_pub = self.create_publisher(BehaviorTreeLog, "/behavior_tree_log", latched)
        result = run(mode)
        self._publish(result)
        print(summary_line(result), flush=True)
        print(f"READY mode={mode}", flush=True)

    def _publish(self, result: dict) -> None:
        stamp = self.get_clock().now().to_msg()
        msg = BehaviorTreeLog()
        msg.timestamp = stamp
        for name, status in result["statuses"]:
            change = BehaviorTreeStatusChange()
            change.timestamp = stamp
            change.node_name = name
            change.previous_status = "IDLE"
            change.current_status = status
            msg.event_log.append(change)
        self._log_pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = Checklist()
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
