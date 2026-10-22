# C — Inflation turns one cell into a disk

## Hypothesis

The same leftover cell, run through the inflation layer, becomes a disk the planner will not enter. The path bends across empty floor. The local costmap still does not contain the cell.

## Method

`mode:=inflated`.

Same remembered cell as B. Inflation then writes cost 253 out to the robot radius, 0.22 m, and a falling cost out to 0.55 m:

```text
cost = 252 * exp(-3.0 * (distance_m - 0.22))
```

That is `InflationLayer::computeCost` from Humble, with `cost_scaling_factor` 3.0. The planner refuses 253 and 254, and the gradient costs extra length, which is the NavFn scale. The local costmap is rebuilt from the current scan only, in a 3 m rolling window.

## Result

```text
SUMMARY mode=inflated global_cushion=254 local_cushion=outside phantom_lethal=1 inscribed_cells=60 gradient_cells=316 path_poses=89 path_length_m=4.90 straight_m=4.40 path_dev_m=0.57 min_clearance_m=0.552 through_cushion=0 mark_range_m=2.325 now_range_m=3.225
```

The global cell is still 254. Around it: 60 inscribed cells and 316 gradient cells. The path is 4.90 m, half a metre longer than the straight line, and it bends 0.57 m off the center line. The closest approach is 0.552 m, just outside the 0.55 m inflation radius. The local costmap does not contain the cell.

The ASCII map in `assets/C_inflated.log` shows the `O` disk on open floor and the `.` path bending around it.

`ros2 topic info` again reported one publisher each for the global costmap, the local costmap, and `/plan`, node `costmap_demo`, durability `TRANSIENT_LOCAL`.

## Conclusion

The robot avoids empty floor because the global costmap still holds one lethal cell, and the inflation layer has grown that cell to the size of the robot. The local map, which is what the sensor sees from here, never had the cushion.
