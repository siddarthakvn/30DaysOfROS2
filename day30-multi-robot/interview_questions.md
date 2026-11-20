# Day 30 — Interview questions

1. You launch three robots with `--ros-args -r __ns:=/r1`, `/r2`, and `/r3`, yet `ros2 topic info /cmd_vel` still shows 3 publishers and 3 subscribers. What bug in the node code caused that?

2. Why did `r1`, `r2`, and `r3` each receive 213 commands and miss the target by `3.88–5.97 m` in Investigation A even though all three controllers were computing proportional velocity toward `(2.50, 3.00)`?

3. Why does `--ros-args -r __ns:=/r1` NOT automatically turn `child_frame_id = "base_link"` into `"r1/base_link"` on `/tf`, and what are the two standard ways to isolate TF trees in multi-robot Nav2?

4. Investigation B had zero topic collisions (`1 pub / 1 sub` on every `/rN/cmd_vel`), yet `min_pair_sep_m` dropped to `0.033 m`. What architectural layer was still missing?

5. When scaling from 3 robots to 30 on Wi-Fi, why can keeping a single shared `/tf` topic or a single `ROS_DOMAIN_ID` still become a bottleneck even when every topic and frame is properly namespaced?

6. How would you upgrade `fleet_coordinator`'s one-shot Euclidean distance check so it handles a robot failing mid-task (combining Day 05 action cancellation, Day 26 mission states, and Day 29 watchdogs)?
