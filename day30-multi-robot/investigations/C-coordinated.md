# C — Namespaces plus a fleet coordinator

## Hypothesis

Placing `fleet_coordinator` between `/fleet/target` and private `/rN/goal` topics dispatches only the closest robot (`r1`), leaving `r2` and `r3` stationary at zero commands.

## Method

`ros2 launch launch/fleet.launch.py mode:=coordinated`. Each controller listens to relative `goal` (`/r1/goal`, `/r2/goal`, `/r3/goal`). `fleet_coordinator` reads `/r1/odom`, `/r2/odom`, `/r3/odom`, computes Euclidean distance to `/fleet/target`, and publishes the target only to the lowest-cost robot.

## Result

```text
COORDINATOR winner=r1 r1_cost_m=1.500 r2_cost_m=2.500 r3_cost_m=3.202
ROBOT mode=coordinated id=r1 pos=(2.464,3.000) travel_m=1.464 err_m=0.036 rx_cmds=35 frame=r1/base_link
ROBOT mode=coordinated id=r2 pos=(1.000,1.000) travel_m=0.000 err_m=2.500 rx_cmds=0 frame=r2/base_link
ROBOT mode=coordinated id=r3 pos=(5.000,1.000) travel_m=0.000 err_m=3.202 rx_cmds=0 frame=r3/base_link
SUMMARY mode=coordinated winner=r1 moved_robots=1 at_target=1 total_travel_m=1.464 min_pair_sep_m=2.479 r1_err_m=0.036 r2_err_m=2.500 r3_err_m=3.202 r1_cmds=35 r2_cmds=0 r3_cmds=0
```

`/fleet/assignment` echoed:

```text
data: winner=r1 costs=r1:1.500,r2:2.500,r3:3.202
```

`tf2_echo map r1/base_link` reported translation `[2.464, 3.000, 0.000]`. `r2` and `r3` stayed at `(1.000, 1.000)` and `(5.000, 1.000)` with `rx_cmds=0`. Fleet travel dropped from `7.091 m` (B) to `1.464 m`, and minimum inter-robot separation stayed `2.479 m`.

## Conclusion

Private control stays inside `/r1`, `/r2`, and `/r3`. Shared coordination lives on `/fleet/target` and `/fleet/assignment`. One target moves one robot.
