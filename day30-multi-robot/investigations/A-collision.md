# A — Leading slashes defeat namespaces

## Hypothesis

Launching three robots under `-r __ns:=/r1`, `/r2`, and `/r3` still merges their control loops if the code uses hardcoded leading slashes (`"/cmd_vel"`, `"/odom"`) and an unprefixed `"base_link"` frame.

## Method

`ros2 launch launch/fleet.launch.py mode:=collision`. Six robot nodes start under `/r1`, `/r2`, and `/r3`, plus `/fleet_auditor` publishing one target at `(2.50, 3.00)`.

## Result

```text
ROBOT mode=collision id=r1 pos=(1.151,7.770) travel_m=4.900 err_m=4.957 rx_cmds=213 frame=base_link
ROBOT mode=collision id=r2 pos=(3.534,-2.880) travel_m=4.970 err_m=5.971 rx_cmds=213 frame=base_link
ROBOT mode=collision id=r3 pos=(5.139,5.839) travel_m=4.970 err_m=3.876 rx_cmds=213 frame=base_link
SUMMARY mode=collision winner=none moved_robots=3 at_target=0 total_travel_m=14.840 min_pair_sep_m=4.431 r1_err_m=4.957 r2_err_m=5.971 r3_err_m=3.876 r1_cmds=213 r2_cmds=213 r3_cmds=213
```

`ros2 node list --no-daemon` showed `/r1/base`, `/r1/controller`, `/r2/base`, `/r2/controller`, `/r3/base`, `/r3/controller`. Yet `ros2 topic info /cmd_vel -v` and `ros2 topic info /odom -v` both reported:

```text
Publisher count: 3
Subscription count: 3
```

Every base absorbed `213` conflicting velocity commands in `3.5 s`, traveled nearly `5 m` off course, and `at_target=0`.

## Conclusion

Node namespaces do not isolate absolute topic names. Three controllers reading interleaved `/odom` samples and publishing onto one `/cmd_vel` cross-drive all three bodies away from the goal.
