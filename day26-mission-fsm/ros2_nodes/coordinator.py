#!/usr/bin/env python3
"""Publish the mission state a rescue coordinator is willing to enter.

missed   seen, then the second look fails, then a confirm is refused.
held     seen, then the second look holds. LOCKDOWN.
stay     after LOCKDOWN, seen, missed, and a finished goal are refused.
"""

from __future__ import annotations

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

from mission import run, summary_line


class Coordinator(Node):
    def __init__(self) -> None:
        super().__init__("coordinator")
        self.declare_parameter("mode", "held")
        mode = str(self.get_parameter("mode").value)
        latched = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._state_pub = self.create_publisher(String, "/mission_state", latched)
        result = run(mode)
        msg = String()
        msg.data = result["final"]
        self._state_pub.publish(msg)
        print(summary_line(result), flush=True)
        print(f"READY mode={mode}", flush=True)


def main() -> None:
    rclpy.init()
    node = Coordinator()
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
