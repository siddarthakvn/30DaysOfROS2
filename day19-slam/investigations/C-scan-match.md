# C — Slide the scan onto the grid, then paint

## Hypothesis

If each new scan is shifted until its hits sit on the walls already drawn, the pose error stops growing and the grid stays a single square.

## Method

Same drifting wheel guess as Investigation B. `mode:=match`.

The first scan is painted at the real start pose. Every later scan starts from the wheel step, then searches ±10 cm in x and ±4 cm in y at 1 cm steps. The pose that puts the beam ends closest to already-occupied cells is the one that gets painted.

Yaw is not searched. This drive is straight and the wheel yaw is already correct.

## Result

```text
SUMMARY mode=match scans=16 mean_pose_error_m=0.0342 final_pose_error_m=0.0361 mean_wall_error_m=0.0240 right_wall_spread_m=0.0169 occupied_cells=317
```

Final pose error is 3.6 cm, against 45.0 cm when the same wheel guess is painted raw. East-wall spread matches Investigation A (1.7 cm). Occupied cells are 317, next to A's 322. The ASCII map is one square again.

## Conclusion

"Building a map" is this correction, then the paint. The wheels still drift. The scan match spends that drift before the cell is written. The leftover error stays near one cell instead of adding 3 cm every step.

This search is a small stand-in for `slam_toolbox`. It will lose a motion bigger than the search window, and a long featureless wall still cannot tell the robot it slid along that wall.
