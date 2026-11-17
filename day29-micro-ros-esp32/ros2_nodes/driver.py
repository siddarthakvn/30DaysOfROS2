#!/usr/bin/env python3
"""Host ROS 2 driver: publishes /cmd_vel and listens to /esp32/status."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from qos import command_qos, latched

TARGET_VX = 0.40
TARGET_WZ = 0.40


class TeleopDriver(Node):
    def __init__(self) -> None:
        super().__init__("teleop_driver")
        self.declare_parameter("mode", "bridged")
        self._mode = str(self.get_parameter("mode").value)
        if self._mode not in ("no_agent", "bridged", "watchdog"):
            raise ValueError(f"unknown mode: {self._mode}")

        self._cmd_pub = self.create_publisher(Twist, "/cmd_vel", command_qos())
        self.create_subscription(String, "/esp32/status", self._on_status, latched())

        self._cmd_tx = 0
        self._status_rx = 0
        self._states: list[str] = []
        self._last_status = "-"
        self._reported = False
        self._ticks = 0
        self.create_timer(0.05, self._on_tick)

    def _on_status(self, msg: String) -> None:
        self._status_rx += 1
        self._last_status = msg.data
        state = "UNKNOWN"
        for token in msg.data.split():
            if token.startswith("state="):
                state = token.split("=", 1)[1]
                break
        if not self._states or self._states[-1] != state:
            self._states.append(state)
        self._check_ready()

    def _publish_cmd(self) -> None:
        msg = Twist()
        msg.linear.x = TARGET_VX
        msg.angular.z = TARGET_WZ
        self._cmd_pub.publish(msg)
        self._cmd_tx += 1

    def _on_tick(self) -> None:
        self._ticks += 1
        if self._mode in ("no_agent", "bridged"):
            self._publish_cmd()
        elif self._mode == "watchdog":
            # Keep sending until the board confirms DRIVING and at least 5 commands went out, then go silent.
            if not ("DRIVING" in self._states and self._cmd_tx >= 5):
                self._publish_cmd()
        self._check_ready()

    def _check_ready(self) -> None:
        if self._reported:
            return
        if self._mode == "no_agent" and self._cmd_tx >= 10:
            self._emit()
        elif self._mode == "bridged" and "DRIVING" in self._states and self._cmd_tx >= 5:
            self._emit()
        elif self._mode == "watchdog" and "WATCHDOG_STOP" in self._states:
            self._emit()

    def _emit(self) -> None:
        if self._reported:
            return
        self._reported = True
        trace = ">".join(self._states) if self._states else "NONE"
        last_state = self._states[-1] if self._states else "NONE"
        print(
            "SUMMARY "
            f"node=driver mode={self._mode} cmd_tx={self._cmd_tx} "
            f"status_rx={self._status_rx} trace={trace} last_state={last_state}",
            flush=True,
        )
        print(f"READY node=driver mode={self._mode}", flush=True)


def main() -> None:
    rclpy.init()
    node = TeleopDriver()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node._emit()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
