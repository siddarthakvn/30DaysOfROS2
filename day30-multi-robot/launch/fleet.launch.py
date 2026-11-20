"""Launch three robots (r1, r2, r3) in namespaces plus the fleet auditor (and coordinator in mode=coordinated)."""

from __future__ import annotations

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration

ROOT = Path(__file__).resolve().parents[1]
NODES = ROOT / "ros2_nodes"


def _build_actions(context):
    mode = LaunchConfiguration("mode").perform(context)
    actions = []

    for rid in ("r1", "r2", "r3"):
        actions.append(
            ExecuteProcess(
                cmd=[
                    "python3",
                    "-u",
                    str(NODES / "robot_base.py"),
                    "--ros-args",
                    "-r",
                    f"__ns:=/{rid}",
                    "-p",
                    f"robot_id:={rid}",
                    "-p",
                    f"mode:={mode}",
                ],
                output="screen",
            )
        )
        actions.append(
            ExecuteProcess(
                cmd=[
                    "python3",
                    "-u",
                    str(NODES / "robot_controller.py"),
                    "--ros-args",
                    "-r",
                    f"__ns:=/{rid}",
                    "-p",
                    f"robot_id:={rid}",
                    "-p",
                    f"mode:={mode}",
                ],
                output="screen",
            )
        )

    if mode == "coordinated":
        actions.append(
            ExecuteProcess(
                cmd=["python3", "-u", str(NODES / "coordinator.py")],
                output="screen",
            )
        )

    actions.append(
        ExecuteProcess(
            cmd=[
                "python3",
                "-u",
                str(NODES / "auditor.py"),
                "--ros-args",
                "-p",
                f"mode:={mode}",
            ],
            output="screen",
        )
    )
    return actions


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="coordinated"),
        OpaqueFunction(function=_build_actions),
    ])
