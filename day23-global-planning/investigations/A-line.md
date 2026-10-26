# A — The straight line meets a wall

## Hypothesis

The segment from A to B is not a path. It crosses a wall, so the planner has nothing legal to publish along that line.

## Method

`planner.py` with `mode:=line`.

A is (1.0, 1.2). B is (7.0, 4.8). The straight distance is 7.00 m. The line is sampled every 5 cm. A sample that lands in a wall cell counts. No search runs. `/plan` is published empty.

## Result

```text
SUMMARY mode=line reached=0 expanded=0 free_cells=4284 path_poses=0 path_length_m=0.00 straight_m=7.00 line_wall_hits=10
```

Ten samples sit on a wall. The path has 0 poses. `ros2 topic info /plan` still reported one publisher, node `global_planner`, type `nav_msgs/msg/Path`, durability `TRANSIENT_LOCAL`.

## Conclusion

The short line on the map is 7.00 m and it is illegal. Choosing a path starts by refusing that line.
