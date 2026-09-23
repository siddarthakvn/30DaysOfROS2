# Investigation C — Conditional camera

## Hypothesis

**H8:** `use_camera:=false` skips starting the camera stub.

## Command

```bash
ros2 launch launch/bringup.launch.py namespace:=robot1 use_camera:=false
```

## Actual results

See [`../assets/C.log`](../assets/C.log).

| Check | Observed |
|---|---|
| Processes started | lidar, imu, control only |
| `start_camera_stub` | **absent** |
| Camera publishing line | **absent** |

## Conclusion

**Supported.** Conditional launch toggles optional subsystems without editing the launch file.
