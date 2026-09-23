#!/usr/bin/env python3
"""Day 10 — sensors subsystem launch (camera / lidar / imu stubs)."""

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration


def _ns_arg(ns: str) -> str:
    return f"__ns:={ns}" if ns.startswith("/") else f"__ns:=/{ns}"


def _launch_setup(context, *args, **kwargs):
    nodes_dir = Path(__file__).resolve().parent.parent / "ros2_nodes"
    config = Path(__file__).resolve().parent.parent / "config" / "robot_params.yaml"
    ns = LaunchConfiguration("namespace").perform(context)
    use_camera = LaunchConfiguration("use_camera").perform(context).lower() in (
        "true",
        "1",
        "yes",
    )

    def sensor(label: str, topic: str, node_name: str) -> ExecuteProcess:
        return ExecuteProcess(
            cmd=[
                "python3",
                str(nodes_dir / "sensor_stub.py"),
                "--ros-args",
                "-r",
                f"__node:={node_name}",
                "-r",
                _ns_arg(ns),
                "--params-file",
                str(config),
                "-p",
                f"label:={label}",
                "-p",
                f"topic:={topic}",
            ],
            output="screen",
            name=f"start_{node_name}",
        )

    actions = [
        sensor("lidar", "scan", "lidar_stub"),
        sensor("imu", "imu", "imu_stub"),
    ]
    if use_camera:
        actions.append(sensor("camera", "image", "camera_stub"))
    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("namespace", default_value="robot1"),
            DeclareLaunchArgument(
                "use_camera",
                default_value="true",
                description="If true, start camera_stub",
            ),
            OpaqueFunction(function=_launch_setup),
        ]
    )
