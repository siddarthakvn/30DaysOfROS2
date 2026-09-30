# Day 14 — References

## Primary

1. **Setting up a robot simulation (Gazebo)** — ROS 2 Humble  
   https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Gazebo/Gazebo.html  
   Official path: Twist, `ros_gz_bridge`, diff-drive model, `teleop_twist_keyboard`.  
   That page targets Gazebo Fortress (`ignition.msgs.Twist`). This day's run is Harmonic (`gz.msgs.Twist`).

2. **geometry_msgs/Twist** — Humble  
   https://docs.ros.org/en/humble/p/geometry_msgs/msg/Twist.html  
   `linear` and `angular` as `Vector3`. Units: m/s and rad/s.

3. **ros_gz_bridge**  
   https://github.com/gazebosim/ros_gz/blob/ros2/ros_gz_bridge/README.md  
   `@` bidirectional, `[` Gazebo→ROS, `]` ROS→Gazebo.

4. **Installed teleop node**  
   `/opt/ros/humble/lib/python3.10/site-packages/teleop_twist_keyboard.py`  
   `moveBindings`: `i` forward, `j` positive yaw, anything else stop. Defaults `speed=0.5`, `turn=1.0`.

5. **World used**  
   `/usr/share/gz/gz-sim8/worlds/diff_drive.sdf`  
   Documents `/model/vehicle_blue/cmd_vel` as `gz.msgs.Twist`.

## Related series days

- Day 10 — launch would start sim, bridge, and teleop together
- Day 12 — odometry may publish `odom` → `base_link` after the wheels move
- Day 16 — wheel rotation becomes a pose
