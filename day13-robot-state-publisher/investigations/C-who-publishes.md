# Investigation C — Who publishes what

## Hypothesis

**H4 / H5:** The angle node owns `/joint_states` only. `robot_state_publisher` owns `/tf` and `/tf_static`. It does not create `map` or `odom`.

## Setup

```bash
ros2 launch launch/tree.launch.py use_joint_angles:=true shoulder:=0.40 elbow:=0.50
ros2 topic info /tf -v
ros2 topic info /tf_static -v
ros2 topic info /joint_states -v
```

## Actual results

Evidence: [`../assets/C.log`](../assets/C.log)

| Topic | Publisher | Subscriber |
|---|---|---|
| `/tf` | `robot_state_publisher` (volatile) | — |
| `/tf_static` | `robot_state_publisher` (`TRANSIENT_LOCAL`) | — |
| `/joint_states` | `joint_angles` | `robot_state_publisher` |

`map` → `base_link` and `odom` → `base_link` stayed **NOT_AVAILABLE**.

The first smoke pass printed `Unknown topic` for this census while earlier launches were still exiting. The table above is the clean recapture on `ROS_DOMAIN_ID=133`.

## Conclusion

**Supported.** Angles and frames are different nodes. The robot tree publisher is `robot_state_publisher`. World frames stay someone else's job.
