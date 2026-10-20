# C — The controller sends the speed

## Hypothesis

If a controller reads the path and publishes `/cmd_vel`, the robot follows the line around the wall and the action succeeds.

## Method

Same goal and the same 27-pose path. `mode:=full`.

The controller aims at a point about 0.45 m ahead on the path and writes `linear.x` and `angular.z`. A unicycle integrates that `Twist`. The action succeeds when the pose is within 0.15 m of the pin and the body never entered the wall.

## Result

```text
SUMMARY mode=full events=goal>path>cmd_vel result=SUCCEEDED path_poses=27 path_length_m=6.69 straight_m=4.60 path_max_y_m=2.50 final_error_m=0.130 cmd_nonzero=279 max_linear=0.45 hit_wall=0
```

The client printed `Goal finished with status: SUCCEEDED`. The event order is `goal > path > cmd_vel`. 279 commands were nonzero. Peak forward speed was 0.45 m/s. Final error is 0.130 m. `hit_wall` is 0. The ASCII map shows `R` on the pin and the dotted path clearing the wall.

`ros2 action info /navigate_to_pose` reported one server, node `navigator`.

## Conclusion

The goal stayed a pose. The planner stayed a path. The controller was the first stage to produce a wheel command. That is the order after a Nav2 goal: action, then path, then `Twist`.
