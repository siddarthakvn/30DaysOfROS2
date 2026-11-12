# Investigation C — No TF

## Question

What if pixel and depth are correct, but the point is never walked into `map`?

## Setup

Same pixel and true depth as A. The optical point is published as if it were already in the map.

## Expected

Coordinates stay next to the camera. `frame_id` is not `map`. Error against the true map pose is large.

## Actual

`assets/C_no_tf.log`:

```text
SUMMARY case=no_tf u=320.00 v=282.86 depth=1.7500 map_x=0.0000 map_y=0.1500 map_z=1.7500 err_xy=2.0056 frame=camera_optical
```

## Conclusion

Depth solved the ray. TF was still missing. The number is useful to the camera and useless to Nav2.
