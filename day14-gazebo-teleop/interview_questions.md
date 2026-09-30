# Day 14 — Interview Questions

1. **You press `i` in teleop. What is published?**  
   A `geometry_msgs/Twist` on `/cmd_vel`. With the default teleop parameters, `linear.x = 0.5` and `angular.z = 0`.

2. **Why doesn't Gazebo move if `ros2 topic echo /cmd_vel` shows messages?**  
   Gazebo Sim listens on Gazebo Transport, not on the ROS graph. `ros_gz_bridge` has to carry the Twist across, and a diff-drive system has to be subscribed.

3. **Which Twist fields does a diff-drive robot use?**  
   `linear.x` for forward speed and `angular.z` for yaw rate. `linear.y` does not strafe.

4. **Is `/cmd_vel` a position command?**  
   No. It is a body velocity. Zero means "commanded stop." The robot can still coast while it decelerates.

5. **Fortress tutorial vs this machine?**  
   Humble's Gazebo tutorial uses Fortress and `ignition.msgs.Twist`. This computer runs Gazebo Harmonic, so the bridge type is `gz.msgs.Twist`.

## One-liner

**The key writes a Twist. The bridge carries it. Diff-drive turns `linear.x` and `angular.z` into two wheel speeds.**
