# Investigation B — Revolute joints + joint states

## Engineering question

Do joint type + joint states change where a link sits in TF?

---

## Hypothesis

**H2 / H3 / H6:** With `r_shoulder` / `r_elbow` as revolute joints, different `JointState` poses move `r_hand` relative to `base_link`.

---

## Setup

```bash
# pose 1
ros2 launch launch/display.launch.py \
  model:=urdf/humanoid_movable.urdf use_joint_demo:=true \
  joints:=r_shoulder,r_elbow positions:=0.0,0.0

# pose 2
ros2 launch launch/display.launch.py \
  model:=urdf/humanoid_movable.urdf use_joint_demo:=true \
  joints:=r_shoulder,r_elbow positions:=0.80,1.20
```

Use separate `ROS_DOMAIN_ID`s when comparing back-to-back (stale `/tf_static` from a prior fixed model can mask motion).

---

## Expected

| Pose | Expect |
|---|---|
| shoulder=0, elbow=0 | hand near the straight-arm fixed pose |
| shoulder=0.80, elbow=1.20 | hand translation **changes** |

---

## Actual results

Evidence: [`../assets/B.log`](../assets/B.log)

| Pose | `base_link` → `r_hand` |
|---|---|
| 0.0 / 0.0 | **x=+0.7200 y=+0.0000 z=+0.4500** |
| 0.80 / 1.20 | **x=+0.2325 y=+0.0000 z=-0.0198** |

---

## Conclusion

**Supported.** Same URDF tree; only joint states changed — the hand frame moved. URDF defines *what can move*; joint states define *where it is now*.
