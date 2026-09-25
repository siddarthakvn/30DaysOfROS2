# Investigation C — Xacro left/right arms

## Engineering question

Can one Xacro macro generate a symmetric two-arm humanoid without duplicating the arm XML?

---

## Hypothesis

**H4:** Expanding `humanoid.urdf.xacro` yields mirrored `l_*` / `r_*` links and joints; at zero joint states the hands mirror in X.

---

## Setup

```bash
xacro xacro/humanoid.urdf.xacro > /tmp/humanoid.urdf
check_urdf /tmp/humanoid.urdf

ros2 launch launch/display.launch.py \
  model:=xacro/humanoid.urdf.xacro use_joint_demo:=true \
  joint_mode:=zero \
  joints:=r_shoulder,r_elbow,l_shoulder,l_elbow
```

---

## Expected

| Check | Expect |
|---|---|
| Expand | both `l_shoulder` and `r_shoulder` |
| `check_urdf` | one root; two arm branches |
| TF | `r_hand` and `l_hand` mirrored in X |

---

## Actual results

Evidence: [`../assets/C.log`](../assets/C.log), expanded file [`../assets/humanoid_xacro_expanded.urdf`](../assets/humanoid_xacro_expanded.urdf)

| Check | Observed |
|---|---|
| Tree | torso → `l_upper_arm` and `r_upper_arm` |
| Names | `r_shoulder` **1**, `l_shoulder` **1** |
| TF `r_hand` | **x=+0.7200** |
| TF `l_hand` | **x=-0.7200** |

Same Z, opposite X — macro `reflect=±1` worked.

---

## Conclusion

**Supported.** Xacro is authoring convenience; the runtime model is still URDF. One macro, two arms, no silent left/right copy-paste drift.
