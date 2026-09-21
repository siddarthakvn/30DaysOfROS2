#!/usr/bin/env python3
"""
Day 08 — Busy robot node (IMU + control + slow LiDAR callback).

Proves what happens when one callback blocks, under:
  - SingleThreadedExecutor
  - MultiThreadedExecutor + shared MutuallyExclusive group
  - MultiThreadedExecutor + separate MutuallyExclusive groups

Key metrics printed in SUMMARY:
  - IMU / control periods and max gaps
  - how many fast callbacks ran *during* an active LiDAR block
  - observed concurrent callback count

Usage:
  python3 busy_robot_node.py --ros-args \\
    -p executor:=single -p group_mode:=default \\
    -p lidar_block_ms:=500 -p run_sec:=8.0
"""

from __future__ import annotations

import statistics
import threading
import time
from typing import List, Optional

import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import (
    ExternalShutdownException,
    MultiThreadedExecutor,
    SingleThreadedExecutor,
)
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Int32


class BusyRobotNode(Node):
    def __init__(self) -> None:
        super().__init__("busy_robot")

        self.declare_parameter("executor", "single")  # single | multi
        self.declare_parameter("num_threads", 4)
        self.declare_parameter("group_mode", "default")
        # default | shared_mutex | separate_mutex | reentrant
        self.declare_parameter("imu_period_ms", 10)
        self.declare_parameter("control_period_ms", 20)
        self.declare_parameter("lidar_block_ms", 500)
        self.declare_parameter("run_sec", 8.0)
        self.declare_parameter("topic", "/day08/lidar")
        self.declare_parameter("depth", 10)

        self._executor_name = str(self.get_parameter("executor").value).lower()
        self._num_threads = int(self.get_parameter("num_threads").value)
        self._group_mode = str(self.get_parameter("group_mode").value).lower()
        self._imu_period_ms = int(self.get_parameter("imu_period_ms").value)
        self._control_period_ms = int(self.get_parameter("control_period_ms").value)
        self._lidar_block_ms = int(self.get_parameter("lidar_block_ms").value)
        self._run_sec = float(self.get_parameter("run_sec").value)
        topic = str(self.get_parameter("topic").value)
        depth = int(self.get_parameter("depth").value)

        self._imu_group, self._control_group, self._lidar_group = self._make_groups()

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=depth,
            reliability=ReliabilityPolicy.RELIABLE,
        )

        self.create_timer(
            self._imu_period_ms / 1000.0,
            self._on_imu,
            callback_group=self._imu_group,
        )
        self.create_timer(
            self._control_period_ms / 1000.0,
            self._on_control,
            callback_group=self._control_group,
        )
        self.create_subscription(
            Int32,
            topic,
            self._on_lidar,
            qos,
            callback_group=self._lidar_group,
        )

        self._lock = threading.Lock()
        self._lidar_busy = False
        self._active = 0
        self._max_concurrent = 0

        self._imu_times: List[float] = []
        self._control_times: List[float] = []
        self._imu_during_lidar = 0
        self._control_during_lidar = 0
        self._lidar_blocks = 0
        self._lidar_durations_ms: List[float] = []

        self._done = threading.Event()
        self.create_timer(self._run_sec, self._on_stop)

        self.get_logger().info(
            f"CONFIG executor={self._executor_name} threads={self._num_threads} "
            f"group_mode={self._group_mode} imu={self._imu_period_ms}ms "
            f"control={self._control_period_ms}ms lidar_block={self._lidar_block_ms}ms "
            f"run={self._run_sec}s topic={topic}"
        )

    def _make_groups(self):
        mode = self._group_mode
        if mode == "default":
            # All entities use the node's default MutuallyExclusive group.
            return None, None, None
        if mode == "shared_mutex":
            g = MutuallyExclusiveCallbackGroup()
            return g, g, g
        if mode == "separate_mutex":
            return (
                MutuallyExclusiveCallbackGroup(),
                MutuallyExclusiveCallbackGroup(),
                MutuallyExclusiveCallbackGroup(),
            )
        if mode == "reentrant":
            g = ReentrantCallbackGroup()
            return g, g, g
        raise ValueError(
            f"Unknown group_mode={mode!r}. "
            "Use default|shared_mutex|separate_mutex|reentrant"
        )

    def _enter(self) -> None:
        with self._lock:
            self._active += 1
            if self._active > self._max_concurrent:
                self._max_concurrent = self._active

    def _leave(self) -> None:
        with self._lock:
            self._active -= 1

    def _on_imu(self) -> None:
        self._enter()
        try:
            now = time.monotonic()
            with self._lock:
                busy = self._lidar_busy
                self._imu_times.append(now)
                if busy:
                    self._imu_during_lidar += 1
        finally:
            self._leave()

    def _on_control(self) -> None:
        self._enter()
        try:
            now = time.monotonic()
            with self._lock:
                busy = self._lidar_busy
                self._control_times.append(now)
                if busy:
                    self._control_during_lidar += 1
        finally:
            self._leave()

    def _on_lidar(self, msg: Int32) -> None:
        self._enter()
        try:
            with self._lock:
                self._lidar_busy = True
                self._lidar_blocks += 1
                block_id = self._lidar_blocks
            scan = int(msg.data)
            self.get_logger().info(
                f"LIDAR START scan={scan} block={block_id} sleep_ms={self._lidar_block_ms}"
            )
            t0 = time.monotonic()
            time.sleep(self._lidar_block_ms / 1000.0)
            dt_ms = (time.monotonic() - t0) * 1000.0
            with self._lock:
                self._lidar_durations_ms.append(dt_ms)
                self._lidar_busy = False
            self.get_logger().info(
                f"LIDAR END   scan={scan} block={block_id} duration_ms={dt_ms:.1f}"
            )
        finally:
            self._leave()

    def _on_stop(self) -> None:
        if not self._done.is_set():
            self._done.set()

    @staticmethod
    def _gaps_ms(times: List[float]) -> List[float]:
        if len(times) < 2:
            return []
        return [(times[i] - times[i - 1]) * 1000.0 for i in range(1, len(times))]

    def print_summary(self) -> None:
        imu_gaps = self._gaps_ms(self._imu_times)
        ctl_gaps = self._gaps_ms(self._control_times)

        def fmt_stats(gaps: List[float], nominal_ms: int) -> str:
            if not gaps:
                return "n=0"
            return (
                f"n={len(gaps)+1} median_gap_ms={statistics.median(gaps):.1f} "
                f"max_gap_ms={max(gaps):.1f} "
                f"missed_gt_2x={sum(1 for g in gaps if g > 2 * nominal_ms)}"
            )

        lidar_dur = (
            f"avg_ms={statistics.mean(self._lidar_durations_ms):.1f}"
            if self._lidar_durations_ms
            else "none"
        )

        lines = [
            "==== SUMMARY ====",
            (
                f"CONFIG executor={self._executor_name} threads={self._num_threads} "
                f"group_mode={self._group_mode}"
            ),
            f"LIDAR blocks={self._lidar_blocks} duration={lidar_dur}",
            f"IMU {fmt_stats(imu_gaps, self._imu_period_ms)} "
            f"during_lidar={self._imu_during_lidar}",
            f"CONTROL {fmt_stats(ctl_gaps, self._control_period_ms)} "
            f"during_lidar={self._control_during_lidar}",
            f"CONCURRENCY max_active_callbacks={self._max_concurrent}",
            "==== END SUMMARY ====",
        ]
        for line in lines:
            self.get_logger().info(line)
            print(line, flush=True)


