# Investigation A — Odom only (smooth, no map)

## Hypothesis

**H1:** With only `odom`→`base_link`, motion is continuous; there is no usable `map` pose.

---

## Setup

```bash
ros2 launch launch/demo.launch.py mode:=a run_sec:=12.0
```

---

## Actual results

Evidence: [`../assets/A.log`](../assets/A.log)

| Metric | Observed |
|---|---|
| `odom_samples` | **109** |
| `map_samples` | **0** (`map_misses=109`) |
| `odom_robot_max_step_m` | **0.0250** |
| `odom_robot_final` | **(+2.695, +0.295)** |

Robot drove smoothly with a quiet yaw bias (drift seed). No global frame.

---

## Conclusion

**Supported.** Odometry alone gives a continuous local story — and nothing you can trust as a floor-plan pose.
