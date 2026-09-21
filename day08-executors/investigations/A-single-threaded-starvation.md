# Investigation A — SingleThreadedExecutor Starvation

## Engineering question

With a `SingleThreadedExecutor`, does a 500 ms LiDAR callback delay IMU (10 ms) and control (20 ms) callbacks on the same executor?

---

## Hypotheses

**H1:** During the LiDAR sleep, IMU/control `during_lidar ≈ 0` and `max_gap_ms` approaches ~500 ms.

**H5:** LiDAR callback duration stays ≈ 500 ms (executor type does not shrink the work).

**H6:** Topics/QoS are healthy — this is a processing-capacity failure, not a DDS failure.

---

## Setup

| | |
|---|---|
| Executor | `SingleThreadedExecutor` |
| Callback groups | Node default (MutuallyExclusive) |
| IMU timer | 10 ms |
| Control timer | 20 ms |
| LiDAR block | `time.sleep(0.5)` per scan |
| LiDAR publishes | 4 scans after 1 s warmup |

```bash
cd day08-executors/ros2_nodes
source ./env.sh
bash run_A.sh

# Terminal 1
python3 lidar_pub.py --ros-args -p period_sec:=1.5 -p warmup_sec:=1.0 -p count:=4

# Terminal 2
python3 busy_robot_node.py --ros-args \
  -p executor:=single -p group_mode:=default \
  -p lidar_block_ms:=500 -p run_sec:=8.0
```

Or: `cd day08-executors && ./run_smoke.sh`

---

## Expected results

| Metric | Expect |
|---|---|
| `during_lidar` (IMU/control) | ≈ 0 |
| `max_gap_ms` (IMU) | ≈ 500+ |
| `max_active_callbacks` | 1 |
| LiDAR duration | ≈ 500 ms |

---

## Actual results

Evidence: [`../assets/A.log`](../assets/A.log)

| Metric | Observed |
|---|---|
| LiDAR blocks | 4 @ avg **500.4 ms** |
| IMU `during_lidar` | **0** |
| IMU `max_gap_ms` | **507.9** |
| CONTROL `during_lidar` | **0** |
| CONTROL `max_gap_ms` | **517.9** |
| `max_active_callbacks` | **1** |
| Missed deadlines (`>2×` period) | 4 (one per LiDAR block) |

---

## Analysis

One executor thread. While LiDAR slept, nothing else could run. IMU and control recovered between blocks (median gaps stayed nominal), but each block punched a ~500 ms hole in the timeline — exactly the starvation pattern.

---

## Conclusion

**H1 supported.** On a SingleThreadedExecutor, a long callback can stall the entire node’s ROS callbacks.
