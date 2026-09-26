#!/usr/bin/env python3
"""
Day 12 Investigation C — Wrong tree: publish map → base_link WHILE
odom → base_link already exists (dual parent). REP-105 forbids this.
"""
from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import Buffer, TransformBroadcaster, TransformException, TransformListener
from rclpy.duration import Duration


def yaw_to_quat(yaw: float) -> tuple[float, float, float, float]:
    half = 0.5 * yaw
    return (0.0, 0.0, math.sin(half), math.cos(half))


class ConflictDemo(Node):
    def __init__(self) -> None:
        super().__init__("conflict_demo")
        self.declare_parameter("run_sec", 6.0)
        self.declare_parameter("hz", 20.0)
        self.run_sec = float(self.get_parameter("run_sec").value)
        self.hz = float(self.get_parameter("hz").value)

        self.br = TransformBroadcaster(self)
        self.buf = Buffer(cache_time=Duration(seconds=10.0))
        self.listener = TransformListener(self.buf, self)

        self.x = 0.0
        self.t0 = self.get_clock().now()
        self.phase = "odom_only"
        self.conflict_started = False
        self.lookup_ok = 0
        self.lookup_fail = 0
        self.timer = self.create_timer(1.0 / max(self.hz, 1.0), self.tick)
        self.get_logger().warn(
            "conflict_demo: will publish BOTH map->base_link AND odom->base_link"
        )

    def _send(self, parent: str, child: str, x: float, y: float = 0.0, yaw: float = 0.0) -> None:
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = parent
        t.child_frame_id = child
        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.translation.z = 0.0
        qx, qy, qz, qw = yaw_to_quat(yaw)
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.br.sendTransform(t)

    def tick(self) -> None:
        now = self.get_clock().now()
        elapsed = (now - self.t0).nanoseconds * 1e-9
        if elapsed > self.run_sec:
            self._summary()
            raise SystemExit(0)

        # Always publish continuous odom -> base_link
        self.x = 0.2 * elapsed
        self._send("odom", "base_link", self.x)

        # After 2s, ALSO publish map -> base_link (illegal second parent)
        if elapsed >= 2.0:
            if not self.conflict_started:
                self.conflict_started = True
                self.phase = "dual_parent"
                self.get_logger().error(
                    "ILLEGAL: adding map->base_link while odom->base_link exists"
                )
            # Different pose on purpose — fights the odom edge
            self._send("map", "base_link", 10.0, 5.0, 0.5)

        # Probe lookups
        for target in ("odom", "map"):
            try:
                self.buf.lookup_transform(target, "base_link", rclpy.time.Time())
                self.lookup_ok += 1
            except TransformException as exc:
                self.lookup_fail += 1
                if self.lookup_fail <= 5 or int(elapsed * 2) % 4 == 0:
                    self.get_logger().warn(f"lookup {target}->base_link FAILED: {exc}")

        # Can we still form map -> odom -> base_link? (no map->odom published)
        try:
            self.buf.lookup_transform("map", "odom", rclpy.time.Time())
            map_odom = "YES"
        except TransformException:
            map_odom = "NO"

        if int(elapsed) != int(elapsed - 1.0 / max(self.hz, 1.0)):
            self.get_logger().info(
                f"t={elapsed:.1f}s phase={self.phase} map->odom_edge={map_odom} "
                f"ok={self.lookup_ok} fail={self.lookup_fail}"
            )

    def _summary(self) -> None:
        lines = [
            "==== SUMMARY ====",
            "scenario=dual_parent_conflict",
            f"phase_final={self.phase}",
            f"lookup_ok={self.lookup_ok}",
            f"lookup_fail={self.lookup_fail}",
            "note=REP-105 requires map->odom->base_link (one parent per frame)",
            "==== END SUMMARY ====",
        ]
        for line in lines:
            self.get_logger().info(line)


def main() -> None:
    rclpy.init()
    node = ConflictDemo()
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
