# B — The obstacle layer remembers one cell

## Hypothesis

A cell marked inside `obstacle_max_range`, then left beyond `raytrace_max_range`, stays lethal. With inflation off, the path only has to miss that one cell.

## Method

`mode:=stale`.

First the robot is at (1.70, 2.00) and the cushion is in the cell at (4.025, 2.025). That return is 2.325 m away, inside the 2.5 m marking range, so the cell is set to 254. The cushion is then removed. The robot is at (0.80, 2.00). The same cell is now 3.225 m away, past the 3.0 m clearing range, so the second scan stops short of it. Inflation is not applied. The planner still refuses cost 253 and 254.

## Result

```text
SUMMARY mode=stale global_cushion=254 local_cushion=outside phantom_lethal=1 inscribed_cells=0 gradient_cells=0 path_poses=89 path_length_m=4.44 straight_m=4.40 path_dev_m=0.02 min_clearance_m=0.050 through_cushion=0 mark_range_m=2.325 now_range_m=3.225
```

One phantom lethal cell. No inscribed cells and no gradient, because inflation is off. The path is 4.44 m, four centimetres longer than the straight line. It does not enter the cell. The center comes within 0.050 m, one grid step. The robot radius in the Humble bringup file is 0.22 m, so a body of that size still covers the cell. The local window still does not contain it.

## Conclusion

The obstacle layer is enough to keep a cushion that the room no longer holds. Without inflation, the planner sidesteps a point, and the robot body would still hit that point.
