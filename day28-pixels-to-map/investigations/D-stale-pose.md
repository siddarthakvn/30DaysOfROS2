# Investigation D — Stale robot pose

## Question

What if the robot moved, the pixel updated, but the camera→map transform did not?

## Setup

Robot rolls `+0.50 m` in map x. A new pixel and depth are computed from that new camera pose. The code still applies the old camera origin at `x = 0.25`.

## Expected

Map error near `0.50 m`, matching the untracked motion.

## Actual

`assets/D_stale_pose.log`:

```text
SUMMARY case=stale_pose u=320.00 v=300.00 depth=1.2500 map_x=1.5000 map_y=0.0000 map_z=0.1500 err_xy=0.5000 frame=map
```

## Conclusion

The image changed. The TF tree did not. The map cell is wrong by exactly the missing robot motion.
