# Day 28 — References

## Primary

1. **sensor_msgs/CameraInfo**  
   http://docs.ros.org/en/humble/p/sensor_msgs/msg/CameraInfo.html  
   `K` holds `fx`, `fy`, `cx`, `cy`. This run uses `fx = fy = 500`, principal point `(320, 240)`, and zero distortion. The header frame is `camera_optical_frame`.

2. **image_geometry.PinholeCameraModel**  
   https://docs.ros.org/en/humble/p/image_geometry/  
   `project3dToPixel` builds the pixel from the box in the optical frame. `projectPixelTo3dRay` returns a unit ray. The camera point is that ray scaled so its Z equals `/depth`.

3. **tf2**  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Introduction-To-Tf2.html  
   Static transforms: `map → base_link → camera_link → camera_optical_frame`. `placer` looks up `map` from `camera_optical_frame` and transforms the camera point. `tf2_echo` on this machine printed the optical frame at `[1.200, 2.000, 0.300]`.

4. **Optical frame**  
   https://www.ros.org/reps/rep-0103.html  
   Optical axes match the image: x right, y down, z forward. The static rotation used here is roll `-π/2`, pitch `0`, yaw `-π/2`. The echo reports that as `-90, 0, -90` degrees and quaternion `[-0.500, 0.500, -0.500, 0.500]`.

5. **geometry_msgs/PoseStamped**  
   http://docs.ros.org/en/humble/p/geometry_msgs/msg/PoseStamped.html  
   `/goal` is one latched pose in `map`. This day publishes it. It does not call `NavigateToPose`.

## This machine

- ROS 2 Humble
- `image_geometry`, `tf2_ros`, `tf2_geometry_msgs` from `/opt/ros/humble`
- `ROS_DOMAIN_ID=226`
- One-sample QoS: `RELIABLE` + `TRANSIENT_LOCAL`, depth 1

## Related days

- Day 12 — frames, including `base_link`, `odom`, and `map`
- Day 20 — a pose on a map
- Day 21 — a goal becomes a path, then a speed
- Day 27 — a detection message. The box center there was a pixel. This day uses a camera we defined, because that photo has no intrinsics and no depth
