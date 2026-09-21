# Investigation B — MultiThreadedExecutor + Shared MutEx Group

## Engineering question

Does switching to `MultiThreadedExecutor` alone fix starvation if all callbacks share one MutuallyExclusive callback group?

---

## Hypotheses

**H2/H3:** MultiThreaded + **shared** MutEx group still serializes — `during_lidar ≈ 0`, `max_active_callbacks = 1`.

**H5:** LiDAR duration remains ≈ 500 ms.

---

## Why this matters

A common misconception: “I enabled MultiThreadedExecutor, so my IMU is safe.”

Official ROS 2 guidance: if everything uses the same MutuallyExclusive group (including the **default** group), the node still behaves as if it were single-threaded for concurrency.

---

## Setup

| | |
|---|---|
| Executor | `MultiThreadedExecutor(num_threads=4)` |
| Callback groups | **One shared** `MutuallyExclusiveCallbackGroup` for IMU + control + LiDAR |
| Workload | Same as Investigation A |

```bash
cd day08-executors/ros2_nodes
source ./env.sh

python3 lidar_pub.py --ros-args -p period_sec:=1.5 -p warmup_sec:=1.0 -p count:=4

python3 busy_robot_node.py --ros-args \
  -p executor:=multi -p num_threads:=4 -p group_mode:=shared_mutex \
  -p lidar_block_ms:=500 -p run_sec:=8.0
```

---

## Expected results

Same starvation signature as A despite four threads.

---

## Actual results

Evidence: [`../assets/B.log`](../assets/B.log)

| Metric | Observed |
|---|---|
| LiDAR blocks | 4 @ avg **500.5 ms** |
| IMU `during_lidar` | **0** |
| IMU `max_gap_ms` | **514.7** |
| CONTROL `during_lidar` | **0** |
| CONTROL `max_gap_ms` | **524.6** |
| `max_active_callbacks` | **1** |

---

## Analysis

Threads existed. The MutuallyExclusive group refused to let IMU or control begin while LiDAR held the group. Extra threads sat idle for this node’s callbacks.

---

## Conclusion

**H2/H3 supported.** MultiThreadedExecutor without callback-group design does not solve blocking.
