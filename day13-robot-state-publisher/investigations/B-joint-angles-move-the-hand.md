# Investigation B — Joint angles move the hand

## Hypothesis

**H2 / H3:** Publishing `/joint_states` lets `robot_state_publisher` fill the revolute chain, and a new angle moves the hand.

## Setup

```bash
ros2 launch launch/tree.launch.py use_joint_angles:=true shoulder:=0.0 elbow:=0.0
ros2 launch launch/tree.launch.py use_joint_angles:=true shoulder:=0.80 elbow:=1.20
```

Separate `ROS_DOMAIN_ID`s (`131` and `132`) so a previous `/tf_static` snapshot cannot mask the pose.

## Actual results

Evidence: [`../assets/B.log`](../assets/B.log)

| Pose (shoulder, elbow) | `base_link` → `hand` |
|---|---|
| 0.0, 0.0 | **x=+0.6000 y=0 z=+0.4200** |
| 0.80, 1.20 | **x=+0.1752 y=0 z=+0.0009** |

## Conclusion

**Supported.** The angle node does not publish TF. The hand moved because `robot_state_publisher` consumed `/joint_states` and published `/tf`.
