# B — The local steer keeps the old plan

## Hypothesis

A controller that may step up to 1.05 m off the line can pass the small box. The published plan stays the original 6.00 m line.

## Method

`mode:=local`.

Same plan, same small box, same moment the box appears. When the next 1.5 m of the plan meets the box, the steer picks a side target that still sits inside 1.05 m of the center line. A unicycle cannot slide, so it first turns toward that target at the current y, then drives forward along the offset until it is past the box, then aims at the old line again. No global search runs.

## Result

```text
SUMMARY mode=local reached=1 hit=0 replans=0 plan_poses=61 plan_length_m=6.00 straight_m=6.00 plan_through_box=1 plan_dev_m=0.00 driven_dev_m=1.05 min_clearance_m=0.315 final_error_m=0.181 commands=369
```

`/plan` is still 61 poses, 6.00 m, through the box, with zero deviation. The body drives 1.05 m off the line, stays 0.315 m clear of the box, and finishes 0.181 m from the goal. 369 commands. Zero replans.

The ASCII map in `assets/B_local.log` shows `r` bending around `#` while `.` still runs through the box.

## Conclusion

Dynamic avoidance can be a local steer. The global path does not have to change for the body to go around a box that fits inside the controller's reach.
