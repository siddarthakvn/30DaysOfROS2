# C — The wide box forces one replan

## Hypothesis

When no sidestep inside the local reach clears the box, the controller stops, one global search draws a new line, and the body follows that line to the goal.

## Method

`mode:=replan`.

The plan starts as the same 6.00 m line. The box is wider: x = 1.55 to 5.55, y = 3.55 to 4.45. Both side targets fall outside the 1.05 m reach, so the steer returns no passage. After ten blocked cycles the global search runs once, from the robot's pose, on the grid with that box closed. The controller then tracks the new line.

## Result

```text
SUMMARY mode=replan reached=1 hit=0 replans=1 plan_poses=56 plan_length_m=6.70 straight_m=6.00 plan_through_box=0 plan_dev_m=1.75 driven_dev_m=1.77 min_clearance_m=0.019 final_error_m=0.195 commands=371
```

One replan. The new plan is 56 poses and 6.70 m, 1.75 m off the old center line, and it does not enter the box. The body follows it out to 1.77 m and stays 0.019 m clear. Final error is 0.195 m. 371 commands.

The ASCII map in `assets/C_replan.log` shows `.` and `r` sharing the detour around the wide box.

`/plan` and `/cmd_vel` again had one publisher each, node `avoidance`.

## Conclusion

A local steer is the first response. When the box is wider than that steer, the global planner runs again, and the path on `/plan` is a new line.
