# Investigation B — Namespace launch argument

## Hypothesis

**H3/H5:** `namespace:=robot2` places the same stubs under `/robot2/...`.

## Command

```bash
ros2 launch launch/bringup.launch.py namespace:=robot2
```

## Actual results

See [`../assets/B.log`](../assets/B.log).

| Check | Observed |
|---|---|
| Process logs | `[robot2.lidar_stub]`, `[robot2.control_stub]`, … |
| Nodes | `/robot2/camera_stub`, `/robot2/control_stub`, `/robot2/imu_stub`, `/robot2/lidar_stub` |
| Topics | `/robot2/cmd_vel`, `/robot2/scan`, `/robot2/imu` |
| Param | `/robot2/control_stub speed` = **0.25** |

Note: if a prior launch’s children were not fully killed, `/robot1/*` may still appear in `ros2 node list`. The **process start log** is the ground truth for this run’s `robot2` bringup.

## Conclusion

**Supported.** Launch arguments reuse the same architecture under a different namespace.
