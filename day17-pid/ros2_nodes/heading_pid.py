#!/usr/bin/env python3
"""Run one heading PID case and print a SUMMARY line."""

from __future__ import annotations

import math

import rclpy
from rclpy.node import Node

from heading import simulate


class HeadingCase(Node):
    def __init__(self) -> None:
        super().__init__("heading_pid")
        self.declare_parameter("kp", 4.0)
        self.declare_parameter("kd", 0.0)
        self.declare_parameter("ki", 0.0)
        self.declare_parameter("plant", "inertia")
        self.declare_parameter("target_deg", 90.0)
        self.declare_parameter("seconds", 8.0)

        result = simulate(
            kp=float(self.get_parameter("kp").value),
            kd=float(self.get_parameter("kd").value),
            ki=float(self.get_parameter("ki").value),
            plant=str(self.get_parameter("plant").value),
            target=math.radians(float(self.get_parameter("target_deg").value)),
            seconds=float(self.get_parameter("seconds").value),
        )
        print(
            "SUMMARY "
            f"crossings={result['crossings']} "
            f"yaw_deg={result['yaw_deg']:.2f} "
            f"error_deg={result['error_deg']:.2f} "
            f"past_deg={result['past_deg']:.2f} "
            f"kp={float(self.get_parameter('kp').value):.1f} "
            f"kd={float(self.get_parameter('kd').value):.1f} "
            f"plant={self.get_parameter('plant').value}"
        )
        raise SystemExit(0)


def main() -> None:
    rclpy.init()
    node = HeadingCase()
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()
