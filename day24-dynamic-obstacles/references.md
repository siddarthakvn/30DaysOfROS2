# Day 24 — References

## Primary

1. **Navigate To Pose with replanning and recovery**  
   `/opt/ros/humble/share/nav2_bt_navigator/behavior_trees/navigate_to_pose_w_replanning_and_recovery.xml`  
   The tree computes a path, follows it, and can compute a path again. This day runs that handoff once: follow, then one new plan when the follow cannot pass.

2. **FollowPath and ComputePathToPose**  
   https://docs.nav2.org/behavior_trees/overview/nav2_specific_nodes.html  
   `FollowPath` is the controller action. `ComputePathToPose` is the global planner action. A box on the old line is a failure of the first and a new call of the second.

3. **Controller server**  
   https://docs.nav2.org/configuration/packages/configuring-controller-server.html  
   The controller tracks the global plan against the local costmap. The progress checker fails the action when the robot stops making progress. The local reach in this day is the small stand-in for that limit.

4. **Robot radius**  
   `/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml` sets `robot_radius: 0.22`. The body in this day uses that radius.

5. **nav_msgs/Path and geometry_msgs/Twist**  
   `/plan` is a latched path. `/cmd_vel` is a live body velocity. Day 21 separated those two messages. Today both are published after the box appears.

## This machine

- ROS 2 Humble
- `nav_msgs` and `geometry_msgs` from `/opt/ros/humble`
- `ROS_DOMAIN_ID=231`

Fast DDS rejects a domain id that pushes the discovery port past 65535. 231 is the domain this day uses.

## Related days

- Day 21 — a goal becomes a path, then a speed
- Day 22 — the costmap is the room the planner believes
- Day 23 — the global search draws one shortest line. Today that line is already drawn, and the floor changes
