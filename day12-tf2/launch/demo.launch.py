#!/usr/bin/env python3
"""Day 12 launch — odom driver ± map localizer ± frame probe."""
from __future__ import annotations

import os
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration


def _setup(context, *args, **kwargs):
    root = Path(__file__).resolve().parents[1]
    nodes = root / "ros2_nodes"
    mode = LaunchConfiguration("mode").perform(context)  # a | b
    run_sec = LaunchConfiguration("run_sec").perform(context)
    jump_at = LaunchConfiguration("jump_at_sec").perform(context)

    env = {
        "ROS_DOMAIN_ID": os.environ.get("ROS_DOMAIN_ID", "120"),
        "RMW_IMPLEMENTATION": os.environ.get("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp"),
        "ROS_LOG_DIR": os.environ.get("ROS_LOG_DIR", str(root / "assets" / ".ros_logs")),
    }

    procs = [
        ExecuteProcess(
            cmd=[
                "python3",
                str(nodes / "odom_driver.py"),
                "--ros-args",
                "-p",
                f"run_sec:={run_sec}",
            ],
            output="screen",
            additional_env=env,
        ),
        ExecuteProcess(
            cmd=[
                "python3",
                str(nodes / "frame_probe.py"),
                "--ros-args",
                "-p",
                f"run_sec:={float(run_sec) - 1.0}",
                "-p",
                f"require_map:={'true' if mode == 'b' else 'false'}",
            ],
            output="screen",
            additional_env=env,
        ),
    ]

    if mode == "b":
        procs.insert(
            1,
            ExecuteProcess(
                cmd=[
                    "python3",
                    str(nodes / "map_localizer.py"),
                    "--ros-args",
                    "-p",
                    f"run_sec:={run_sec}",
                    "-p",
                    f"jump_at_sec:={jump_at}",
                ],
                output="screen",
                additional_env=env,
            ),
        )

    return procs


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("mode", default_value="a"),
            DeclareLaunchArgument("run_sec", default_value="12.0"),
            DeclareLaunchArgument("jump_at_sec", default_value="5.0"),
            OpaqueFunction(function=_setup),
        ]
    )
