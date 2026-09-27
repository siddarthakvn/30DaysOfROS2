# Investigation A — RSP with no joint states

## Hypothesis

**H1:** Fixed links appear without `/joint_states`. The revolute chain to the hand does not.

## Setup

```bash
ros2 launch launch/tree.launch.py use_joint_angles:=false
```

## Actual results

Evidence: [`../assets/A.log`](../assets/A.log)

| Check | Observed |
|---|---|
| Nodes | `/robot_state_publisher` only |
| `/tf` publisher | `robot_state_publisher` (volatile) |
| `/tf_static` publisher | `robot_state_publisher` (`TRANSIENT_LOCAL`) |
| `/joint_states` publishers | **0** (RSP is a subscriber) |
| `base_link` → `torso` | **(0, 0, 0.10)** fixed |
| `forearm` → `hand` | **(0.24, 0, 0)** fixed wrist |
| `base_link` → `hand` | **NOT_AVAILABLE** |
| `map` → `base_link` | **NOT_AVAILABLE** |

## Conclusion

**Supported.** The publisher can advertise `/tf` and still leave a hole where revolute joints have no angles. Fixed joints are already on `/tf_static`.
