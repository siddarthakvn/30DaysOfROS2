# Day 18 — References

## Primary

1. **robot_localization state estimation nodes**  
   https://docs.ros.org/en/humble/p/robot_localization/  
   The EKF predicts between measurements and corrects when one arrives. Process noise (Q) is the uncertainty added in the prediction. The estimate covariance (P) is how unsure the current guess is. A measurement with a large variance is trusted slowly. Humble’s package is `robot_localization` 3.5.4 (`ekf_node`). It is not installed here, so this day runs the same two steps in `ros2_nodes/ekf.py`.

2. **Two absolute poses that disagree**  
   The configuring notes for `robot_localization` warn that two pose sources for the same variable, both with a small covariance that does not grow, pull the estimate back and forth. Investigation D is that warning on a single angle.

3. **REP 105 — Coordinate Frames for Mobile Platforms**  
   https://www.ros.org/reps/rep-0105.html  
   `odom` is continuous and may drift. A later map correction is allowed to jump, and it does so on `map` → `odom`, not by giving `base_link` a second parent. This day’s message is the continuous edge: `header.frame_id` `odom`, `child_frame_id` `base_link`.

4. **nav_msgs/Odometry**  
   https://docs.ros.org/en/humble/p/nav_msgs/msg/Odometry.html  
   Pose is in the header frame. Twist is in the child frame. The pose covariance is a 6×6 matrix for x, y, z, roll, pitch, yaw.

## This repository

- Day 16 — wheel rotation becomes one pose, and a wrong radius scales it. That pose is an input here.
- Day 12 — `odom` stays smooth. `map` may jump. This day fills the smooth edge only.

## Limit

The drive is scripted. There is no Gazebo, no real IMU, and no `ekf_node` process. The gyro bias is a constant 0.02 rad/s. The wheel speed is a constant 1.10 m/s. Yaw-rate noise is Gaussian with a fixed seed.
