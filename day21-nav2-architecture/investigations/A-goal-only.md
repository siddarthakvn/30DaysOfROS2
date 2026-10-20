# A — The goal arrives alone

## Hypothesis

A `NavigateToPose` goal does not move the robot. Without a planner and a controller, the pose stays at the start and the action does not succeed.

## Method

`navigate.py` with `mode:=goal_only`.

The client is `ros2 action send_goal /navigate_to_pose`. The pin is (5.2, 0.6). The robot starts at (0.6, 0.6). The server records the goal and does not plan or drive.

## Result

```text
SUMMARY mode=goal_only events=goal result=ABORTED path_poses=0 path_length_m=0.00 straight_m=4.60 path_max_y_m=0.00 final_error_m=4.600 cmd_nonzero=0 max_linear=0.00 hit_wall=0
```

The action client printed `Goal finished with status: ABORTED`. `/plan` had a publisher and an empty path. No nonzero `Twist` was produced.

## Conclusion

The pin was delivered. The wheels were never given a speed. The robot finished exactly where it started, 4.60 m from the goal.
