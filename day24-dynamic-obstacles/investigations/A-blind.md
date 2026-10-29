# A — The controller follows the old line

## Hypothesis

If the controller tracks the planned line and never looks at the box, the body stops at the box with the goal still ahead.

## Method

`drive.py` with `mode:=blind`.

The plan is the straight line from (3.0, 1.0) to (3.0, 7.0), 6.00 m, drawn before the box exists. The box is the 0.90 m square from x = 2.55 to 3.45 and y = 3.55 to 4.45. It becomes active once the robot passes y = 2.20. The tracker aims along the line. The step that would put the 0.22 m body into the box is refused, and the run stops.

## Result

```text
SUMMARY mode=blind reached=0 hit=1 replans=0 plan_poses=61 plan_length_m=6.00 straight_m=6.00 plan_through_box=1 plan_dev_m=0.00 driven_dev_m=0.00 min_clearance_m=0.010 final_error_m=3.680 commands=117
```

The plan still goes through the box. The body never leaves the center line. It stops 0.010 m clear of the box and 3.680 m short of the goal, after 117 commands. No replan.

`/plan` had one publisher, node `avoidance`, type `nav_msgs/msg/Path`, durability `TRANSIENT_LOCAL`. `/cmd_vel` had one publisher, type `geometry_msgs/msg/Twist`, durability `VOLATILE`.

## Conclusion

The old path survives the box. A controller that only tracks that path stops on it.
