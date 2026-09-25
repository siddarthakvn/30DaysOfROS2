# Investigation A — Fixed humanoid URDF

## Engineering question

Can a valid URDF describe a rooted link/joint tree that ROS 2 can load as `robot_description`?

---

## Hypothesis

**H1 / H5:** `check_urdf` accepts the model; `robot_state_publisher` exposes `robot_description` and publishes TF for the fixed chain.

---

## Setup

```bash
source ros2_nodes/env.sh
check_urdf urdf/humanoid_fixed.urdf
ros2 launch launch/display.launch.py model:=urdf/humanoid_fixed.urdf
```

---

## Expected

| Check | Expect |
|---|---|
| `check_urdf` | root `base_link` → torso → arm → hand |
| Param | `robot_description` contains `base_link` / `r_hand` |
| TF | `base_link` → `r_hand` at a fixed pose |

---

## Actual results

Evidence: [`../assets/A.log`](../assets/A.log)

| Check | Observed |
|---|---|
| `check_urdf` | Parsed OK; tree as expected |
| `robot_description` | **2144** chars; `base_link` + `r_hand` present |
| TF `base_link`→`r_hand` | **x=+0.7200 y=+0.0000 z=+0.4500** |
| TF `base_link`→`torso` | **z=+0.1000** |

---

## Conclusion

**Supported.** The fixed URDF is a single rooted tree, loaded as `robot_description`, and realized as TF without joint states.
