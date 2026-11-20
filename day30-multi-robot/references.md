# Day 30 — References

## Primary

1. **ROS 2 Topic and Service Name Mapping (Namespaces vs Leading Slashes)**  
   https://design.ros2.org/articles/topic_and_service_names.html  
   Relative names (`cmd_vel`, `odom`, `goal`) expand under the node's namespace (`/r1/cmd_vel`). Fully qualified names starting with `/` (`/cmd_vel`) ignore the namespace completely.

2. **ROS 2 Humble Launch & Remapping (`__ns`)**  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html  
   `launch/fleet.launch.py` spawns three identical copies of `robot_base.py` and `robot_controller.py` differentiated only by `-r __ns:=/rN` and `robot_id`.

3. **Nav2 Multi-Robot Bringup Patterns**  
   https://docs.nav2.org/tutorials/docs/navigation2_with_multiple_robots.html  
   Each robot runs an isolated navigation stack inside its own namespace with distinct frame identities (or remapped `/tf` and `/tf_static`), while fleet-level task dispatch sits above individual navigators.

4. **TF2 Frame Naming in Multi-Robot Systems**  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Introduction-To-Tf2.html  
   Frame IDs live inside message strings (`header.frame_id`, `child_frame_id`), so ROS topic namespaces do not rewrite them automatically; explicit per-robot frame names (`r1/base_link`, `r2/base_link`, `r3/base_link`) or namespaced `/tf` remaps are required.

## This machine

- Ubuntu 22.04 LTS, ROS 2 Humble, Fast DDS (`rmw_fastrtps_cpp`)
- `ROS_DOMAIN_ID=224`

## Related days across the series

- Day 01 — DDS discovery connects every matching topic name on the same domain
- Day 10 — Launch files and remapping
- Day 12 — TF2 coordinate frames (`map`, `odom`, `base_link`)
- Day 21 & Day 26 — Single-robot navigation pipeline and mission coordinator
