# A — A pixel is not a goal

## Hypothesis

Camera info, a pixel, and a depth can be on the graph while `/goal` still does not exist.

## Method

`scene` only. It broadcasts the TF tree, projects the surveyed box to a pixel, and publishes `/camera_info`, `/pixel`, `/depth`, and `/survey_map`. `ray` and `placer` are not started.

The box is at `(3.500, 2.200, 0.250)` m. The base is at `(1.00, 2.00, 0.00)`. The camera link is `0.20` m forward and `0.30` m up.

## Result

```text
SUMMARY node=scene u=276.522 v=250.870 depth_m=2.300000 cam_x=-0.200000 cam_y=0.050000 cam_z=2.300000 target_x=3.500 target_y=2.200 target_z=0.250 fx=500.0 fy=500.0 cx=320.0 cy=240.0 base_x=1.00 base_y=2.00 base_z=0.00 cam_dx=0.20 cam_dz=0.30 map_goal=0
```

`/pixel` echoed `x: 276.52173913043487`, `y: 250.86956521739143`, `frame_id: camera_optical_frame`. `/depth` echoed `data: 2.3`.

```text
Unknown topic '/point_camera'
Unknown topic '/point_map'
Unknown topic '/goal'
```

## Conclusion

The picture location is known. The depth is known. Nav2 still has no goal, because nothing has built a map point from them.
