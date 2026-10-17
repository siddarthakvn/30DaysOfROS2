# C — The laser keeps the guesses that fit

## Hypothesis

If each guess is scored by how well it would have seen the measured walls, the copies pile up on the true pose and the other rooms empty out.

## Method

Same 400 starting guesses and the same wheel steps as Investigation B. `mode:=laser_vote`.

After each step the measured scan is compared with the scan that guess would have produced. High scores are copied. Low scores are dropped. Each copy is nudged by about 10 cm so the cloud can still slide toward a better fit. At the end of the walk the robot stands still for four more scans.

The reported pose is the average of the surviving guesses.

## Result

```text
SUMMARY mode=laser_vote particles=400 final_error_m=0.030 final_spread_m=0.221 kitchen_fraction=1.000
step=0 error_m=2.605 spread_m=0.950 kitchen_fraction=0.988
step=9 error_m=0.030 spread_m=0.221 kitchen_fraction=1.000
```

After the first scan, 98.8% of the guesses are in the kitchen and the reported place is still 2.605 m off. The kitchen is long, and the first view fits more than one spot along it. By the last still scan the error is 0.030 m, every surviving guess is in the kitchen, and the ASCII cluster sits on `T`.

`ros2 topic info` reported one publisher on `/map` (`nav_msgs/msg/OccupancyGrid`, transient local) and one publisher on `/particle_cloud` (`geometry_msgs/msg/PoseArray`). The node name is `localizer`.

## Conclusion

The laser does not draw a new map here. It votes on guesses that were already on the old one. The first vote picks the room. The rest of the walk picks the spot. The final cloud is 22 cm wide because the copies are nudged on purpose. The average of that cloud is 3 cm from the truth.
