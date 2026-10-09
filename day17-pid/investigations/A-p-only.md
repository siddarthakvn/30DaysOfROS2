# Investigation A — P only, and the heading remembers its turn rate

## Question

Does a strong P term, with no D, swing a heading past the target when turn rate is stored?

## Setup

Target 90°. P gain 4. D gain 0. I gain 0. Eight seconds. The command is an angular acceleration, so turn rate carries on after the command drops.

## Expected

The heading crosses 90° more than once.

## Actual

`assets/A_p_only.log`:

```text
SUMMARY crossings=5 yaw_deg=175.92 error_deg=-85.92 past_deg=90.00 kp=4.0 kd=0.0 plant=inertia
```

It crossed five times, went a full 90° past the target, and after 8 seconds was still near 176°, not parked on 90°.

## Conclusion

P built the turn and then went silent at the target. The stored turn rate carried the heading through.
