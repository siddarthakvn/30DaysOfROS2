# Investigation B — Wrong depth

## Question

What happens if the pixel is right but the distance is guessed?

## Setup

Same pixel as A. Depth forced to `1.0 m` instead of the true `1.75 m`. Transform still applied.

## Expected

The map point is short along the camera ray. Error is meters, not pixels.

## Actual

`assets/B_bad_depth.log`:

```text
SUMMARY case=bad_depth u=320.00 v=282.86 depth=1.0000 map_x=1.2500 map_y=0.0000 map_z=0.2143 err_xy=0.7500 frame=map
```

## Conclusion

The detection box did not move. The distance did. Nav2 would still get a map point, and that point would be 0.75 m wrong.
