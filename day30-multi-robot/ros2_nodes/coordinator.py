#!/usr/bin/env python3
"""Fleet coordinator: reads /r1/odom, /r2/odom, /r3/odom and routes /fleet/target to the closest robot."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from fleet_spec import ROBOTS, dist
from qos import latched, stream


class FleetCoordinator(Node):
    def __init__(self) -> None:
        super().__init__("fleet_coordinator")
        self._poses: dict[str, tuple[float, float]] = {}
        self._target: PoseStamped | None = None
        self._assigned = False

        self._goal_pubs = {
            rid: self.create_publisher(PoseStamped, f"/{rid}/goal", latched())
            for rid in ROBOTS
        }
        self._assign_pub = self.create_publisher(String, "/fleet/assignment", latched())

        for rid in ROBOTS:
            self.create_subscription(
                Odometry,
                f"/{rid}/odom",
                lambda msg, robot_id=rid: self._on_odom(robot_id, msg),
                stream(),
            )
        self.create_subscription(PoseStamped, "/fleet/target", self._on_target, latched())
        self.create_timer(0.05, self._try_assign)

    def _on_odom(self, rid: str, msg: Odometry) -> None:
        self._poses[rid] = (
            float(msg.pose.pose.position.x),
            float(msg.pose.pose.position.y),
        )

    def _on_target(self, msg: PoseStamped) -> None:
        self._target = msg

    def _try_assign(self) -> None:
        if self._assigned or self._target is None or len(self._poses) < len(ROBOTS):
            return
        self._assigned = True
        goal_xy = (
            float(self._target.pose.position.x),
            float(self._target.pose.position.y),
        )
        costs = {rid: dist(self._poses[rid], goal_xy) for rid in ROBOTS}
        winner = min(ROBOTS, key=lambda rid: costs[rid])
        self._goal_pubs[winner].publish(self._target)

        cost_str = ",".join(f"{rid}:{costs[rid]:.3f}" for rid in ROBOTS)
        msg = String()
        msg.data = f"winner={winner} costs={cost_str}"
        self._assign_pub.publish(msg)
        print(
            f"COORDINATOR winner={winner} "
            + " ".join(f"{rid}_cost_m={costs[rid]:.3f}" for rid in ROBOTS),
            flush=True,
        )


def main() -> None:
    rclpy.init()
    node = FleetCoordinator()
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
