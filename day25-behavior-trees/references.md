# Day 25 — References

## Primary

1. **Navigate To Pose with replanning and recovery**  
   `/opt/ros/humble/share/nav2_bt_navigator/behavior_trees/navigate_to_pose_w_replanning_and_recovery.xml`  
   A `RecoveryNode` ticks a navigate sequence, and on failure ticks a `ReactiveFallback` of clear, spin, wait, and back up. This day keeps that shape and counts what an extra recovery costs.

2. **RecoveryNode**  
   https://docs.nav2.org/behavior_trees/overview/nav2_specific_nodes.html  
   The first child is the main job. If it fails, the second child runs. If that child succeeds, the first child is ticked again, up to `number_of_retries`.

3. **BehaviorTreeLog**  
   `/opt/ros/humble/share/nav2_msgs/msg/BehaviorTreeLog.msg`  
   A timestamp and a list of `BehaviorTreeStatusChange`. Each change names a node and a status of IDLE, RUNNING, SUCCESS, or FAILURE. Published latched on `/behavior_tree_log`.

4. **Behavior trees as the Nav2 checklist**  
   https://docs.nav2.org/behavior_trees/index.html  
   `bt_navigator` loads the XML and ticks it. Swapping a recovery is an edit to the tree, not a new transition out of every state in the controller.

## This machine

- ROS 2 Humble
- `nav2_msgs` from `/opt/ros/humble`
- `ROS_DOMAIN_ID=229`

## Related days

- Day 21 — after a goal, the order is plan, then speed. The tree is the checklist that calls those stages
- Day 24 — follow failed on a wide box, and one replan ran. Today that second try is a line in the list
