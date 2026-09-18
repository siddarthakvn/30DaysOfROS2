#!/usr/bin/env python3
"""
Day 05 — Warehouse delivery Action server.

Real-life story: an AMR drives ``distance_m`` toward Station B.
Feedback reports remaining distance. If allow_cancel is true, a CancelGoal
request is accepted and the execute loop stops → CANCELED. If false, cancel
is rejected and the delivery continues to SUCCEEDED.
"""

from __future__ import annotations

import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node

from day05_delivery_interfaces.action import DeliverToStation


class DeliveryServer(Node):
    def __init__(self) -> None:
        super().__init__("delivery_server")
        self.declare_parameter("allow_cancel", True)
        self.declare_parameter("speed_mps", 1.0)
        self.declare_parameter("tick_sec", 0.2)
        self.declare_parameter("action_name", "deliver_to_station")

        self._allow_cancel = bool(self.get_parameter("allow_cancel").value)
        self._speed = float(self.get_parameter("speed_mps").value)
        self._tick = float(self.get_parameter("tick_sec").value)
        action_name = str(self.get_parameter("action_name").value)

        self._server = ActionServer(
            self,
            DeliverToStation,
            action_name,
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup(),
        )
        self.get_logger().info(
            f"Delivery server ready on '{action_name}' "
            f"(allow_cancel={self._allow_cancel}, speed={self._speed} m/s)"
        )

    def goal_callback(self, goal_request: DeliverToStation.Goal) -> GoalResponse:
        distance = float(goal_request.distance_m)
        if distance <= 0.0:
            self.get_logger().warn(f"Rejecting invalid distance_m={distance}")
            return GoalResponse.REJECT
        self.get_logger().info(
            f"Accepting delivery goal distance_m={distance:.2f} "
            "(warehouse aisle toward Station B)"
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle) -> CancelResponse:
        if self._allow_cancel:
            self.get_logger().warn(
                "Operator STOP accepted — transitioning goal toward CANCELING"
            )
            return CancelResponse.ACCEPT
        self.get_logger().warn(
            "Operator STOP rejected — allow_cancel=false; delivery continues"
        )
        return CancelResponse.REJECT

    def execute_callback(self, goal_handle):
        goal_distance = float(goal_handle.request.distance_m)
        traveled = 0.0
        step = self._speed * self._tick

        self.get_logger().info(
            f"EXECUTING delivery: {goal_distance:.2f} m at {self._speed:.2f} m/s"
        )

        while traveled < goal_distance:
            if goal_handle.is_cancel_requested:
                remaining = max(goal_distance - traveled, 0.0)
                result = DeliverToStation.Result()
                result.distance_traveled_m = traveled
                result.distance_remaining_m = remaining
                goal_handle.canceled()
                self.get_logger().info(
                    f"CANCELED after {traveled:.2f} m "
                    f"(remaining={remaining:.2f} m) — robot stopped cleanly"
                )
                return result

            traveled = min(traveled + step, goal_distance)
            remaining = goal_distance - traveled
            percent = 100.0 * traveled / goal_distance if goal_distance > 0 else 100.0

            feedback = DeliverToStation.Feedback()
            feedback.distance_remaining_m = remaining
            feedback.percent_complete = percent
            goal_handle.publish_feedback(feedback)

            time.sleep(self._tick)

        result = DeliverToStation.Result()
        result.distance_traveled_m = traveled
        result.distance_remaining_m = 0.0
        goal_handle.succeed()
        self.get_logger().info(
            f"SUCCEEDED delivery: traveled={traveled:.2f} m — arrived Station B"
        )
        return result


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DeliveryServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
