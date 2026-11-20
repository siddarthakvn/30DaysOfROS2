#!/usr/bin/env python3
"""Position controller for one robot.

- collision:      hardcoded '/odom', '/cmd_vel', and shared '/fleet/target'
- uncoordinated:  relative 'odom' and 'cmd_vel', but still subscribed directly to '/fleet/target'
- coordinated:    relative 'odom', 'cmd_vel', and private 'goal' assigned by fleet_coordinator
"""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Bool

from fleet_spec import DT, GOAL_TOLERANCE, KP, clamp_vec, dist
from qos import latched, stream


class RobotController(Node):
    def __init__(self) -> None:
        super().__init__("controller")
        self.declare_parameter("robot_id", "r1")
        self.declare_parameter("mode", "coordinated")
        self._id = str(self.get_parameter("robot_id").value)
        self._mode = str(self.get_parameter("mode").value)

        self._pose: tuple[float, float] | None = None
        self._goal: tuple[float, float] | None = None
        self._done = False
        self._frozen = False

        if self._mode == "collision":
            odom_topic = "/odom"
            cmd_topic = "/cmd_vel"
            goal_topic = "/fleet/target"
        elif self._mode == "uncoordinated":
            odom_topic = "odom"
            cmd_topic = "cmd_vel"
            goal_topic = "/fleet/target"
        elif self._mode == "coordinated":
            odom_topic = "odom"
            cmd_topic = "cmd_vel"
            goal_topic = "goal"
        else:
            raise ValueError(f"unknown mode: {self._mode}")

        self._cmd_pub = self.create_publisher(Twist, cmd_topic, stream())
        self.create_subscription(Odometry, odom_topic, self._on_odom, stream())
        self.create_subscription(PoseStamped, goal_topic, self._on_goal, latched())
        self.create_subscription(Bool, "/fleet/freeze", self._on_freeze, latched())
        self.create_timer(DT, self._tick)

    def _on_odom(self, msg: Odometry) -> None:
        self._pose = (
            float(msg.pose.pose.position.x),
            float(msg.pose.pose.position.y),
        )

    def _on_goal(self, msg: PoseStamped) -> None:
        self._goal = (
            float(msg.pose.position.x),
            float(msg.pose.position.y),
        )
        self._done = False

    def _on_freeze(self, msg: Bool) -> None:
        if msg.data:
            self._frozen = True

    def _tick(self) -> None:
        if self._frozen or self._pose is None or self._goal is None or self._done:
            return
        err = dist(self._pose, self._goal)
        cmd = Twist()
        if err <= GOAL_TOLERANCE:
            self._done = True
            self._cmd_pub.publish(cmd)
            return
        vx, vy = clamp_vec(
            KP * (self._goal[0] - self._pose[0]),
            KP * (self._goal[1] - self._pose[1]),
        )
        cmd.linear.x = vx
        cmd.linear.y = vy
        self._cmd_pub.publish(cmd)


def main() -> None:
    rclpy.init()
    node = RobotController()
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
