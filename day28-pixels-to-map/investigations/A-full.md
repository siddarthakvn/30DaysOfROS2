# Investigation A — Full pipeline

## Question

Does pixel + true depth + camera→map transform recover the box in the map frame?

## Setup

Box at map `(2.000, 0.000, 0.150)`. Camera at `(0.25, 0, 0.30)`. Pinhole `fx = fy = 500`, principal point `(320, 240)`.

## Expected

`err_xy` near zero. `frame_id` is `map`.

## Actual

`assets/A_full.log`:

```text
SUMMARY case=full u=320.00 v=282.86 depth=1.7500 map_x=2.0000 map_y=0.0000 map_z=0.1500 err_xy=0.0000 frame=map
```

## Conclusion

With all three pieces present, the pixel lands on the true map point.
