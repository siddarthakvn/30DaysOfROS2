# Investigation B — Map jump, odom stays smooth

## Hypothesis

**H2 / H5:** A discrete `map`→`odom` jump moves the robot in `map` without breaking continuity of `odom`→`base_link`.

---

## Setup

```bash
ros2 launch launch/demo.launch.py mode:=b jump_at_sec:=5.0
```

At t≈5s localization applies Δ ≈ (1.5 m, 0.8 m, 0.35 rad) on `map`→`odom`.

---

## Actual results

Evidence: [`../assets/B.log`](../assets/B.log)

| Metric | Observed |
|---|---|
| MAP JUMP | applied at ~5s |
| `odom_robot_max_step_m` | **0.0250** (unchanged vs A) |
| `map_robot_max_step_m` | **1.5504** ← the jump |
| `map_nose_max_step_m` | **1.6979** |
| `kitchen_in_base_max_step_m` | **2.3272** |
| Before jump (t=4s) | odom≈map ≈ (0.99, 0.04) |
| After jump (t=5s) | odom=(1.24, 0.06) · **map=(2.40, 1.06)** |

The “nose” point (1 m ahead in `base_link`) and the fixed kitchen landmark both snap in `map` / body views when localization corrects — while odometry keeps walking smoothly.

---

## Conclusion

**Supported.** Localization publishes the correcting edge (`map`→`odom`). Control keeps the continuous edge (`odom`→`base_link`). That is why both frames exist.
