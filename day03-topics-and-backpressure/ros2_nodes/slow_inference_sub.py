#!/usr/bin/env python3
"""
Day 03 — Slow inference / perception stand-in.

Subscribes to /perception/frames, sleeps process_ms per callback (fake compute),
and logs frame gaps + age versus a depth-1 frontier watcher on the same topic.

The frontier subscription is KEEP_LAST depth=1 (same reliability). It never sleeps.
It runs on a separate callback group + MultiThreadedExecutor thread so it can
update while the slow path is blocked in time.sleep (stand-in for heavy inference).

Usage:
  python3 slow_inference_sub.py --ros-args \\
    -p process_ms:=100 -p depth:=10 -p reliability:=reliable
"""

from __future__ import annotations

import time

import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Int32

from qos_utils import build_qos


class SlowInferenceSub(Node):
    def __init__(self) -> None:
        super().__init__("slow_inference")

        self.declare_parameter("process_ms", 100)
        self.declare_parameter("depth", 10)
        self.declare_parameter("reliability", "reliable")
        self.declare_parameter("topic", "/perception/frames")
        self.declare_parameter("enable_frontier", True)

        self._process_ms = int(self.get_parameter("process_ms").value)
        depth = int(self.get_parameter("depth").value)
        reliability = str(self.get_parameter("reliability").value)
        topic = str(self.get_parameter("topic").value)
        enable_frontier = bool(self.get_parameter("enable_frontier").value)

        if self._process_ms < 0:
            raise ValueError(f"process_ms must be >= 0, got {self._process_ms}")

        self._slow_group = MutuallyExclusiveCallbackGroup()
        self._frontier_group = MutuallyExclusiveCallbackGroup()

        qos = build_qos(depth, reliability)
        self.create_subscription(
            Int32,
            topic,
            self._on_frame,
            qos,
            callback_group=self._slow_group,
        )

        self._live_seq = 0
        self._frontier_enabled = enable_frontier
        if enable_frontier:
            frontier_qos = build_qos(1, reliability)
            self.create_subscription(
                Int32,
                topic,
                self._on_frontier,
                frontier_qos,
                callback_group=self._frontier_group,
            )

        self._last_processed: int | None = None
        self._processed_count = 0
        self._gap_total = 0
        self._window_start = time.monotonic()
        self._window_processed = 0
        self._age_sum = 0
        self._age_max = 0

        self.get_logger().info(
            f"Processing {topic} with process_ms={self._process_ms} | "
            f"KEEP_LAST depth={depth} reliability={reliability} | "
            f"frontier_watch={'on' if enable_frontier else 'off'} | "
            f"executor=MultiThreaded(2)"
        )

    def _on_frontier(self, msg: Int32) -> None:
        # Depth-1 watcher: stay near the live frontier; never sleep here.
        if msg.data > self._live_seq:
            self._live_seq = msg.data

    def _on_frame(self, msg: Int32) -> None:
        frame_id = int(msg.data)
        gap = 0
        if self._last_processed is not None:
            gap = frame_id - self._last_processed - 1
            if gap < 0:
                self.get_logger().warn(
                    f"non-monotonic frame: last={self._last_processed} got={frame_id}"
                )
                gap = 0
            self._gap_total += gap

        # Snapshot live frontier before sleeping (and again after for reporting).
        live_before = max(self._live_seq, frame_id)
        age_before = max(0, live_before - frame_id)

        time.sleep(self._process_ms / 1000.0)

        live_after = max(self._live_seq, frame_id)
        age_after = max(0, live_after - frame_id)

        self._last_processed = frame_id
        self._processed_count += 1
        self._window_processed += 1
        self._age_sum += age_after
        self._age_max = max(self._age_max, age_after)

        self.get_logger().info(
            f"PROC frame={frame_id}  gap={gap}  "
            f"age_frames={age_after} (pre_sleep_age={age_before})  "
            f"live={live_after}  process_ms={self._process_ms}"
        )

        now = time.monotonic()
        elapsed = now - self._window_start
        if elapsed >= 1.0:
            rate = self._window_processed / elapsed
            avg_age = self._age_sum / max(1, self._window_processed)
            self.get_logger().info(
                f"STATS process_hz={rate:.1f}  "
                f"avg_age_frames={avg_age:.1f}  max_age_frames={self._age_max}  "
                f"gaps_cumulative={self._gap_total}  processed_total={self._processed_count}"
            )
            self._window_start = now
            self._window_processed = 0
            self._age_sum = 0
            self._age_max = 0


def main() -> None:
    rclpy.init()
    node = SlowInferenceSub()
    # Two threads: slow inference can block one while frontier updates on the other.
    executor = MultiThreadedExecutor(num_threads=2)
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
