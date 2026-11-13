# B — Camera numbers labeled as the map

## Hypothesis

Back-projecting the pixel gives a point in the camera frame. Writing those meters into a message whose frame is `map` puts the goal in the wrong place.

## Method

`scene`, `ray`, and `placer` with `mode:=origin`. `ray` uses `image_geometry.projectPixelTo3dRay` and the optical-axis depth. `placer` copies that camera point into `/point_map` and `/goal` with `frame_id: map`. It does not look up TF. `used_tf=0`.

## Result

```text
SUMMARY node=ray u=276.522 v=250.870 depth_m=2.300000 cam_x=-0.200000 cam_y=0.050000 cam_z=2.300000 frame=camera_optical_frame
SUMMARY node=placer mode=origin used_tf=0 frame=map x=-0.200000 y=0.050000 z=2.300000 target_x=3.500000 target_y=2.200000 target_z=0.250000 error_m=4.744997 cam_in_map_x=0.000000 cam_in_map_y=0.000000 cam_in_map_z=0.000000 goal=1
```

The echoed `/goal` position is `x: -0.19999999999999962`, `y: 0.05000000000000056`, `z: 2.3`, `frame_id: map`. The surveyed box is `(3.500, 2.200, 0.250)`.

## Conclusion

The ray math is the same math as the projection. The frame name is wrong. The goal misses the box by `4.744997` m.
