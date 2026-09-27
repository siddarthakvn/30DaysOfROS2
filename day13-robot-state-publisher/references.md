# Day 13 — References

## Primary

1. **robot_state_publisher** (Humble README)  
   https://github.com/ros/robot_state_publisher/blob/humble/README.md  
   - URDF at startup + `/joint_states` → tf2  
   - Fixed joints: `/tf_static`, transient local, once  
   - Movable joints: `/tf` when joint states update  
   - `robot_description` must be set or the node fails to start

2. **joint_state_publisher** (Humble README)  
   https://github.com/ros/joint_state_publisher/blob/humble/joint_state_publisher/README.md  
   - Publishes `sensor_msgs/JointState` for movable joints  
   - Does not publish TF  
   - Used when encoders are absent so RSP still has angles

3. **Using URDF with robot_state_publisher** (Humble)  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Using-URDF-with-Robot-State-Publisher.html

## This machine

`ros-humble-joint-state-publisher` is not installed. `ros2_nodes/joint_angles.py` is a stand-in that only publishes `/joint_states`.

## Related series days

- Day 11 — the URDF blueprint
- Day 12 — `map` → `odom` → `base_link` (different publishers)
- Day 14+ — sim and teleop assume this tree exists
