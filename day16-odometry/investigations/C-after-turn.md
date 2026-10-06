# Investigation C — Drive after a turn

## Question

After the robot has turned 90°, does the same forward wheel command still increase `x`?

## Setup

Same wheels as Investigation A: both at 5 rad/s for 2 s. Starting yaw is already 90°.

## Expected

The body is still driving "forward" at 0.50 m/s, with sideways speed 0. In the world, forward is now along `y`, so `y = 1.000` m and `x` stays 0.

## Actual

`assets/C_after_turn.log`:

```text
SUMMARY x=0.0000 y=1.0000 yaw_deg=90.00 body_vx=0.5000 body_vy=0.0000 frame=odom child=base_link
```

## Conclusion

The wheels did the same thing as in the straight run. The position changed on a different axis because the heading had changed. Body sideways speed stayed 0. A differential-drive robot still cannot slide sideways.
