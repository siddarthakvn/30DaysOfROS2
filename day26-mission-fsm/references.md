# Day 26 — References

## Primary

1. **Mission state as a coordinator**  
   A finite state machine here is the list of legal steps for the rescue, not the navigation checklist from Day 25. SEARCHING may call a navigator. VERIFYING checks. LOCKDOWN holds. The state, not the planner, decides which of those runs.

2. **std_msgs/String**  
   http://docs.ros.org/en/humble/p/std_msgs/msg/String.html  
   One string. Published latched on `/mission_state` with the final state of the script.

3. **Nav2 stays a tool**  
   https://docs.nav2.org/  
   `bt_navigator` still ticks plan and follow when the coordinator allows a goal. This day does not send `NavigateToPose`. It records whether that call would be allowed.

## This machine

- ROS 2 Humble
- `std_msgs` from `/opt/ros/humble`
- `ROS_DOMAIN_ID=228`

## Related days

- Day 21 — a navigation goal becomes a path, then a speed
- Day 25 — plan, follow, and recover are a behavior tree, because they are a checklist. The rescue mission is a short list of legal steps, so the coordinator is a state machine
