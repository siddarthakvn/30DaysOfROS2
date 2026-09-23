# Investigation A — One-command multi-node bringup

## Hypothesis

**H1/H2:** One `ros2 launch` starts multiple nodes under a namespace and applies parameters.

## Command

```bash
ros2 launch launch/bringup.launch.py
```

## Actual results

See [`../assets/A.log`](../assets/A.log).

| Check | Observed |
|---|---|
| Processes | lidar, imu, camera, control started |
| Nodes | `/robot1/camera_stub`, `imu_stub`, `lidar_stub`, `control_stub` |
| Topics | `/robot1/scan`, `/imu`, `/image`, `/cmd_vel` |
| Param `speed` | **0.25** |

## Conclusion

**Supported.** One command brought up the stub robot stack.
