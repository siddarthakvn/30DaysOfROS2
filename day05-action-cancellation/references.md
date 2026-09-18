# References — Day 05 (Action Cancellation)

Official / primary sources (Humble-first).

| Resource | URL |
|---|---|
| About Actions | https://docs.ros.org/en/humble/Concepts/Basic/About-Actions.html |
| Understanding actions (CLI / turtlesim) | https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Actions/Understanding-ROS2-Actions.html |
| Writing an action server/client (Python) | https://docs.ros.org/en/humble/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html |
| Writing an action server/client (C++) | https://docs.ros.org/en/humble/Tutorials/Intermediate/Writing-an-Action-Server-Client/Cpp.html |
| ROS 2 Actions design | https://design.ros2.org/articles/actions.html |
| `GoalStatus.msg` | https://github.com/ros2/rcl_interfaces/blob/humble/action_msgs/msg/GoalStatus.msg |
| `CancelGoal.srv` | https://github.com/ros2/rcl_interfaces/blob/humble/action_msgs/srv/CancelGoal.srv |
| rclpy minimal cancel client example | https://github.com/ros2/examples/blob/humble/rclpy/actions/minimal_action_client/examples_rclpy_minimal_action_client/client_cancel.py |
| rclpy minimal action server example | https://github.com/ros2/examples/blob/humble/rclpy/actions/minimal_action_server/examples_rclpy_minimal_action_server/server.py |
| Nav2 Simple Commander (`cancelTask`) | https://docs.nav2.org/configuration_and_development/simple_commander_api/simple_commander_api.html |

## Key facts used this day

- An Action is Goal + Result + Feedback, implemented as 3 services + 2 topics under `/_action/`.
- Cancel is two-phase: CancelGoal accept → `CANCELING` → execute honors cancel → `CANCELED`.
- rclpy default cancel callback rejects cancels; servers must opt in.
- Cancel ≠ preempt (new goal often → `ABORTED`); cancel ≠ killing the client node.

## Day 04 bridge

See `day04-communication-patterns/` for Topic vs Service vs Action contrast (turtlesim).
