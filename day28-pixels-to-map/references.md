# Day 28 — References

## Primary

1. **REP-105 — Coordinate Frames for Mobile Platforms**  
   https://www.ros.org/reps/rep-0105.html  
   `map` → `odom` → `base_link`. A detection must end in a frame Nav2 already uses. This day lands the point in `map`.

2. **TF2 — ROS 2 Humble**  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html  
   TF2 stores timed transforms between frames. Pixel geometry gives a point in `camera_optical`. TF2 renames it into `base_link` and then `map`.

3. **image_geometry / camera_info**  
   Camera intrinsics (`fx`, `fy`, `cx`, `cy`) turn a pixel and a depth into a 3D ray in the optical frame. This day's script uses that pinhole step explicitly.

## This repository

- Day 12 — named `base_link`, `odom`, and `map`.
- Day 27 — puts a detector on a ROS image topic. This day asks what that pixel becomes for navigation.

## Limit

No live YOLO, no depth camera, and no Nav2 goal in this folder. The four cases fix the geometry so each missing piece shows up as a measured map error.
