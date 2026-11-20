# B — Isolated bodies, uncoordinated mission

## Hypothesis

Switching to relative topic names (`cmd_vel`, `odom`) and prefixed TF frames (`rN/base_link`) isolates each robot's control loop, but subscribing all three controllers directly to `/fleet/target` sends all three bodies into the same coordinate.

## Method

`ros2 launch launch/fleet.launch.py mode:=uncoordinated`. Same three bays `(1.00, 3.00)`, `(1.00, 1.00)`, `(5.00, 1.00)` and target `(2.50, 3.00)`. No coordinator node runs.

## Result

```text
ROBOT mode=uncoordinated id=r1 pos=(2.464,3.000) travel_m=1.464 err_m=0.036 rx_cmds=35 frame=r1/base_link
ROBOT mode=uncoordinated id=r2 pos=(2.478,2.970) travel_m=2.463 err_m=0.037 rx_cmds=49 frame=r2/base_link
ROBOT mode=uncoordinated id=r3 pos=(2.529,2.977) travel_m=3.164 err_m=0.037 rx_cmds=59 frame=r3/base_link
SUMMARY mode=uncoordinated winner=none moved_robots=3 at_target=3 total_travel_m=7.091 min_pair_sep_m=0.033 r1_err_m=0.036 r2_err_m=0.037 r3_err_m=0.037 r1_cmds=35 r2_cmds=49 r3_cmds=59
```

`ros2 topic info /r1/cmd_vel -v` and `/r2/cmd_vel -v` each reported `Publisher count: 1` and `Subscription count: 1`. Every robot converged cleanly to `(2.50, 3.00)` (`at_target=3`), ending `0.033 m` (`3.3 cm`) apart after `7.091 m` of combined travel.

## Conclusion

Namespaces fix control cross-talk, not fleet behavior. Without an allocator, one mission broadcast becomes a three-robot pile-up at the goal.
