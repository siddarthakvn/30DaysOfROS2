#!/usr/bin/env python3
"""Launch robot_state_publisher (+ optional joint_demo) from a URDF/Xacro path."""
from __future__ import annotations

import os
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _expand_description(model_path: Path) -> str:
    if model_path.suffix == ".xacro" or model_path.name.endswith(".urdf.xacro"):
        import subprocess

        return subprocess.check_output(
            ["xacro", str(model_path)],
            cwd=str(model_path.parent),
            text=True,
        )
    return model_path.read_text(encoding="utf-8")


def _launch_setup(context, *args, **kwargs):
    root = Path(__file__).resolve().parents[1]
    model_path = (root / LaunchConfiguration("model").perform(context)).resolve()
    if not model_path.is_file():
        raise FileNotFoundError(f"model not found: {model_path}")

    robot_description = _expand_description(model_path)
    use_joint_demo = LaunchConfiguration("use_joint_demo").perform(context).lower()
    joint_mode = LaunchConfiguration("joint_mode").perform(context)
    joints = LaunchConfiguration("joints").perform(context)
    positions = LaunchConfiguration("positions").perform(context)
    run_sec = LaunchConfiguration("run_sec").perform(context)

    nodes = [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[
                {
                    "robot_description": robot_description,
                    "use_sim_time": False,
                    "ignore_timestamp": True,
                }
            ],
        )
    ]

    if use_joint_demo in ("1", "true", "yes"):
        nodes.append(
            ExecuteProcess(
                cmd=[
                    "python3",
                    str(root / "ros2_nodes" / "joint_demo.py"),
                    "--ros-args",
                    "-p",
                    f"mode:={joint_mode}",
                    "-p",
                    f"joints:={joints}",
                    "-p",
                    f"positions:={positions}",
                    "-p",
                    f"run_sec:={run_sec}",
                ],
                output="screen",
                additional_env={
                    "ROS_DOMAIN_ID": os.environ.get("ROS_DOMAIN_ID", "110"),
                    "RMW_IMPLEMENTATION": os.environ.get(
                        "RMW_IMPLEMENTATION", "rmw_fastrtps_cpp"
                    ),
                    "ROS_LOG_DIR": os.environ.get("ROS_LOG_DIR", ""),
                },
            )
        )

    return nodes


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model",
                default_value="urdf/humanoid_fixed.urdf",
                description="Path relative to day11-urdf-xacro/",
            ),
            DeclareLaunchArgument("use_joint_demo", default_value="false"),
            DeclareLaunchArgument("joint_mode", default_value="pose"),
            DeclareLaunchArgument(
                "joints",
                default_value="r_shoulder,r_elbow",
            ),
            DeclareLaunchArgument(
                "positions",
                default_value="0.0,0.0",
            ),
            DeclareLaunchArgument("run_sec", default_value="8.0"),
            OpaqueFunction(function=_launch_setup),
        ]
    )
