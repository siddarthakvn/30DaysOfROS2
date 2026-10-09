# Investigation B — The same P, plus a brake

## Question

Does D stop the swing without changing P?

## Setup

Identical to Investigation A, except D gain is 4. D multiplies the turn rate and subtracts it from the command.

## Expected

Fewer crossings. The heading ends near 90°.

## Actual

`assets/B_with_d.log`:

```text
SUMMARY crossings=0 yaw_deg=90.00 error_deg=0.00 past_deg=0.00 kp=4.0 kd=4.0 plant=inertia
```

No crossing. No travel past the target. Final heading 90.00°.

## Conclusion

The gap term was unchanged. The brake on turn rate is what stopped the oscillation.
