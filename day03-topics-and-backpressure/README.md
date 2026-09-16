# Day 03 — Topics, Queues, and Backpressure

> **Engineering Question**
>
> **What happens when sensor data is published faster than a robot can process it?**

*(Alternate phrasing: What happens when reality produces information faster than your robot can understand it?)*

---

## The story

On a real robot, the world updates at **sensor rate**. Compute updates at **pipeline rate**. Those are almost never equal.

ROS 2 will **not** slow your sensor to match your brain. Under overload it **buffers**, then — with `KEEP_LAST` — **drops the oldest** samples. A deep queue does not make you thorough; it makes you **late**.

This day proves that with a minimal stand-in:

| Reality | This experiment |
|---|---|
| Camera / LiDAR stream | `frame_camera_pub` @ **30 Hz** (`std_msgs/Int32` frame id) |
| Slow detector / planner (~100 ms) | `slow_inference_sub` with `process_ms` sleep |
| Acting on a stale world | Logged **`age_frames`** vs a depth-1 frontier watcher |

---

## Objective

Show that topic overload is a **bounded-history + FIFO-drain** problem:

1. No app-level backpressure on the publisher
2. `KEEP_LAST` depth is a **staleness budget**, not a “never drop” button
3. Depth **1** prefers freshness; depth **10** prefers absorbing backlog (and processing the past)

Full QoS (deadline, lifespan, liveliness, multi-machine loss) is **Day 07** — here we only touch history/depth and a light reliability contrast.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| RMW (pinned) | `rmw_fastrtps_cpp` (Fast DDS) |
| Domain | `ROS_DOMAIN_ID=30` |
| Scope | One host (localhost) |

### Pin middleware (every terminal)

```bash
cd day03-topics-and-backpressure/ros2_nodes
source ./env.sh
ros2 daemon stop
ros2 doctor --report | grep -i rmw
# expect: rmw_fastrtps_cpp
```

---

## Learning objectives

- What a ROS 2 “queue” actually is (QoS History + Depth)
- Publisher vs subscription history under overload
- Oldest-drop behavior of `KEEP_LAST`
- Why FIFO among cached samples creates **staleness**
- Why real-time stacks often prefer dropping frames to staying fresh

### Key terms (one line each)

| Term | Meaning |
|---|---|
| **depth** | Max unread frames kept in the subscription queue (`KEEP_LAST` size) |
| **process_ms** | Fake inference sleep per frame (brain speed) |
| **gap** | Frame IDs skipped since the last processed frame |
| **age_frames** | How many frames behind “live” the frame you’re processing is |

---

## Investigations

| ID | Title | File |
|---|---|---|
| **A** | The firehose does not wait | [investigations/A-firehose-no-backpressure.md](investigations/A-firehose-no-backpressure.md) |
| **B** | Deep queue = high-latency zombie (hero) | [investigations/B-queue-depth-vs-staleness.md](investigations/B-queue-depth-vs-staleness.md) |
| **C** | Sensor QoS contrast (light) | [investigations/C-sensor-qos-contrast.md](investigations/C-sensor-qos-contrast.md) |

Quick command sheets: `ros2_nodes/run_A.sh`, `run_B.sh`, `run_C.sh` (print procedures).

---

## Nodes

| Node | Role |
|---|---|
| `frame_camera_pub.py` | Publishes increasing frame ids on `/perception/frames` |
| `slow_inference_sub.py` | Slow callback + depth-1 frontier watcher; logs `gap` and `age_frames` |

Shared QoS builder: `qos_utils.py`.

---

## Reproduction (quick start — Investigation A1)

```bash
cd day03-topics-and-backpressure/ros2_nodes
source ./env.sh
ros2 daemon stop

# Terminal 1
python3 frame_camera_pub.py --ros-args \
  -p publish_hz:=30.0 -p depth:=10 -p reliability:=reliable

# Terminal 2
python3 slow_inference_sub.py --ros-args \
  -p process_ms:=100 -p depth:=10 -p reliability:=reliable
```

Watch for: `PUB ... measured_hz≈30`, `STATS process_hz≈10`, `gap>0`, `age_frames` saturating.

---

## Actual results (summary)

Observed 2026-09-15 · Fast DDS · domain 30 · evidence under `assets/`.

| Run | What changed | Key observation |
|---|---|---|
| A0 | `process_ms=25` | 30 Hz both sides; gap=0; age=0 |
| A1 | `process_ms=100`, depth=10 | Pub **stays 30 Hz**; process ~10 Hz; gaps; age~**12** |
| B1 | depth=**1** | Same overload; age~**3** (fresher) |
| B2 | depth=**10** | Same overload; age~**12** (staler) |
| C1 | depth=5, RELIABLE | age~**7** |
| C2 | depth=5, BEST_EFFORT | age~**7** ≈ C1 on localhost |

Rates looked “the same” under overload on purpose. **`age_frames`** was the metric that moved with depth.

---

## Engineering takeaway

**When the sensor is faster than the robot can think, ROS 2 does not slow the sensor.**  
With `KEEP_LAST`, unread frames fill a queue of size **depth**; then **oldest** are dropped. You still process what remains in order — so a deep queue makes you **late**, not thorough.

For live autonomy, prefer a **small depth** (often 1) and drop frames on purpose. Save large queues for paths that need fewer gaps and can tolerate staleness. Reliability is a separate loss path; on localhost it did not change the story.

---

## Interview prep

See [interview_questions.md](interview_questions.md).

## References

See [references.md](references.md).
