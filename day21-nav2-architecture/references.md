# Day 21 — References

## Primary

1. **NavigateToPose**  
   The Humble action in `nav2_msgs/action/NavigateToPose.action`. The goal field is `geometry_msgs/PoseStamped`. The result is empty. Feedback carries the current pose and the distance remaining. This day sends that action with `ros2 action send_goal`.

2. **Nav2 architecture**  
   https://docs.nav2.org/  
   `bt_navigator` accepts the goal and ticks a behavior tree. `planner_server` writes a `nav_msgs/Path`. `controller_server` writes `geometry_msgs/Twist` on `/cmd_vel`. This day runs that order in one node so each stage can be switched off.

3. **nav_msgs/Path**  
   http://docs.ros.org/en/humble/p/nav_msgs/msg/Path.html  
   A header and a sequence of poses. Published latched on `/plan`.

## This machine

- ROS 2 Humble
- `nav2_msgs` from `/opt/ros/humble`
- `ROS_DOMAIN_ID=210`

## Related days

- Day 5 — an action is a goal that can finish or be cancelled
- Day 14 — `/cmd_vel` is a body velocity, not a key and not a pose
- Day 20 — the robot already knows where it is. Today it is asked to be somewhere else
