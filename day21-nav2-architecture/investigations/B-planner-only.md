# B — A path is not a command

## Hypothesis

Once a planner runs, a path appears around the wall, and the robot still does not move until something publishes speed.

## Method

Same goal as Investigation A. `mode:=planner_only`.

The planner is a grid search on 0.2 m cells. Cells inside the wall (x = 2.3 to 3.5 m, y = 0 to 2.35 m) are blocked. The path is published on `/plan`. No controller runs.

## Result

```text
SUMMARY mode=planner_only events=goal>path result=ABORTED path_poses=27 path_length_m=6.69 straight_m=4.60 path_max_y_m=2.50 final_error_m=4.600 cmd_nonzero=0 max_linear=0.00 hit_wall=0
```

The path has 27 poses and is 6.69 m long. Its highest point is y = 2.50 m, above the wall top at 2.35 m. The action is still `ABORTED`. The final error is still 4.600 m. `cmd_nonzero` is 0.

## Conclusion

The goal became a line. The line goes around the wall, which a straight speed toward the pin would not. The robot did not follow it, because nothing turned the line into `Twist`.
