# Investigation C — No stored turn rate

## Question

If the heading rate equals the command immediately, does this same P still overshoot?

## Setup

P gain 4, D gain 0, target 90°, 8 seconds. The plant sets turn rate equal to `P × error` on every step. Nothing is carried over.

## Expected

The heading approaches 90° without a crossing.

## Actual

`assets/C_instant.log`:

```text
SUMMARY crossings=0 yaw_deg=90.00 error_deg=0.00 past_deg=0.00 kp=4.0 kd=0.0 plant=instant
```

## Conclusion

The gain that oscillated in Investigation A settled here. The wobble needed a heading that still had turn speed when the error hit zero.
