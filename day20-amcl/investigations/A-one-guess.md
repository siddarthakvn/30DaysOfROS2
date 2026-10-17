# A — One guess, dropped in the bedroom

## Hypothesis

If the only guess is in the wrong room, copying the wheel steps cannot move it to the kitchen.

## Method

`localize.py` with `mode:=one_guess`.

The floor plan is frozen. The robot walks in the kitchen and stops at (1.9 m, 3.0 m). The single guess starts at (6.5 m, 2.6 m) in the bedroom, facing the same way, and receives the same body steps.

## Result

```text
SUMMARY mode=one_guess particles=1 final_error_m=5.316 final_spread_m=0.000 kitchen_fraction=0.000
```

The error is 5.316 m at every step. The ASCII map shows `T` in the kitchen and `E` in the bedroom.

## Conclusion

One guess is not a search. It is a claim. The wheels carry that claim along. Nothing in this mode is allowed to throw it away, so the robot finishes 5.3 m from the truth.
