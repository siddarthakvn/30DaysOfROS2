# Investigation D — Two certain yaw readings that disagree

## Question

If two yaw measurements disagree and both carry a tiny variance, does the guess settle between them?

## Setup

No driving. One reading is 0 rad. The other is 0.20 rad (11.46°). Each has variance `1e-6`. They alternate for 20 updates. A little process noise is added before each update so the filter is willing to listen again.

## Expected

The guess snaps from one reading to the other instead of sitting in the middle.

## Actual

`assets/D_fight.log`:

```text
SUMMARY case=fight yaw_deg=11.46 jumps=19 span_deg=11.46 yaw_var=1.000e-06 frame=odom child=base_link
```

Nineteen jumps. The span is 11.46°, the full gap between the two readings. The variance at the end is `1e-6`, the same tiny number each reading claimed.

## Conclusion

Tiny covariance means the filter pulls hard. When both sides claim that and they disagree, the pose jumps. A small variance is not proof the pose is right.
