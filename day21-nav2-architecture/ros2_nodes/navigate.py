#!/usr/bin/env python3
"""Accept a NavigateToPose goal and show which stage actually runs.

goal_only     the action arrives. No path. No speed.
planner_only  a path is drawn around the wall. The robot does not move.
full          the controller turns that path into Twist and the pose arrives.
"""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Path
from rclpy.action import ActionServer
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from route import GOAL, ascii_scene, run


def _yaw_to_quat(yaw: float) -> tuple[float, float]:
    return math.sin(yaw / 2.0), math.cos(yaw / 2.0)


class Navigator(Node):
    def __init__(self) -> None:
        super().__init__("navigator")
        self.declare_parameter("mode", "full")
        self._mode = str(self.get_parameter("mode").value)
        latched = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        live = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self._path_pub = self.create_publisher(Path, "/plan", latched)
        self._cmd_pub = self.create_publisher(Twist, "/cmd_vel", live)
        self._pose_pub = self.create_publisher(PoseStamped, "/robot_pose", latched)
        self._last = None
        self._server = ActionServer(self, NavigateToPose, "navigate_to_pose", self._execute)
        print(f"READY mode={self._mode}", flush=True)

    def _execute(self, goal_handle):
        request = goal_handle.request.pose.pose
        goal = (request.position.x, request.position.y, 0.0)
        # The day's goal is fixed so the wall stays between start and pin.
        if abs(goal[0] - GOAL[0]) > 0.2 or abs(goal[1] - GOAL[1]) > 0.2:
            goal = GOAL
        result = run(self._mode, goal)
        self._last = result
        self._publish(result)
        print(
            f"SUMMARY mode={result['mode']} events={result['events']} "
            f"result={result['result']} path_poses={result['path_poses']} "
            f"path_length_m={result['path_length_m']:.2f} "
            f"straight_m={result['straight_m']:.2f} "
            f"path_max_y_m={result['path_max_y_m']:.2f} "
            f"final_error_m={result['final_error_m']:.3f} "
            f"cmd_nonzero={result['cmd_nonzero']} "
            f"max_linear={result['max_linear']:.2f} "
            f"hit_wall={int(result['hit_wall'])}",
            flush=True,
        )
        print("MAP", flush=True)
        print(ascii_scene(result["path"], result["pose"]), flush=True)
        print("MAP_END", flush=True)
        if result["result"] == "SUCCEEDED":
            goal_handle.succeed()
        else:
            goal_handle.abort()
        return NavigateToPose.Result()

    def _publish(self, result: dict) -> None:
        stamp = self.get_clock().now().to_msg()
        path = Path()
        path.header.stamp = stamp
        path.header.frame_id = "map"
        for x, y in result["path"]:
            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self._path_pub.publish(path)
        cmd = Twist()
        cmd.linear.x = float(result["first_linear"])
        cmd.angular.z = float(result["first_angular"])
        self._cmd_pub.publish(cmd)
        pose = PoseStamped()
        pose.header.stamp = stamp
        pose.header.frame_id = "map"
        pose.pose.position.x = result["pose"][0]
        pose.pose.position.y = result["pose"][1]
        qz, qw = _yaw_to_quat(result["pose"][2])
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw
        self._pose_pub.publish(pose)

    def destroy_node(self) -> bool:
        self._server.destroy()
        return super().destroy_node()


def main() -> None:
    rclpy.init()
    node = Navigator()
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
