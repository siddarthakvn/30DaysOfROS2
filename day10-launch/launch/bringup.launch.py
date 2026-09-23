#!/usr/bin/env python3
"""
Day 10 — top-level robot bringup.

One command starts sensors (include) + control stub with remapped cmd_vel.

  ros2 launch launch/bringup.launch.py
  ros2 launch launch/bringup.launch.py namespace:=robot2 use_camera:=false
"""

from pathlib import Path

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def _ns_arg(ns: str) -> str:
    return f"__ns:={ns}" if ns.startswith("/") else f"__ns:=/{ns}"


def _control(context, *args, **kwargs):
    nodes_dir = Path(__file__).resolve().parent.parent / "ros2_nodes"
    config = Path(__file__).resolve().parent.parent / "config" / "robot_params.yaml"
    ns = LaunchConfiguration("namespace").perform(context)
    # Relative cmd_vel -> /<ns>/cmd_vel via namespace.
    # Extra remap demo: also publish a fleet-facing absolute alias.
    # (absolute left side would bypass ns; we remap relative name only.)
    return [
        ExecuteProcess(
            cmd=[
                "python3",
                str(nodes_dir / "control_stub.py"),
                "--ros-args",
                "-r",
                "__node:=control_stub",
                "-r",
                _ns_arg(ns),
                "--params-file",
                str(config),
                "-p",
                "speed:=0.25",
            ],
            output="screen",
            name="start_control_stub",
        )
    ]


def generate_launch_description():
    launch_dir = Path(__file__).resolve().parent

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "namespace",
                default_value="robot1",
                description="ROS namespace for all robot nodes",
            ),
            DeclareLaunchArgument(
                "use_camera",
                default_value="true",
                description="Start camera stub if true",
            ),
            # Modular include: sensors subsystem
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(launch_dir / "sensors.launch.py")
                ),
                launch_arguments={
                    "namespace": LaunchConfiguration("namespace"),
                    "use_camera": LaunchConfiguration("use_camera"),
                }.items(),
            ),
            # Slight delay so sensor processes appear first in logs (NOT readiness).
            TimerAction(period=0.5, actions=[OpaqueFunction(function=_control)]),
        ]
    )
