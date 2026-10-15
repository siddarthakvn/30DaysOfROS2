# B — Paint where the wheels think you are

## Hypothesis

If the pose used for painting walks away from the truth, the same wall is stored in more than one place.

## Method

Same scans as Investigation A. `mode:=drift`.

Wheel pose at step i is the real pose plus `0.03 * i` meters in x. After 15 steps that is 0.45 m. Nothing else changes.

## Result

```text
SUMMARY mode=drift scans=16 mean_pose_error_m=0.2250 final_pose_error_m=0.4500 mean_wall_error_m=0.1114 right_wall_spread_m=0.1306 occupied_cells=553
```

Occupied cells went from 322 to 553. The ASCII map grows a second edge: `##` and `###` where A had a single `#`. Mean distance from a painted hit to the real wall is 0.111 m. It is lower than the 0.225 m pose error because a sideways miss still lands on the north or south wall.

## Conclusion

The laser did not get worse. The pose used to place the scan did. A map painted from drifting wheels smears.
