#!/usr/bin/env python3
"""Simulated mobile base for one robot.

In mode=collision, topics and TF frame names use hardcoded leading slashes / global names
('/cmd_vel', '/odom', 'base_link'), breaking namespace isolation even when launched under /rN.
In mode=uncoordinated and mode=coordinated, relative names ('cmd_vel', 'odom') and frame
prefixes ('rN/base_link') isolate each robot's body.
"""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Bool, String
from tf2_ros import TransformBroadcaster

from fleet_spec import DT, START_POSES, TARGET_XY, dist
from qos import latched, stream


class RobotBase(Node):
    def __init__(self) -> None:
        super().__init__("base")
        self.declare_parameter("robot_id", "r1")
        self.declare_parameter("mode", "coordinated")
        self._id = str(self.get_parameter("robot_id").value)
        self._mode = str(self.get_parameter("mode").value)

        x0, y0 = START_POSES[self._id]
        self._x = float(x0)
        self._y = float(y0)
        self._vx = 0.0
        self._vy = 0.0
        self._travel = 0.0
        self._rx_cmds = 0
        self._frozen = False

        if self._mode == "collision":
            cmd_topic = "/cmd_vel"
            odom_topic = "/odom"
            self._child_frame = "base_link"
        else:
            cmd_topic = "cmd_vel"
            odom_topic = "odom"
            self._child_frame = f"{self._id}/base_link"

        self._tf = TransformBroadcaster(self)
        self._odom_pub = self.create_publisher(Odometry, odom_topic, stream())
        self._ready_pub = self.create_publisher(Bool, f"/fleet/ready_{self._id}", latched())
        self._report_pub = self.create_publisher(String, f"/fleet/report_{self._id}", latched())

        self.create_subscription(Twist, cmd_topic, self._on_cmd, stream())
        self.create_subscription(Bool, "/fleet/freeze", self._on_freeze, latched())
        self.create_timer(DT, self._step)

        ready = Bool()
        ready.data = True
        self._ready_pub.publish(ready)

    def _on_cmd(self, msg: Twist) -> None:
        if self._frozen:
            return
        self._rx_cmds += 1
        self._vx = float(msg.linear.x)
        self._vy = float(msg.linear.y)

    def _on_freeze(self, msg: Bool) -> None:
        if not msg.data or self._frozen:
            return
        self._frozen = True
        self._vx = 0.0
        self._vy = 0.0
        err = dist((self._x, self._y), TARGET_XY)
        report = String()
        report.data = (
            f"robot={self._id} x={self._x:.3f} y={self._y:.3f} "
            f"travel_m={self._travel:.3f} err_m={err:.3f} "
            f"rx_cmds={self._rx_cmds} frame={self._child_frame}"
        )
        self._report_pub.publish(report)

    def _step(self) -> None:
        if not self._frozen:
            dx = self._vx * DT
            dy = self._vy * DT
            self._x += dx
            self._y += dy
            self._travel += math.hypot(dx, dy)

        stamp = self.get_clock().now().to_msg()
        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = "map"
        odom.child_frame_id = self._child_frame
        odom.pose.pose.position.x = self._x
        odom.pose.pose.position.y = self._y
        odom.pose.pose.orientation.w = 1.0
        odom.twist.twist.linear.x = self._vx
        odom.twist.twist.linear.y = self._vy
        self._odom_pub.publish(odom)

        tf_msg = TransformStamped()
        tf_msg.header.stamp = stamp
        tf_msg.header.frame_id = "map"
        tf_msg.child_frame_id = self._child_frame
        tf_msg.transform.translation.x = self._x
        tf_msg.transform.translation.y = self._y
        tf_msg.transform.rotation.w = 1.0
        self._tf.sendTransform(tf_msg)


def main() -> None:
    rclpy.init()
    node = RobotBase()
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
