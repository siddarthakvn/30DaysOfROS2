# Day 13 — Interview Questions

1. **Who publishes the robot's transform tree?**  
   `robot_state_publisher`. It loads the URDF and subscribes to `/joint_states`, then publishes link poses.

2. **What is the difference between `/tf` and `/tf_static`?**  
   Fixed joints go out once on `/tf_static` with transient-local durability. Moving joints go on `/tf` when joint states update.

3. **Does `joint_state_publisher` publish TF?**  
   No. It publishes angles. `robot_state_publisher` turns those angles into frames.

4. **Why can `/tf` have a publisher and the hand still be missing?**  
   Revolute edges are not filled until a `JointState` arrives. Fixed edges can already be on `/tf_static`.

5. **Does robot state publisher own `map` and `odom`?**  
   No. Odometry and localization publish those edges. RSP owns the kinematic tree from the URDF.

## One-liner

**Angles in, frames out — and only `robot_state_publisher` writes the robot tree.**
