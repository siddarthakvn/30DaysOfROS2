#!/usr/bin/env python3
"""
One robot subsystem, implemented as a real ROS 2 node.

This single class is used by BOTH topologies in Investigation C:

  separate processes  ->  run this file four times, once per subsystem
  one shared process  ->  composed_container.py imports this class four times

The node code is therefore the *controlled variable*. The only thing that
changes between the two experiments is how many OS processes the nodes are
distributed across.

Usage:
    python3 sensor_node.py <name> [crash_after_ticks]

Examples:
    python3 sensor_node.py gps            # runs forever
    python3 sensor_node.py camera 5       # raises on the 5th timer callback
"""

import os
import sys

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SensorNode(Node):
    """Publishes a heartbeat, and optionally fails like a real driver would."""

    def __init__(self, name: str, period_s: float = 1.0, crash_after: int | None = None):
        super().__init__(f"{name}_node")
        self._name = name
        self._crash_after = crash_after
        self._tick = 0

        self._publisher = self.create_publisher(String, f"/{name}/status", 10)
        self.create_timer(period_s, self._on_timer)

        self.get_logger().info(f"{name} node started in pid {os.getpid()}")

    def _on_timer(self) -> None:
        self._tick += 1

        message = String()
        message.data = f"{self._name} tick {self._tick}"
        self._publisher.publish(message)

        self.get_logger().info(f"[{self._name}] tick {self._tick}  (pid {os.getpid()})")

        # A driver-level failure. Deliberately unhandled: we want to observe how
        # far the failure propagates, which is the entire point of this experiment.
        if self._crash_after is not None and self._tick >= self._crash_after:
            raise RuntimeError(f"{self._name} driver crashed!")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"usage: {sys.argv[0]} <name> [crash_after_ticks]")

    name = sys.argv[1]
    crash_after = int(sys.argv[2]) if len(sys.argv) > 2 else None

    rclpy.init()
    node = SensorNode(name, crash_after=crash_after)

    # No try/except: an unhandled exception must be allowed to terminate this
    # process, exactly as an unhandled driver fault would in production.
    rclpy.spin(node)


if __name__ == "__main__":
    main()
