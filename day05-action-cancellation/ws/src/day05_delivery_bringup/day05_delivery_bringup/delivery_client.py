#!/usr/bin/env python3
"""
Day 05 — Operator / mission client for DeliverToStation.

Sends a warehouse delivery goal, prints aisle progress feedback, and
optionally issues CancelGoal after cancel_after_sec (supervisor STOP).
"""

from __future__ import annotations

import time

import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from day05_delivery_interfaces.action import DeliverToStation


STATUS_MAP = {
    GoalStatus.STATUS_UNKNOWN: "UNKNOWN",
    GoalStatus.STATUS_ACCEPTED: "ACCEPTED",
    GoalStatus.STATUS_EXECUTING: "EXECUTING",
    GoalStatus.STATUS_CANCELING: "CANCELING",
    GoalStatus.STATUS_SUCCEEDED: "SUCCEEDED",
    GoalStatus.STATUS_CANCELED: "CANCELED",
    GoalStatus.STATUS_ABORTED: "ABORTED",
}


class DeliveryClient(Node):
    def __init__(self) -> None:
        super().__init__("delivery_client")
        self.declare_parameter("action_name", "deliver_to_station")
        self.declare_parameter("distance_m", 10.0)
        self.declare_parameter("cancel_after_sec", -1.0)

        name = str(self.get_parameter("action_name").value)
        self._distance = float(self.get_parameter("distance_m").value)
        self._cancel_after = float(self.get_parameter("cancel_after_sec").value)
        self._client = ActionClient(self, DeliverToStation, name)
        self._feedback_count = 0

    def run(self) -> str:
        self.get_logger().info(f"Waiting for action '{self._client._action_name}' ...")
        if not self._client.wait_for_server(timeout_sec=15.0):
            self.get_logger().error("Action server not available")
            return "NO_SERVER"

        goal = DeliverToStation.Goal()
        goal.distance_m = self._distance
        if self._cancel_after >= 0.0:
            self.get_logger().info(
                f"Sending delivery goal distance_m={self._distance:.2f}; "
                f"supervisor will STOP after {self._cancel_after:.2f}s"
            )
        else:
            self.get_logger().info(
                f"Sending delivery goal distance_m={self._distance:.2f}; "
                "no cancel scheduled (run to completion)"
            )

        send_future = self._client.send_goal_async(
            goal, feedback_callback=self._on_feedback
        )
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error("Goal rejected")
            return "REJECTED"

        uuid_hex = bytes(goal_handle.goal_id.uuid).hex()
        self.get_logger().info(f"Goal accepted id={uuid_hex}")

        result_future = goal_handle.get_result_async()
        t0 = time.monotonic()
        canceled = False

        while rclpy.ok() and not result_future.done():
            rclpy.spin_once(self, timeout_sec=0.05)
            if (
                not canceled
                and self._cancel_after >= 0.0
                and (time.monotonic() - t0) >= self._cancel_after
            ):
                self.get_logger().warn("Requesting CANCEL now (supervisor STOP)")
                cancel_future = goal_handle.cancel_goal_async()
                rclpy.spin_until_future_complete(
                    self, cancel_future, timeout_sec=5.0
                )
                canceled = True
                cancel_response = cancel_future.result()
                if cancel_response is None:
                    self.get_logger().error("Cancel response is None")
                else:
                    n = len(cancel_response.goals_canceling)
                    self.get_logger().info(
                        f"Cancel response: return_code={cancel_response.return_code} "
                        f"goals_canceling={n}"
                    )

        wrapped = result_future.result()
        status = wrapped.status
        status_name = STATUS_MAP.get(status, f"STATUS_{status}")
        result = wrapped.result
        self.get_logger().info(
            f"Terminal status={status_name} ({status}) "
            f"traveled={result.distance_traveled_m:.3f} m "
            f"remaining={result.distance_remaining_m:.3f} m "
            f"feedback_msgs={self._feedback_count}"
        )
        print(
            f"FINAL_STATUS={status_name} "
            f"traveled={result.distance_traveled_m:.3f} "
            f"remaining={result.distance_remaining_m:.3f} "
            f"feedback={self._feedback_count}"
        )
        return status_name

    def _on_feedback(self, feedback_msg) -> None:
        self._feedback_count += 1
        fb = feedback_msg.feedback
        if self._feedback_count == 1 or self._feedback_count % 5 == 0:
            self.get_logger().info(
                f"Feedback n={self._feedback_count} "
                f"remaining={fb.distance_remaining_m:.3f} m "
                f"percent={fb.percent_complete:.1f}%"
            )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DeliveryClient()
    status = "ERROR"
    try:
        status = node.run()
    except ExternalShutdownException:
        status = "EXTERNAL_SHUTDOWN"
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if not status.startswith("FINAL") and status not in (
        "SUCCEEDED",
        "CANCELED",
        "ABORTED",
        "REJECTED",
        "NO_SERVER",
        "EXTERNAL_SHUTDOWN",
        "ERROR",
    ):
        print(f"FINAL_STATUS={status}")


if __name__ == "__main__":
    main()