def build_executor(node: BusyRobotNode):
    name = node._executor_name
    if name == "single":
        return SingleThreadedExecutor()
    if name == "multi":
        return MultiThreadedExecutor(num_threads=node._num_threads)
    raise ValueError(f"Unknown executor={name!r}. Use single|multi")


def main() -> None:
    rclpy.init()
    node = BusyRobotNode()
    executor = build_executor(node)
    executor.add_node(node)

    try:
        # Spin until the stop timer fires, then drain briefly for in-flight work.
        while rclpy.ok() and not node._done.is_set():
            executor.spin_once(timeout_sec=0.05)
        # Allow any in-flight MultiThreaded callbacks to finish logging.
        deadline = time.monotonic() + (node._lidar_block_ms / 1000.0) + 0.5
        while rclpy.ok() and time.monotonic() < deadline:
            executor.spin_once(timeout_sec=0.05)
            with node._lock:
                busy = node._lidar_busy
                active = node._active
            if not busy and active == 0:
                break
        node.print_summary()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        # Tear down without blocking forever on executor worker threads.
        try:
            executor.remove_node(node)
        except Exception:
            pass
        try:
            executor.shutdown(timeout_sec=1.0)
        except TypeError:
            # Older signature without timeout.
            try:
                executor.shutdown()
            except Exception:
                pass
        except Exception:
            pass
        try:
            node.destroy_node()
        except Exception:
            pass
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
