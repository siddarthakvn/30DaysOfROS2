#!/usr/bin/env python3
"""
Day 09 — Velocity governor (parameter-driven behavior).

Publishes a fixed "requested" speed and clamps it with parameter max_velocity.
Demonstrates:
  - declare + descriptor
  - YAML / CLI startup overrides
  - runtime ros2 param set
  - on-set validation (reject out of range)
  - live-read vs cache-once application paths

Usage:
  python3 velocity_governor.py --ros-args \\
    -p max_velocity:=1.0 -p request_vx:=1.5 -p run_sec:=6.0
"""

from __future__ import annotations

import time
from typing import Optional

import rclpy
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist


class VelocityGovernor(Node):
    def __init__(self) -> None:
        super().__init__("velocity_governor")

        desc = ParameterDescriptor(
            description=(
                "Maximum allowed linear.x (m/s). "
                "Validated to [0.0, 2.0] on every set."
            )
        )
        # Code default — YAML / -p overrides this at startup.
        self.declare_parameter("max_velocity", 1.0, desc)
        self.declare_parameter("request_vx", 1.5)
        self.declare_parameter("publish_hz", 2.0)
        self.declare_parameter("run_sec", 8.0)
        # live: re-read param every tick | once: freeze value after first read
        self.declare_parameter("apply_mode", "live")

        self._max_velocity = float(self.get_parameter("max_velocity").value)
        self._request_vx = float(self.get_parameter("request_vx").value)
        publish_hz = float(self.get_parameter("publish_hz").value)
        self._run_sec = float(self.get_parameter("run_sec").value)
        self._apply_mode = str(self.get_parameter("apply_mode").value).lower()
        if self._apply_mode not in ("live", "once"):
            raise ValueError("apply_mode must be 'live' or 'once'")

        self._cached_max: Optional[float] = (
            self._max_velocity if self._apply_mode == "once" else None
        )
        self._accepts = 0
        self._rejects = 0
        self._ticks = 0

        self._pub = self.create_publisher(Twist, "/day09/cmd_vel_limited", 10)
        self._cb_handle = self.add_on_set_parameters_callback(self._on_set_parameters)

        period = 1.0 / max(publish_hz, 0.1)
        self.create_timer(period, self._on_tick)
        self.create_timer(self._run_sec, self._on_stop)
        self._done = False

        self.get_logger().info(
            f"CONFIG max_velocity={self._max_velocity:.3f} "
            f"request_vx={self._request_vx:.3f} apply_mode={self._apply_mode} "
            f"run_sec={self._run_sec:.1f}"
        )
        self.get_logger().info(
            f"EFFECTIVE_MAX start={self._effective_max():.3f}"
        )

    def _effective_max(self) -> float:
        if self._apply_mode == "once":
            assert self._cached_max is not None
            return float(self._cached_max)
        return float(self.get_parameter("max_velocity").value)

    def _on_set_parameters(self, params: list[Parameter]) -> SetParametersResult:
        result = SetParametersResult()
        result.successful = True
        for p in params:
            if p.name != "max_velocity":
                continue
            if p.type_ != Parameter.Type.DOUBLE:
                result.successful = False
                result.reason = "max_velocity must be a float64"
                self._rejects += 1
                self.get_logger().warn(
                    f"PARAM_REJECT name=max_velocity reason={result.reason}"
                )
                return result
            value = float(p.value)
            if value < 0.0 or value > 2.0:
                result.successful = False
                result.reason = "max_velocity must be in [0.0, 2.0]"
                self._rejects += 1
                self.get_logger().warn(
                    f"PARAM_REJECT name=max_velocity value={value} "
                    f"reason={result.reason}"
                )
                return result
            self._accepts += 1
            self.get_logger().info(
                f"PARAM_ACCEPT name=max_velocity value={value:.3f}"
            )
        return result

    def _on_tick(self) -> None:
        if self._done:
            return
        vmax = self._effective_max()
        out_vx = min(self._request_vx, vmax)
        msg = Twist()
        msg.linear.x = out_vx
        self._pub.publish(msg)
        self._ticks += 1
        self.get_logger().info(
            f"TICK request={self._request_vx:.3f} max={vmax:.3f} "
            f"out={out_vx:.3f} mode={self._apply_mode}"
        )

    def _on_stop(self) -> None:
        if self._done:
            return
        self._done = True
        self.print_summary()

    def print_summary(self) -> None:
        stored = float(self.get_parameter("max_velocity").value)
        lines = [
            "==== SUMMARY ====",
            (
                f"CONFIG apply_mode={self._apply_mode} "
                f"request_vx={self._request_vx:.3f}"
            ),
            f"STORED max_velocity={stored:.3f}",
            f"EFFECTIVE_MAX={self._effective_max():.3f}",
            f"TICKS={self._ticks} accepts={self._accepts} rejects={self._rejects}",
            "==== END SUMMARY ====",
        ]
        for line in lines:
            self.get_logger().info(line)
            print(line, flush=True)


def main() -> None:
    rclpy.init()
    node = VelocityGovernor()
    try:
        while rclpy.ok() and not node._done:
            rclpy.spin_once(node, timeout_sec=0.05)
        # brief drain for late logs
        deadline = time.monotonic() + 0.3
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.05)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        try:
            node.destroy_node()
        except Exception:
            pass
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
