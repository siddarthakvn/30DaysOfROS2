#!/usr/bin/env python3
"""
Day 04 Investigation B — Client for the long-running rotate service.

Blocks until the single Trigger response arrives (or you Ctrl+C the client).
Ctrl+C here does not send a cancel to the server — there is no cancel API.

Usage:
  python3 long_rotate_client.py
  python3 long_rotate_client.py --ros-args -p service_name:=/long_rotate
"""

from __future__ import annotations

import sys

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import Trigger


class LongRotateClient(Node):
    def __init__(self) -> None:
        super().__init__("long_rotate_client")
        self.declare_parameter("service_name", "/long_rotate")
        self.declare_parameter("timeout_sec", 30.0)

        name = str(self.get_parameter("service_name").value)
        self._timeout = float(self.get_parameter("timeout_sec").value)
        self._cli = self.create_client(Trigger, name)
        self.get_logger().info(f"Waiting for service {name} ...")

    def call(self) -> int:
        if not self._cli.wait_for_service(timeout_sec=10.0):
            self.get_logger().error("Service not available")
            return 1

        self.get_logger().info(
            "Calling long_rotate — will block for ONE response "
            "(Ctrl+C cancels THIS client only, not the server work)"
        )
        future = self._cli.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=self._timeout)

        if not future.done():
            self.get_logger().error(f"Timed out after {self._timeout:.1f}s")
            return 2

        result = future.result()
        if result is None:
            self.get_logger().error("Call failed (no result)")
            return 3

        self.get_logger().info(
            f"RESPONSE success={result.success} message={result.message!r}"
        )
        return 0 if result.success else 4


def main() -> None:
    rclpy.init()
    node = LongRotateClient()
    code = 1
    try:
        code = node.call()
    except KeyboardInterrupt:
        node.get_logger().warn(
            "Client interrupted — server may STILL be rotating (no cancel protocol)"
        )
        code = 130
    except ExternalShutdownException:
        code = 0
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    sys.exit(code)


if __name__ == "__main__":
    main()
