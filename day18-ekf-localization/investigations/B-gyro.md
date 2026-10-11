# Investigation B — Gyro only

## Question

What does a constant gyro bias of 0.02 rad/s do to the pose after 10 seconds of straight driving?

## Setup

Same truth as A. The gyro reads 0.02 rad/s the whole time. Position is integrated with the true speed, 1.0 m/s, and with the heading that comes from that gyro. No wheel yaw rate.

## Expected

Heading near 0.02 × 10 s = 0.20 rad, about 11.5°. The path bends sideways.

## Actual

`assets/B_gyro.log`:

```text
SUMMARY case=gyro x=9.9334 y=0.9977 yaw_deg=11.46 err_x=-0.0666 err_y=0.9977 err_yaw_deg=11.46 frame=odom child=base_link
```

Heading error is 11.46°. Sideways error is 0.998 m. Along-track error is only 0.067 m, because this case used the true speed.

## Conclusion

The gyro drift is a heading walk. Once the heading is wrong, straight driving becomes a curve.
