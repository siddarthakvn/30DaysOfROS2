#!/usr/bin/env python3
"""
Day 04 Investigation C1 — Action client that cancels mid-goal.

Sends /turtle1/rotate_absolute, prints feedback, then cancels after
cancel_after_sec to demonstrate CANCELING → CANCELED vs Topic/Service interrupt.

Usage:
  python3 action_cancel_demo.py --ros-args -p theta:=3.14 -p cancel_after_sec:=1.0
"""

from __future__ import annotations

import time

import rclpy
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlesim.action import RotateAbsolute


class ActionCancelDemo(Node):
    def __init__(self) -> None:
        super().__init__("action_cancel_demo")
        self.declare_parameter("action_name", "/turtle1/rotate_absolute")
        self.declare_parameter("theta", 3.14)
        self.declare_parameter("cancel_after_sec", 1.0)

        name = str(self.get_parameter("action_name").value)
        self._theta = float(self.get_parameter("theta").value)
        self._cancel_after = float(self.get_parameter("cancel_after_sec").value)
        self._client = ActionClient(self, RotateAbsolute, name)
        self._feedback_count = 0
        self._done = False
        self._status_name = "UNKNOWN"

    def run(self) -> str:
        self.get_logger().info(f"Waiting for action {self._client._action_name} ...")
        if not self._client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("Action server not available")
            return "NO_SERVER"

        goal = RotateAbsolute.Goal()
        goal.theta = self._theta
        self.get_logger().info(
            f"Sending goal theta={self._theta:.3f}; "
            f"will cancel after {self._cancel_after:.2f}s"
        )
        send_future = self._client.send_goal_async(
            goal, feedback_callback=self._on_feedback
        )
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error("Goal rejected")
            return "REJECTED"

        self.get_logger().info(f"Goal accepted id={goal_handle.goal_id}")
        result_future = goal_handle.get_result_async()

        t0 = time.monotonic()
        canceled = False
        while rclpy.ok() and not result_future.done():
            rclpy.spin_once(self, timeout_sec=0.05)
            if not canceled and (time.monotonic() - t0) >= self._cancel_after:
                self.get_logger().warn("Requesting CANCEL now")
                cancel_future = goal_handle.cancel_goal_async()
                rclpy.spin_until_future_complete(self, cancel_future, timeout_sec=5.0)
                canceled = True
                cancel_response = cancel_future.result()
                self.get_logger().info(f"Cancel response: {cancel_response}")

        result = result_future.result()
        status = result.status
        # action_msgs/GoalStatus values
        status_map = {
            1: "ACCEPTED",
            2: "EXECUTING",
            3: "CANCELING",
            4: "SUCCEEDED",
            5: "CANCELED",
            6: "ABORTED",
        }
        self._status_name = status_map.get(status, f"STATUS_{status}")
        delta = result.result.delta
        self.get_logger().info(
            f"Terminal status={self._status_name} ({status}) "
            f"delta={delta:.4f} feedback_msgs={self._feedback_count}"
        )
        return self._status_name

    def _on_feedback(self, feedback_msg) -> None:
        self._feedback_count += 1
        remaining = feedback_msg.feedback.remaining
        if self._feedback_count == 1 or self._feedback_count % 10 == 0:
            self.get_logger().info(
                f"Feedback n={self._feedback_count} remaining={remaining:.4f}"
            )


def main() -> None:
    rclpy.init()
    node = ActionCancelDemo()
    status = "ERROR"
    try:
        status = node.run()
    except ExternalShutdownException:
        status = "EXTERNAL_SHUTDOWN"
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    print(f"FINAL_STATUS={status}")


if __name__ == "__main__":
    main()
