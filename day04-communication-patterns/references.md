# References — Day 04

Official resources for **Day 04 – Topics, Services, and Actions** (Humble-first).

---

## Official ROS 2 documentation

| Topic | URL |
|---|---|
| Interfaces (topics, services, actions) | https://docs.ros.org/en/humble/Concepts/Basic/About-Interfaces.html |
| About Topics | https://docs.ros.org/en/humble/Concepts/Basic/About-Topics.html |
| About Services | https://docs.ros.org/en/humble/Concepts/Basic/About-Services.html |
| About Actions | https://docs.ros.org/en/humble/Concepts/Basic/About-Actions.html |
| Understanding actions (CLI / turtlesim) | https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Actions/Understanding-ROS2-Actions.html |
| Understanding services | https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Services/Understanding-ROS2-Services.html |
| ROS 2 Actions design | https://design.ros2.org/articles/actions.html |

Source mirrors (when docs.ros.org bot-check blocks fetch):

- https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Basic/Interfaces-Topics-Services-Actions.rst
- https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Basic/About-Services.rst

---

## Key quotes (paraphrased for study)

- Topics: continuous data streams; async one-way; many↔many.
- Services: short request/response; **never** for longer-running / preemptable work — use an action.
- Actions: long-running goal + feedback + cancel/preempt + result.
- Design: an action is implemented as **3 services + 2 topics** under `/_action/`.

---

## Commands used

```bash
source ./env.sh
ros2 daemon stop
ros2 doctor --report | grep -i rmw

ros2 run turtlesim turtlesim_node

ros2 topic info /turtle1/cmd_vel
ros2 topic echo /turtle1/pose --once

ros2 service list | grep long_rotate
ros2 service type /long_rotate

ros2 action list
ros2 action info /turtle1/rotate_absolute
ros2 action send_goal --feedback /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute "{theta: 3.14}"

python3 action_cancel_demo.py --ros-args -p theta:=3.14 -p cancel_after_sec:=1.0
```

---

## Packages

- `turtlesim` (`ros-humble-turtlesim`)
- `std_srvs` (`Trigger`)
- `geometry_msgs` (`Twist`)
- `rclpy` (+ `rclpy.action`)
