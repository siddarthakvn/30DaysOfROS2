#!/usr/bin/env python3
"""Send one rescue target to the 3-robot fleet, freeze after the window, and print SUMMARY."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Bool, String

from fleet_spec import GOAL_TOLERANCE, ROBOTS, TARGET_XY, WINDOW_SEC, dist
from qos import latched


def _parse_kv(line: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for tok in line.strip().split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


class FleetAuditor(Node):
    def __init__(self) -> None:
        super().__init__("fleet_auditor")
        self.declare_parameter("mode", "coordinated")
        self._mode = str(self.get_parameter("mode").value)

        self._ready: set[str] = set()
        self._reports: dict[str, dict[str, str]] = {}
        self._winner = "none"
        self._phase = "wait_ready"
        self._t0: float | None = None

        self._target_pub = self.create_publisher(PoseStamped, "/fleet/target", latched())
        self._freeze_pub = self.create_publisher(Bool, "/fleet/freeze", latched())
        self._summary_pub = self.create_publisher(String, "/fleet/summary", latched())

        for rid in ROBOTS:
            self.create_subscription(
                Bool,
                f"/fleet/ready_{rid}",
                lambda msg, robot_id=rid: self._on_ready(robot_id, msg),
                latched(),
            )
            self.create_subscription(
                String,
                f"/fleet/report_{rid}",
                lambda msg, robot_id=rid: self._on_report(robot_id, msg),
                latched(),
            )
        self.create_subscription(String, "/fleet/assignment", self._on_assign, latched())
        self.create_timer(0.05, self._tick)

    def _on_ready(self, rid: str, msg: Bool) -> None:
        if msg.data:
            self._ready.add(rid)

    def _on_report(self, rid: str, msg: String) -> None:
        self._reports[rid] = _parse_kv(msg.data)

    def _on_assign(self, msg: String) -> None:
        kv = _parse_kv(msg.data)
        self._winner = kv.get("winner", "none")

    def _now(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    def _tick(self) -> None:
        now = self._now()
        if self._phase == "wait_ready":
            if len(self._ready) == len(ROBOTS):
                self._t0 = now
                self._phase = "settle"
        elif self._phase == "settle":
            assert self._t0 is not None
            if now - self._t0 >= 0.5:
                goal = PoseStamped()
                goal.header.stamp = self.get_clock().now().to_msg()
                goal.header.frame_id = "map"
                goal.pose.position.x = float(TARGET_XY[0])
                goal.pose.position.y = float(TARGET_XY[1])
                goal.pose.orientation.w = 1.0
                self._target_pub.publish(goal)
                self._t0 = now
                self._phase = "drive"
        elif self._phase == "drive":
            assert self._t0 is not None
            if now - self._t0 >= WINDOW_SEC:
                freeze = Bool()
                freeze.data = True
                self._freeze_pub.publish(freeze)
                self._phase = "wait_reports"
        elif self._phase == "wait_reports":
            if len(self._reports) == len(ROBOTS):
                self._emit_summary()
                self._phase = "done"

    def _emit_summary(self) -> None:
        poses = {
            rid: (float(self._reports[rid]["x"]), float(self._reports[rid]["y"]))
            for rid in ROBOTS
        }
        travels = {rid: float(self._reports[rid]["travel_m"]) for rid in ROBOTS}
        errs = {rid: float(self._reports[rid]["err_m"]) for rid in ROBOTS}
        cmds = {rid: int(self._reports[rid]["rx_cmds"]) for rid in ROBOTS}

        moved = sum(1 for rid in ROBOTS if travels[rid] > 0.05)
        at_target = sum(1 for rid in ROBOTS if errs[rid] <= GOAL_TOLERANCE + 0.02)
        total_travel = sum(travels.values())
        pair_dists = [
            dist(poses[a], poses[b])
            for i, a in enumerate(ROBOTS)
            for b in ROBOTS[i + 1 :]
        ]
        min_sep = min(pair_dists)

        for rid in ROBOTS:
            print(
                f"ROBOT mode={self._mode} id={rid} "
                f"pos=({poses[rid][0]:.3f},{poses[rid][1]:.3f}) "
                f"travel_m={travels[rid]:.3f} err_m={errs[rid]:.3f} "
                f"rx_cmds={cmds[rid]} frame={self._reports[rid]['frame']}",
                flush=True,
            )

        summary = (
            f"SUMMARY mode={self._mode} winner={self._winner} "
            f"moved_robots={moved} at_target={at_target} "
            f"total_travel_m={total_travel:.3f} min_pair_sep_m={min_sep:.3f} "
            f"r1_err_m={errs['r1']:.3f} r2_err_m={errs['r2']:.3f} r3_err_m={errs['r3']:.3f} "
            f"r1_cmds={cmds['r1']} r2_cmds={cmds['r2']} r3_cmds={cmds['r3']}"
        )
        msg = String()
        msg.data = summary
        self._summary_pub.publish(msg)
        print(summary, flush=True)
        print(f"READY mode={self._mode}", flush=True)


def main() -> None:
    rclpy.init()
    node = FleetAuditor()
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
