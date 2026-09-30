#!/usr/bin/env python3
"""Publish the same Twist teleop_twist_keyboard would publish for one key.

This node does not read the keyboard. It uses the installed package's
moveBindings so the numbers match the real teleop node (speed 0.5, turn 1.0).
"""
from __future__ import annotations

import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from teleop_twist_keyboard import moveBindings


class KeyTwist(Node):
    def __init__(self) -> None:
        super().__init__("key_twist")
        self.declare_parameter("key", "i")
        self.declare_parameter("speed", 0.5)
        self.declare_parameter("turn", 1.0)
        self.declare_parameter("topic", "/model/vehicle_blue/cmd_vel")
        self.declare_parameter("hz", 10.0)
        self.declare_parameter("run_sec", 3.0)
        # "" uses the key. "linear_y" publishes only a sideways speed.
        self.declare_parameter("override", "")
        self.declare_parameter("override_speed", 0.5)

        key = str(self.get_parameter("key").value)
        speed = float(self.get_parameter("speed").value)
        turn = float(self.get_parameter("turn").value)
        override = str(self.get_parameter("override").value)
        override_speed = float(self.get_parameter("override_speed").value)
        binding = moveBindings.get(key)
        if binding is None:
            x = y = z = th = 0.0
            source = "stop (key not in moveBindings)"
        else:
            x, y, z, th = binding
            source = f"moveBindings[{key!r}]"
        if override == "linear_y":
            x, y, z, th = 0.0, 1.0, 0.0, 0.0
            speed = override_speed
            source = "override linear_y only"

        self.twist = Twist()
        self.twist.linear.x = x * speed
        self.twist.linear.y = y * speed
        self.twist.linear.z = z * speed
        self.twist.angular.z = th * turn
        self.run_sec = float(self.get_parameter("run_sec").value)
        self.hz = float(self.get_parameter("hz").value)
        topic = str(self.get_parameter("topic").value)
        self.pub = self.create_publisher(Twist, topic, 10)
        self.t0 = time.monotonic()
        self.timer = self.create_timer(1.0 / max(self.hz, 1.0), self.tick)
        self.get_logger().info(
            f"KEY source={source} topic={topic} "
            f"linear.x={self.twist.linear.x:.3f} "
            f"linear.y={self.twist.linear.y:.3f} "
            f"angular.z={self.twist.angular.z:.3f}"
        )

    def tick(self) -> None:
        if time.monotonic() - self.t0 > self.run_sec:
            self.get_logger().info("key_twist complete - exiting")
            raise SystemExit(0)
        self.pub.publish(self.twist)


def main() -> None:
    rclpy.init()
    node = KeyTwist()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
