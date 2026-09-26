#!/usr/bin/env python3
"""
Day 12 — Probe: robot pose + a 'nose' point 1 m ahead in base_link,
expressed in odom and map. Measures continuity (max step) per frame.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.duration import Duration
from rclpy.node import Node
from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, TransformException, TransformListener


@dataclass
class Series:
    xs: list[float] = field(default_factory=list)
    ys: list[float] = field(default_factory=list)

    def add(self, x: float, y: float) -> None:
        self.xs.append(x)
        self.ys.append(y)

    def max_step(self) -> float:
        if len(self.xs) < 2:
            return 0.0
        best = 0.0
        for i in range(1, len(self.xs)):
            dx = self.xs[i] - self.xs[i - 1]
            dy = self.ys[i] - self.ys[i - 1]
            best = max(best, math.hypot(dx, dy))
        return best

    def last(self) -> tuple[float, float] | None:
        if not self.xs:
            return None
        return self.xs[-1], self.ys[-1]


class FrameProbe(Node):
    def __init__(self) -> None:
        super().__init__("frame_probe")
        self.declare_parameter("hz", 10.0)
        self.declare_parameter("run_sec", 11.0)
        self.declare_parameter("require_map", False)
        self.declare_parameter("kitchen_x", 5.0)  # fixed landmark in map
        self.declare_parameter("kitchen_y", 0.0)

        self.hz = float(self.get_parameter("hz").value)
        self.run_sec = float(self.get_parameter("run_sec").value)
        self.require_map = bool(self.get_parameter("require_map").value)
        self.kitchen_x = float(self.get_parameter("kitchen_x").value)
        self.kitchen_y = float(self.get_parameter("kitchen_y").value)

        self.buf = Buffer(cache_time=Duration(seconds=30.0))
        self.listener = TransformListener(self.buf, self)

        self.odom_robot = Series()
        self.map_robot = Series()
        self.odom_nose = Series()
        self.map_nose = Series()
        self.kitchen_in_base = Series()

        self.map_ok_count = 0
        self.odom_ok_count = 0
        self.map_fail_count = 0

        self.t0 = self.get_clock().now()
        self.timer = self.create_timer(1.0 / max(self.hz, 1.0), self.tick)
        self.get_logger().info(
            f"frame_probe require_map={self.require_map} "
            f"kitchen=({self.kitchen_x},{self.kitchen_y})"
        )

    def _lookup_xy(self, target: str, source: str) -> tuple[float, float] | None:
        try:
            t = self.buf.lookup_transform(target, source, rclpy.time.Time())
            return t.transform.translation.x, t.transform.translation.y
        except TransformException:
            return None

    def _nose_in(self, target: str) -> tuple[float, float] | None:
        """1 m forward of base_link, expressed in target frame."""
        try:
            tf = self.buf.lookup_transform(target, "base_link", rclpy.time.Time())
        except TransformException:
            return None
        pt = PointStamped()
        pt.header.frame_id = "base_link"
        pt.header.stamp = tf.header.stamp
        pt.point.x = 1.0
        pt.point.y = 0.0
        pt.point.z = 0.0
        out = do_transform_point(pt, tf)
        return out.point.x, out.point.y

    def tick(self) -> None:
        now = self.get_clock().now()
        elapsed = (now - self.t0).nanoseconds * 1e-9
        if elapsed > self.run_sec:
            self._summary()
            raise SystemExit(0)

        odom_xy = self._lookup_xy("odom", "base_link")
        if odom_xy:
            self.odom_ok_count += 1
            self.odom_robot.add(*odom_xy)
            nose = self._nose_in("odom")
            if nose:
                self.odom_nose.add(*nose)

        map_xy = self._lookup_xy("map", "base_link")
        if map_xy:
            self.map_ok_count += 1
            self.map_robot.add(*map_xy)
            nose = self._nose_in("map")
            if nose:
                self.map_nose.add(*nose)
        else:
            self.map_fail_count += 1

        # Fixed kitchen (map) → where is it relative to the robot body?
        try:
            tf = self.buf.lookup_transform("base_link", "map", rclpy.time.Time())
            pt = PointStamped()
            pt.header.frame_id = "map"
            pt.header.stamp = tf.header.stamp
            pt.point.x = self.kitchen_x
            pt.point.y = self.kitchen_y
            pt.point.z = 0.0
            out = do_transform_point(pt, tf)
            self.kitchen_in_base.add(out.point.x, out.point.y)
        except TransformException:
            pass

        if int(elapsed) != int(elapsed - 1.0 / max(self.hz, 1.0)):
            msg = f"t={elapsed:5.2f}s"
            if odom_xy:
                msg += f"  odom_robot=({odom_xy[0]:+.3f},{odom_xy[1]:+.3f})"
            if map_xy:
                msg += f"  map_robot=({map_xy[0]:+.3f},{map_xy[1]:+.3f})"
            elif self.require_map:
                msg += "  map_robot=MISSING"
            self.get_logger().info(msg)

    def _summary(self) -> None:
        lines = [
            "==== SUMMARY ====",
            f"odom_samples={self.odom_ok_count}  map_samples={self.map_ok_count}  "
            f"map_misses={self.map_fail_count}",
            f"odom_robot_max_step_m={self.odom_robot.max_step():.4f}",
            f"map_robot_max_step_m={self.map_robot.max_step():.4f}",
            f"odom_nose_max_step_m={self.odom_nose.max_step():.4f}",
            f"map_nose_max_step_m={self.map_nose.max_step():.4f}",
            f"kitchen_in_base_max_step_m={self.kitchen_in_base.max_step():.4f}",
        ]
        o_last = self.odom_robot.last()
        m_last = self.map_robot.last()
        k_last = self.kitchen_in_base.last()
        if o_last:
            lines.append(f"odom_robot_final=({o_last[0]:+.3f},{o_last[1]:+.3f})")
        if m_last:
            lines.append(f"map_robot_final=({m_last[0]:+.3f},{m_last[1]:+.3f})")
        if k_last:
            lines.append(f"kitchen_in_base_final=({k_last[0]:+.3f},{k_last[1]:+.3f})")
        lines.append("==== END SUMMARY ====")
        for line in lines:
            self.get_logger().info(line)


def main() -> None:
    rclpy.init()
    node = FrameProbe()
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
