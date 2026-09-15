#!/usr/bin/env python3
"""
The same four ROS 2 nodes — but all sharing ONE process and ONE executor.

This is the Python equivalent of what `rclcpp_components` /
`ComposableNodeContainer` do in C++: several independent nodes are loaded into
a single container process so they can share memory and avoid serialising
messages between each other.

Architecturally nothing has changed. There are still four nodes, still four
distinct responsibilities, still four separate topics. The ROS graph looks
identical to the four-process version.

Only the process topology changed — and that is what this experiment measures.

Usage:
    python3 composed_container.py [crash_after_ticks]
"""

import os
import sys

import rclpy
from rclpy.executors import SingleThreadedExecutor

from sensor_node import SensorNode

SUBSYSTEMS = ("camera", "gps", "imu", "motor")


def main() -> None:
    crash_after = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    rclpy.init()

    # Only the camera is given a fault, exactly as in the four-process run.
    nodes = [
        SensorNode(name, crash_after=crash_after if name == "camera" else None)
        for name in SUBSYSTEMS
    ]

    executor = SingleThreadedExecutor()
    for node in nodes:
        executor.add_node(node)

    print(f"\n>>> {len(nodes)} ROS 2 nodes composed into a single process (pid {os.getpid()})\n")

    # As in sensor_node.py, the exception is deliberately left unhandled.
    executor.spin()


if __name__ == "__main__":
    main()
