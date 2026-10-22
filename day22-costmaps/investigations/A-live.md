# A — The live scan of an empty room

## Hypothesis

If the obstacle layer holds only the scan from the robot's current pose, the old cushion cell is free and the path is the straight line.

## Method

`costmaps.py` with `mode:=live`.

The room is 6 m by 4 m. Walls come from the static layer. The scan marks hits inside 2.5 m and clears cells out to 3.0 m. No cushion is in the room, and nothing is remembered. Inflation uses robot radius 0.22 m, inflation radius 0.55 m, cost scaling 3.0. The planner refuses cost 253 and 254 and prices the rest the way NavFn does: length times `(50 + 0.8 * cost) / 50`.

## Result

```text
SUMMARY mode=live global_cushion=0 local_cushion=outside phantom_lethal=0 inscribed_cells=0 gradient_cells=0 path_poses=89 path_length_m=4.40 straight_m=4.40 path_dev_m=0.02 min_clearance_m=0.000 through_cushion=1 mark_range_m=2.325 now_range_m=3.225
```

The global cell cost is 0. The path is 89 poses and 4.40 m, the same as the straight line. `through_cushion=1`. The closest approach is 0.000 m, which means a path pose sits on that cell. The local window does not contain the cell.

`ros2 topic info` reported one publisher on `/global_costmap/costmap`, one on `/local_costmap/costmap`, and one on `/plan`. Node `costmap_demo`. Type `nav2_msgs/msg/Costmap` for both costmaps, `nav_msgs/msg/Path` for the plan. Durability `TRANSIENT_LOCAL`.

## Conclusion

With only the current scan, the empty floor stays empty in the costmap, and the path crosses it.
