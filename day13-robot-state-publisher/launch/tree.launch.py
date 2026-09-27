#!/usr/bin/env python3
"""Launch robot_state_publisher, optionally with a joint-angle source."""
from __future__ import annotations

import os
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _setup(context, *args, **kwargs):
    root = Path(__file__).resolve().parents[1]
    urdf = (root / "urdf" / "arm.urdf").read_text(encoding="utf-8")
    use_angles = LaunchConfiguration("use_joint_angles").perform(context).lower()
    shoulder = LaunchConfiguration("shoulder").perform(context)
    elbow = LaunchConfiguration("elbow").perform(context)
    run_sec = LaunchConfiguration("run_sec").perform(context)

    env = {
        "ROS_DOMAIN_ID": os.environ.get("ROS_DOMAIN_ID", "130"),
        "RMW_IMPLEMENTATION": os.environ.get("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp"),
        "ROS_LOG_DIR": os.environ.get("ROS_LOG_DIR", str(root / "assets" / ".ros_logs")),
    }

    nodes = [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[
                {
                    "robot_description": urdf,
                    "ignore_timestamp": True,
                }
            ],
        )
    ]

    if use_angles in ("1", "true", "yes"):
        nodes.append(
            ExecuteProcess(
                cmd=[
                    "python3",
                    str(root / "ros2_nodes" / "joint_angles.py"),
                    "--ros-args",
                    "-p",
                    f"shoulder:={shoulder}",
                    "-p",
                    f"elbow:={elbow}",
                    "-p",
                    f"run_sec:={run_sec}",
                ],
                output="screen",
                additional_env=env,
            )
        )
    return nodes


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_joint_angles", default_value="false"),
            DeclareLaunchArgument("shoulder", default_value="0.0"),
            DeclareLaunchArgument("elbow", default_value="0.0"),
            DeclareLaunchArgument("run_sec", default_value="10.0"),
            OpaqueFunction(function=_setup),
        ]
    )
