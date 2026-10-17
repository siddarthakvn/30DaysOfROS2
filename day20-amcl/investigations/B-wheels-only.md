# B — Many guesses, wheels only

## Hypothesis

If guesses are scattered over the house and only the wheels move them, the cloud stays spread out and the average pose stays far from the robot.

## Method

Same walk as Investigation A. `mode:=wheels_only`.

400 guesses are dropped on open floor, with random headings. Each wheel step is applied to every guess, plus a few centimetres of noise. The laser is not consulted. The reported pose is the average of the cloud.

## Result

```text
SUMMARY mode=wheels_only particles=400 final_error_m=2.201 final_spread_m=3.304 kitchen_fraction=0.345
```

The cloud width grows from 2.504 m to 3.304 m. The share of guesses in the kitchen stays near 0.35, which is the share a random drop lands there. The ASCII map is dotted across the kitchen, the hall, and the bedroom.

## Conclusion

The wheels tell every guess how the body moved. They do not tell the robot which guess is the body. The average of a cloud spread over the house is 2.2 m away from the kitchen pose.
