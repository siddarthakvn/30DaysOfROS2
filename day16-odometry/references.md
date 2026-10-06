# Day 16 — References

## Primary

1. **REP-105 — Coordinate Frames for Mobile Platforms**  
   https://reps.openrobotics.org/rep-0105/  
   `odom` is a smooth, world-fixed local frame. The pose in it may drift. The transform `odom` → `base_link` comes from an odometry source. `map` is allowed to jump later. This day only builds the wheel source.

2. **nav_msgs/Odometry**  
   https://docs.ros.org/en/humble/p/nav_msgs/msg/Odometry.html  
   The pose is expressed in `header.frame_id`. The twist is expressed in `child_frame_id`. Here those are `odom` and `base_link`.

3. **Differential-drive kinematics**  
   Contact speed is wheel spin times radius. Forward speed is the average of the left and right contact speeds. Yaw rate is their difference divided by the track width. Position is that body motion added up.

## This repository

- Day 12 — why `odom` and `map` are different frames
- Day 14 — a command becomes wheel motion on the Harmonic diff-drive model (`wheel_radius` 0.3 m, `wheel_separation` 1.25 m in `diff_drive.sdf`)

## Limit

These four runs use the kinematic sum directly. They do not include wheel slip. A matching result here is not a claim that a real floor will agree.
