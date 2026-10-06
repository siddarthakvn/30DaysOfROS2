# Investigation B — Wheels opposite ways

## Question

If the wheels spin at the same rate in opposite directions, does the center stay put?

## Setup

- Left wheel −2 rad/s, right wheel +2 rad/s, radius 0.10 m
- Contact speeds: −0.20 m/s and +0.20 m/s
- Track width 0.40 m, so yaw rate is `(0.20 − (−0.20)) / 0.40 = 1` rad/s
- Duration 1.570796 s, a quarter turn at that rate

## Expected

`x` and `y` stay 0. Yaw is about 90°.

## Actual

`assets/B_spin.log`:

```text
SUMMARY x=0.0000 y=0.0000 yaw_deg=90.01 body_vx=0.0000 body_vy=0.0000 frame=odom child=base_link
```

Yaw is 90.01° rather than 90.00° because the integrator steps by 1 ms, and the duration does not land on an exact number of steps.

## Conclusion

Opposite wheel rotation became a new heading, not a new place. The center of the robot did not move.
