# A — Paint at the real pose

## Hypothesis

If every scan is painted where the robot actually is, each beam ends on the real wall and the grid is one square.

## Method

`build_map.py` with `mode:=truth`.

The room is the square (0,0) to (4,4). Sixteen scans. The robot moves from (1.00, 1.50) to (1.90, 1.50). Each scan is 120 beams, full turn, max range 6 m. Cells are 5 cm. A cell the beam passes through is marked open. The cell where the beam stops is marked occupied.

## Result

```text
SUMMARY mode=truth scans=16 mean_pose_error_m=0.0000 final_pose_error_m=0.0000 mean_wall_error_m=0.0000 right_wall_spread_m=0.0172 occupied_cells=322
```

`ros2 topic info /map -v` reported one publisher, node `map_builder`, type `nav_msgs/msg/OccupancyGrid`, durability `TRANSIENT_LOCAL`.

The ASCII map is one `#` border around open `.` cells. 322 occupied cells is the perimeter. The east-wall spread of 1.7 cm is the beam ending on the shared edge of two 5 cm cells, not a second wall.

## Conclusion

With the right pose, a scan becomes a map by painting along the beam. The pose error is zero because this case is given the real pose. It is the picture the other two cases are judged against.
