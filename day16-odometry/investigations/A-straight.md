# Investigation A — Both wheels the same way

## Question

If both wheels spin at the same rate, does the robot drive straight?

## Setup

- Radius 0.10 m, track width 0.40 m
- Both wheels 5 rad/s for 2.0 s
- Contact speed of each wheel: `5 * 0.10 = 0.50` m/s
- Yaw rate: zero, because the wheels match

## Expected

`x = 1.000` m, `y = 0`, yaw `0°`. Body sideways speed `0`.

## Actual

`assets/A_straight.log`:

```text
SUMMARY x=1.0000 y=0.0000 yaw_deg=0.00 body_vx=0.5000 body_vy=0.0000 frame=odom child=base_link
```

## Conclusion

Equal wheel rotation became a straight position. The pose is in `odom`. The speed is in `base_link`, and that speed has no sideways part.
