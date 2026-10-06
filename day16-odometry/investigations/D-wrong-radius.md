# Investigation D — Wrong wheel radius

## Question

If the wheels spin exactly as in the straight run, but the radius in the formula is wrong, does the position change?

## Setup

Same spin as Investigation A: both wheels 5 rad/s for 2 s. The radius used to turn spin into distance is 0.11 m instead of 0.10 m.

## Expected

Contact speed becomes `5 * 0.11 = 0.55` m/s. In 2 s the reported distance is 1.100 m, not 1.000 m.

## Actual

`assets/D_wrong_radius.log`:

```text
SUMMARY x=1.1000 y=0.0000 yaw_deg=0.00 body_vx=0.5500 body_vy=0.0000 frame=odom child=base_link
```

## Conclusion

The wheels did not spin any faster. The position did. Odometry trusts the radius you gave it. Ten percent wrong on the wheel is ten percent wrong on the distance, and that error is in the sum from the first step.
