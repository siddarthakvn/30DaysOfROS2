# Investigation C — Forward moves, sideways does not

## Hypothesis

**H4 / H5:** With the bridge up, `linear.x = 0.5` changes the model pose. `linear.y = 0.5` does not strafe it.

## Setup

Bridge:

```text
/model/vehicle_blue/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
```

The `]` direction is ROS → Gazebo. Message type is `gz.msgs.Twist` because this machine runs Gazebo Harmonic, not the Fortress `ignition.msgs` type in the Humble tutorial.

Sequence: pose, key `i` for 3 s, stop, then `linear.y` only for 3 s.

The world caps `vehicle_blue` at `0.5` m/s linear, which matches the teleop default speed.

## Actual results

Evidence: [`../assets/C.log`](../assets/C.log)

| Sample | Pose x (m) | Pose y (m) |
|---|---|---|
| Before | ~0 | ~0 |
| After `i` (`linear.x=0.5`) | **1.71** | ~0 |
| After stop | **2.06** | ~0 |
| After `linear.y=0.5` | **2.06** | ~0 |

The extra motion between “after i” and “after stop” is the robot decelerating. The sideways command does not add x or y after that.

Gazebo Transport then shows a publisher on `/model/vehicle_blue/cmd_vel`. That publisher was absent in Investigation B.

## Conclusion

**Supported.** Diff-drive spends `linear.x` on the wheels. `linear.y` is published and ignored. The bridge is what made the forward command visible to the plugin.
