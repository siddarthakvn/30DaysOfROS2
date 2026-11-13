# C — TF puts the pin on the box

## Hypothesis

The same camera point, transformed by `map → camera_optical_frame`, lands on the surveyed box.

## Method

`scene`, `ray`, and `placer` with `mode:=map`. `placer` looks up the transform and publishes `/point_map` and `/goal` in `map`. The goal stamp is the pixel stamp.

## Result

```text
SUMMARY node=ray u=276.522 v=250.870 depth_m=2.300000 cam_x=-0.200000 cam_y=0.050000 cam_z=2.300000 frame=camera_optical_frame
SUMMARY node=placer mode=map used_tf=1 frame=map x=3.500000 y=2.200000 z=0.250000 target_x=3.500000 target_y=2.200000 target_z=0.250000 error_m=0.000000 cam_in_map_x=1.200000 cam_in_map_y=2.000000 cam_in_map_z=0.300000 goal=1
```

The echoed goal:

```text
frame_id: map
position:
  x: 3.5
  y: 2.2
  z: 0.24999999999999994
```

That stamp is `sec: 1794543239`, `nanosec: 32370236`, the same stamp as `/pixel` and `/point_camera`.

`tf2_echo map camera_optical_frame`:

```text
- Translation: [1.200, 2.000, 0.300]
- Rotation: in Quaternion (xyzw) [-0.500, 0.500, -0.500, 0.500]
- Rotation: in RPY (degree) [-90.000, -0.000, -90.000]
```

## Conclusion

The camera origin is at `(1.200, 2.000, 0.300)` in the map. After that transform the goal is the box. The node reports `error_m=0.000000`. The echoed `z` prints `0.24999999999999994`, the same point at this precision.

This is a round trip through a defined camera and a defined TF tree. The depth was given. No detector ran, and Nav2 was not asked to drive.
