# Investigation C — Separate Callback Groups (Hero)

## Engineering question

With a `MultiThreadedExecutor`, can IMU and control keep meeting their periods while LiDAR blocks for 500 ms — if each lives in a **different** MutuallyExclusive callback group?

---

## Hypotheses

**H4:** Different MutEx groups + MultiThreaded → IMU/control run during LiDAR (`during_lidar >> 0`).

**H5:** LiDAR duration still ≈ 500 ms (concurrency ≠ faster work).

---

## Setup

| | |
|---|---|
| Executor | `MultiThreadedExecutor(num_threads=4)` |
| Callback groups | **Separate** MutEx group per entity (IMU / control / LiDAR) |
| Workload | Same as A/B |

```bash
cd day08-executors/ros2_nodes
source ./env.sh

python3 lidar_pub.py --ros-args -p period_sec:=1.5 -p warmup_sec:=1.0 -p count:=4

python3 busy_robot_node.py --ros-args \
  -p executor:=multi -p num_threads:=4 -p group_mode:=separate_mutex \
  -p lidar_block_ms:=500 -p run_sec:=8.0
```

---

## Expected results

| Metric | Expect |
|---|---|
| IMU `during_lidar` | ≫ 0 (order of ~50 per 500 ms block × 4) |
| IMU `max_gap_ms` | near nominal (~10 ms) |
| `max_active_callbacks` | ≥ 2 |
| LiDAR duration | still ≈ 500 ms |

---

## Actual results

Evidence: [`../assets/C.log`](../assets/C.log) · comparison: [`../assets/comparison.txt`](../assets/comparison.txt)

| Metric | Observed |
|---|---|
| LiDAR blocks | 4 @ avg **500.6 ms** |
| IMU `during_lidar` | **200** |
| IMU `max_gap_ms` | **10.5** |
| CONTROL `during_lidar` | **100** |
| CONTROL `max_gap_ms` | **20.7** |
| `max_active_callbacks` | **2** |
| Missed deadlines | **0** |

---

## Analysis

Same 500 ms LiDAR sleep. Different outcome: IMU and control kept their periods because the executor could schedule them on other threads while LiDAR occupied its own group.

Rough check: 4 × 500 ms = 2.0 s of LiDAR-busy time → ~200 IMU ticks @ 10 ms and ~100 control ticks @ 20 ms — matches the counters.

---

## Conclusion

**H4 and H5 supported.** Concurrency requires **both** threads and permissive callback-group configuration. The slow callback itself remains slow.
